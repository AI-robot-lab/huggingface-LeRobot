# Praktyczne Przykłady Projekty z Robotem Unitree G1 EDU

## Wprowadzenie

Ten dokument zawiera praktyczne przykłady projektów, które studenci mogą realizować z robotem humanoidalnym Unitree G1 EDU. Każdy przykład jest opisany krok po kroku z wyjaśnieniem celów edukacyjnych.

---

## Przykład 1: Podstawowa Lokomotoryka - "Hello World" Robotyki

### Cel Edukacyjny
Nauka podstaw sterowania robotem humanoidalnym i zrozumienie działania polityk lokomotorycznych.

### Opis Projektu
Robot uczy się utrzymywać równowagę i reagować na proste komendy ruchu z kontrolera.

### Krok po Kroku

#### 1. Połączenie z Robotem

```bash
# Na robocie (SSH)
ssh unitree@192.168.123.164
cd lerobot
conda activate lerobot
python src/lerobot/robots/unitree_g1/run_g1_server.py
```

**Co się dzieje:**
- Łączysz się z komputerem wbudowanym w robota (Orin)
- Uruchamiasz serwer mostka DDS-ZMQ
- Serwer czeka na połączenia od klientów

#### 2. Uruchomienie Polityki GR00T

```bash
# Na swoim komputerze
cd lerobot
conda activate lerobot
python examples/unitree_g1/gr00t_locomotion.py --repo-id "nepyope/GR00T-WholeBodyControl_g1"
```

**Co się dzieje:**
- Program pobiera wytrenowany model GR00T z Hugging Face Hub
- Łączy się z serwerem na robocie przez WiFi/Ethernet
- Zaczyna wysyłać komendy sterowania 50 razy na sekundę

#### 3. Eksperymenty

**A. Test Balansu**
- Pozostaw joystick w pozycji neutralnej
- Obserwuj jak robot utrzymuje równowagę
- Spróbuj lekko popchnąć robota - obserwuj korekcje

**Pytania do przemyślenia:**
- Jak szybko robot reaguje na zakłócenia?
- Czy widzisz ciągłe małe korekty pozycji?
- Co się dzieje z pozycją stawów kolan i bioder?

**B. Test Chodzenia**
- Wychyl lewy joystick do przodu (LY)
- Robot powinien zacząć iść do przodu
- Zaobserwuj zmianę chodu

**Pytania do przemyślenia:**
- Jak płynne są przejścia między krokami?
- Czy robot unosi stopy wystarczająco wysoko?
- Jak stabilna jest górna część ciała podczas chodzenia?

**C. Test Obrotów**
- Wychyl prawy joystick w bok (RX)
- Robot obraca się wokół pionowej osi
- Obserwuj jak zmienia się orientacja

**D. Test Ruchów Bocznych**
- Wychyl lewy joystick w bok (LX)
- Robot porusza się w bok (strafe)
- Zaobserwuj różnicę względem chodzenia do przodu

#### 4. Zbieranie Danych

Zanotuj swoje obserwacje:

| Test | Stabilność (1-10) | Płynność (1-10) | Uwagi |
|------|-------------------|-----------------|-------|
| Balans | | | |
| Chodzenie | | | |
| Obrót | | | |
| Bok | | | |

### Zadania dla Studentów

**Zadanie 1: Analiza Parametrów**
Zmień parametry w `gr00t_locomotion.py`:
- `ACTION_SCALE` (spróbuj 0.1, 0.25, 0.5)
- Jak zmiana wpływa na zachowanie robota?

**Zadanie 2: Wizualizacja**
Napisz skrypt do logowania i wizualizacji:
- Pozycji stawów w czasie
- Prędkości ruchu
- Danych IMU (orientacja)

**Zadanie 3: Raport**
Napisz 2-stronicowy raport:
- Jak działa system lokomotoryczny?
- Jakie są ograniczenia modelu GR00T?
- Propozycje ulepszeń

---

## Przykład 2: Zbieranie Datasetu - Uczenie przez Demonstrację

### Cel Edukacyjny
Zrozumienie procesu zbierania danych demonstracyjnych i ich roli w uczeniu maszynowym.

