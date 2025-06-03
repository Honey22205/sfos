import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder

# Load the dataset
file_path = r"C:\Users\BIT\Downloads\flask\data\billing_data.csv"
df = pd.read_csv(file_path)

# Simulate "market_price" based on part_name (as per original logic)
np.random.seed(42)
part_market_price_map = {part: round(np.random.uniform(5, 500), 2) for part in df['part_name'].unique()}
df['market_price'] = df['part_name'].map(part_market_price_map)

# Calculate difference and recommendation
df['difference'] = df['market_price'] - df['tender_price']
df['recommendation'] = np.where(df['tender_price'] <= df['market_price'], 'Accept Tender', 'Re-evaluate Pricing')

# Encode categorical features
label_encoders = {}
for col in ['part_name', 'country']:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le

# Define features and target
X = df[['part_name', 'country', 'quantity', 'tender_price']]
y = df['recommendation']

# Encode target
target_le = LabelEncoder()
y = target_le.fit_transform(y)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Predict and evaluate
y_pred = model.predict(X_test)
report = classification_report(y_test, y_pred, target_names=target_le.classes_)
conf_matrix = confusion_matrix(y_test, y_pred)

model, report, conf_matrix, target_le.classes_

import joblib
joblib.dump(model, 'billing_model.pkl')


joblib.dump(label_encoders['part_name'], 'part_encoder.pkl')
joblib.dump(label_encoders['country'], 'country_encoder.pkl')
joblib.dump(target_le, 'target_encoder.pkl') 