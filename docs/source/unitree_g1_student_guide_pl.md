# Przewodnik Studenta: Projekt z Robotem Unitree G1 EDU

## Wprowadzenie

Witaj w świecie robotyki humanoidalnej! Ten przewodnik pomoże Ci krok po kroku zrozumieć i wykorzystać platformę LeRobot do pracy z robotem Unitree G1 EDU.

## Czego się nauczysz?

1. **Podstawy robotyki** - Jak działają roboty humanoidalne
2. **Uczenie maszynowe w robotyce** - Jak roboty się uczą
3. **Praktyczne umiejętności** - Konfiguracja, zbieranie danych, trenowanie modeli
4. **Wdrażanie AI** - Od symulacji do prawdziwego robota

---

## Moduł 1: Podstawy Teoretyczne

### 1.1 Czym jest Robot Humanoidalny?

Robot humanoidalny to robot zaprojektowany tak, aby przypominał kształt i ruchy człowieka. Unitree G1 EDU posiada:

**Stopnie Swobody (DOF - Degrees of Freedom):**
- **23 DOF** (wersja podstawowa) lub **29 DOF** (wersja rozszerzona)
- Każdy stopień swobody to jeden ruchomy staw
- Więcej DOF = bardziej złożone ruchy możliwe do wykonania

**Przykład:** 
- Człowiek ma ~244 DOF w całym ciele
- G1 z 29 DOF może wykonywać złożone zadania manipulacyjne
- G1 z 23 DOF skupia się na lokomotoryce i prostych ruchach ramion

**Główne Komponenty:**
1. **Silniki (Motors)** - Poruszają stawami robota
2. **Enkodery (Encoders)** - Mierzą pozycję i prędkość stawów
3. **IMU (Inertial Measurement Unit)** - Czujnik orientacji i przyspieszenia
4. **Kamery** - Umożliwiają percepcję wizualną
5. **Komputer Orin** - Mózg robota (procesor NVIDIA)
6. **Kontroler bezprzewodowy** - Do manualnego sterowania

### 1.2 Przestrzeń Stanów i Akcji

#### Przestrzeń Obserwacji (Observation Space)

To wszystkie dane sensoryczne, które robot otrzymuje w danym momencie:

```python
obserwacja = {
    # Pozycje stawów (29 wartości, w radianach)
    "left_hip_pitch.q": 0.15,
    "left_knee.q": 0.30,
    # ... pozostałe stawy
    
    # Prędkości stawów (29 wartości, rad/s)
    "left_hip_pitch.dq": 0.05,
    
    # Dane IMU
    "imu.quat.w": 1.0,  # Kwaternion orientacji
    "imu.gyro.x": 0.01,  # Prędkość kątowa
    
    # Kontroler zdalny
    "remote.lx": 0.0,  # Joystick lewy X
    "remote.ly": 0.5,  # Joystick lewy Y (ruch do przodu)
}
```

**Dlaczego to ważne?**
Model AI potrzebuje tych danych, aby "wiedzieć" co się dzieje i podjąć właściwą decyzję.

#### Przestrzeń Akcji (Action Space)

To polecenia, które wysyłamy do robota:

```python
akcja = {
    # Docelowe pozycje stawów (w radianach)
    "left_hip_pitch.q": 0.20,  # Cel dla lewego biodra
    "left_knee.q": 0.35,  # Cel dla lewego kolana
    # ... pozostałe stawy
}
```

**Jak to działa?**
Robot ma wbudowane regulatory PD (Proportional-Derivative), które płynnie przesuwają stawy z obecnej pozycji do docelowej.

### 1.3 Paradygmaty Uczenia

#### Uczenie przez Imitację (Imitation Learning)

```
Demonstracje Eksperta → Model → Powtórzenie Zachowania
```

**Proces:**
1. **Demonstracja:** Ekspert (Ty) pokazuje jak wykonać zadanie
2. **Zbieranie danych:** System zapisuje (obserwacje, akcje)
3. **Trenowanie:** Model uczy się mapowania obserwacje → akcje
4. **Wykonanie:** Robot powtarza nauczone zadanie

**Zalety:**
- Nie wymaga funkcji nagrody (jak w RL)
- Szybkie uczenie się prostych zadań
- Intuicyjne dla ludzi

**Wady:**
- Ograniczone do zademonstrowanych sytuacji
- Wymaga wielu demonstracji wysokiej jakości

#### Uczenie przez Wzmacnianie (Reinforcement Learning)

```
Próby → Nagroda/Kara → Optymalizacja Polityki
```

