# Materiały Edukacyjne LeRobot - Indeks i Przewodnik dla Wykładowców

## Przegląd

Niniejszy dokument stanowi centralny punkt wyjścia dla wszystkich materiałów edukacyjnych przygotowanych dla studentów uczących się pracy z robotem humanoidalnym Unitree G1 EDU przy użyciu platformy LeRobot.

Wszystkie materiały zostały przetłumaczone na język polski z zachowaniem oryginalnych nazw klas, funkcji i terminów technicznych, zgodnie z najlepszymi praktykami dokumentacji technicznej.

---

## Struktura Materiałów Edukacyjnych

### 1. Dokumenty Wprowadzające

#### 1.1 README_PL.md
**Lokalizacja:** `/README_PL.md`

**Przeznaczenie:** Główny dokument wprowadzający do projektu LeRobot

**Zawartość:**
- Ogólny opis platformy LeRobot i jej możliwości
- Podstawowe koncepcje (obserwacje, akcje, polityki, epizody, datasety)
- Szybki start i instalacja
- Przegląd wspieranych robotów i modeli
- Specjalne informacje dla pracy z Unitree G1 EDU
- Linki do dalszych zasobów

**Dla kogo:**
- Studenci rozpoczynający pracę z LeRobot
- Osoby szukające szybkiego przeglądu możliwości platformy
- Wykładowcy przygotowujący materiały do zajęć wprowadzających

**Czas czytania:** ~15-20 minut

**Poziom trudności:** Początkujący

---

### 2. Dokumentacja Techniczna

#### 2.1 docs/source/unitree_g1_pl.mdx
**Lokalizacja:** `/docs/source/unitree_g1_pl.mdx`

**Przeznaczenie:** Kompletna dokumentacja techniczna dla robota Unitree G1

**Zawartość:**
- **Część 1:** Przewodnik po połączeniu z robotem (Ethernet, WiFi, SSH)
- **Część 2:** Aktywacja WiFi i konfiguracja sieci
- **Część 3:** Instalacja i uruchomienie serwera robota
- **Część 4:** Zdalne sterowanie i kontrola
- **Część 5:** Praca w trybie symulacji (MuJoCo)
- **Część 6:** Teleopereacja i nagrywanie na prawdziwym robocie
- **Przepływ pracy:** Od zbierania danych do wdrożenia
- **Rozwiązywanie problemów:** Typowe błędy i ich naprawy

**Dla kogo:**
- Studenci wykonujący praktyczne laboratorium z robotem
- Osoby konfigurujące infrastrukturę robotyczną
- Asystenci wspierający zajęcia praktyczne

**Czas czytania:** ~45-60 minut

**Poziom trudności:** Średniozaawansowany

**Wymagania:**
- Podstawowa znajomość Linux
- Umiejętność pracy z terminalem
- Zrozumienie sieci komputerowych (IP, porty, routing)

---

### 3. Przewodniki Edukacyjne

#### 3.1 docs/source/unitree_g1_student_guide_pl.md
**Lokalizacja:** `/docs/source/unitree_g1_student_guide_pl.md`

**Przeznaczenie:** Kompleksowy przewodnik studenta przez wszystkie aspekty projektu

**Struktura (9 modułów):**

**Moduł 1: Podstawy Teoretyczne**
- Anatomia robota humanoidalnego (DOF, komponenty)
- Przestrzeń stanów i akcji
- Paradygmaty uczenia (Imitation Learning, Reinforcement Learning)

**Moduł 2: Architektura Systemu**
- Architektura komunikacji (DDS, ZMQ)
- Protokoły i wzorce
- Przepływ danych

**Moduł 3: Praktyczna Praca z Kodem**
- Struktura projektu
- Główne klasy i ich odpowiedzialności
- Szczegółowa analiza kontrolera GR00T

**Moduł 4: Zbieranie i Zarządzanie Danymi**
- Format LeRobotDataset
- Proces zbierania danych
- Wizualizacja i walidacja

**Moduł 5: Trenowanie Modeli**
- Wybór architektury (ACT, Diffusion)
- Hyperparametry i ich znaczenie
- Monitorowanie i debugging

**Moduł 6: Wdrożenie i Testowanie**
- Problem sim-to-real gap
- Bezpieczne testowanie
- Debugging typowych problemów

**Moduł 7: Projekt Zaliczeniowy**
- Propozycje projektów (3 poziomy trudności)
- Szablon raportu
- Kryteria oceny

**Moduł 8: Najlepsze Praktyki**
- Zarządzanie projektem (Git, dokumentacja)
- Optymalizacja wydajności
- Troubleshooting checklist

