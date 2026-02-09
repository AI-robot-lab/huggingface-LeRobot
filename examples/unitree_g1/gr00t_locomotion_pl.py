#!/usr/bin/env python

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
KONTROLER LOKOMOTORYCZNY GR00T DLA ROBOTA UNITREE G1
================================================================================

Ten skrypt implementuje kontroler lokomotoryczny (chodzenia) dla robota 
humanoidalnego Unitree G1 używając modeli GR00T (Generalist Robot 00T) 
opracowanych przez NVIDIA.

PRZEZNACZENIE:
--------------
- Umożliwienie robotowi humanoidalnemu chodzenia, obracania się i utrzymywania równowagi
- Wykorzystanie zaawansowanych modeli AI (sieci neuronowych) do generowania 
  naturalnych, stabilnych ruchów
- Obsługa zdalnego sterowania robotem przez kontroler bezprzewodowy

JAK TO DZIAŁA:
--------------
1. Modele GR00T to sieci neuronowe wytrenowane na danych motion capture 
   ludzkich ruchów i demonstracjach robotycznych
2. System używa dwóch specjalizowanych modeli:
   - Balance policy: Do stania w miejscu i małych korekt
   - Walk policy: Do chodzenia i większych ruchów
3. W pętli sterowania:
   a) Czytamy stan robota (pozycje stawów, IMU, kontroler)
   b) Przetwarzamy dane do formatu wejściowego modelu
   c) Model przewiduje optymalne akcje (docelowe pozycje stawów)
   d) Wysyłamy akcje do robota
   e) Powtarzamy z częstotliwością 50Hz (co 20ms)

WYMAGANIA:
----------
- Działający robot Unitree G1 lub symulacja
- Połączenie sieciowe z robotem
- Zainstalowane zależności: onnxruntime, numpy, huggingface_hub

UŻYCIE:
-------
python gr00t_locomotion.py --repo-id "nepyope/GR00T-WholeBodyControl_g1"

STEROWANIE:
-----------
- Lewy joystick (LY): Ruch do przodu/tyłu
- Lewy joystick (LX): Ruch w bok (lewo/prawo)  
- Prawy joystick (RX): Obrót wokół osi pionowej
- R1: Podniesienie talii robota
- R2: Opuszczenie talii robota
- Ctrl+C: Zatrzymanie programu

UWAGA: Ten kod jest przykładem edukacyjnym pokazującym jak używać 
       wytrenowanych modeli do sterowania prawdziwym robotem.