**Proces:**
1. **Eksploracja:** Robot próbuje różnych akcji
2. **Ocena:** System przypisuje nagrodę (sukces) lub karę (błąd)
3. **Uczenie:** Model optymalizuje akcje, aby maksymalizować nagrodę
4. **Iteracja:** Powtarzanie procesu tysiące razy

**Zalety:**
- Może odkryć strategie niemożliwe do zademonstrowania
- Optymalizuje do określonego celu

**Wady:**
- Wymaga dużo czasu obliczeniowego
- Trudne projektowanie funkcji nagrody

---

## Moduł 2: Architektura Systemu

### 2.1 Architektura Komunikacji

```
┌─────────────────────────────────────────────────────┐
│                   ROBOT UNITREE G1                  │
│  ┌──────────────────────────────────────────────┐   │
│  │         Komputer Orin (na robocie)           │   │
│  │  ┌────────────────────────────────────────┐  │   │
│  │  │     run_g1_server.py (Bridge)          │  │   │
│  │  │  ┌──────────────┬──────────────────┐   │  │   │
│  │  │  │  DDS Topics  │   ZMQ Sockets    │   │  │   │
│  │  │  │  (lokalne)   │   (sieć)         │   │  │   │
│  │  │  └──────┬───────┴─────────┬────────┘   │  │   │
│  │  └─────────┼─────────────────┼────────────┘  │   │
│  │            │                 │                │   │
│  │     ┌──────▼──────┐   ┌──────▼──────┐        │   │
│  │     │   Silniki   │   │   Czujniki  │        │   │
│  │     │  (Actuators)│   │   (Sensors) │        │   │
│  │     └─────────────┘   └─────────────┘        │   │
│  └──────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────┘
                       │ WiFi/Ethernet
                       │
┌──────────────────────▼──────────────────────────────┐
│              KOMPUTER STERUJĄCY (Twój laptop)       │
│  ┌──────────────────────────────────────────────┐   │
│  │        unitree_g1.py (Robot Client)          │   │
│  │                     │                         │   │
│  │         ┌───────────▼───────────┐             │   │
│  │         │   Polityka (Policy)   │             │   │
│  │         │  - GR00T (ONNX)       │             │   │
│  │         │  - ACT (PyTorch)      │             │   │
│  │         └───────────────────────┘             │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

**Wyjaśnienie przepływu danych:**

1. **Obserwacja (Robot → Komputer):**
   - Czujniki → DDS Topics → Bridge → ZMQ → Robot Client → Polityka

2. **Akcja (Komputer → Robot):**
   - Polityka → Robot Client → ZMQ → Bridge → DDS Topics → Silniki

### 2.2 Protokoły Komunikacyjne

#### DDS (Data Distribution Service)

**Co to jest?**
Protokół komunikacji używany wewnątrz robota (lokalnie).

**Dlaczego DDS?**
- **Niska latencja** - bardzo szybka komunikacja
- **Niezawodność** - gwarantuje dostarczenie wiadomości
- **Standard w robotyce** - używany przez wielu producentów

#### ZMQ (ZeroMQ)

**Co to jest?**
Biblioteka do przesyłania wiadomości przez sieć.

**Dlaczego ZMQ?**
- **Prosty w użyciu** - łatwe API
- **Wydajny** - szybkie przesyłanie danych
- **Elastyczny** - różne wzorce komunikacji (PUB/SUB, PUSH/PULL)

**Wzorce używane w projekcie:**
```python
# PUB/SUB - obserwacje (jeden nadawca, wielu odbiorców)
# Robot publikuje stan, wiele programów może słuchać
publisher.send(observation)