**Moduł 9: Zasoby i Dalsza Nauka**
- Kursy online
- Książki i papers
- Społeczność i kariera

**Dla kogo:**
- Studenci realizujący projekt semestralny
- Osoby samodzielnie uczące się robotyki AI
- Grupy projektowe szukające kompleksowego źródła wiedzy

**Czas nauki:** 20-30 godzin (z praktyką)

**Poziom trudności:** Od podstawowego do zaawansowanego

**Wymagania:**
- Podstawy Pythona
- Podstawy uczenia maszynowego
- Matematyka (algebra liniowa, rachunek różniczkowy)

---

#### 3.2 docs/source/unitree_g1_practical_examples_pl.md
**Lokalizacja:** `/docs/source/unitree_g1_practical_examples_pl.md`

**Przeznaczenie:** Zbiór praktycznych przykładów projektów z robot

**Zawartość (5 przykładów):**

**Przykład 1: Podstawowa Lokomotoryka** (Poziom: Łatwy)
- Uruchomienie kontrolera GR00T
- Eksperymenty z parametrami
- Analiza zachowania robota
- **Czas realizacji:** 2-3 godziny

**Przykład 2: Zbieranie Datasetu** (Poziom: Średni)
- Definicja zadania "Podnieś i przestaw kubek"
- Kalibracja teleoperatora
- Nagrywanie demonstracji
- Inspekcja i czyszczenie danych
- **Czas realizacji:** 4-6 godzin

**Przykład 3: Trenowanie Modelu ACT** (Poziom: Średni-Zaawansowany)
- Konfiguracja środowiska GPU
- Trenowanie z monitoringiem
- Analiza metryk i wykresów
- Ewaluacja wydajności
- **Czas realizacji:** 8-12 godzin (+ czas GPU)

**Przykład 4: Transfer Learning** (Poziom: Zaawansowany)
- Domain randomization w symulacji
- Fine-tuning na prawdziwych danych
- Analiza sim-to-real gap
- Techniki poprawy transferu
- **Czas realizacji:** 12-16 godzin

**Przykład 5: Projekt Zaliczeniowy** (Poziom: Kompleksowy)
- Propozycje zadań (3 opcje)
- Harmonogram 8-tygodniowy
- Kryteria oceny
- Szablony i narzędzia
- **Czas realizacji:** 8 tygodni (projekt semestralny)

**Dla kogo:**
- Studenci wykonujący ćwiczenia laboratoryjne
- Grupy projektowe
- Osoby przygotowujące się do zawodów robotycznych

**Poziom trudności:** Zróżnicowany (od podstawowego do zaawansowanego)

---

### 4. Kod Źródłowy z Komentarzami

#### 4.1 examples/unitree_g1/gr00t_locomotion_pl.py
**Lokalizacja:** `/examples/unitree_g1/gr00t_locomotion_pl.py`

**Przeznaczenie:** Fully commented przykład kontrolera lokomotorycznego

**Charakterystyka:**
- **Linie kodu:** ~900 (z czego ~600 to komentarze/dokumentacja)
- **Język:** Python z obszernymi komentarzami po polsku
- **Styl:** Edukacyjny - każda sekcja szczegółowo wyjaśniona

**Zawartość komentarzy:**
- Cel i przeznaczenie każdej funkcji/klasy
- Wyjaśnienie algorytmów krok po kroku
- Znaczenie parametrów i stałych
- Przykłady użycia i edge cases
- Analogie i porównania ułatwiające zrozumienie

**Kluczowe sekcje:**
1. Ładowanie modeli ONNX (co to jest ONNX, dlaczego używamy)
2. Przygotowanie obserwacji (normalizacja, dlaczego jest ważna)
3. Historia obserwacji (dlaczego 6 klatek, znaczenie pamięci)
4. Inferencja modelu (co się dzieje w środku)
5. Konwersja akcji (delta vs. absolute, safety scaling)

**Dla kogo:**
- Studenci uczący się implementacji kontrolerów
- Osoby chcące zrozumieć działanie GR00T od środka
- Programiści implementujący własne kontrolery

**Czas studiowania:** 3-4 godziny (ze zrozumieniem)

**Poziom trudności:** Średniozaawansowany

---

#### 4.2 src/lerobot/robots/unitree_g1/run_g1_server_pl.py
**Lokalizacja:** `/src/lerobot/robots/unitree_g1/run_g1_server_pl.py`

**Przeznaczenie:** Fully commented implementacja serwera mostka DDS-ZMQ

