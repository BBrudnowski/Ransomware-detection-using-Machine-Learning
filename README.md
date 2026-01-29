# Wykrywanie ataków typu Ransomware poprzez analizę entropii danych plikowych przy pomocy uczenia maszynowego

Autorzy: [Przemysław Bryzek](https://github.com/przemyslawbryzek), [Błażej Brudnowski](https://github.com/BBrudnowski)

## 1. Wstęp

Ransomware stanowi jedno z najpoważniejszych zagrożeń cyberbezpieczeństwa współczesnych systemów informatycznych. Ataki tego typu mogą sparaliżować działanie całych organizacji, powodując nieodwracalne straty danych oraz ogromne koszty finansowe. Tradycyjne metody detekcji oparte na sygnaturach wirusów często okazują się niewystarczające wobec dynamicznie ewoluujących wariantów złośliwego oprogramowania.

Niniejszy projekt przedstawia innowacyjne podejście do wykrywania ransomware oparte na analizie entropii Shannona plików binarnych. Entropia, jako miara losowości i nieporządku danych, stanowi skuteczny wskaźnik pozwalający odróżnić pliki zaszyfrowane przez ransomware od plików benignware. Pliki poddane szyfrowaniu wykazują charakterystycznie wysoką entropię, zbliżoną do rozkładu równomiernego, co stanowi kluczową cechę wykorzystywaną w procesie klasyfikacji.

Projekt implementuje aplikację webową umożliwiającą automatyczną analizę plików pod kątem potencjalnego zainfekowania ransomware. System wykorzystuje model uczenia maszynowego wytrenowany na zbiorze danych NapierOne, zawierającym tysiące próbek plików benignware oraz ich zaszyfrowanych odpowiedników.

### 1.1 Cele projektu

- Implementacja algorytmu obliczania entropii Shannona dla plików binarnych
- Budowa modelu klasyfikacyjnego opartego na cechach entropijnych
- Stworzenie interfejsu webowego umożliwiającego łatwą analizę plików
- Walidacja skuteczności podejścia na rzeczywistych próbkach ransomware

## 1.2 Stos technologiczny

### Backend i Machine Learning
- **Python 3.x** - główny język programowania
- **Scikit-learn** - biblioteka do uczenia maszynowego (modele klasyfikacyjne)
- **Pandas** - przetwarzanie i analiza danych
- **NumPy** - operacje na tablicach i obliczenia numeryczne

### Frontend
- **Flask** - framework webowy do budowy aplikacji
- **HTML/CSS** - interfejs użytkownika
- **Bootstrap** - responsywny design

### Narzędzia pomocnicze
- **Matplotlib/Seaborn** - wizualizacja danych i wyników
- **Jupyter Notebook** - eksploracja danych i prototypowanie

## 2. Teoria Entropii Shannona

### 2.1 Definicja Matematyczna

Entropia Shannona dla dyskretnego rozkładu prawdopodobieństwa definiowana jest wzorem:

$$H(X) = -\sum_{i=1}^{n} p(x_i) \log_2 p(x_i)$$

gdzie:
- $H(X)$ - entropia rozkładu,
- $p(x_i)$ - prawdopodobieństwo wystąpienia symbolu $x_i$,
- $n$ - liczba unikalnych symboli,
- $\log_2$ - logarytm o podstawie 2 (wynik wyrażony w bitach).

### 2.2 Interpretacja Fizyczna i Informacyjna

Entropia mierzy średnią ilość informacji zawartej w losowej zmiennej. Im wyższa wartość entropii, tym większy stopień niepewności i losowości rozkładu. Dla pliku binarnego:

- **Niska entropia** ($H \approx 0$ bitów): Plik zawiera powtarzające się bajty, wysoki stopień compresji, struktura regularna
- **Wysoka entropia** ($H \approx 8$ bitów): Rozkład bajtów zbliżony do rozkładu równomiernego, wysoki stopień losowości
- **Maksymalna entropia** ($H = 8$ bitów): Każdy z 256 możliwych bajtów pojawia się z równym prawdopodobieństwem

### 2.3 Znaczenie w Kontekście Bezpieczeństwa

Entropię można zastosować do detekcji zagrożeń na podstawie obserwacji:

1. **Pliki originalne**: Zwykle posiadają umiarkowaną entropię ze względu na strukturę formatów (nagłówki, dane metadanych, skompresowane zasoby)
2. **Pliki zaszyfrowane/spakowane**: Wykazują znacznie wyższą entropię ze względu na właściwości kryptograficzne i algorytmów kompresji
3. **Malware/Ransomware**: Często wykorzystuje szyfrowanie, co skutkuje podwyższoną entropią pliku docelowego

## 3. Metodyka Obliczeniowa

### 3.1 Algorytm Obliczania Entropii

Proces obliczania entropii dla pliku binarnego:

1. Odczytanie zawartości pliku jako ciągu bajtów
2. Policzenie częstości występowania każdego z 256 możliwych wartości bajtów
3. Obliczenie prawdopodobieństwa dla każdej wartości: p_i = count_i / total_bytes
4. Zastosowanie wzoru Shannona z logarytmem binarnym

### 3.2 Entropia Blokowa

Oprócz entropii globalnej (całego pliku), proponuje się analizę entropii blokowej - podziału pliku na fragmenty o stałym rozmiarze i obliczeniu entropii dla każdego bloku.

Niech $B_j$ oznacza $j$-ty blok o rozmiarze $s$:

$$H_j = -\sum_{i=0}^{255} p_{i,j} \log_2 p_{i,j}$$

gdzie $p_{i,j}$ jest prawdopodobieństwem bajtu $i$ w bloku $j$.

### 3.3 Wariancja Entropii Blokowej

Istotnym wskaźnikiem jest wariancja entropii blokowej, definiowana jako:

$$\sigma^2_{H} = \frac{1}{m}\sum_{j=1}^{m} (H_j - \bar{H})^2$$

gdzie:
- $m$ - liczba bloków,
- $\bar{H}$ - średnia entropia blokowa,
- $H_j$ - entropia bloku $j$.

Wariancja ta dostarcza informacji o spójności rozkładu entropii w całym pliku. Niska wariancja wskazuje na regularny rozkład, wysoka na zmienność.

## 4. Konstrukcja Datasetu

### 4.1 Źródło Danych

Dataset składa się z próbek pochodzących z repozytorium NapierOne, zawierającego:
- Pliki benignware (klasa 0): Pliki nie szyfrowane przez ransomware
- Pliki malware/ransomware (klasa 1): Te same pliki zaszyfrowane przez różne próbki ransomware

Link do repozytorium: http://napierone.com/

### 4.2 Ekstrakcja Cech

Dla każdego pliku w datasecie ekstrahuje się następujące cechy:

| Cecha | Opis | Jednostka |
|-------|------|-----------|
| **Entropia globalna** | Entropia całego pliku | bity (0-8) |
| **Wariancja entropii** | Wariancja entropii blokowej | bity² |
| **Rozmiar pliku** | Wielkość pliku binarnego | bajty |
| **Typ pliku** | Kategoria/typ pliku | indeks (0-n) |
| **Etykieta klasy** | Klasa pliku (benign/malware) | binarny (0/1) |

### 4.3 Metodyka Przetwarzania

Proces tworzenia datasetu obejmuje:

1. **Skanowanie**: Przejście przez strukturę katalogów zawierających pliki
2. **Filtracja**: Selekcja plików zgodnie z kryteriami (np. format nazwy)
3. **Obliczenia**: Dla każdego pliku:
   - Obliczenie entropii globalnej
   - Obliczenie entropii bloków o rozmiarze 2048 bajtów
   - Obliczenie wariancji entropii blokowej
   - Pobieranie metadanych (rozmiar, typ)
4. **Agregacja**: Zestawienie wyników w strukturę tabelaryczną
5. **Serializacja**: Zapis datasetu do pliku CSV

### 4.4 Rozmiar Bloku

Rozmiar bloku 2048 bajtów (2 KB) został wybrany jako kompromis:
- Wystarczająco duży, aby zawierać istotne statystki
- Wystarczająco mały, aby uchwycić lokalne fluktuacje entropii
- Zgodny z typowymi rozmiarami sektorów dyskowych

### 4.5 Format Wyjściowy

Wygenerowany dataset zapisywany jest w formacie CSV z następującymi kolumnami:

```
id,type,size,entropy,variance,label
0,0,5120,6.234,0.412,0
1,1,8192,7.892,0.156,1
...
```

Gdzie:
- `id`: Unikatowy identyfikator próbki
- `type`: Kategoria pliku (zakodowana numerycznie)
- `size`: Rozmiar pliku w bajtach
- `entropy`: Globalna entropia Shannona
- `variance`: Wariancja entropii blokowej
- `label`: Klasa: 0 (benignware) lub 1 (malware/ransomware)

### 4.6 Mapowanie Typów

Równolegle z dataselem generuje się plik `types.json` zawierający mapowanie między indeksami numerycznymi a rzeczywistymi typami plików:

```json
{
  "exe": 0,
  "dll": 1,
  "doc": 2,
  ...
}
```

## 5. Entropy Sharing - Nowa Technika Ewaluacji
Najnowsze badania z 2024 roku ujawniły metodę o nazwie "Entropy Sharing", którą może stosować zaawansowany ransomware. Technika ta dzieli zaszyfrowane dane na części, rekombinuje je w sposób obniżający średnią entropię. Ma ona niski koszt obliczeniowy oraz utrudnia obejście tradycyjnych metod opartych wyłącznie na entropii.


## 6. Działanie nodelu uczenia maszynowego
Projekt wykorzystuje algorytmy uczenia maszynowego do wykrywania ransomware na podstawie statycznych cech pliku. Model ocenia prawdopodobieństwo, że analizowany plik jest złośliwy, oraz przypisuje mu poziom ryzyka.


## Cel modelu

Celem modelu jest:
- wykrywanie potencjalnego ransomware,
- minimalizacja ryzyka false negatives,
- dostarczenie prawdopodobieństwa oraz czytelnego poziomu ryzyka.


## Dane wejściowe (cechy)

Model korzysta wyłącznie z cech stabilnych i istotnych z punktu widzenia analizy statycznej plików:

| Cecha | Opis |
|------|------|
| `type` | Typ pliku (zakodowany numerycznie) |
| `size` | Rozmiar pliku |
| `entropy` | Entropia – miara losowości danych |
| `variance` | Wariancja bajtów |

> Pole `id` zostało celowo pominięte, ponieważ jest losowe i pogarsza zdolność generalizacji modelu.


## Przetwarzanie danych

- Wszystkie cechy numeryczne są **standaryzowane** (`StandardScaler`)
- Preprocessing oraz model są połączone w jeden **Pipeline**
- Zapewnia to identyczne przetwarzanie danych treningowych i predykcyjnych

```text
Dane → Skalowanie → Model ML → Predykcja
```

## RandomForestClassifier – szczegółowe wyjaśnienie działania

`RandomForestClassifier` jest algorytmem zespołowym, który łączy wiele drzew decyzyjnych w jeden model o lepszej jakości predykcji i większej odporności na błędy.


### Drzewo decyzyjne – fundament Random Forest

Pojedyncze drzewo decyzyjne działa jak sekwencja pytań logicznych:

- na każdym węźle wybierana jest cecha i próg (np. `entropy > 7.3`),
- dane są dzielone na dwa podzbiory,
- proces trwa aż do osiągnięcia liścia decyzyjnego,
- liść zwraca decyzję klasyfikacyjną.

Zalety:
- prostota,
- łatwa interpretacja.

Wady:
- bardzo wysoka podatność na **overfitting**,
- duża wrażliwość na szum w danych.

---

### Idea lasu losowego (Random Forest)

Random Forest eliminuje wady pojedynczych drzew poprzez **losowość i zespołowość**.

Algorytm:
1. Tworzy wiele drzew decyzyjnych (np. 200).
2. Każde drzewo:
   - uczy się na losowej próbce danych (bootstrap sampling),
   - w każdym węźle widzi tylko losowy podzbiór cech.
3. Każde drzewo podejmuje niezależną decyzję.
4. Wynik końcowy to **głosowanie większościowe**.

```text
Drzewo 1 → ransomware
Drzewo 2 → ransomware
Drzewo 3 → benign
...
Finalna decyzja → ransomware
```

### Rola losowości

Losowość w algorytmie Random Forest występuje na dwóch kluczowych poziomach:

- **losowy wybór próbek danych** (bootstrap sampling),
- **losowy wybór cech** przy każdym podziale w drzewie.

Dzięki temu:
- poszczególne drzewa różnią się od siebie,
- błędy pojedynczych drzew nie kumulują się,
- model lepiej generalizuje na nowych, nieznanych danych.

Losowość jest kluczowym elementem, który odróżnia Random Forest od klasycznych drzew decyzyjnych i znacząco poprawia jego stabilność.


### Prawdopodobieństwa klas

Random Forest umożliwia estymację prawdopodobieństw klas zamiast zwracania wyłącznie decyzji binarnej.

Mechanizm:
- każde drzewo w lesie oddaje głos na jedną z klas,
- prawdopodobieństwo klasy to odsetek drzew głosujących na tę klasę.

Przykład:
```text
Liczba drzew: 200
Ransomware:   140
Benign:        60

P(ransomware) = 140 / 200 = 70%
```
Takie podejście jest szczególnie istotne w cyberbezpieczeństwie, gdzie kluczowa jest ocena poziomu ryzyka, a nie jedynie binarna decyzja o tym, czy plik jest złośliwy. Pozwala to na elastyczne reagowanie systemu w zależności od stopnia zagrożenia.


### Random Forest a niezbalansowane dane

W problemach związanych z wykrywaniem malware dane są zazwyczaj niezbalansowane – liczba plików benign znacząco przewyższa liczbę próbek ransomware.

W projekcie zastosowano następujące mechanizmy:
- `class_weight = 'balanced'`, który zwiększa wagę błędów popełnianych na klasie mniejszościowej,
- decyzję opartą na prawdopodobieństwie, a nie standardowym progu 50%.

Efektem jest:
- zwiększona czułość modelu,
- zmniejszone ryzyko przeoczenia realnego zagrożenia,
- bardziej konserwatywne podejście do bezpieczeństwa.


### Dlaczego Random Forest w tym projekcie?

Random Forest został wybrany jako główny algorytm klasyfikacyjny, ponieważ:
- dobrze radzi sobie z danymi tablicowymi,
- jest odporny na overfitting,
- nie wymaga skomplikowanego tuningu hiperparametrów,
- umożliwia analizę ważności cech,
- zapewnia stabilne i powtarzalne wyniki.

Algorytm ten stanowi kompromis pomiędzy skutecznością, interpretowalnością oraz złożonością obliczeniową.


### Ograniczenia algorytmu

Pomimo licznych zalet, Random Forest posiada również pewne ograniczenia:

- mniejsza interpretowalność niż pojedyncze drzewo decyzyjne,
- wolniejsze działanie przy bardzo dużych zbiorach danych,
- brak zdolności do uczenia zależności sekwencyjnych i czasowych.

Z tego powodu model traktowany jest jako solidna baza, a nie rozwiązanie ostateczne.