# PUSH/PULL - akcje (jeden nadawca, jeden odbiorca)
# Tylko jeden program steruje robotem na raz
socket.send(action)
```

---

## Moduł 3: Praktyczna Praca z Kodem

### 3.1 Struktura Projektu

```
lerobot/
├── src/lerobot/
│   ├── robots/
│   │   └── unitree_g1/          # Główny kod robota
│   │       ├── unitree_g1.py    # Klasa robota
│   │       ├── run_g1_server.py # Serwer na robocie
│   │       ├── config_unitree_g1.py  # Konfiguracja
│   │       └── g1_utils.py      # Narzędzia pomocnicze
│   ├── datasets/                # Zarządzanie danymi
│   └── policies/                # Modele AI
├── examples/
│   └── unitree_g1/              # Przykładowe skrypty
│       ├── gr00t_locomotion.py  # Kontroler GR00T
│       └── holosoma_locomotion.py  # Kontroler Holosoma
└── docs/                        # Dokumentacja
```

### 3.2 Główne Klasy i Ich Rola

#### Klasa `UnitreeG1`

**Plik:** `src/lerobot/robots/unitree_g1/unitree_g1.py`

**Odpowiedzialność:**
- Abstrakcja sprzętu - ukrywa szczegóły implementacyjne
- Komunikacja z robotem przez ZMQ
- Konwersja danych między formatami

**Kluczowe metody:**

```python
class UnitreeG1(Robot):
    def connect(self):
        """
        Nawiązuje połączenie z robotem przez ZMQ.
        Tworzy sockety do wysyłania akcji i odbierania obserwacji.
        """
        
    def get_observation(self) -> dict:
        """
        Pobiera aktualny stan robota.
        
        Returns:
            Słownik z pozycjami stawów, danymi IMU, stanem kontrolera
        """
        
    def send_action(self, action: dict):
        """
        Wysyła akcję do robota.
        
        Args:
            action: Słownik z docelowymi pozycjami stawów
        """
        
    def disconnect(self):
        """
        Bezpiecznie zamyka połączenie z robotem.
        """
```

#### Serwer Robota

**Plik:** `src/lerobot/robots/unitree_g1/run_g1_server.py`

**Rola:** Most komunikacyjny między DDS (lokalne) a ZMQ (sieć)

**Funkcje kluczowe:**

```python
def state_forward_loop():
    """
    Pętla działająca w osobnym wątku.
    Ciągle odczytuje stan z DDS i publikuje przez ZMQ.
    """
    while not shutdown:
        # 1. Odczytaj z DDS
        msg = lowstate_sub.Read()
        
        # 2. Konwertuj do JSON
        state_dict = lowstate_to_dict(msg)
        
        # 3. Wyślij przez ZMQ
        lowstate_sock.send(json.dumps(state_dict))

def cmd_forward_loop():
    """
    Pętla główna.
    Odbiera akcje z ZMQ i przekazuje do DDS.
    """
    while True:
        # 1. Odbierz z ZMQ
        payload = lowcmd_sock.recv()
        
        # 2. Konwertuj z JSON
        cmd_data = json.loads(payload)
        
        # 3. Wyślij do DDS
        lowcmd_pub.Write(cmd)
```

### 3.3 Przykład: Kontroler GR00T

**Plik:** `examples/unitree_g1/gr00t_locomotion.py`

To praktyczny przykład użycia polityki lokomotorycznej. Przeanalizujmy krok po kroku:

#### Krok 1: Ładowanie Polityki

```python
def load_groot_policies(repo_id: str):
    """
    Ładuje dwie polityki ONNX z Hugging Face Hub:
    - Balance: Dla stania i małych ruchów
    - Walk: Dla chodzenia i większych ruchów
    
    Dlaczego dwie polityki?
    - Specjalizacja: każda jest lepiej wytrenowana do swojego celu
    - Efektywność: mniejsze modele = szybsza inferencja
    """
    # Pobierz pliki ONNX z Hub
    balance_path = hf_hub_download(repo_id, "GR00T-WholeBodyControl-Balance.onnx")
    walk_path = hf_hub_download(repo_id, "GR00T-WholeBodyControl-Walk.onnx")
    
    # Załaduj jako sesje ONNX Runtime
    policy_balance = ort.InferenceSession(balance_path)
    policy_walk = ort.InferenceSession(walk_path)
    
    return policy_balance, policy_walk
```

**Co to jest ONNX?**
ONNX (Open Neural Network Exchange) to format do zapisywania modeli AI. Pozwala na:
- **Przenośność** - model wytrenowany w PyTorch działa w innych frameworkach
- **Optymalizację** - ONNX Runtime jest bardzo szybkie
- **Wdrożenie** - łatwe użycie w produkcji

#### Krok 2: Przygotowanie Obserwacji

```python
def run_step(self):
    # 1. Pobierz surowy stan z robota
    obs = self.robot.get_observation()
    
    # 2. Ekstrakcja pozycji i prędkości stawów
    for motor in G1_29_JointIndex:
        idx = motor.value
        self.groot_qj_all[idx] = obs[f"{motor.name}.q"]
        self.groot_dqj_all[idx] = obs[f"{motor.name}.dq"]
    
    # 3. Przetwarzanie danych IMU
    # Kwaternion → orientacja w przestrzeni
    quat = [obs["imu.quat.w"], obs["imu.quat.x"], ...]
    gravity_orientation = self.robot.get_gravity_orientation(quat)
    
    # 4. Normalizacja danych (bardzo ważne!)
    # Dlaczego normalizujemy?
    # - Sieci neuronowe uczą się lepiej gdy dane są w podobnych skalach
    # - Pozycje w radianach (-3.14, 3.14) vs. prędkości (0, 100) → problemy
    qj_obs = (qj_obs - GROOT_DEFAULT_ANGLES) * DOF_POS_SCALE
    dqj_obs = dqj_obs * DOF_VEL_SCALE
    ang_vel_scaled = ang_vel * ANG_VEL_SCALE