**Charakterystyka:**
- **Linie kodu:** ~750 (z czego ~500 to komentarze/dokumentacja)
- **Język:** Python z obszernymi komentarzami po polsku
- **Styl:** Edukacyjny z naciskiem na architekturę systemową

**Zawartość komentarzy:**
- Architektura komunikacji (DDS vs ZMQ, dlaczego oba)
- Protokoły i wzorce (PUB/SUB, PUSH/PULL)
- Threading i synchronizacja
- Serializacja i bezpieczeństwo (JSON vs pickle)
- Graceful shutdown i czyszczenie zasobów

**Kluczowe sekcje:**
1. Konwersja formatów (LowState ↔ dict, LowCmd ↔ dict)
2. State forward loop (DDS → ZMQ, threading)
3. Command forward loop (ZMQ → DDS, blocking recv)
4. Inicjalizacja i shutdown (porządek operacji)
5. Error handling i troubleshooting

**Dla kogo:**
- Studenci uczący się systemów rozproszonych
- Osoby implementujące własne mosty komunikacyjne
- Programiści integrujący LeRobot z innymi robotami

**Czas studiowania:** 3-4 godziny

**Poziom trudności:** Średniozaawansowany-Zaawansowany

**Wymagania:**
- Znajomość wielowątkowości
- Podstawy sieci (sockety, protokoły)
- Pojęcie serializacji danych

---

## Ścieżki Nauki dla Różnych Grup

### Ścieżka A: "Quick Start" (Weekend)
**Dla:** Osób chcących szybko zobaczyć działającego robota

**Kolejność:**
1. README_PL.md (przegląd) - 15 min
2. unitree_g1_pl.mdx (Część 1-4: połączenie i sterowanie) - 30 min
3. unitree_g1_practical_examples_pl.md (Przykład 1) - 2h
4. gr00t_locomotion_pl.py (przejrzenie kodu) - 30 min

**Rezultat:** Działający robot sterowany kontrolerem

---

### Ścieżka B: "Zbieranie Danych" (Tydzień)
**Dla:** Grup tworzących dataset do projektu

**Kolejność:**
1. README_PL.md (pełny) - 20 min
2. unitree_g1_student_guide_pl.md (Moduły 1-4) - 4h
3. unitree_g1_practical_examples_pl.md (Przykład 2) - 6h
4. unitree_g1_pl.mdx (Część 5-6: teleopereacja) - 1h
5. Praktyczne nagrywanie - 8h

**Rezultat:** High-quality dataset opublikowany na HF Hub

---

### Ścieżka C: "Pełny Pipeline ML" (Miesiąc)
**Dla:** Studentów realizujących projekt badawczy

**Kolejność:**
1. README_PL.md - 20 min
2. unitree_g1_student_guide_pl.md (Moduły 1-6) - 12h
3. unitree_g1_practical_examples_pl.md (Przykłady 1-4) - 30h
4. Studium kodu źródłowego (oba pliki _pl.py) - 8h
5. unitree_g1_pl.mdx (reference dokumentacja) - 2h
6. Własny projekt - 40h

**Rezultat:** Kompletny projekt z wytrenowanym modelem, dokumentacją i wdrożeniem

---

### Ścieżka D: "Expert - Rozwój Platformy" (Semester)
**Dla:** Zaawansowanych studentów/doktorantów rozwijających LeRobot

**Kolejność:**
1. Wszystkie materiały podstawowe - 20h
2. Głębokie studium kodu źródłowego - 40h
3. Studium oryginalnych papers (ACT, Diffusion, GR00T) - 30h
4. Implementacja własnej architektury - 80h
5. Eksperymenty i benchmarking - 60h
6. Publikacja wyników - 30h

**Rezultat:** Nowy wkład do LeRobot, możliwość publikacji naukowej

---

## Sugerowane Syllaby Kursów

### Kurs 1: "Wprowadzenie do Robotyki AI" (15 tygodni, 2h wykład + 2h lab)

**Tydzień 1-2: Podstawy**
- Wykład: Wprowadzenie do robotyki, LeRobot overview
- Lab: Instalacja, konfiguracja, pierwsze uruchomienie
- Materiały: README_PL.md, unitree_g1_pl.mdx (Część 1-3)

**Tydzień 3-4: Architektura Systemów**
- Wykład: DDS, ZMQ, protokoły komunikacji
- Lab: Analiza run_g1_server_pl.py, modyfikacje parametrów
- Materiały: unitree_g1_student_guide_pl.md (Moduł 2), run_g1_server_pl.py

