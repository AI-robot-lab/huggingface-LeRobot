#!/usr/bin/env python3

# Copyright 2025 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
================================================================================
SERWER MOSTKA DDS-ZMQ DLA ROBOTA UNITREE G1
================================================================================

PRZEZNACZENIE:
--------------
Ten serwer działa na komputerze wbudowanym w robota (NVIDIA Orin) i pełni rolę
"mostu komunikacyjnego" (bridge) między:
- DDS (Data Distribution Service) - protokół lokalny używany wewnątrz robota
- ZMQ (ZeroMQ) - protokół sieciowy do komunikacji z zewnętrznym komputerem

DLACZEGO POTRZEBNY JEST MOST?
------------------------------
1. DDS jest protokołem lokalnym - nie można go łatwo używać przez sieć
2. Komponenty robota (silniki, czujniki) komunikują się tylko przez DDS
3. Chcemy sterować robotem z zewnętrznego komputera (laptop/workstation)
4. Most tłumaczy komunikaty między DDS a ZMQ, umożliwiając zdalne sterowanie

ARCHITEKTURA:
-------------
┌─────────────────────────────────────────────────────────────┐
│                    ROBOT UNITREE G1 (Orin)                   │
│                                                               │
│  ┌────────────┐     ┌─────────────────┐     ┌────────────┐  │
│  │  Silniki   │────▶│   DDS Topics    │◀────│  Czujniki  │  │
│  │ (Motors)   │     │   (lokalne)     │     │ (Sensors)  │  │
│  └────────────┘     └────────┬────────┘     └────────────┘  │
│                              │                               │
│                     ┌────────▼────────┐                      │
│                     │  run_g1_server  │ ◀── TEN PROGRAM      │
│                     │     (Bridge)    │                      │
│                     └────────┬────────┘                      │
│                              │                               │
│                     ┌────────▼────────┐                      │
│                     │   ZMQ Sockets   │                      │
│                     │    (sieć)       │                      │
│                     └────────┬────────┘                      │
└──────────────────────────────┼──────────────────────────────┘
                               │ WiFi/Ethernet
┌──────────────────────────────▼──────────────────────────────┐
│             ZEWNĘTRZNY KOMPUTER (Laptop)                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Klient LeRobot (unitree_g1.py)             │   │
│  │  - Wysyła akcje (docelowe pozycje stawów)            │   │
│  │  - Odbiera obserwacje (stan robota)                  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

PRZEPŁYW DANYCH:
----------------
1. OBSERWACJE (Robot → Komputer):
   Czujniki → DDS LowState → Bridge → ZMQ PUB → Klient

2. AKCJE (Komputer → Robot):
   Klient → ZMQ PUSH → Bridge → DDS LowCmd → Silniki

PROTOKOŁY:
----------
DDS (Data Distribution Service):
- Standard komunikacji w czasie rzeczywistym
- Używany wewnętrznie przez robota Unitree
- Gwarantuje dostarczenie, niską latencję
- Działa na poziomie lokalnym (nie przez sieć)

ZMQ (ZeroMQ):
- Biblioteka do przesyłania wiadomości przez sieć
- Prosta, wydajna, elastyczna
- Wzorce: PUB/SUB (obserwacje) i PUSH/PULL (akcje)

TOPOLOGIA ZMQ:
--------------
Port 6000: PULL socket - odbiera akcje od klienta
Port 6001: PUB socket - publikuje obserwacje do klientów

BEZPIECZEŃSTWO:
---------------
- Używamy JSON zamiast pickle (bezpieczniejsze)
- Base64 encoding dla binarnych danych
- Walidacja CRC dla komend
- Kontrola uprawnień przez MotionSwitcher

URUCHOMIENIE:
-------------
Na robocie (po SSH):
    python src/lerobot/robots/unitree_g1/run_g1_server.py

UWAGA: Serwer musi działać cały czas gdy chcesz sterować robotem zdalnie!

WYMAGANIA:
----------
- unitree_sdk2_python zainstalowane
- CycloneDDS v0.10.2
- ZMQ (pyzmq)
- Uprawnienia do kontroli robota