```

**Dlaczego odejmujemy GROOT_DEFAULT_ANGLES?**
To pozycja "neutralna" robota. Trenujemy sieć na odchyleniach od neutralnej, nie na absolutnych wartościach.

#### Krok 3: Historia Obserwacji

```python
# GR00T używa 6 ostatnich klatek (516D = 6 × 86D)
self.groot_obs_history.append(self.groot_obs_single.copy())

for i, obs_frame in enumerate(self.groot_obs_history):
    start_idx = i * 86
    end_idx = start_idx + 86
    self.groot_obs_stacked[start_idx:end_idx] = obs_frame
```

**Dlaczego 6 klatek?**
- **Dynamika czasowa** - robot potrzebuje "pamięci" co się działo
- **Prędkość** - jedna klatka nie mówi czy robot przyspiesza czy zwalnia
- **Stabilność** - historia pomaga w płynnych ruchach

**Analogia:**
Jak przy jeździe samochodem - patrzysz nie tylko na obecną pozycję, ale pamiętasz ostatnie kilka sekund (skręcałeś? przyspieszyłeś?).

#### Krok 4: Inferencja Polityki

```python
# Wybór polityki na podstawie prędkości komendy
cmd_magnitude = np.linalg.norm(self.cmd)
selected_policy = (
    self.policy_balance if cmd_magnitude < 0.05 
    else self.policy_walk
)

# Uruchomienie sieci neuronowej
ort_inputs = {
    selected_policy.get_inputs()[0].name: 
    np.expand_dims(self.groot_obs_stacked, axis=0)
}
ort_outs = selected_policy.run(None, ort_inputs)
self.groot_action = ort_outs[0].squeeze()
```

**Co się dzieje w środku?**
1. Obserwacja (516D) → Warstwy sieci neuronowej → Akcja (15D)
2. Tysiące operacji matematycznych w milisekundach!
3. Model "nauczył się" jakie akcje są dobre w danej sytuacji

#### Krok 5: Konwersja Akcji do Poleceń

```python
# Model zwraca delta (zmianę), nie absolutną pozycję
target_dof_pos_15 = GROOT_DEFAULT_ANGLES[:15] + self.groot_action * ACTION_SCALE

# Budowa słownika akcji
action_dict = {}
for i in range(15):
    motor_name = G1_29_JointIndex(i).name
    action_dict[f"{motor_name}.q"] = float(target_dof_pos_15[i])

# Wysłanie do robota
self.robot.send_action(action_dict)
```

**Dlaczego ACTION_SCALE?**
Mnożnik bezpieczeństwa - ogranicza maksymalną zmianę pozycji. Zapobiega nagłym, niebezpiecznym ruchom.

---

## Moduł 4: Zbieranie i Zarządzanie Danymi

### 4.1 Format LeRobotDataset

**Struktura katalogów:**
```
dataset_name/
├── metadata/
│   ├── chunks/         # Pliki Parquet z danymi
│   │   ├── chunk-000.parquet
│   │   └── chunk-001.parquet
│   └── info.json      # Metadane datasetu
├── videos/            # Nagrania z kamer
│   ├── episode_000001.mp4
│   └── episode_000002.mp4
└── README.md          # Opis datasetu
```

**Co zawiera Parquet?**
```python
{
    "timestamp": [0.00, 0.02, 0.04, ...],  # Czas w sekundach
    "episode_index": [0, 0, 0, ...],       # Numer epizodu
    "frame_index": [0, 1, 2, ...],         # Numer klatki w epizodzie
    
    # Obserwacje
    "observation.state": [...],            # Pozycje stawów
    "observation.image": [...],            # Indeksy do klatek video
    
    # Akcje
    "action": [...],                       # Docelowe pozycje stawów
    
    # Metadane
    "task": ["pick_object", ...],          # Nazwa zadania
}
```

### 4.2 Proces Zbierania Danych

#### Przygotowanie

1. **Planowanie zadania**
   - Zdefiniuj jasno co robot ma robić
   - Przygotuj środowisko (obiekty, układ)
   - Ćwicz sam przed nagrywaniem

2. **Kalibracja sprzętu**
   ```bash
   # Kalibracja teleoperatora
   lerobot-calibrate \
       --teleop.type=unitree_g1 \
       --teleop.left_arm_config.port=/dev/ttyACM1 \
       --teleop.right_arm_config.port=/dev/ttyACM0
   ```

3. **Test połączenia**
   - Sprawdź czy robot odpowiada
   - Przetestuj kamery
   - Sprawdź synchronizację

#### Nagrywanie

```bash
python -m lerobot.scripts.lerobot_record \
    --robot.type=unitree_g1 \
    --robot.is_simulation=false \
    --dataset.repo_id=twoja-nazwa/dataset-nazwa \
    --dataset.single_task="Podnieś kubek" \
    --dataset.num_episodes=50 \
    --dataset.episode_time_s=10 \
    --dataset.reset_time_s=5