**Tydzień 5-6: Sterowanie Robotem**
- Wykład: Polityki, inferencja, control loops
- Lab: Analiza gr00t_locomotion_pl.py, eksperymenty
- Materiały: unitree_g1_student_guide_pl.md (Moduł 3), gr00t_locomotion_pl.py

**Tydzień 7-9: Zbieranie Danych**
- Wykład: Formaty danych, teleopereacja, jakość demonstracji
- Lab: Nagrywanie własnego datasetu
- Materiały: unitree_g1_practical_examples_pl.md (Przykład 2)

**Tydzień 10-12: Uczenie Maszynowe**
- Wykład: ACT, Diffusion, training loops
- Lab: Trenowanie modelu na własnym datasecie
- Materiały: unitree_g1_practical_examples_pl.md (Przykład 3)

**Tydzień 13-14: Sim-to-Real**
- Wykład: Transfer learning, domain adaptation
- Lab: Fine-tuning na prawdziwym robocie
- Materiały: unitree_g1_practical_examples_pl.md (Przykład 4)

**Tydzień 15: Prezentacje Projektów**

---

### Kurs 2: "Zaawansowana Robotyka - Projekt" (Semester, 6 ECTS)

**Miesiąc 1: Planowanie**
- Definicja zadania
- Przegląd literatury
- Proof of concept w symulacji

**Miesiąc 2: Implementacja**
- Konfiguracja sprzętu
- Zbieranie danych
- Pierwsze treningi

**Miesiąc 3: Optymalizacja**
- Hyperparameter tuning
- Ablation studies
- Benchmarking

**Miesiąc 4: Wdrożenie i Dokumentacja**
- Transfer na prawdziwego robota
- Testy i ewaluacja
- Pisanie raportu

**Materiały:** Wszystkie + dodatkowo samodzielne studium literatury

---

## Wskazówki dla Wykładowców

### Przygotowanie Zajęć

**Przed Semestrem:**
1. Przeczytaj wszystkie materiały edukacyjne (szacowany czas: 15-20h)
2. Przetestuj wszystkie przykłady na własnym setupie
3. Przygotuj dodatkowe datasety do demonstracji
4. Skonfiguruj środowisko laboratoryjne (roboty, komputery, sieć)
5. Przygotuj awaryjne procedury (co jeśli robot przestanie działać?)

**Pierwsze Zajęcia:**
- Przedstaw całość materiałów i ich strukturę
- Pokaż "end-to-end demo" - działający robot z wytrenowanym modelem
- Wyjaśnij ścieżki nauki i wymagania projektu
- Rozdaj checkliste bezpieczeństwa