### Opis Projektu
Nagraj dataset demonstracji prostego zadania manipulacyjnego używając teleoperatora egzoszkieletowego.

### Definicja Zadania

**Zadanie: "Podnieś i przestaw kubek"**

**Specyfikacja:**
- Punkt startowy: Kubek stoi na stole po lewej stronie
- Punkt końcowy: Kubek ma stać na stole po prawej stronie
- Ograniczenia: Robot stoi w jednym miejscu (bez chodzenia)
- Sukces: Kubek stoi stabilnie na końcowym miejscu

### Krok po Kroku

#### 1. Przygotowanie Środowiska

**Fizyczne:**
```
┌─────────────────────────────────┐
│           Stół                  │
│                                 │
│  [Kubek]              [ ]       │
│  START              META        │
│                                 │
│        [Robot tutaj]            │
└─────────────────────────────────┘
```

**Checklist:**
- [ ] Stół jest stabilny i na odpowiedniej wysokości
- [ ] Kubek jest lekki i łatwy do chwycenia
- [ ] Obszar jest dobrze oświetlony dla kamer
- [ ] Brak przeszkód w zasięgu robota
- [ ] Oznacz pozycję START i META taśmą

#### 2. Kalibracja Teleoperatora

```bash
lerobot-calibrate \
    --teleop.type=unitree_g1 \
    --teleop.left_arm_config.port=/dev/ttyACM1 \
    --teleop.right_arm_config.port=/dev/ttyACM0 \
    --teleop.id=exo
```

**Co robi kalibracja:**
- Mapuje zakres ruchu egzoszkieletu na zakres stawów robota
- Znajduje pozycje neutralne (środki zakresów)
- Zapisuje parametry do pliku

**Wskazówki:**
- Wykonaj pełen zakres ruchów w każdej osi
- Zatrzymaj się na sekundę w skrajnych pozycjach
- Powtórz jeśli czujesz, że coś jest nie tak

#### 3. Trening (Nauka Zadania)

Przed nagrywaniem, przećwicz zadanie 10-20 razy:
1. Załóż egzoszkielet
2. Uruchom teleoperację (bez nagrywania)
3. Wykonaj zadanie powoli i płynnie
4. Zwracaj uwagę na:
   - Trajektorię ruchu (najkrótsza ścieżka?)
   - Orientację dłoni (stabilna?)
   - Siłę chwytu (nie za mocno, nie za słabo)
   - Płynność (bez szarpnięć)

#### 4. Nagrywanie Datasetu

```bash
# W symulacji (bezpieczniejsze na początek)
python -m lerobot.scripts.lerobot_record \
    --robot.type=unitree_g1 \
    --robot.is_simulation=true \
    --teleop.type=unitree_g1 \
    --teleop.left_arm_config.port=/dev/ttyACM1 \
    --teleop.right_arm_config.port=/dev/ttyACM0 \
    --teleop.id=exo \
    --dataset.repo_id=student-username/pickup-cup \
    --dataset.single_task="Pickup and place cup" \
    --dataset.num_episodes=50 \
    --dataset.episode_time_s=10 \
    --dataset.reset_time_s=5
```

**Parametry wyjaśnione:**
- `num_episodes=50`: Nagraj 50 prób (demonstracji)
- `episode_time_s=10`: Każda próba trwa 10 sekund
- `reset_time_s=5`: 5 sekund na zresetowanie środowiska między próbami

**Podczas nagrywania:**
1. **Sygnał startu** - usłyszysz dźwięk/zobaczysz komunikat
2. **Wykonanie** - wykonaj zadanie płynnie (10s)
3. **Sygnał końca** - stop nagrywania
4. **Reset** - postaw kubek z powrotem na START (5s)
5. **Powtórz** - kolejna próba

**Wskazówki jakości:**
- **Sukces przede wszystkim**: Nagrywaj głównie udane próby
- **Konsystencja**: Wykonuj podobnie każdym razem
- **Płynność**: Unikaj nagłych ruchów i zatrzymań
- **Kompletność**: Pokaż pełne wykonanie od początku do końca
- **Różnorodność**: Trochę zmieniaj pozycję kubka (±2cm)