```

**Parametry wyjaśnione:**
- `num_episodes=50` - Nagraj 50 prób wykonania zadania
- `episode_time_s=10` - Każda próba trwa 10 sekund
- `reset_time_s=5` - 5 sekund przerwy między próbami (reset środowiska)

**Wskazówki dla jakości:**
1. **Konsystencja** - wykonuj zadanie podobnie każdym razem
2. **Płynność** - unikaj nagłych ruchów
3. **Kompletność** - pokaż pełne wykonanie od początku do końca
4. **Różnorodność** - trochę zmieniaj pozycje obiektów
5. **Sukces** - nagrywaj głównie udane próby

### 4.3 Wizualizacja Danych

```python
from lerobot.datasets.lerobot_dataset import LeRobotDataset

# Załaduj dataset
dataset = LeRobotDataset("twoja-nazwa/dataset-nazwa")

# Podstawowe informacje
print(f"Liczba epizodów: {dataset.num_episodes}")
print(f"Liczba klatek: {len(dataset)}")
print(f"Częstotliwość: {dataset.fps} FPS")

# Przeglądanie danych
episode = dataset[0]
print(f"Kształt obserwacji: {episode['observation.state'].shape}")
print(f"Kształt akcji: {episode['action'].shape}")

# Wizualizacja w przeglądarce
from lerobot.visualize import visualize_dataset
visualize_dataset(dataset, episode_index=0)
```

---

## Moduł 5: Trenowanie Modeli

### 5.1 Wybór Architektury

#### ACT (Action Chunking Transformer)

**Kiedy używać?**
- Zadania manipulacyjne (chwytanie, przenoszenie)
- Potrzebujesz płynnych, długich sekwencji akcji
- Masz ~100-500 demonstracji

**Jak działa?**
```
Obserwacja → Vision Encoder → Transformer → Decoder → Sekwencja Akcji
                                  ↓
                            Latent Space (CVAE)
```

**Unikalność:** Przewiduje wiele akcji naraz (chunk), nie pojedynczą.

#### Diffusion Policy

**Kiedy używać?**
- Zadania wymagające precyzji
- Multimodalne zachowania (wiele sposobów wykonania zadania)
- Masz więcej danych (~500-1000 demonstracji)

**Jak działa?**
```
Obserwacja → Encoder → Iteracyjna Denoise → Akcja
                            ↓
                      Proces Dyfuzji
```

**Analogia:** Jak odszumianie obrazu - model stopniowo "czyści" losowy szum do sensownej akcji.

### 5.2 Trenowanie w Praktyce

#### Przygotowanie środowiska

```bash
# Instalacja z GPU support
conda create -n lerobot python=3.10
conda activate lerobot
pip install lerobot[train]

# Weryfikacja GPU
python -c "import torch; print(torch.cuda.is_available())"
```

#### Uruchomienie treningu

```bash
lerobot-train \
    --policy=act \
    --dataset.repo_id=twoja-nazwa/dataset-nazwa \
    --training.batch_size=8 \
    --training.num_epochs=1000 \
    --training.lr=1e-4 \
    --training.save_freq=100 \
    --output_dir=outputs/my_policy
```

**Parametry wyjaśnione:**

- **batch_size=8** 
  - Ile przykładów naraz do GPU
  - Większe = szybsze, ale wymaga więcej pamięci
  - Zależy od rozmiaru modelu i GPU

- **num_epochs=1000**
  - Ile razy przejść przez cały dataset
  - Za mało = niedouczony model
  - Za dużo = overfitting (model "zapamiętuje" nie "rozumie")

- **lr=1e-4** (learning rate)
  - Jak duże kroki w optymalizacji
  - Za małe = wolne uczenie
  - Za duże = niestabilność, brak konwergencji

#### Monitorowanie treningu

```python
# Metryki do obserwowania
1. Training Loss - powinien spadać
2. Validation Loss - powinien spadać, ale wolniej
3. Action Error - średni błąd przewidywanych akcji