**Podczas Semestru:**
- Regularnie sprawdzaj postępy grup (milestone'y)
- Organizuj "office hours" dla problemów technicznych
- Zbieraj feedback o trudnościach w materiałach
- Dziel się ciekawymi znaleziskami grup między sobą

### Typowe Problemy i Rozwiązania

**Problem:** Studenci gubią się w ilości materiałów
**Rozwiązanie:** Wskaż konkretną ścieżkę nauki (A/B/C/D)

**Problem:** Robot nie działa podczas zajęć
**Rozwiązanie:** Zawsze miej przygotowaną symulację jako backup

**Problem:** Treningi trwają za długo
**Rozwiązanie:** Pre-trenuj modele bazowe, studenci tylko fine-tuning

**Problem:** Brak GPU do treningów
**Rozwiązanie:** 
- Użyj Google Colab (darmowe GPU)
- Trenuj modele mniejsze (zmniejsz dim_model)
- Kolejkuj dostęp do GPU laboratoryjnego

**Problem:** Niski success rate na prawdziwym robocie
**Rozwiązanie:**
- To normalne! Omów problem sim-to-real
- Użyj jako okazję do dyskusji o wyzwaniach
- Pokaż techniki poprawy (domain randomization, fine-tuning)

### Ocenianie Projektów

**Rubric Project Grading:**

| Kategoria | 0-50% | 51-70% | 71-85% | 86-100% |
|-----------|-------|--------|--------|---------|
| **Dataset** | Niekompletny | 30+ demos | 50+ demos | 75+ demos, wysoka jakość |
| **Model** | Nie trenuje | Trainuje, ale słabo | Success >50% sim | Success >70% real |
| **Kod** | Niedziałający | Działa, chaotyczny | Czysty, udokumentowany | Profesjonalny, reusable |
| **Dokumentacja** | Brak/bardzo krótka | Podstawowa | Kompletna | Poziom publikacji |
| **Prezentacja** | Niewyraźna | Zrozumiała | Dobra | Excellent, inspirująca |

**Bonus Points:**
- +10%: Publikacja na HF Hub z przykładami użycia
- +10%: Wkład do LeRobot (PR zaakceptowany)
- +5%: Oryginalny pomysł na zadanie
- +5%: Szczególnie staranna wizualizacja

### Etyka i Bezpieczeństwo

**Zasady Pracy z Robotem:**
1. Nigdy nie zostawiaj robota bez nadzoru podczas ruchu
2. Zawsze miej "emergency stop" w zasięgu ręki
3. Rozpocznij od symulacji, stopniowo przechodź do prawdziwego robota
4. Testuj nowy kod najpierw w "safe mode" (niskie prędkości)
5. Dokumentuj wszystkie incydenty

**Etyka AI:**
- Dyskutuj o biasie w dataseetach
- Omów konsekwencje automatyzacji
- Zachęcaj do open-source i dzielenia się wiedzą

---

## Dodatkowe Zasoby

### Dla Studentów

**Online Communities:**
- Discord LeRobot: https://discord.gg/q8Dzzpym3f
- Reddit r/robotics: https://reddit.com/r/robotics
- ROS Discourse: https://discourse.ros.org

**Video Tutorials:**
- LeRobot YouTube Channel
- Robot Learning @ Berkeley
- NVIDIA GR00T Demos

**Papers Must-Read:**
1. "Action Chunking with Transformers" (ACT)
2. "Diffusion Policy: Visuomotor Policy Learning via Action Diffusion"
3. "GR00T: Foundation Model for Humanoid Robots"
4. "Learning Dexterous Manipulation from Human Demonstrations"

### Dla Wykładowców

**Teaching Resources:**
- Stanford CS336: Robot Learning Course Materials
- MIT 6.4210: Robotic Manipulation
- Berkeley CS287: Advanced Robotics

**Research Groups:**
- Berkeley Robot Learning Lab
- Stanford Vision and Learning Lab
- MIT CSAIL Robotics
- NVIDIA Research (GR00T team)

**Funding Opportunities:**
- NSF Robotics Education Grants
- EU Horizon Robotics Projects
- Industry Partnerships (Unitree, Hugging Face)

---

## Aktualizacje i Rozwój Materiałów

### Feedback Loop

**Zbieramy feedback od:**
1. Studentów (ankiety po każdym module)
2. Wykładowców (spotkania co semestr)
3. Społeczności LeRobot (GitHub issues)

**Priorytet aktualizacji:**
- Krytyczne błędy → Natychmiast
- Niejasności w wyjaśnieniach → W ciągu tygodnia
- Nowe features LeRobot → W ciągu miesiąca
- Dodatkowe przykłady → Gdy dostępne

### Planowane Rozszerzenia

**Krótkoterminowe (3-6 miesięcy):**
- Video tutoriale do każdego przykładu
- Interaktywne Jupyter notebooks
- Więcej przykładów zadań (manipulacja, navigation)

**Średnioterminowe (6-12 miesięcy):**
- Tłumaczenia na inne języki (angielski, niemiecki, francuski)
- Materiały dla robotów SO-100, Koch
- Advanced topics (RLHF, Model-based RL)

**Długoterminowe (1-2 lata):**
- Pełny kurs MOOC
- Certyfikacja "LeRobot Practitioner"
- Książka "Robotyka AI z LeRobot"

---

## Kontakt i Wsparcie

**Dla pytań technicznych:**
- GitHub Issues: https://github.com/huggingface/lerobot/issues
- Discord: LeRobot channel

**Dla pytań edukacyjnych:**
- Email: lerobot-edu@huggingface.co
- Forum: https://discuss.huggingface.co/c/lerobot

**Dla współpracy:**
- Partnerships: partnerships@huggingface.co

---

## Podsumowanie

Te materiały edukacyjne stanowią kompletny ekosystem do nauki robotyki AI z użyciem platformy LeRobot i robota Unitree G1 EDU. Zostały zaprojektowane z myślą o:

✅ **Progresywnym uczeniu** - od podstaw do zaawansowanych tematów
✅ **Praktycznym podejściu** - każda koncepcja z kodem i przykładami
✅ **Accessibility** - jasne wyjaśnienia w języku polskim
✅ **Skalowalności** - materiały dla 1 studenta lub całego kursu
✅ **Open-source** - wolne do użycia, modyfikacji, dzielenia się

**Życzymy owocnej nauki i ekscytujących projektów robotycznych!** 🤖🎓

---

_Materiały przygotowane dla studentów i wykładowców_
_Ostatnia aktualizacja: Luty 2025_
_Wersja: 1.0_