#### 5. Inspekcja Datasetu

```python
from lerobot.datasets.lerobot_dataset import LeRobotDataset

# Załaduj lokalnie
dataset = LeRobotDataset("student-username/pickup-cup")

# Podstawowe statystyki
print(f"Liczba epizodów: {dataset.num_episodes}")
print(f"Liczba klatek: {len(dataset)}")
print(f"Średni czas epizodu: {len(dataset) / dataset.num_episodes / dataset.fps:.2f}s")

# Sprawdź pierwszy epizod
episode_0 = dataset[0]
print(f"Kształt akcji: {episode_0['action'].shape}")
print(f"Dostępne kamery: {[k for k in episode_0.keys() if 'image' in k]}")

# Wizualizacja
from lerobot.visualize import visualize_dataset
visualize_dataset(dataset, episode_index=0)
```

**Co sprawdzać:**
- Czy wszystkie epizody mają podobną długość?
- Czy obrazy z kamer są wyraźne?
- Czy pozycje stawów zmieniają się płynnie?
- Czy synchronizacja obraz-akcje jest poprawna?

#### 6. Czyszczenie Datasetu

```python
# Usuń nieudane epizody (np. upuścił kubek)
dataset.delete_episodes([5, 12, 23])  # Indeksy do usunięcia

# Zapisz oczyszczony dataset
dataset.save()

# Push do Hugging Face Hub
dataset.push_to_hub()
```

### Zadania dla Studentów

**Zadanie 1: Analiza Jakości Danych**
```python
import matplotlib.pyplot as plt

# Wykres trajektorii dla wszystkich epizodów
for i in range(dataset.num_episodes):
    episode = dataset[i]
    plt.plot(episode['action'][:, 0])  # Pozycja pierwszego stawu
    
plt.xlabel('Klatka')
plt.ylabel('Pozycja stawu [rad]')
plt.title('Trajektorie wszystkich epizodów')
plt.show()
```

**Pytania:**
- Czy trajektorie są podobne?
- Gdzie są największe różnice?
- Które epizody są "outliery"?

**Zadanie 2: Statystyki Datasetu**
Oblicz i przedstaw:
- Rozkład długości epizodów
- Zakresy ruchów każdego stawu
- Średnie prędkości ruchów
- Korelacje między stawami

**Zadanie 3: Eksperyment z Różnorodnością**
Nagraj dwa datasety:
1. 50 epizodów, kubek zawsze w tym samym miejscu
2. 50 epizodów, kubek w losowych miejscach (±5cm)

Porównaj:
- Którą politykę łatwiej wytrenować?
- Która jest bardziej robustna?

---

## Przykład 3: Trenowanie Modelu ACT

### Cel Edukacyjny
Zrozumienie procesu trenowania modelu uczenia maszynowego dla robotyki.

### Opis Projektu
Wytrenowanie polityki ACT (Action Chunking Transformer) na zebranym datasecie.

### Architektura ACT

```
┌─────────────────────────────────────────────────────┐
│                  MODEL ACT                          │
│                                                     │
│  ┌──────────────┐      ┌─────────────────┐         │
│  │   Obserwacje │─────▶│  Vision Encoder │         │
│  │   (obrazy +  │      │   (ResNet-18)   │         │
│  │    stawy)    │      └────────┬────────┘         │
│  └──────────────┘               │                  │
│                                  │                  │
│                         ┌────────▼────────┐         │
│                         │  Transformer    │         │
│                         │  (Self-Attn)    │         │
│                         └────────┬────────┘         │
│                                  │                  │
│                         ┌────────▼────────┐         │
│                         │  CVAE Decoder   │         │
│                         │  (Variational)  │         │
│                         └────────┬────────┘         │
│                                  │                  │
│                         ┌────────▼────────┐         │
│                         │ Sekwencja Akcji │         │
│                         │    (chunk=100)  │         │
│                         └─────────────────┘         │
└─────────────────────────────────────────────────────┘
```

