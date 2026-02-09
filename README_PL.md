# LeRobot - Biblioteka Robotyki Hugging Face

<p align="center">
  <img alt="LeRobot, Hugging Face Robotics Library" src="./media/readme/lerobot-logo-thumbnail.png" width="100%">
</p>

## O Projekcie

**LeRobot** to kompleksowa biblioteka oferująca modele, zbiory danych i narzędzia do pracy z rzeczywistymi robotami w środowisku PyTorch. Głównym celem jest obniżenie bariery wejścia, aby każdy mógł wnosić wkład i korzystać ze wspólnych zbiorów danych oraz wytrenowanych modeli.

### Kluczowe Cechy

🤗 **Uniwersalny interfejs Python** niezależny od sprzętu, który standaryzuje sterowanie na różnych platformach - od niedrogich ramion robotycznych (SO-100) po humanoidalne roboty (Unitree G1 EDU).

🤗 **Standardowy, skalowalny format LeRobotDataset** (Parquet + MP4 lub obrazy) hostowany na Hugging Face Hub, umożliwiający efektywne przechowywanie, strumieniowanie i wizualizację masywnych zbiorów danych robotycznych.

🤗 **Najnowocześniejsze polityki (policies)** - algorytmy sterowania, które zostały przebadane i sprawdzone w rzeczywistych zastosowaniach, gotowe do trenowania i wdrożenia.

🤗 **Kompleksowe wsparcie dla ekosystemu open-source** w celu demokratyzacji sztucznej inteligencji fizycznej.

## Czym Jest LeRobot?

LeRobot to platforma edukacyjna i badawcza, która:

1. **Umożliwia naukę robotów** - Dzięki uczeniu maszynowemu roboty mogą uczyć się wykonywania zadań przez obserwację i imitację
2. **Standaryzuje dane robotyczne** - Jednolity format danych ułatwia dzielenie się doświadczeniami między różnymi robotami
3. **Dostarcza gotowe rozwiązania** - Zawiera sprawdzone algorytmy sterowania (policies) używane w badaniach naukowych
4. **Wspiera integrację sprzętową** - Współpracuje z wieloma rodzajami robotów, w tym z humanoidalnym robotem Unitree G1 EDU

## Zastosowanie w Projekcie z Robotem Unitree G1 EDU

Robot humanoidalny **Unitree G1 EDU** to zaawansowana platforma edukacyjna, która dzięki integracji z LeRobot umożliwia:

- **Zbieranie danych demonstracyjnych** - Nauczanie robota poprzez teleopereację (zdalne sterowanie)
- **Trenowanie modeli AI** - Wykorzystanie zebranych danych do nauczenia modeli uczenia maszynowego
- **Kontrolę lokomotywną** - Uruchamianie zaawansowanych algorytmów chodzenia (GR00T, Holosoma)
- **Symulację i walidację** - Testowanie algorytmów w symulatorze MuJoCo przed wdrożeniem na prawdziwym robocie

## Szybki Start

LeRobot można zainstalować bezpośrednio z PyPI:

```bash
pip install lerobot
lerobot-info
```

