import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import joblib

FEATURES = ['CO AQI Value', 'Ozone AQI Value', 'NO2 AQI Value', 'PM2.5 AQI Value']
TARGET = 'AQI Category'
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'aqi_model.pkl')

def train_model(df):
    X = df[FEATURES]
    y = df[TARGET]

    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    accuracy = model.score(X_test, y_test)
    joblib.dump((model, encoder), MODEL_PATH)

    return model, encoder, accuracy

def load_or_train_model(df):
    if os.path.exists(MODEL_PATH):
        model, encoder = joblib.load(MODEL_PATH)
        return model, encoder, None
    return train_model(df)

def predict_category(model, encoder, co, ozone, no2, pm25):
    input_df = pd.DataFrame([[co, ozone, no2, pm25]], columns=FEATURES)
    pred_encoded = model.predict(input_df)[0]
    return encoder.inverse_transform([pred_encoded])[0]