**Kluczowe cechy:**
- **Action Chunking**: Przewiduje 100 akcji naraz, nie pojedynczą
- **Transformer**: Uwzględnia zależności czasowe
- **CVAE**: Variational bottleneck dla generalizacji

### Krok po Kroku

#### 1. Przygotowanie Środowiska

```bash
# Utwórz środowisko z GPU support
conda create -n lerobot-train python=3.10
conda activate lerobot-train
pip install lerobot[train]

# Sprawdź GPU
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

**Wymagania sprzętowe:**
- GPU: Minimum 8GB VRAM (RTX 3070, A4000, lub lepsze)
- RAM: Minimum 16GB
- Dysk: ~50GB wolnej przestrzeni

#### 2. Konfiguracja Treningu

Utwórz plik `config_train.yaml`:

```yaml
# Podstawowa konfiguracja treningu ACT

policy:
  name: act
  
  # Architektura
  chunk_size: 100          # Ile akcji przewidywać naraz
  n_obs_steps: 1          # Ile klatek obserwacji jako wejście
  dim_model: 512          # Wymiar ukryty transformera
  n_heads: 8              # Liczba głów attention
  dim_feedforward: 3200   # Wymiar warstw feed-forward
  n_encoder_layers: 4     # Głębokość enkodera
  n_decoder_layers: 1     # Głębokość dekodera
  
  # CVAE
  use_vae: true
  latent_dim: 32          # Wymiar przestrzeni latentnej
  
  # Normalizacja
  normalize_inputs: true
  normalize_targets: true

training:
  # Optymalizacja
  batch_size: 8           # Ile przykładów naraz
  num_epochs: 1000        # Ile przejść przez dataset
  lr: 1e-4                # Learning rate
  weight_decay: 1e-4      # L2 regularization
  
  # Harmonogram LR
  lr_scheduler: cosine
  lr_warmup_epochs: 50
  
  # Zapis modelu
  save_freq: 50           # Co ile epok zapisywać
  eval_freq: 10           # Co ile epok ewaluować
  
  # Losowość
  seed: 42
  
dataset:
  repo_id: student-username/pickup-cup
  split_ratio: 0.9        # 90% train, 10% val

output_dir: outputs/act_pickup_cup
```

#### 3. Uruchomienie Treningu

```bash
lerobot-train \
    --config config_train.yaml \
    --wandb.enable=true \
    --wandb.project=unitree-g1-pickup
```

**Co się dzieje:**
1. Ładowanie datasetu z Hugging Face Hub
2. Inicjalizacja modelu (losowe wagi)
3. Pętla trenowania:
   - Forward pass (przewidywanie)
   - Obliczenie loss (błąd)
   - Backward pass (gradienty)
   - Update wag (optymalizacja)
4. Walidacja co N epok
5. Zapis checkpointów

**Metryki do obserwowania:**

| Metryka | Co oznacza | Docelowa wartość |
|---------|------------|------------------|
| train_loss | Błąd na danych treningowych | Spadek do ~0.01 |
| val_loss | Błąd na danych walidacyjnych | Podobny do train |
| mse_action | Średni kwadrat błędu akcji | < 0.05 |
| kl_divergence | Regularizacja CVAE | ~0.1-1.0 |

#### 4. Monitorowanie przez TensorBoard

```bash
# W osobnym terminalu
tensorboard --logdir outputs/act_pickup_cup/logs
```

Otwórz w przeglądarce: http://localhost:6006

**Zakładki do sprawdzenia:**
- **Scalars**: Wykresy metryk w czasie
- **Images**: Wizualizacje przewidywanych akcji
- **Distributions**: Rozkłady wag i gradientów
- **Graphs**: Architektura modelu

#### 5. Analiza Treningu

**Czy trening idzie dobrze?**

✅ **Dobry trening:**
```
Epoch  Train Loss  Val Loss
-----  ----------  --------
1      0.850       0.920
10     0.520       0.580
50     0.150       0.180
100    0.080       0.095
500    0.012       0.018
1000   0.008       0.015
```
- Loss stabilnie spada
- Val loss podąża za train loss
- Niewielka różnica między train a val

❌ **Overfitting:**
```
Epoch  Train Loss  Val Loss
-----  ----------  --------
1      0.850       0.920
50     0.150       0.180
100    0.050       0.120
500    0.005       0.150  ← Rośnie!
1000   0.001       0.200
```
- Train loss spada, val loss rośnie
- Model "zapamiętuje" dane treningowe

**Rozwiązania overfittingu:**
1. Więcej danych (zwiększ num_episodes)
2. Data augmentation
3. Zwiększ weight_decay
4. Zmniejsz model (mniej parametrów)
5. Early stopping

❌ **Underfitting:**
```
Epoch  Train Loss  Val Loss
-----  ----------  --------
1      0.850       0.920
100    0.750       0.800
500    0.720       0.780
1000   0.710       0.775
```
- Loss prawie się nie zmienia
- Wartości wysokie

**Rozwiązania underfittingu:**
1. Zwiększ learning rate
2. Większy model (więcej parametrów)
3. Więcej epok treningu
4. Lepsze features (dodaj więcej kamer?)

#### 6. Ewaluacja Modelu

```bash
# Symulacja
lerobot-eval \
    --policy.path=outputs/act_pickup_cup/checkpoints/best.pth \
    --env.type=mujoco \
    --env.task=pickup_cup \
    --eval.n_episodes=20