# Ostrzeżenia
❌ Val loss rośnie a train loss spada → Overfitting
❌ Loss nie spada → Learning rate za mały lub błąd w danych
❌ Loss exploduje → Learning rate za duży
```

**Wizualizacja:**
```bash
# TensorBoard
tensorboard --logdir outputs/my_policy/logs

# Otwórz przeglądarkę: http://localhost:6006
```

### 5.3 Ocena Modelu

#### Metryki ilościowe

```python
# Success Rate - procent udanych wykonań
success_rate = successful_episodes / total_episodes

# Average Return - średnia nagroda
avg_return = sum(episode_rewards) / num_episodes

# Action Error - średnia różnica między przewidywaną a rzeczywistą akcją
action_error = mean(|predicted_action - ground_truth_action|)
```

#### Ocena jakościowa

1. **Płynność ruchów** - Czy robot porusza się naturalnie?
2. **Robustość** - Czy działa przy małych zmianach środowiska?
3. **Bezpieczeństwo** - Czy wykonuje niebezpieczne ruchy?
4. **Efektywność** - Czy wykonuje zadanie optymalną ścieżką?

---

## Moduł 6: Wdrożenie i Testowanie

### 6.1 Przejście Symulacja → Rzeczywistość

**Sim-to-Real Gap** - główny problem w robotyce AI

**Dlaczego model działa w symulacji, ale nie na prawdziwym robocie?**

1. **Fizyka** - Symulator to przybliżenie
   - Tarcie, bezwładność, sprężystość mogą się różnić
   
2. **Czujniki** - Idealne vs. rzeczywiste
   - Szum, opóźnienia, kalibracja
   
3. **Timing** - Różne częstotliwości kontroli
   
4. **Wizja** - Renderowane vs. rzeczywiste obrazy

**Techniki zmniejszania gap:**

```python
# 1. Domain Randomization w symulacji
config.sim.randomize_physics = True
config.sim.randomize_lighting = True
config.sim.add_sensor_noise = True

# 2. Augmentacja danych
transform = transforms.Compose([
    RandomBrightness(0.8, 1.2),
    RandomNoise(std=0.01),
    RandomBlur(kernel_size=3),
])

# 3. Progressive deployment
# Krok 1: Test w symulacji
# Krok 2: Test z robotem w bezpiecznej klatce
# Krok 3: Test w kontrolowanych warunkach
# Krok 4: Wdrożenie pełne
```

### 6.2 Bezpieczne Testowanie

**Protokół bezpieczeństwa:**

1. **Przed testem**
   - [ ] Sprawdź limity stawów w konfiguracji
   - [ ] Upewnij się, że Emergency Stop jest dostępny
   - [ ] Usuń przeszkody z obszaru roboczego
   - [ ] Powiadom osoby w pobliżu

2. **Podczas testu**
   - Obserwuj temperaturę silników
   - Słuchaj nietypowych dźwięków
   - Gotowość do awaryjnego zatrzymania

3. **Po teście**
   - Analiza logów (czy były błędy?)
   - Inspekcja mechaniczna robota
   - Dokumentacja obserwacji

**Awaryjne zatrzymanie:**

```python
# W kodzie - zawsze miej shutdown hook
import signal

def emergency_stop(signum, frame):
    print("EMERGENCY STOP!")
    robot.disconnect()
    sys.exit(0)

signal.signal(signal.SIGINT, emergency_stop)  # Ctrl+C
```

### 6.3 Debugging Problemów

#### Problem: Robot wykonuje chaotyczne ruchy

**Możliwe przyczyny:**
1. Model niedouczony/przeuczony
2. Błędna normalizacja danych
3. Niekompatybilna konfiguracja robota
4. Zbyt wysokie gejny PD

**Debugging:**
```python
# 1. Sprawdź zakresy akcji
print(f"Action min: {action.min()}, max: {action.max()}")
# Powinny być w rozsądnych granicach (np. -0.5, 0.5 dla delta)

# 2. Wizualizuj przewidywania vs. rzeczywistość
plt.plot(predicted_actions, label='Predicted')
plt.plot(ground_truth_actions, label='Ground Truth')
plt.legend()
plt.show()