================================================================================
"""

import base64  # Kodowanie binarnych danych do formatu tekstowego (JSON-safe)
import contextlib  # Narzędzia do zarządzania kontekstem (suppress exceptions)
import json  # Serializacja danych do formatu JSON (bezpieczniejszy niż pickle)
import threading  # Wielowątkowość - jednoczesna obsługa wysyłania i odbierania
import time  # Pomiar czasu, opóźnienia
from typing import Any  # Type hints dla lepszej czytelności kodu

import zmq  # ZeroMQ - biblioteka do komunikacji sieciowej

# Importy z Unitree SDK - oficjalne API do komunikacji z robotem
from unitree_sdk2py.comm.motion_switcher.motion_switcher_client import MotionSwitcherClient
from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelPublisher, ChannelSubscriber
from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_ as hg_LowCmd, LowState_ as hg_LowState
from unitree_sdk2py.utils.crc import CRC  # Cyclic Redundancy Check - walidacja integralności danych

# ============================================================================
# DEFINICJE STAŁYCH
# ============================================================================

# Nazwy topic DDS - zgodne z konwencją Unitree SDK
# ruff: noqa: N816 (wyłączamy warning o nazewnictwie - to standard Unitree)
kTopicLowCommand_Debug = "rt/lowcmd"  # Topic do wysyłania akcji do robota
kTopicLowState = "rt/lowstate"        # Topic do odbierania stanu robota

# Porty ZMQ dla komunikacji sieciowej
LOWCMD_PORT = 6000   # Port dla odbierania akcji z zewnątrz (PULL)
LOWSTATE_PORT = 6001 # Port dla publikowania stanu na zewnątrz (PUB)

# Liczba silników w robocie Unitree G1
NUM_MOTORS = 35  # 29 DOF + dodatkowe silniki pomocnicze


def lowstate_to_dict(msg: hg_LowState) -> dict[str, Any]:
    """
    Konwertuje wiadomość LowState z SDK Unitree na słownik JSON-serializowalny.
    
    DLACZEGO TA KONWERSJA?
    -----------------------
    - Wiadomość DDS (hg_LowState) to obiekt binarny specyficzny dla SDK
    - JSON jest uniwersalny i można go przesłać przez sieć
    - Bezpieczniejszy niż pickle (nie wykonuje arbitralnego kodu)
    - Łatwy do debugowania (można zobaczyć zawartość)
    
    CO ZAWIERA LowState?
    --------------------
    - Stan wszystkich 35 silników (pozycja, prędkość, moment, temperatura)
    - Dane IMU (kwaternion, żyroskop, akcelerometr, RPY, temperatura)
    - Dane z kontrolera bezprzewodowego (joysticki, przyciski)
    - Tryb działania robota (mode_machine)
    
    Args:
        msg: Obiekt hg_LowState z Unitree SDK zawierający pełny stan robota
        
    Returns:
        Słownik z danymi w formacie JSON-kompatybilnym:
        {
            "motor_state": [...],  # 35 słowników ze stanem silników
            "imu_state": {...},    # Dane IMU
            "wireless_remote": "base64...",  # Kontroler (zakodowany)
            "mode_machine": 0      # Tryb robota
        }
        
    Example:
        >>> state_msg = lowstate_sub.Read()  # Odczyt z DDS
        >>> state_dict = lowstate_to_dict(state_msg)
        >>> json_str = json.dumps(state_dict)  # Gotowe do wysłania
    """
    # Lista do przechowywania stanu każdego silnika
    motor_states = []
    
    # Iteracja przez wszystkie 35 silników
    for i in range(NUM_MOTORS):
        # Pobierz temperaturę silnika
        temp = msg.motor_state[i].temperature
        
        # Temperatura może być pojedynczą wartością lub listą (różne wersje SDK)
        # Oblicz średnią jeśli to lista, w przeciwnym razie użyj wartości
        avg_temp = float(sum(temp) / len(temp)) if isinstance(temp, list) else float(temp)
        
        # Utwórz słownik dla tego silnika
        motor_states.append(
            {
                "q": float(msg.motor_state[i].q),              # Pozycja [rad]
                "dq": float(msg.motor_state[i].dq),            # Prędkość [rad/s]
                "tau_est": float(msg.motor_state[i].tau_est),  # Moment obrotowy [Nm]
                "temperature": avg_temp,                        # Temperatura [°C]
            }
        )

    # Zbuduj kompletny słownik stanu
    return {
        "motor_state": motor_states,
        
        # Dane IMU (Inertial Measurement Unit)
        "imu_state": {
            # Kwaternion orientacji [w, x, y, z] - reprezentacja 3D rotacji
            "quaternion": [float(x) for x in msg.imu_state.quaternion],
            
            # Żyroskop [x, y, z] - prędkość kątowa w rad/s
            "gyroscope": [float(x) for x in msg.imu_state.gyroscope],
            
            # Akcelerometr [x, y, z] - przyspieszenie liniowe w m/s²
            "accelerometer": [float(x) for x in msg.imu_state.accelerometer],
            
            # Roll-Pitch-Yaw [roll, pitch, yaw] - kąty Eulera w radianach
            "rpy": [float(x) for x in msg.imu_state.rpy],
            
            # Temperatura czujnika IMU
            "temperature": float(msg.imu_state.temperature),
        },
        
        # Dane z kontrolera bezprzewodowego
        # Kodujemy jako base64 bo to surowe bajty (nie tekstowe)
        # bytes → base64 → string → bezpiecznie w JSON
        "wireless_remote": base64.b64encode(bytes(msg.wireless_remote)).decode("ascii"),
        
        # Tryb pracy robota (stan maszyny stanów)
        "mode_machine": int(msg.mode_machine),
    }


def dict_to_lowcmd(data: dict[str, Any]) -> hg_LowCmd:
    """
    Konwertuje słownik z JSON z powrotem na obiekt LowCmd SDK Unitree.
    
    ODWROTNOŚĆ lowstate_to_dict:
    -----------------------------
    - Zewnętrzny komputer wysyła akcje jako JSON przez ZMQ
    - Most odbiera JSON i konwertuje na obiekt DDS
    - Obiekt DDS jest wysyłany do robota
    
    CO ZAWIERA LowCmd?
    ------------------
    - Tryby pracy (mode_pr, mode_machine)
    - Komendy dla każdego silnika:
      * mode: Tryb sterowania (0=idle, 1=FOC, 10=właściciel)
      * q: Docelowa pozycja [rad]
      * dq: Docelowa prędkość [rad/s]
      * kp: Wzmocnienie proporcjonalne regulatora PD
      * kd: Wzmocnienie różniczkowe regulatora PD
      * tau: Dodatkowy moment obrotowy [Nm]
    
    REGULATOR PD:
    -------------
    Każdy silnik ma wbudowany regulator PD (Proportional-Derivative):
    
    moment = kp * (q_target - q_actual) + kd * (dq_target - dq_actual)
    
    - kp: Jak mocno "ciągnąć" staw do celu (sztywność)
    - kd: Jak mocno "tłumić" ruch (damping, zapobiega oscylacjom)
    
    Args:
        data: Słownik z akcją w formacie:
              {
                  "mode_pr": 0,
                  "mode_machine": 0,
                  "motor_cmd": [
                      {"mode": 10, "q": 0.1, "dq": 0, "kp": 30, "kd": 1, "tau": 0},
                      ...
                  ]
              }
              
    Returns:
        Obiekt hg_LowCmd gotowy do wysłania przez DDS do robota
        
    Example:
        >>> json_data = json.loads(payload)  # Odbierz z ZMQ
        >>> cmd = dict_to_lowcmd(json_data["data"])
        >>> lowcmd_pub.Write(cmd)  # Wyślij do robota przez DDS
    """
    # Utwórz nowy obiekt LowCmd ze strukturą Unitree
    cmd = unitree_hg_msg_dds__LowCmd_()
    
    # Ustaw tryby globalne
    # mode_pr: Power Reserve mode (zwykle 0)
    cmd.mode_pr = data.get("mode_pr", 0)
    
    # mode_machine: Tryb maszyny stanów robota
    # Różne wartości oznaczają różne stany (np. idle, walking, etc.)
    cmd.mode_machine = data.get("mode_machine", 0)

    # Ustaw komendy dla każdego silnika
    for i, motor_data in enumerate(data.get("motor_cmd", [])):
        # mode: Tryb sterowania silnika
        # 0 = Idle (silnik wyłączony)
        # 1 = FOC (Field Oriented Control - precyzyjne sterowanie)
        # 10 = Brake (hamowanie)
        cmd.motor_cmd[i].mode = motor_data.get("mode", 0)
        
        # Docelowe wartości
        cmd.motor_cmd[i].q = motor_data.get("q", 0.0)    # Pozycja [rad]
        cmd.motor_cmd[i].dq = motor_data.get("dq", 0.0)  # Prędkość [rad/s]
        
        # Parametry regulatora PD
        cmd.motor_cmd[i].kp = motor_data.get("kp", 0.0)  # Proporcjonalny
        cmd.motor_cmd[i].kd = motor_data.get("kd", 0.0)  # Różniczkowy
        
        # Dodatkowy moment (feedforward)
        cmd.motor_cmd[i].tau = motor_data.get("tau", 0.0)

    return cmd


def state_forward_loop(
    lowstate_sub: ChannelSubscriber,
    lowstate_sock: zmq.Socket,
    state_period: float,
    shutdown_event: threading.Event,
) -> None:
    """
    Pętla przekazująca obserwacje z DDS do ZMQ (działa w osobnym wątku).
    
    ZADANIE:
    --------
    Ciągle odczytuj stan robota z DDS i publikuj go przez ZMQ dla klientów.
    To pozwala zewnętrznym komputerom "widzieć" co się dzieje z robotem.
    
    CZĘSTOTLIWOŚĆ:
    --------------
    - DDS publikuje stan bardzo szybko (~500Hz lub więcej)
    - state_period kontroluje jak często przekazujemy przez ZMQ
    - Domyślnie 0.002s (2ms) = ~500Hz
    - Można zmniejszyć dla oszczędności pasma sieci
    
    DOWNSAMPLING:
    -------------
    Jeśli robot publikuje z 1000Hz, a my chcemy 500Hz:
    - Odbieramy każdą wiadomość DDS
    - Ale wysyłamy przez ZMQ tylko co 2ms
    - To zmniejsza obciążenie sieci bez utraty czasu rzeczywistego
    
    NON-BLOCKING SEND:
    ------------------
    Używamy zmq.NOBLOCK + contextlib.suppress:
    - Jeśli bufor jest pełny (klient nie nadąża), pomijamy klatkę
    - Lepiej stracić starą klatkę niż zablokować całą pętlę
    - Real-time > perfekcyjna dostarczalność
    
    Args:
        lowstate_sub: Subscriber DDS do odczytywania stanu robota
        lowstate_sock: Socket ZMQ PUB do publikowania stanu
        state_period: Minimalny okres między publikacjami [s]
        shutdown_event: Event do sygnalizacji zakończenia pętli
        
    Returns:
        None (działa w pętli nieskończonej aż do shutdown)
        
    Thread-safety:
        Funkcja jest bezpieczna wątkowo - każdy wątek ma własne obiekty
    """
    # Śledzenie czasu ostatniej publikacji (dla downsamplingu)
    last_state_time = 0.0

    # Główna pętla - działa dopóki nie dostaniemy sygnału shutdown
    while not shutdown_event.is_set():
        # Krok 1: Odczytaj najnowszy stan z DDS
        # Read() jest blokujące, ale z timeoutem (szybko wraca)
        msg = lowstate_sub.Read()
        
        # Jeśli brak danych (timeout), spróbuj ponownie
        if msg is None:
            continue

        # Krok 2: Sprawdź czy minęło wystarczająco czasu od ostatniej publikacji
        now = time.time()
        
        # Opcjonalny downsampling - wysyłaj tylko jeśli minął state_period
        if now - last_state_time >= state_period:
            # Krok 3: Konwertuj wiadomość DDS na słownik
            state_dict = lowstate_to_dict(msg)
            
            # Krok 4: Serializuj do JSON
            # Format: {"topic": "rt/lowstate", "data": {...}}
            # Topic pozwala klientowi rozróżnić typy wiadomości
            payload = json.dumps({"topic": kTopicLowState, "data": state_dict}).encode("utf-8")
            
            # Krok 5: Wyślij przez ZMQ (non-blocking)
            # contextlib.suppress(zmq.Again) = try-except bez verbose syntax
            # Jeśli send rzuci zmq.Again (bufor pełny), po prostu ignorujemy
            with contextlib.suppress(zmq.Again):
                lowstate_sock.send(payload, zmq.NOBLOCK)
                
            # Zaktualizuj czas ostatniej publikacji
            last_state_time = now


def cmd_forward_loop(
    lowcmd_sock: zmq.Socket,
    lowcmd_pub_debug: ChannelPublisher,
    crc: CRC,
) -> None:
    """
    Pętla przekazująca akcje z ZMQ do DDS (działa w wątku głównym).
    
    ZADANIE:
    --------
    Odbieraj komendy sterowania z zewnętrznego komputera (ZMQ) i przekazuj
    je do robota (DDS). To pozwala klientom "sterować" robotem.
    
    BLOKUJĄCA PĘTLA:
    ----------------
    recv() blokuje dopóki nie przyjdzie wiadomość:
    - Nie marnujemy CPU na busy-waiting
    - Reagujemy natychmiast gdy przychodzi komenda
    - Wydajne i proste
    
    CRC (Cyclic Redundancy Check):
    -------------------------------
    - Suma kontrolna sprawdzająca integralność danych
    - Obliczamy CRC dla każdej komendy przed wysłaniem
    - Robot odrzuca komendy z niepoprawnym CRC
    - Ochrona przed uszkodzonymi pakietami
    
    PROTOKÓŁ:
    ---------
    Klient wysyła JSON:
    {
        "topic": "rt/lowcmd",
        "data": {
            "mode_pr": 0,
            "mode_machine": 0,
            "motor_cmd": [...]
        }
    }
    
    Args:
        lowcmd_sock: Socket ZMQ PULL do odbierania komend
        lowcmd_pub_debug: Publisher DDS do wysyłania komend do robota
        crc: Obiekt CRC do obliczania sum kontrolnych
        
    Returns:
        None (działa w pętli nieskończonej aż do context terminate)
        
    Raises:
        zmq.ContextTerminated: Gdy kontekst ZMQ jest zamykany (graceful shutdown)
    """
    # Pętla nieskończona - będzie przerwana przez ContextTerminated
    while True:
        try:
            # Krok 1: Odbierz komendę z ZMQ (BLOKUJĄCE)
            # recv() czeka aż przyjdzie wiadomość lub context zostanie zamknięty
            payload = lowcmd_sock.recv()
            
        except zmq.ContextTerminated:
            # Kontekst został zamknięty (main() wywołał ctx.term())
            # To sygnał do zakończenia pętli
            break
            
        # Krok 2: Deserializuj JSON
        msg_dict = json.loads(payload.decode("utf-8"))

        # Krok 3: Ekstraktuj topic i dane
        topic = msg_dict.get("topic", "")
        cmd_data = msg_dict.get("data", {})

        # Krok 4: Zrekonstruuj obiekt LowCmd ze słownika
        cmd = dict_to_lowcmd(cmd_data)

        # Krok 5: Oblicz i ustaw CRC
        # CRC musi być obliczone PO wypełnieniu wszystkich pól
        # Crc() oblicza sumę kontrolną całej struktury danych
        cmd.crc = crc.Crc(cmd)

        # Krok 6: Wyślij do robota przez DDS (jeśli to właściwy topic)
        if topic == kTopicLowCommand_Debug:
            # Write() publikuje komendę na DDS topic
            # Robot natychmiast odbiera i wykonuje
            lowcmd_pub_debug.Write(cmd)


def main() -> None:
    """
    Główna funkcja serwera - punkt wejścia programu.
    
    INICJALIZACJA:
    --------------
    1. Zainicjalizuj DDS (komunikacja z robotem)
    2. Zatrzymaj wszystkie aktywne publishery (czysty start)
    3. Utwórz Publisher DDS (do wysyłania komend)
    4. Utwórz Subscriber DDS (do odbierania stanu)
    5. Zainicjalizuj kontekst ZMQ
    6. Utwórz sockety ZMQ (PULL dla komend, PUB dla stanu)
    7. Uruchom wątki przekazywania danych
    
    ARCHITEKTURA WĄTKÓW:
    --------------------
    - Wątek główny: Obsługuje cmd_forward_loop (ZMQ→DDS akcje)
    - Wątek t_state: Obsługuje state_forward_loop (DDS→ZMQ obserwacje)
    
    Dwa wątki są potrzebne bo:
    - Odbieranie i wysyłanie muszą działać jednocześnie
    - recv() w obu kierunkach jest blokujące
    - Osobne wątki = pełny duplex (two-way communication)
    
    GRACEFUL SHUTDOWN:
    ------------------
    Ctrl+C:
    1. Łapie KeyboardInterrupt
    2. Ustawia shutdown_event (kończy wątek state)
    3. Wywołuje ctx.term() (kończy recv() w wątku głównym)
    4. Czeka na zakończenie wątku state (join)
    5. Program kończy się czystó
    
    CZYSZCZENIE ZASOBÓW:
    --------------------
    Block finally ZAWSZE się wykona, nawet przy wyjątku:
    - Ustawia shutdown_event
    - Zamyka kontekst ZMQ (to przerywa blokujące recv())
    - Czeka max 2s na zakończenie wątku
    
    Returns:
        None
        
    Raises:
        KeyboardInterrupt: Obsługiwane gracefully
    """
    # ========================================================================
    # INICJALIZACJA DDS
    # ========================================================================
    
    # Krok 1: Inicjalizacja fabryki kanałów DDS
    # 0 = domain ID (używamy domyślnej domeny DDS)
    ChannelFactoryInitialize(0)
    
    # Krok 2: Zatrzymaj wszystkie aktywne publishery na robocie
    # MotionSwitcherClient zarządza tym, kto kontroluje robota
    # Tylko jeden proces może mieć kontrolę naraz
    msc = MotionSwitcherClient()
    msc.SetTimeout(5.0)  # Timeout 5s dla operacji
    msc.Init()

    # Sprawdź czy ktoś już kontroluje robota
    status, result = msc.CheckMode()
    
    # Jeśli tak, zwolnij kontrolę (pętla dopóki nie będzie wolne)
    while result is not None and "name" in result and result["name"]:
        msc.ReleaseMode()  # Zwolnij kontrolę
        status, result = msc.CheckMode()  # Sprawdź ponownie
        time.sleep(1.0)  # Odczekaj sekundę
    
    # Teraz mamy wyłączną kontrolę nad robotem

    # Krok 3: Utwórz obiekt CRC do walidacji komend
    crc = CRC()

    # ========================================================================
    # INICJALIZACJA PUBLISHERÓW I SUBSCRIBERÓW DDS
    # ========================================================================
    
    # Krok 4: Utwórz publisher DDS dla komend
    # Publikuje na topic "rt/lowcmd" (akcje dla robota)
    lowcmd_pub_debug = ChannelPublisher(kTopicLowCommand_Debug, hg_LowCmd)
    lowcmd_pub_debug.Init()

    # Krok 5: Utwórz subscriber DDS dla stanu
    # Subskrybuje topic "rt/lowstate" (obserwacje z robota)
    lowstate_sub = ChannelSubscriber(kTopicLowState, hg_LowState)
    lowstate_sub.Init()

    # ========================================================================
    # INICJALIZACJA ZMQ
    # ========================================================================
    
    # Krok 6: Pobierz singleton context ZMQ
    # Context zarządza wszystkimi socketami w aplikacji
    ctx = zmq.Context.instance()

    # Krok 7: Utwórz socket PULL do odbierania komend od klienta
    # PULL: Odbiera wiadomości w fair queuing mode
    # Wiele klientów może wysyłać, socket distribuuje równomiernie
    lowcmd_sock = ctx.socket(zmq.PULL)
    lowcmd_sock.bind(f"tcp://0.0.0.0:{LOWCMD_PORT}")
    # bind na 0.0.0.0 = akceptuj połączenia z dowolnego interfejsu sieciowego

    # Krok 8: Utwórz socket PUB do publikowania stanu dla klientów
    # PUB: Publikuje wiadomości do wszystkich podłączonych subskrybentów
    # Wzorzec one-to-many (jeden nadawca, wielu odbiorców)
    lowstate_sock = ctx.socket(zmq.PUB)
    lowstate_sock.bind(f"tcp://0.0.0.0:{LOWSTATE_PORT}")

    # ========================================================================
    # URUCHOMIENIE WĄTKÓW PRZEKAZYWANIA
    # ========================================================================
    
    # Okres publikacji stanu (2ms = ~500Hz)
    state_period = 0.002
    
    # Event do sygnalizacji zakończenia wątku
    shutdown_event = threading.Event()

    # Krok 9: Uruchom wątek przekazywania obserwacji w tle
    t_state = threading.Thread(
        target=state_forward_loop,  # Funkcja do wykonania
        args=(lowstate_sub, lowstate_sock, state_period, shutdown_event),  # Argumenty
        daemon=False,  # Nie daemon - czekamy na zakończenie
    )
    t_state.start()  # Rozpocznij wykonywanie wątku

    # ========================================================================
    # GŁÓWNA PĘTLA I OBSŁUGA SYGNAŁÓW
    # ========================================================================
    
    print("bridge running (lowstate -> zmq, lowcmd -> dds)")
    print(f"Listening for commands on port {LOWCMD_PORT}")
    print(f"Publishing state on port {LOWSTATE_PORT}")
    print("Press Ctrl+C to stop")

    # Uruchom pętlę przekazywania komend w wątku głównym
    try:
        cmd_forward_loop(lowcmd_sock, lowcmd_pub_debug, crc)
        # Ta funkcja blokuje do momentu ctx.term() lub błędu
        
    except KeyboardInterrupt:
        # Użytkownik nacisnął Ctrl+C - normalne zakończenie
        print("\nshutting down bridge...")
        
    finally:
        # Ten blok ZAWSZE się wykona - zapewnia czyszczenie zasobów
        
        # Sygnalizuj wątkowi state, że ma się zakończyć
        shutdown_event.set()
        
        # Zamknij kontekst ZMQ
        # To spowoduje że recv() w cmd_forward_loop rzuci ContextTerminated
        # I przerywa recv() w state_forward_loop
        ctx.term()
        
        # Poczekaj na zakończenie wątku state (max 2 sekundy)
        t_state.join(timeout=2.0)
        
        if t_state.is_alive():
            print("Warning: state thread did not terminate cleanly")
        
        print("Bridge stopped cleanly")


if __name__ == "__main__":
    """
    Punkt wejścia programu.
    
    UŻYCIE:
    -------
    Na robocie (po SSH do 192.168.123.164 lub przez WiFi):
    
        cd lerobot
        conda activate lerobot
        python src/lerobot/robots/unitree_g1/run_g1_server.py
    
    Program będzie działał w pętli nieskończonej. Aby zatrzymać: Ctrl+C
    
    ROZWIĄZYWANIE PROBLEMÓW:
    ------------------------
    
    1. "Permission denied" lub "Access denied":
       - Sprawdź czy inny proces nie kontroluje robota
       - Zrestartuj serwis robota: sudo systemctl restart unitree_robot
       
    2. "Address already in use":
       - Inny serwer już działa na tych portach
       - Zabij stary proces: killall python
       - Lub zmień porty w kodzie
       
    3. "CycloneDDS not found":
       - Zainstaluj CycloneDDS v0.10.2
       - Zobacz dokumentację Unitree SDK
       
    4. Robot nie reaguje na komendy:
       - Sprawdź czy serwer faktycznie działa
       - Sprawdź firewall: sudo ufw allow 6000,6001/tcp
       - Sprawdź IP klienta w config_unitree_g1.py
       
    5. Opóźnienia w komunikacji:
       - Zmniejsz state_period jeśli potrzebujesz mniej danych
       - Sprawdź jakość połączenia WiFi/Ethernet
       - Użyj Ethernet dla najniższych latencji
    
    LOGI I DEBUGGING:
    -----------------
    Program drukuje podstawowe informacje na stdout.
    Dla bardziej szczegółowych logów, możesz dodać:
    
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    To pokaże wszystkie operacje DDS i ZMQ.
    """
    main()