# Prawdziwy robot (ostrożnie!)
lerobot-eval \
    --policy.path=outputs/act_pickup_cup/checkpoints/best.pth \
    --robot.type=unitree_g1 \
    --robot.is_simulation=false \
    --eval.n_episodes=10
```

**Metryki sukcesu:**
- **Success Rate**: % udanych wykonań (cel: >70%)
- **Average Return**: Średnia nagroda (im wyższa tym lepiej)
- **Execution Time**: Czas wykonania zadania

### Zadania dla Studentów

**Zadanie 1: Hyperparameter Tuning**
Eksperymentuj z parametrami:

| Parametr | Wartość domyślna | Test 1 | Test 2 | Test 3 |
|----------|------------------|--------|--------|--------|
| batch_size | 8 | 4 | 16 | 32 |
| lr | 1e-4 | 1e-5 | 5e-4 | 1e-3 |
| chunk_size | 100 | 50 | 200 | 300 |

Który zestaw daje najlepsze wyniki?

**Zadanie 2: Ablation Study**
Wytrenuj modele z:
1. Pełnym ACT
2. ACT bez CVAE
3. ACT bez Transformera (tylko MLP)
4. ACT z mniejszym chunk_size (10 vs 100)

Porównaj:
- Czas treningu
- Success rate
- Smoothness trajektorii

**Zadanie 3: Visualize Predictions**
```python
import torch
from lerobot.policies.act import ACTPolicy

# Załaduj model
policy = ACTPolicy.from_pretrained("outputs/act_pickup_cup/checkpoints/best.pth")

# Predykcja
obs = dataset[0]['observation']
predicted_actions = policy.select_action(obs)

# Wykres
plt.plot(predicted_actions.cpu().numpy(), label='Predicted')
plt.plot(dataset[0]['action'].numpy(), label='Ground Truth')
plt.legend()
plt.show()
```

Gdzie model popełnia największe błędy?

---

## Przykład 4: Transfer Learning - Od Symulacji do Rzeczywistości

### Cel Edukacyjny
Zrozumienie problemu sim-to-real gap i technik jego zmniejszania.

### Opis Projektu
Trenowanie modelu w symulacji, a następnie transfer na prawdziwego robota z fine-tuningiem.

### Problem: Sim-to-Real Gap

**Dlaczego model działa w symulacji, ale nie na prawdziwym robocie?**

| Aspekt | Symulacja | Rzeczywistość |
|--------|-----------|---------------|
| Fizyka | Idealna | Tarcie, bezwładność, sprężystość |
| Czujniki | Bez szumu | Szum, opóźnienia, bias |
| Timing | Precyzyjny | Jitter, dropsy |
| Wizja | Renderowane obrazy | Oświetlenie, refleksy, motion blur |
| Dynamika | Deterministyczna | Stochastyczna |

### Krok po Kroku

#### 1. Trening Bazowy w Symulacji

```bash
# Zbierz duży dataset w symulacji (taniej i szybciej)
python -m lerobot.scripts.lerobot_record \
    --robot.is_simulation=true \
    --dataset.repo_id=student/sim-pickup-large \
    --dataset.num_episodes=500  # Dużo danych!
    --dataset.episode_time_s=10