> [!IMPORTANT]
> Szczegółowy przewodnik instalacji znajduje się w [Dokumentacji Instalacji](https://huggingface.co/docs/lerobot/installation).

## Roboty i Sterowanie

LeRobot zapewnia zunifikowany interfejs klasy `Robot`, który oddziela logikę sterowania od specyfiki sprzętowej. Wspiera szeroki zakres robotów i urządzeń teleoperacyjnych.

```python
from lerobot.robots.myrobot import MyRobot

# Połącz się z robotem
robot = MyRobot(config=...)
robot.connect()

# Odczytaj obserwację i wyślij akcję
obs = robot.get_observation()
action = model.select_action(obs)
robot.send_action(action)
```

**Wspierane urządzenia:** SO100, LeKiwi, Koch, HopeJR, OMX, EarthRover, Reachy2, Gamepady, Klawiatury, Telefony, OpenARM, **Unitree G1**.

## Format Danych LeRobotDataset

Aby rozwiązać problem fragmentacji danych w robotyce, wykorzystujemy format **LeRobotDataset**:

- **Struktura:** Zsynchronizowane filmy MP4 (lub obrazy) dla wizji oraz pliki Parquet dla danych stanu/akcji
- **Integracja z HF Hub:** Tysiące zbiorów danych robotycznych na [Hugging Face Hub](https://huggingface.co/lerobot)
- **Narzędzia:** Możliwość usuwania epizodów, dzielenia według indeksów/frakcji, dodawania/usuwania cech i łączenia wielu zbiorów danych

```python
from lerobot.datasets.lerobot_dataset import LeRobotDataset

# Załaduj zbiór danych z Hub
dataset = LeRobotDataset("lerobot/aloha_mobile_cabinet")

# Dostęp do danych (automatyczna dekompresja wideo)
episode_index = 0
print(f"{dataset[episode_index]['action'].shape=}\n")
```

## Modele Uczenia Maszynowego

LeRobot implementuje najnowocześniejsze polityki w czystym PyTorch, obejmując:
- **Uczenie przez Imitację (Imitation Learning):** ACT, Diffusion, VQ-BeT
- **Uczenie przez Wzmacnianie (Reinforcement Learning):** HIL-SERL, TDMPC
- **Modele VLA (Vision-Language-Action):** Pi0Fast, Pi0.5, GR00T N1.5, SmolVLA, XVLA

Trenowanie polityki jest tak proste jak uruchomienie skryptu konfiguracyjnego:

```bash
lerobot-train \
  --policy=act \
  --dataset.repo_id=lerobot/aloha_mobile_cabinet
```

## Podstawowe Koncepcje dla Studentów

### 1. Obserwacja (Observation)
Dane sensoryczne z robota (pozycje stawów, obrazy z kamer, dane IMU). Robot "widzi" i "czuje" swoje otoczenie.

### 2. Akcja (Action)
Polecenia wysyłane do robota (docelowe pozycje stawów, prędkości). To "decyzje" podejmowane przez algorytm sterowania.

### 3. Polityka (Policy)
Model uczenia maszynowego, który mapuje obserwacje na akcje. To "mózg" robota, który decyduje co zrobić w danej sytuacji.

### 4. Epizod (Episode)
Pojedyncza sekwencja obserwacji i akcji od początku do końca zadania. Przykład: robot podnosi kubek i stawia go na stole.

### 5. Dataset (Zbiór Danych)
Kolekcja epizodów używanych do trenowania modelu. Im więcej dobrych przykładów, tym lepiej robot się uczy.

## Zasoby

- **[Dokumentacja](https://huggingface.co/docs/lerobot/index):** Kompletny przewodnik po tutorialach i API
- **[Przewodnik po Unitree G1](./docs/source/unitree_g1_pl.mdx):** Szczegółowa dokumentacja dla robota humanoidalnego
- **[Discord](https://discord.gg/q8Dzzpym3f):** Dołącz do serwera LeRobot, aby dyskutować ze społecznością
- **[X](https://x.com/LeRobotHF):** Śledź nas na X, aby być na bieżąco z najnowszymi rozwojem

## Dla Studentów Pracujących z Unitree G1 EDU

Jeśli pracujesz nad projektem z robotem humanoidalnym Unitree G1 EDU, sprawdź te zasoby:

1. **[Przewodnik po Unitree G1 (Polski)](./docs/source/unitree_g1_pl.mdx)** - Kompletna instrukcja konfiguracji i użytkowania
2. **[Przykłady kodu z komentarzami](./examples/unitree_g1/)** - Praktyczne przykłady z dokładnymi wyjaśnieniami
3. **[Przewodnik studenta](./docs/source/unitree_g1_student_guide_pl.md)** - Krok po kroku wprowadzenie do pracy z robotem

## Wkład w Projekt

Zapraszamy wszystkich do współtworzenia! Przeczytaj nasz przewodnik [CONTRIBUTING.md](./CONTRIBUTING.md). Niezależnie od tego, czy dodajesz nową funkcję, poprawiasz dokumentację, czy naprawiasz błąd - Twoja pomoc jest nieoceniona!

<div align="center">
<sub>Zbudowane przez zespół <a href="https://huggingface.co/lerobot">LeRobot</a> w <a href="https://huggingface.co">Hugging Face</a> z ❤️</sub>
</div>