# 3. Test z "known-good" modelem
# Użyj sprawdzonego modelu z Hub do weryfikacji setupu
```

#### Problem: Robot nie reaguje na komendy

**Możliwe przyczyny:**
1. Brak połączenia z serwerem
2. Błędny adres IP w konfiguracji
3. Firewall blokuje porty ZMQ
4. Serwer nie działa na robocie

**Debugging:**
```bash
# 1. Test ping
ping <ROBOT_IP>

# 2. Test połączenia ZMQ
python -c "
import zmq
ctx = zmq.Context()
sock = ctx.socket(zmq.REQ)
sock.connect('tcp://<ROBOT_IP>:6000')
print('Connected!')
"

# 3. Sprawdź logi serwera
# Na robocie, terminal z run_g1_server.py powinien pokazywać aktywność
```

---

## Moduł 7: Projekt Zaliczeniowy

### 7.1 Propozycje Projektów

#### Projekt 1: Imitacja Prostego Gestu (Łatwy)

**Cel:** Nauczenie robota powtarzania prostego gestu (np. machanie ręką)

**Kroki:**
1. Zbierz 50 demonstracji w symulacji
2. Wytrenuj model ACT
3. Oceń success rate
4. Wdróż na prawdziwym robocie (jeśli dostępny)

**Kryteria oceny:**
- 80%+ success rate w symulacji
- Płynne wykonanie
- Raport z analizą wyników

#### Projekt 2: Manipulacja Obiektem (Średni)

**Cel:** Robot podnosi i przenosi obiekt z punktu A do B

**Kroki:**
1. Zbierz 100-200 demonstracji
2. Eksperymentuj z różnymi modelami (ACT vs Diffusion)
3. Porównaj wyniki
4. Domain randomization

**Kryteria oceny:**
- Porównanie modeli (metryki + analiza)
- 70%+ success rate
- Raport naukowy

#### Projekt 3: Lokomotoryka z RL (Zaawansowany)

**Cel:** Nauczenie robota chodzenia używając Reinforcement Learning

**Kroki:**
1. Zaprojektuj funkcję nagrody
2. Implementacja w IsaacGym/MuJoCo
3. Trenowanie (wiele godzin GPU)
4. Transfer do prawdziwego robota

**Kryteria oceny:**
- Stabilne chodzenie w symulacji
- Analiza reward shaping
- Porównanie z GR00T
- Szczegółowy raport

### 7.2 Szablon Raportu

```markdown
# Raport z Projektu: [Tytuł]

## 1. Wprowadzenie
- Opis problemu
- Motywacja
- Cele projektu

## 2. Przegląd Literatury
- Podobne prace
- Wykorzystane metody
- Inspiracje

## 3. Metodologia
- Architektura modelu
- Dataset (jak zbierany, ile danych)
- Parametry treningu
- Środowisko testowe

## 4. Eksperymenty
- Opis eksperymentów
- Warunki testowe
- Metryki

## 5. Wyniki
- Metryki ilościowe (tabele, wykresy)
- Analiza jakościowa
- Wizualizacje (screenshoty, wideo)

## 6. Dyskusja
- Interpretacja wyników
- Napotkane problemy
- Wnioski
- Przyszłe prace

## 7. Podsumowanie

## Bibliografia

## Dodatki
- Kod (kluczowe fragmenty lub link do repo)
- Dane treningowe (link do HF Hub)
- Dodatkowe wizualizacje
```

---

## Moduł 8: Najlepsze Praktyki i Porady

### 8.1 Zarządzanie Projektem

**Git i kontrola wersji:**
```bash
# Dobra struktura commitów
git commit -m "feat: Add new policy architecture"
git commit -m "fix: Correct action normalization"
git commit -m "docs: Update README with training instructions"

# Używaj branchy
git checkout -b feature/new-policy
git checkout -b fix/data-loading

# Regularne push do remote
git push origin main
```

**Dokumentacja:**
- Komentuj skomplikowany kod
- Prowadź research notebook
- Zapisuj parametry eksperymentów

**Reprodukowalność:**
```python
# Zawsze ustaw seed!
import random
import numpy as np
import torch

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

set_seed(42)
```

### 8.2 Optymalizacja Wydajności

**Training speed:**
```python
# 1. Używaj DataLoader z multiple workers
train_loader = DataLoader(
    dataset, 
    batch_size=32,
    num_workers=4,  # Ładowanie danych w tle
    pin_memory=True  # Szybszy transfer CPU->GPU
)