# Trenuj
lerobot-train \
    --dataset.repo_id=student/sim-pickup-large \
    --policy=act \
    --training.num_epochs=2000 \
    --output_dir=outputs/act_sim_base
```

**Cel: Solidny bazowy model wytrenowany na dużej ilości danych syntetycznych**

#### 2. Domain Randomization

Zmodyfikuj symulację aby była bardziej realistyczna:

```python
# W pliku konfiguracji symulacji
sim_config = {
    # Randomizacja fizyki
    "friction_range": [0.5, 1.5],          # Losowe tarcie
    "mass_range": [0.9, 1.1],               # ±10% masy obiektów
    "damping_range": [0.8, 1.2],            # Losowe tłumienie
    
    # Randomizacja wizualna
    "lighting": {
        "intensity_range": [0.7, 1.3],
        "position_random": True,
        "color_temp_range": [3000, 7000],   # Różne temperatury światła
    },
    
    # Randomizacja czujników
    "imu_noise_std": 0.01,                  # Szum IMU
    "encoder_noise_std": 0.001,             # Szum enkoderów
    "camera_noise_std": 5.0,                # Szum obrazu
    
    # Randomizacja zadania
    "object_position_range": [-0.05, 0.05], # ±5cm pozycji
    "object_rotation_range": [-0.2, 0.2],   # ±11° obrotu
}
```

**Retrenuj z randomizacją:**
```bash
lerobot-train \
    --dataset.repo_id=student/sim-pickup-randomized \
    --policy=act \
    --policy.pretrained=outputs/act_sim_base/checkpoints/best.pth \
    --training.num_epochs=1000 \
    --output_dir=outputs/act_sim_robust
```

#### 3. Zbierz Małą Ilość Danych z Prawdziwego Robota

```bash
# Tylko 20-50 epizodów (drogi czas prawdziwego robota!)
python -m lerobot.scripts.lerobot_record \
    --robot.is_simulation=false \
    --dataset.repo_id=student/real-pickup-small \
    --dataset.num_episodes=30
    --dataset.episode_time_s=10
```

**Dlaczego tylko tyle?**
- Czas na prawdziwym robocie jest cenny
- Ryzyko uszkodzenia sprzętu
- Zmęczenie operatora

#### 4. Fine-Tuning na Rzeczywistych Danych

```bash
lerobot-train \
    --dataset.repo_id=student/real-pickup-small \
    --policy=act \
    --policy.pretrained=outputs/act_sim_robust/checkpoints/best.pth \
    --training.num_epochs=500 \
    --training.lr=1e-5 \  # Mniejszy LR dla fine-tuningu!
    --training.freeze_encoder=true \  # Zamroź encoder wizyjny
    --output_dir=outputs/act_real_finetuned
```

**Strategia fine-tuningu:**
- Niski learning rate (nie chcemy "zapomnieć" wiedzy z symulacji)
- Zamrożony encoder (główne features są dobre)
- Dostrajamy tylko decoder (adaptacja do rzeczywistości)

#### 5. Ewaluacja Transfer Learning

```bash
# Test na prawdziwym robocie
lerobot-eval \
    --policy.path=outputs/act_real_finetuned/checkpoints/best.pth \
    --robot.type=unitree_g1 \
    --robot.is_simulation=false \
    --eval.n_episodes=20