================================================================================
"""

import argparse
import logging
import time
from collections import deque  # Struktura danych do przechowywania historii obserwacji

import numpy as np  # Biblioteka do obliczeń numerycznych (wektory, macierze)
import onnxruntime as ort  # Runtime do uruchamiania modeli ONNX (zoptymalizowane sieci neuronowe)
from huggingface_hub import hf_hub_download  # Pobieranie modeli z Hugging Face Hub

# Importy z lerobot - nasza biblioteka do robotyki
from lerobot.robots.unitree_g1.config_unitree_g1 import UnitreeG1Config
from lerobot.robots.unitree_g1.g1_utils import G1_29_JointIndex
from lerobot.robots.unitree_g1.unitree_g1 import UnitreeG1

# Konfiguracja logowania - aby widzieć co się dzieje podczas działania programu
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# STAŁE KONFIGURACYJNE
# ============================================================================

# GROOT_DEFAULT_ANGLES - Pozycja "neutralna" robota
# Jest to pozycja referencyjna, od której liczone są wszystkie ruchy
# Wartości w radianach (1 radian ≈ 57.3 stopnia)
GROOT_DEFAULT_ANGLES = np.zeros(29, dtype=np.float32)
GROOT_DEFAULT_ANGLES[[0, 6]] = -0.1  # Hip pitch (biodra w przód/tył): lekko zgięte do tyłu
GROOT_DEFAULT_ANGLES[[3, 9]] = 0.3   # Knee (kolana): zgięte do przodu (robot lekko przykucnięty)
GROOT_DEFAULT_ANGLES[[4, 10]] = -0.2 # Ankle pitch (kostki): kompensują zgięcie kolan

# Ta pozycja jest ważna, ponieważ:
# 1. Daje robotowi stabilną podstawę
# 2. Model GR00T został wytrenowany używając tej referencji
# 3. Pozwala na szybką reakcję w dowolnym kierunku

# Konfiguracja wersji robota G1
MISSING_JOINTS = []  # Lista stawów, które nie są dostępne w danej wersji
G1_MODEL = "g1_23"   # Możliwe wartości: "g1_23" lub "g1_29"

if G1_MODEL == "g1_23":
    # Wersja 23-DOF nie posiada niektórych stawów obecnych w wersji 29-DOF:
    # - Waist yaw/pitch (12, 14): Rotacja i pochylenie talii
    # - Wrist pitch/yaw (20, 21, 27, 28): Ruchy nadgarstków
    MISSING_JOINTS = [12, 14, 20, 21, 27, 28]
    # Te stawy będą ustawione na 0 - nie mogą się ruszać

# Parametry sterowania - Te wartości kontrolują jak agresywnie robot się porusza
ACTION_SCALE = 0.25    # Skala akcji: Ogranicza maksymalną zmianę pozycji stawu
                       # Mniejsza wartość = wolniejsze, bezpieczniejsze ruchy
                       # Większa wartość = szybsze, ale potencjalnie niestabilne ruchy

CONTROL_DT = 0.02      # Delta time: Okres pętli sterowania w sekundach (20ms)
                       # 1/0.02 = 50Hz - robot otrzymuje nowe komendy 50 razy na sekundę
                       # Wyższa częstotliwość = płynniejsze sterowanie, ale więcej obliczeń

# Skale normalizacji danych - Bardzo ważne dla sieci neuronowej!
# Sieci neuronowe uczą się najlepiej gdy wszystkie wejścia są w podobnej skali
ANG_VEL_SCALE: float = 0.25   # Skala prędkości kątowych z IMU (żyroskop)
DOF_POS_SCALE: float = 1.0    # Skala pozycji stawów (Degrees of Freedom)
DOF_VEL_SCALE: float = 0.05   # Skala prędkości stawów
CMD_SCALE: list = [2.0, 2.0, 0.25]  # Skala komend: [vx, vy, obrót]
                                      # vx, vy: Prędkości liniowe (przód/tył, lewo/prawo)
                                      # obrót: Prędkość kątowa (rotacja)

# Przykład: Jeśli joystick jest wychylony na max (1.0), to:
# - Prędkość liniowa = 1.0 * 2.0 = 2.0 m/s
# - Prędkość obrotowa = 1.0 * 0.25 = 0.25 rad/s

# Domyślne repozytorium z modelami GR00T na Hugging Face Hub
DEFAULT_GROOT_REPO_ID = "nepyope/GR00T-WholeBodyControl_g1"


def load_groot_policies(
    repo_id: str = DEFAULT_GROOT_REPO_ID,
) -> tuple[ort.InferenceSession, ort.InferenceSession]:
    """
    Ładuje system dwóch polityk GR00T (Balance + Walk) z Hugging Face Hub.
    
    POLITYKA (Policy) to model uczenia maszynowego, który mapuje obserwacje na akcje.
    Inaczej mówiąc: "Co robot powinien zrobić w danej sytuacji?"
    
    DLACZEGO DWA MODELE?
    ---------------------
    1. BALANCE POLICY (stanie):
       - Specjalizuje się w utrzymywaniu równowagi
       - Używana gdy robot stoi w miejscu lub wykonuje małe korekty
       - Mniejsza, szybsza, bardziej precyzyjna
       
    2. WALK POLICY (chodzenie):
       - Specjalizuje się w lokomocji (poruszaniu się)
       - Używana gdy robot chodzi, obraca się, porusza do przodu/tyłu
       - Większa, generuje bardziej dynamiczne ruchy
    
    Dzięki specjalizacji każdy model jest lepszy w swoim zadaniu niż
    jeden uniwersalny model próbujący robić wszystko.
    
    FORMAT ONNX:
    ------------
    ONNX (Open Neural Network Exchange) to standardowy format zapisywania
    modeli sieci neuronowych. Korzyści:
    - Przenośność: Model wytrenowany w PyTorch działa w innych frameworkach
    - Optymalizacja: ONNX Runtime jest bardzo szybkie (ważne dla real-time!)
    - Wdrożenie: Łatwe użycie w produkcji na różnych platformach
    
    Args:
        repo_id: Identyfikator repozytorium na Hugging Face Hub zawierającego
                 modele ONNX w formacie "username/repo-name"
                 
    Returns:
        Krotka (policy_balance, policy_walk) - dwie sesje inferencji ONNX
        gotowe do wykonywania przewidywań
        
    Example:
        >>> balance, walk = load_groot_policies()
        >>> # Teraz możemy używać modeli do przewidywania akcji
        >>> action = balance.run(None, {balance.get_inputs()[0].name: observation})
    """
    logger.info(f"Loading GR00T dual-policy system from the hub ({repo_id})...")

    # Krok 1: Pobierz pliki ONNX z Hugging Face Hub
    # hf_hub_download automatycznie:
    # - Pobiera plik jeśli go nie ma lokalnie
    # - Używa cache jeśli plik już był pobrany
    # - Zwraca ścieżkę do lokalnego pliku
    balance_path = hf_hub_download(
        repo_id=repo_id,
        filename="GR00T-WholeBodyControl-Balance.onnx",  # Model dla balansu
    )
    walk_path = hf_hub_download(
        repo_id=repo_id,
        filename="GR00T-WholeBodyControl-Walk.onnx",     # Model dla chodzenia
    )

    # Krok 2: Załaduj modele ONNX do pamięci
    # InferenceSession tworzy środowisko wykonawcze dla modelu:
    # - Parsuje strukturę sieci neuronowej
    # - Optymalizuje grafy obliczeniowe
    # - Przygotowuje do wykonywania inferencji (przewidywań)
    policy_balance = ort.InferenceSession(balance_path)
    policy_walk = ort.InferenceSession(walk_path)

    logger.info("GR00T policies loaded successfully")
    # Modele są teraz gotowe do użycia!

    return policy_balance, policy_walk


class GrootLocomotionController:
    """
    Kontroler lokomotoryczny GR00T dla dolnej części ciała robota Unitree G1.
    
    ODPOWIEDZIALNOŚĆ:
    -----------------
    Ta klasa zarządza całym przepływem sterowania robotem:
    1. Odbiera stan robota (obserwacje)
    2. Przetwarza dane do formatu oczekiwanego przez model
    3. Wybiera odpowiednią politykę (balance/walk)
    4. Wykonuje inferencję modelu (przewidywanie akcji)
    5. Konwertuje akcje do komend dla robota
    6. Wysyła komendy do robota
    
    ARCHITEKTURA OBSERWACJI:
    -------------------------
    Model GR00T przyjmuje 516-wymiarową obserwację:
    - 6 klatek historii × 86 wymiarów na klatkę = 516D
    
    Każda klatka (86D) zawiera:
    - 3D: Komendy prędkości (vx, vy, omega)
    - 1D: Komenda wysokości talii
    - 3D: Komenda orientacji (roll, pitch, yaw)
    - 3D: Prędkość kątowa z IMU (gyroscope)
    - 3D: Orientacja względem grawitacji
    - 29D: Pozycje stawów
    - 29D: Prędkości stawów
    - 15D: Poprzednie akcje
    
    DLACZEGO HISTORIA?
    ------------------
    Robot potrzebuje "pamięci" aby:
    - Rozumieć dynamikę (czy przyspiesza? zwalnia?)
    - Planować płynne trajektorie
    - Reagować na ciągłe zmiany, nie pojedyncze snapshoty
    
    Attributes:
        policy_balance: Model ONNX dla utrzymywania równowagi
        policy_walk: Model ONNX dla chodzenia
        robot: Instancja klasy UnitreeG1 do komunikacji z robotem
        config: Konfiguracja robota
        cmd: Aktualne komendy sterowania [vx, vy, omega]
        groot_qj_all: Pozycje wszystkich 29 stawów
        groot_dqj_all: Prędkości wszystkich 29 stawów
        groot_action: Ostatnia przewidziana akcja (15D dla dolnej części ciała)
        groot_obs_single: Pojedyncza klatka obserwacji (86D)
        groot_obs_history: Kolejka ostatnich 6 klatek
        groot_obs_stacked: Zsumowana historia (516D) gotowa dla modelu
        groot_height_cmd: Komenda wysokości talii (0.50-1.00m)
        groot_orientation_cmd: Komenda orientacji ciała [roll, pitch, yaw]
    """

    def __init__(self, policy_balance, policy_walk, robot, config):
        """
        Inicjalizuje kontroler lokomotoryczny.
        
        Args:
            policy_balance: Załadowana sesja ONNX dla polityki balansu
            policy_walk: Załadowana sesja ONNX dla polityki chodzenia
            robot: Instancja UnitreeG1 do komunikacji z robotem
            config: Obiekt konfiguracji UnitreeG1Config
        """
        # Zapisz referencje do modeli i robota
        self.policy_balance = policy_balance
        self.policy_walk = policy_walk
        self.robot = robot
        self.config = config

        # Inicjalizacja komend sterowania - robot zaczyna w stanie spoczynku
        self.cmd = np.array([0.0, 0.0, 0.0], dtype=np.float32)  
        # cmd[0] = vx: prędkość do przodu/tyłu (m/s)
        # cmd[1] = vy: prędkość w bok lewo/prawo (m/s)
        # cmd[2] = theta_dot: prędkość obrotowa (rad/s)

        # Inicjalizacja buforów stanu robota
        # Wszystkie tablice są typu float32 - zgodne z ONNX
        self.groot_qj_all = np.zeros(29, dtype=np.float32)    # Pozycje stawów
        self.groot_dqj_all = np.zeros(29, dtype=np.float32)   # Prędkości stawów
        self.groot_action = np.zeros(15, dtype=np.float32)    # Ostatnia akcja (15 stawów dolnej części)
        self.groot_obs_single = np.zeros(86, dtype=np.float32)   # Jedna klatka obserwacji
        
        # Historia obserwacji - deque z maxlen=6 automatycznie usuwa najstarsze
        # gdy dodajemy nową, zachowując stały rozmiar
        self.groot_obs_history = deque(maxlen=6)
        
        # Bufor dla zsumowanej historii - to będzie wejście do modelu
        self.groot_obs_stacked = np.zeros(516, dtype=np.float32)  # 6 * 86 = 516
        
        # Komendy wysokościowe i orientacyjne
        self.groot_height_cmd = 0.74  # Domyślna wysokość talii w metrach
                                       # 0.74m to komfortowa wysokość dla G1
                                       
        self.groot_orientation_cmd = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        # [roll, pitch, yaw] w radianach - robot ma stać prosto

        # Wypełnij historię zerowymi obserwacjami na start
        # Bez tego pierwsze przewidywania byłyby niepoprawne (brak pełnej historii)
        for _ in range(6):
            self.groot_obs_history.append(np.zeros(86, dtype=np.float32))

        logger.info("GrootLocomotionController initialized")

    def run_step(self):
        """
        Wykonuje jeden krok pętli sterowania (wywoływany co CONTROL_DT = 20ms).
        
        PRZEPŁYW KROKU STEROWANIA:
        --------------------------
        1. Odbierz obserwację ze stanu robota
        2. Przetwórz komendy z kontrolera bezprzewodowego
        3. Przygotuj dane wejściowe dla modelu:
           a) Ekstraktuj pozycje i prędkości stawów
           b) Przetwórz dane IMU (orientacja, prędkość kątowa)
           c) Normalizuj wszystkie wartości
           d) Zbuduj jedną klatkę obserwacji (86D)
           e) Dodaj do historii i stwórz stos (516D)
        4. Wybierz odpowiednią politykę (balance vs walk)
        5. Wykonaj inferencję modelu (forward pass sieci neuronowej)
        6. Konwertuj przewidzianą akcję na docelowe pozycje stawów
        7. Wyślij akcję do robota
        
        UWAGA: Ta metoda musi działać szybko (<20ms), aby nadążyć za
               częstotliwością sterowania 50Hz. Inferencja ONNX jest
               zoptymalizowana i zwykle zajmuje ~2-5ms.
        """
        # Krok 1: Pobierz aktualny stan robota
        # get_observation() zwraca słownik ze wszystkimi danymi sensorycznymi
        obs = self.robot.get_observation()

        # Sprawdzenie bezpieczeństwa - jeśli brak danych, pomiń ten krok
        if not obs:
            return

        # Krok 2: Przetwórz wejście z kontrolera bezprzewodowego
        # R1 - podniesienie talii (zwiększ wysokość)
        if obs["remote.buttons"][0]:  # R1 button (indeks 0)
            self.groot_height_cmd += 0.001  # Bardzo małe przyrosty dla płynności
            self.groot_height_cmd = np.clip(self.groot_height_cmd, 0.50, 1.00)
            # clip zapewnia że wartość pozostanie w bezpiecznym zakresie
            # 0.50m - minimalna wysokość (robot przysiad)
            # 1.00m - maksymalna wysokość (robot wyprostowany)
            
        # R2 - opuszczenie talii (zmniejsz wysokość)
        if obs["remote.buttons"][4]:  # R2 button (indeks 4)
            self.groot_height_cmd -= 0.001
            self.groot_height_cmd = np.clip(self.groot_height_cmd, 0.50, 1.00)

        # Odczyt joysticków - wartości od -1.0 do 1.0
        self.cmd[0] = obs["remote.ly"]       # Lewy Y: przód(+)/tył(-)
        self.cmd[1] = obs["remote.lx"] * -1  # Lewy X: prawo(+)/lewo(-), odwrócony
        self.cmd[2] = obs["remote.rx"] * -1  # Prawy X: obrót, odwrócony
        
        # UWAGA: Mnożenie przez -1 jest konwencją kontrolera - dostosowuje
        # kierunek osi do naturalnych oczekiwań użytkownika

        # Krok 3a: Ekstraktuj pozycje i prędkości stawów ze słownika obserwacji
        # G1_29_JointIndex to enum zawierający wszystkie 29 stawów robota
        for motor in G1_29_JointIndex:
            name = motor.name   # Nazwa stawu np. "left_hip_pitch"
            idx = motor.value   # Indeks w tablicy (0-28)
            
            # Pobierz z obserwacji (klucze mają format "nazwa_stawu.q" i "nazwa_stawu.dq")
            self.groot_qj_all[idx] = obs[f"{name}.q"]   # q = position (pozycja)
            self.groot_dqj_all[idx] = obs[f"{name}.dq"] # dq = velocity (prędkość)

        # Krok 3b: Obsługa brakujących stawów (dla wersji g1_23)
        # Stawy których nie ma w sprzęcie muszą być wyzerowane
        for idx in MISSING_JOINTS:
            self.groot_qj_all[idx] = 0.0
            self.groot_dqj_all[idx] = 0.0

        # Krok 3c: Przygotuj dane do normalizacji
        # Kopiujemy, aby nie modyfikować oryginalnych wartości
        qj_obs = self.groot_qj_all.copy()
        dqj_obs = self.groot_dqj_all.copy()

        # Krok 3d: Przetwarzanie danych IMU
        # IMU (Inertial Measurement Unit) dostarcza informacji o orientacji
        # i ruchu robota w przestrzeni
        
        # Kwaternion - reprezentacja orientacji w 3D (unika gimbal lock)
        # Format: [w, x, y, z] gdzie w^2 + x^2 + y^2 + z^2 = 1
        quat = [obs["imu.quat.w"], obs["imu.quat.x"], obs["imu.quat.y"], obs["imu.quat.z"]]
        
        # Prędkość kątowa (angular velocity) z żyroskopu
        # Mierzy jak szybko robot się obraca wokół każdej osi
        ang_vel = np.array([obs["imu.gyro.x"], obs["imu.gyro.y"], obs["imu.gyro.z"]], dtype=np.float32)
        
        # Konwersja kwaternionu na wektor grawitacji
        # Pokazuje gdzie jest "dół" z perspektywy robota
        # To kluczowe dla balansu - robot musi "wiedzieć" gdzie jest pionowo
        gravity_orientation = self.robot.get_gravity_orientation(quat)

        # Krok 3e: NORMALIZACJA - Bardzo ważny krok!
        # Sieci neuronowe uczą się znacznie lepiej gdy dane są znormalizowane
        
        # Pozycje stawów: odejmujemy pozycję neutralną i skalujemy
        # Dlaczego? Model uczy się "odchyleń od normy", nie absolutnych wartości
        qj_obs = (qj_obs - GROOT_DEFAULT_ANGLES) * DOF_POS_SCALE
        
        # Prędkości stawów: skalujemy do mniejszego zakresu
        # Typowe prędkości mogą być duże (kilkadziesiąt rad/s)
        dqj_obs = dqj_obs * DOF_VEL_SCALE
        
        # Prędkość kątowa z IMU: skalujemy podobnie
        ang_vel_scaled = ang_vel * ANG_VEL_SCALE

        # Krok 3f: Budowa pojedynczej klatki obserwacji (86 wymiarów)
        # Każdy wymiar reprezentuje konkretną informację dla modelu
        
        # [0:3] - Komendy sterowania (skalowane)
        self.groot_obs_single[:3] = self.cmd * np.array(CMD_SCALE)
        
        # [3] - Komenda wysokości talii
        self.groot_obs_single[3] = self.groot_height_cmd
        
        # [4:7] - Komenda orientacji (zazwyczaj [0,0,0] = stój prosto)
        self.groot_obs_single[4:7] = self.groot_orientation_cmd
        
        # [7:10] - Prędkość kątowa (gyroscope, skalowana)
        self.groot_obs_single[7:10] = ang_vel_scaled
        
        # [10:13] - Orientacja względem grawitacji (gdzie jest "dół")
        self.groot_obs_single[10:13] = gravity_orientation
        
        # [13:42] - Pozycje stawów (29 wymiarów, znormalizowane)
        self.groot_obs_single[13:42] = qj_obs
        
        # [42:71] - Prędkości stawów (29 wymiarów, znormalizowane)
        self.groot_obs_single[42:71] = dqj_obs
        
        # [71:86] - Poprzednie akcje (15 wymiarów)
        # To daje modelowi "pamięć" co ostatnio polecił robotowi zrobić
        self.groot_obs_single[71:86] = self.groot_action

        # Krok 3g: Aktualizacja historii obserwacji
        # Dodaj nową klatkę do kolejki (automatycznie usuwa najstarszą)
        self.groot_obs_history.append(self.groot_obs_single.copy())

        # Krok 3h: Stwórz stos 6 klatek (516D) - wejście dla modelu
        # Model widzi ostatnie 6 kroków czasowych naraz
        for i, obs_frame in enumerate(self.groot_obs_history):
            start_idx = i * 86      # Początek segmentu dla klatki i
            end_idx = start_idx + 86  # Koniec segmentu
            self.groot_obs_stacked[start_idx:end_idx] = obs_frame
        
        # Teraz mamy: [klatka_t-5, klatka_t-4, ..., klatka_t-1, klatka_t]
        # gdzie t to obecna chwila

        # Krok 4: Wybór polityki - Balance vs Walk
        # Oblicz magnitude (długość) wektora komendy
        cmd_magnitude = np.linalg.norm(self.cmd)
        # np.linalg.norm([vx, vy, omega]) = sqrt(vx^2 + vy^2 + omega^2)
        
        # Prosta heurystyka wyboru:
        # - Jeśli komendy są małe (< 0.05) → użyj balance policy
        # - Jeśli komendy są większe → użyj walk policy
        selected_policy = (
            self.policy_balance if cmd_magnitude < 0.05 
            else self.policy_walk
        )
        # 0.05 to próg empiryczny - może być dostrojony do preferencji

        # Krok 5: INFERENCJA MODELU - Tu dzieje się magia!
        # ====================================================
        
        # 5a: Przygotuj dane wejściowe dla ONNX Runtime
        # ONNX wymaga słownika: {nazwa_wejścia: dane}
        ort_inputs = {
            selected_policy.get_inputs()[0].name:  # Pobierz nazwę pierwszego wejścia
            np.expand_dims(self.groot_obs_stacked, axis=0)  # Dodaj wymiar batch (1, 516)
        }
        # expand_dims: (516,) → (1, 516) 
        # Bo model oczekuje batcha, nawet jeśli jest tylko jedna próbka
        
        # 5b: Uruchom model (forward pass sieci neuronowej)
        # To wykonuje tysiące operacji macierzowych w kilka milisekund
        ort_outs = selected_policy.run(None, ort_inputs)
        # None = "zwróć wszystkie wyjścia"
        # ort_outs[0] to pierwsza (i jedyna) warstwa wyjściowa
        
        # 5c: Ekstraktuj akcję i usuń wymiar batch
        self.groot_action = ort_outs[0].squeeze()  # (1, 15) → (15,)
        # Model zwrócił 15 wartości - akcje dla 15 stawów dolnej części ciała

        # Krok 6: Konwersja akcji modelu na docelowe pozycje stawów
        # ============================================================
        
        # Model przewiduje DELTA (zmianę), nie absolutną pozycję
        # Więc: pozycja_docelowa = pozycja_neutralna + (akcja * skala)
        target_dof_pos_15 = GROOT_DEFAULT_ANGLES[:15] + self.groot_action * ACTION_SCALE
        # [:15] bo GR00T kontroluje tylko dolną część ciała (15 pierwszych stawów)
        # ACTION_SCALE (0.25) ogranicza maksymalną zmianę dla bezpieczeństwa

        # Krok 7: Budowa słownika akcji dla robota
        # ==========================================
        action_dict = {}
        
        # Wypełnij akcje dla pierwszych 15 stawów (dolna część ciała + ramiona)
        for i in range(15):
            motor_name = G1_29_JointIndex(i).name  # Pobierz nazwę stawu
            action_dict[f"{motor_name}.q"] = float(target_dof_pos_15[i])
            # Format klucza: "left_hip_pitch.q" itp.
            # .q oznacza docelową pozycję (position target)

        # Krok 8: Wyzeruj brakujące stawy (dla wersji g1_23)
        # ===================================================
        for joint_idx in MISSING_JOINTS:
            motor_name = G1_29_JointIndex(joint_idx).name
            action_dict[f"{motor_name}.q"] = 0.0
            # Stawy których nie ma muszą mieć akcję 0.0

        # Krok 9: Wysłanie akcji do robota!
        # ==================================
        self.robot.send_action(action_dict)
        # Ta akcja zostanie wysłana przez ZMQ do serwera na robocie,
        # a następnie przez DDS do sterowników silników.
        # Robot wykona płynną interpolację od obecnej do docelowej pozycji
        # używając wbudowanych regulatorów PD.


def run(repo_id: str = DEFAULT_GROOT_REPO_ID) -> None:
    """
    Główna funkcja uruchamiająca kontroler lokomotoryczny GR00T.
    
    PRZEPŁYW PROGRAMU:
    ------------------
    1. Załaduj modele AI z Hugging Face Hub
    2. Połącz się z robotem (fizycznym lub symulacją)
    3. Zainicjalizuj kontroler lokomotoryczny
    4. Przestaw robota do pozycji startowej
    5. Uruchom główną pętlę sterowania (50Hz)
    6. Reaguj na Ctrl+C do bezpiecznego zakończenia
    
    PĘTLA STEROWANIA:
    -----------------
    while robot_aktywny:
        start = czas_teraz
        wykonaj_krok_sterowania()  # ~2-5ms
        elapsed = czas_teraz - start
        sleep(20ms - elapsed)  # Czekaj do następnego cyklu
        
    Ta struktura zapewnia stałą częstotliwość 50Hz niezależnie od
    czasu wykonania kodu (dopóki execution time < 20ms).
    
    Args:
        repo_id: Identyfikator repozytorium Hugging Face Hub z modelami GR00T
                 Może być zmieniony przez argument wiersza poleceń --repo-id
                 
    Raises:
        KeyboardInterrupt: Obsługiwane gracefully - robot bezpiecznie się rozłącza
        Exception: Inne wyjątki są propagowane, ale robot nadal się rozłącza (finally)
    """
    # Krok 1: Załaduj polityki (modele AI)
    # ======================================
    policy_balance, policy_walk = load_groot_policies(repo_id=repo_id)
    # Te dwa modele będą używane do generowania akcji

    # Krok 2: Inicjalizacja robota
    # =============================
    config = UnitreeG1Config()  # Załaduj domyślną konfigurację
    robot = UnitreeG1(config)    # Stwórz instancję robota
    
    # Połącz się z robotem (przez ZMQ jeśli prawdziwy robot, lub uruchom symulację)
    robot.connect()
    # Po tym kroku robot jest gotowy do odbierania komend

    # Krok 3: Inicjalizacja kontrolera lokomotorycznego
    # ==================================================
    groot_controller = GrootLocomotionController(
        policy_balance=policy_balance,
        policy_walk=policy_walk,
        robot=robot,
        config=config,
    )
    # Kontroler jest teraz gotowy do generowania akcji

    try:
        # Krok 4: Reset robota do pozycji startowej
        # ==========================================
        robot.reset(CONTROL_DT, GROOT_DEFAULT_ANGLES)
        # reset() wykonuje:
        # 1. Płynnie przesuwa robota do pozycji neutralnej
        # 2. Konfiguruje częstotliwość sterowania (50Hz)
        # 3. Inicjalizuje wewnętrzne buffery
        
        # Wyświetl instrukcje dla użytkownika
        logger.info("Use joystick: LY=fwd/back, LX=left/right, RX=rotate, R1=raise waist, R2=lower waist")
        logger.info("Press Ctrl+C to stop")

        # Krok 5: GŁÓWNA PĘTLA STEROWANIA
        # ================================
        # Ta pętla będzie działać w kółko dopóki nie zostanie przerwana
        # Uwaga: robot._shutdown_event jest ustawiane przez robot.disconnect()
        while not robot._shutdown_event.is_set():
            # Zmierz czas początku iteracji
            start_time = time.time()
            
            # Wykonaj jeden krok sterowania (całe przetwarzanie i inferencja)
            groot_controller.run_step()
            
            # Oblicz ile czasu zajęło wykonanie
            elapsed = time.time() - start_time
            
            # Oblicz ile trzeba czekać do następnego cyklu
            # Cel: stała częstotliwość 50Hz (1 cykl co 20ms)
            sleep_time = max(0, CONTROL_DT - elapsed)
            # max(0, ...) zapewnia że nie śpimy ujemnie (gdy kod trwa dłużej)
            
            # Odczekaj do następnego cyklu
            time.sleep(sleep_time)
            
            # Jeśli elapsed > CONTROL_DT, znaczy że nie nadążamy!
            # W praktyce inferencja ONNX jest na tyle szybka, że to rzadki problem
            
    except KeyboardInterrupt:
        # Użytkownik nacisnął Ctrl+C - normalne zakończenie
        logger.info("Stopping locomotion...")
        # Program wyjdzie z pętli while i przejdzie do bloku finally
        
    finally:
        # Ten blok ZAWSZE się wykona, niezależnie od tego jak kończymy
        # To gwarantuje bezpieczne zamknięcie połączenia z robotem
        if robot.is_connected:
            robot.disconnect()
            # disconnect():
            # 1. Zatrzymuje wszystkie ruchy
            # 2. Zamyka sockety ZMQ
            # 3. Czyści zasoby
        logger.info("Done!")
        # Program kończy pracę


if __name__ == "__main__":
    """
    Punkt wejścia programu - uruchamiany gdy skrypt jest wykonywany bezpośrednio.
    
    ARGUMENTY WIERSZA POLECEŃ:
    --------------------------
    --repo-id: (Opcjonalny) Identyfikator repozytorium z modelami
               Domyślnie: "nepyope/GR00T-WholeBodyControl_g1"
               
    PRZYKŁADY UŻYCIA:
    -----------------
    # Użyj domyślnych modeli:
    python gr00t_locomotion.py
    
    # Użyj własnych modeli:
    python gr00t_locomotion.py --repo-id "username/my-groot-models"
    
    # Wyświetl pomoc:
    python gr00t_locomotion.py --help
    """
    # Konfiguracja parsera argumentów wiersza poleceń
    parser = argparse.ArgumentParser(
        description="GR00T Locomotion Controller for Unitree G1",
        # Dodatkowe informacje w pomocy:
        epilog="""
        Ten kontroler implementuje system lokomotoryczny GR00T dla robota
        humanoidalnego Unitree G1. Używa dwóch specjalizowanych modeli
        (balance i walk) do generowania stabilnych i naturalnych ruchów.
        
        Więcej informacji: https://github.com/huggingface/lerobot
        """
    )
    
    # Dodaj argument --repo-id
    parser.add_argument(
        "--repo-id",
        type=str,
        default=DEFAULT_GROOT_REPO_ID,
        help=f"Hugging Face Hub repo ID for GR00T policies (default: {DEFAULT_GROOT_REPO_ID})",
    )
    
    # Parsuj argumenty z linii poleceń
    args = parser.parse_args()
    # Teraz args.repo_id zawiera wartość z --repo-id lub domyślną

    # Uruchom główną funkcję z podanym repo_id
    run(repo_id=args.repo_id)
