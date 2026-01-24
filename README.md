# Wykrywanie ataków typu Ransomware poprzez analize entropii (zbackupowanych) danych plikowych przy pomocy uczenia maszynowego (ML).
Autorzy: [Przemysław Bryzek](https://github.com/przemyslawbryzek), [Błażej Brudnowski](https://github.com/BBrudnowski)
## 1. Wstęp


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
3. Obliczenie prawdopodobieństwa dla każdej wartości: $p_i = \frac{\text{count}_i}{\text{total\_bytes}}$
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

## 5. Entropy Sharing - Nowa Technika Ewaluac
Najnowsze badania z 2024 roku ujawniły metodę o nazwie "Entropy Sharing", którą może stosować zaawansowany ransomware. Technika ta dzieli zaszyfrowane dane na części, rekombinuje je w sposób obniżający średnią entropię.Ma ona niski koszt obliczeniowy oraz utrudnia obejście tradycyjnych metod opartych wyłącznie na entropii.