```

**Porównaj modele:**

| Model | Dane treningowe | Success Rate (sim) | Success Rate (real) |
|-------|----------------|-------------------|---------------------|
| Sim Base | 500 sim | 95% | 20% ← Sim-to-real gap! |
| Sim + Domain Rand | 500 sim (rand) | 90% | 45% ← Lepiej! |
| Fine-tuned | 500 sim + 30 real | 85% | 75% ← Najlepszy! |

### Zadania dla Studentów

**Zadanie 1: Ablation Study Randomizacji**

Przetestuj wpływ różnych typów randomizacji:

| Randomizacja | Success Rate Real |
|--------------|-------------------|
| Brak | |
| Tylko fizyka | |
| Tylko wizja | |
| Tylko czujniki | |
| Wszystko | |

Która ma największy wpływ?

**Zadanie 2: Analiza Błędów**

Nagrywaj video niepowodzeń:
- Sklasyfikuj typy błędów (nie trafił, upuścił, kolizja...)
- Które błędy są częste?
- Czy można je naprawić data augmentation?

**Zadanie 3: Progressive Realism**

Stopniowo zwiększaj realizm symulacji:
1. Bazowa symulacja (idealna)
2. + losowe tarcie
3. + szum czujników
4. + randomizacja wizualna
5. + wszystko razem

Na której iteracji model zaczyna działać na prawdziwym robocie?

---

## Przykład 5: Projekt Zaliczeniowy - Kompletny Pipeline

### Cel
Zrealizowanie kompletnego projektu od początku do końca: definicja zadania, zbieranie danych, trening, wdrożenie, dokumentacja.

### Propozycje Zadań

#### Opcja A: "Robot Kelner"
Robot bierze przedmiot z jednego stołu i przenosi na drugi (z chodzeniem).

#### Opcja B: "Sortowanie Kolorów"
Robot rozpoznaje kolor kostki i wkłada ją do odpowiedniego pudełka.

#### Opcja C: "Otwarcie Drzwi"
Robot chwyta klamkę i otwiera drzwi (koordynacja ręka-noga).

### Wymagania Projektu

**1. Dokumentacja (30%)**
- [ ] Opis zadania i motywacja
- [ ] Specyfikacja środowiska i setupu
- [ ] Architektura systemu
- [ ] Analiza zebranych danych
- [ ] Wyniki treninigów (wykresy, metryki)
- [ ] Ewaluacja na prawdziwym robocie
- [ ] Wnioski i przyszłe prace

**2. Dataset (20%)**
- [ ] Minimum 50 udanych demonstracji
- [ ] Wysokiej jakości (płynne, konsystentne)
- [ ] Opublikowany na Hugging Face Hub
- [ ] README z opisem

**3. Model (30%)**
- [ ] Wytrenowany i działający
- [ ] Eksperymenty z hyperparametrami
- [ ] Porównanie przynajmniej 2 architektur
- [ ] Analiza błędów

**4. Wdrożenie (20%)**
- [ ] Działa w symulacji (>70% success)
- [ ] Przetestowany na prawdziwym robocie
- [ ] Video demonstracji
- [ ] Kod opublikowany na GitHub

### Harmonogram (8 tygodni)

**Tydzień 1-2: Przygotowanie**
- Definicja zadania
- Setup środowiska
- Trening teleopereacji
- Pilot dataset (10 demonstracji)

**Tydzień 3-4: Zbieranie Danych**
- Nagranie pełnego datasetu (50+ demonstracji)
- Czyszczenie i inspekcja
- Augmentacja jeśli potrzebna

**Tydzień 5-6: Trenowanie**
- Bazowy model
- Hyperparameter tuning
- Ablation studies

**Tydzień 7: Ewaluacja**
- Testy w symulacji
- Transfer na prawdziwego robota
- Fine-tuning

**Tydzień 8: Dokumentacja**
- Pisanie raportu
- Przygotowanie prezentacji
- Publikacja materiałów

### Kryteria Oceny

| Kryterium | Punkty | Opis |
|-----------|--------|------|
| Dataset jakość | 20 | Płynność, konsystencja, różnorodność |
| Dataset ilość | 10 | ≥50 demonstracji |
| Model performance | 20 | Success rate na prawdziwym robocie |
| Eksperymenty | 15 | Ablations, porównania, analizy |
| Dokumentacja | 20 | Kompletność, czytelność, techniczna poprawność |
| Kod | 10 | Czytelny, udokumentowany, reprodukowalny |
| Prezentacja | 5 | Jasna, zwięzła, profesjonalna |

**Skala:**
- 90-100: Celujący (6.0)
- 80-89: Bardzo dobry (5.0)
- 70-79: Dobry plus (4.5)
- 60-69: Dobry (4.0)
- 50-59: Dostateczny plus (3.5)
- <50: Niedostateczny

---

## Dodatek: Szablony i Narzędzia

### Szablon Raportu Projektu

```markdown
# Tytuł Projektu