# 2. Mixed precision training
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()
with autocast():
    output = model(input)
    loss = criterion(output, target)
scaler.scale(loss).backward()

# 3. Gradient accumulation (dla większych batch)
for i, batch in enumerate(train_loader):
    loss = model(batch) / accumulation_steps
    loss.backward()
    
    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

**Inference speed:**
```python
# 1. Model w trybie eval
model.eval()
with torch.no_grad():  # Wyłącz gradient computation
    output = model(input)

# 2. Batch inference (gdy możliwe)
# 3. ONNX export dla production
torch.onnx.export(model, dummy_input, "model.onnx")

# 4. TensorRT dla NVIDIA (najszybsze)
```

### 8.3 Troubleshooting Checklist

**Model nie uczy się:**
- [ ] Sprawdź czy dane są poprawnie załadowane
- [ ] Zweryfikuj normalizację (mean=0, std=1?)
- [ ] Czy loss się liczy poprawnie?
- [ ] Learning rate - spróbuj 10x mniejszy/większy
- [ ] Czy gradient flow jest OK? (print grad norms)

**Model overfittuje:**
- [ ] Więcej danych
- [ ] Data augmentation
- [ ] Regularization (dropout, weight decay)
- [ ] Mniejszy model (mniej parametrów)
- [ ] Early stopping

**Sim-to-real nie działa:**
- [ ] Domain randomization w symulacji
- [ ] Real-world data augmentation
- [ ] Fine-tuning na małym real dataset
- [ ] Analiza distribution shift

---

## Moduł 9: Zasoby i Dalsza Nauka

### 9.1 Rekomendowane Materiały

**Kursy Online:**
1. **Deep Learning for Robotics** - edX
2. **Robot Learning** - YouTube (Berkeley)
3. **Reinforcement Learning** - David Silver (DeepMind)

**Książki:**
1. "Robotics, Vision and Control" - Peter Corke
2. "Probabilistic Robotics" - Thrun, Burgard, Fox
3. "Deep Learning" - Goodfellow, Bengio, Courville

**Papers (Must Read):**
1. ACT: "Action Chunking with Transformers" (2023)
2. Diffusion Policy: "Diffusion Policy" (2023)
3. GR00T: "Foundation Model for Humanoid Robots" (2024)

### 9.2 Społeczność

**Fora i Grupy:**
- Discord LeRobot - https://discord.gg/q8Dzzpym3f
- r/robotics - Reddit
- ROS Discourse - https://discourse.ros.org/

**Konferencje:**
- ICRA (International Conference on Robotics and Automation)
- RSS (Robotics: Science and Systems)
- CoRL (Conference on Robot Learning)

### 9.3 Kariera w Robotyce AI

**Ścieżki zawodowe:**
1. **Research Scientist** - badania, publikacje
2. **Robotics Engineer** - implementacja systemów
3. **ML Engineer** - optymalizacja modeli
4. **Application Engineer** - wdrożenia u klientów

**Umiejętności do rozwijania:**
- Python, C++ (języki)
- PyTorch, TensorFlow (frameworks)
- ROS/ROS2 (middleware)
- Linux, Docker (devops)
- Git, CI/CD (collaboration)

**Portfolio:**
- Projekty na GitHub
- Datasets na HF Hub
- Blog posts / YouTube
- Wkład w open-source

---

## Podsumowanie

Gratulacje! Ukończyłeś przewodnik. Teraz masz kompletną wiedzę do pracy z robotem Unitree G1 EDU i platformą LeRobot.

**Kluczowe punkty:**
1. ✅ Rozumiesz architekturę systemu
2. ✅ Potrafisz zbierać i zarządzać danymi
3. ✅ Wiesz jak trenować modele
4. ✅ Możesz wdrażać na prawdziwym robocie
5. ✅ Znasz best practices

**Następne kroki:**
1. Zacznij od prostego projektu
2. Eksperymentuj i ucz się z błędów
3. Dziel się wynikami ze społecznością
4. Rozwijaj umiejętności dalej

**Pamiętaj:**
> "Robotyka to połączenie teorii i praktyki. Nie bój się brudzić rąk i testować w rzeczywistości!" 

---

**Powodzenia w Twoich projektach robotycznych! 🤖**

## Kontakt i Wsparcie

Pytania? Problemy? Skontaktuj się:
- Discord: LeRobot server
- GitHub Issues: huggingface/lerobot
- Email: lerobot@huggingface.co

---

_Dokument stworzony dla studentów przez wykładowców z pasją do robotyki._
_Ostatnia aktualizacja: Luty 2025_
