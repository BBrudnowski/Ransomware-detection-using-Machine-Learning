import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.ensemble import RandomForestClassifier


def Check_if_ransomware(examined_file):
    """
    Ocenia czy dany plik to ransomware na podstawie cech.
    
    Args:
        examined_file (dict): Słownik z danymi pliku:
            {'id': int, 'type': int, 'size': int, 'entropy': float, 'variance': float}
    
    Returns:
        dict: {'is_ransomware': bool, 'confidence': float}
    """
    
    # Pobranie ścieżki do folderu projektu
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(project_dir, 'napierone_entropy_data.csv')
    
    df = pd.read_csv(data_path)
    target = 'label'

    # Oddzielenie plików ransomware od zwykłych  
    X = df.drop(columns=[target])
    y = df[target]

    #Liczenie odchylenia standardowego oraz skalowanie liczb
    numeric_transformer = Pipeline(steps=[('scaler', StandardScaler())]) 

    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()

    preprocess = ColumnTransformer(transformers=[
        ('num', numeric_transformer, numeric_features),
    ])
    #Model - RandomForestClassifier
    clf = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced'
    )

    model = Pipeline(steps=[('preprocess', preprocess), ('classifier', clf)])

    model.fit(X, y)

    # Konwersja słownika do DataFrame z tą samą kolejnością kolumn jak X
    examined_file_df = pd.DataFrame([examined_file])
    examined_file_df = examined_file_df[X.columns]  # Upewnia się że kolumny są w poprawnej kolejności
    
    # Predykcja: 0 = BENIGN, 1 = RANSOMWARE
    y_pred = model.predict(examined_file_df)[0]
    
    # Prawdopodobieństwo dla każdej klasy
    y_pred_proba = model.predict_proba(examined_file_df)[0]
    
    # Pewność w tym co model przewiduje
    # Jeśli to ransomware (1) - zwróć % szansy na ransomware
    # Jeśli to bezpieczny (0) - zwróć % szansy na bezpieczny = 100%
    if y_pred == 1:
        confidence = y_pred_proba[1] * 100
    else:
        confidence = y_pred_proba[0] * 100
    
    # Określenie poziomu ryzyka
    if confidence < 10:
        risk_level = 'VERY HIGH'
    elif confidence < 20:
        risk_level = 'HIGH'
    elif confidence < 30:
        risk_level = 'MEDIUM'
    elif confidence < 50:
        risk_level = 'LOW'
    elif confidence == 100:
        risk_level = 'NO RISK'

    else:
        risk_level = 'VERY LOW'
    
    result = {
        'is_ransomware': bool(y_pred),
        'confidence': round(confidence, 2),
        'risk_level': risk_level
    }
    
    return result