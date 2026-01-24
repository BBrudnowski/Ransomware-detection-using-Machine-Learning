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

    # Używamy tylko stabilnych cech (bez 'id', który jest losowy i szkodliwy dla generalizacji)
    feature_cols = ['type', 'size', 'entropy', 'variance']
    X = df[feature_cols]
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
    
    # Prawdopodobieństwo dla każdej klasy
    y_pred_proba = model.predict_proba(examined_file_df)[0]
    
    # ZAWSZE zwracamy prawdopodobieństwo ransomware (klasa 1)
    ransomware_probability = float(y_pred_proba[1] * 100)
    
    # Obniżony próg decyzyjny (20% zamiast 50%) ze względu na niezbalansowane dane
    y_pred = 1 if y_pred_proba[1] >= 0.20 else 0
    
    # Określenie poziomu ryzyka na podstawie prawdopodobieństwa ransomware
    if ransomware_probability >= 80:
        risk_level = 'VERY HIGH'
    elif ransomware_probability >= 60:
        risk_level = 'HIGH'
    elif ransomware_probability >= 40:
        risk_level = 'MEDIUM'
    elif ransomware_probability >= 20:
        risk_level = 'LOW'
    else:
        risk_level = 'VERY LOW'
    
    result = {
        'is_ransomware': bool(y_pred),
        'confidence': round(ransomware_probability, 2),
        'risk_level': risk_level
    }
    
    return result