**Autor:** Imię Nazwisko
**Data:** YYYY-MM-DD
**Repozytorium:** github.com/username/project

## Streszczenie
(150-200 słów)

## 1. Wprowadzenie
### 1.1 Motywacja
### 1.2 Cele projektu
### 1.3 Przegląd literatury

## 2. Metodologia
### 2.1 Definicja zadania
### 2.2 Setup eksperymentalny
### 2.3 Zbieranie danych
### 2.4 Architektura modelu
### 2.5 Procedura treningowa

## 3. Eksperymenty
### 3.1 Analiza datasetu
### 3.2 Bazowy trening
### 3.3 Hyperparameter search
### 3.4 Ablation studies

## 4. Wyniki
### 4.1 Metryki ilościowe
### 4.2 Analiza jakościowa
### 4.3 Porównanie z baseline

## 5. Dyskusja
### 5.1 Interpretacja wyników
### 5.2 Limitations
### 5.3 Przyszłe prace

## 6. Podsumowanie

## Bibliografia

## Dodatki
### A. Hyperparametry
### B. Kod źródłowy
### C. Dodatkowe wizualizacje
```

### Narzędzia Diagnostyczne

```python
# check_dataset.py - Sprawdź jakość datasetu

from lerobot.datasets.lerobot_dataset import LeRobotDataset
import numpy as np
import matplotlib.pyplot as plt

def analyze_dataset(repo_id):
    dataset = LeRobotDataset(repo_id)
    
    print("=== PODSTAWOWE STATYSTYKI ===")
    print(f"Liczba epizodów: {dataset.num_episodes}")
    print(f"Liczba klatek: {len(dataset)}")
    print(f"FPS: {dataset.fps}")
    
    print("\n=== DŁUGOŚCI EPIZODÓW ===")
    episode_lengths = []
    for i in range(dataset.num_episodes):
        length = len([x for x in range(len(dataset)) if dataset[x]['episode_index'] == i])
        episode_lengths.append(length)
    
    print(f"Średnia: {np.mean(episode_lengths):.1f} klatek")
    print(f"Min: {np.min(episode_lengths)}, Max: {np.max(episode_lengths)}")
    print(f"Std: {np.std(episode_lengths):.1f}")
    
    # Wykres
    plt.hist(episode_lengths, bins=20)
    plt.xlabel('Długość epizodu [klatki]')
    plt.ylabel('Liczba epizodów')
    plt.title('Rozkład długości epizodów')
    plt.savefig('episode_lengths.png')
    
    print("\n=== ZAKRESY AKCJI ===")
    all_actions = []
    for i in range(min(1000, len(dataset))):  # Sample
        all_actions.append(dataset[i]['action'])
    all_actions = np.array(all_actions)
    
    for j in range(all_actions.shape[1]):
        print(f"Staw {j}: [{all_actions[:,j].min():.3f}, {all_actions[:,j].max():.3f}]")
    
    return dataset

if __name__ == "__main__":
    analyze_dataset("student-username/pickup-cup")
```

---

## Podsumowanie

Te przykłady pokazują kompletny workflow pracy z robotem humanoidalnym:
1. **Podstawy** - Nauka sterowania i obserwacji zachowania
2. **Dane** - Zbieranie wysokiej jakości demonstracji
3. **Trenowanie** - Uczenie modeli AI
4. **Transfer** - Przenoszenie z symulacji do rzeczywistości
5. **Projekt** - Realizacja kompletnego pipeline'u

Każdy kolejny przykład buduje na poprzednich, tworząc solidną podstawę do pracy badawczej lub przemysłowej w robotyce AI.

**Powodzenia w Waszych projektach! 🤖🎓**
