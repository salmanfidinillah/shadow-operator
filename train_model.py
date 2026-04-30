import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import random

print("⚙️ Generating FUTURE SIMULATION Dataset (v2)...")

np.random.seed(42)
data_size = 2500 # Kita perbanyak biar AI makin pinter

actions = ['kirim_barang', 'set_harga', 'update_stok', 'hapus_data']
times = ['pagi', 'siang', 'sore', 'malam']
user_roles = ['admin', 'staff', 'intern']

dataset = {
    "action": np.random.choice(actions, data_size),
    "stock": np.random.randint(0, 1000, data_size),
    "price": np.random.randint(1000, 500000, data_size),
    "time": np.random.choice(times, data_size),
    "user_role": np.random.choice(user_roles, data_size),
    # 0 = Sukses, 1 = Delay/Peringatan, 2 = Gagal Fatal/Error
    "outcome": np.zeros(data_size, dtype=int) 
}

df = pd.DataFrame(dataset)

# 🧠 RULES BARU: Bikin AI punya "Personal Behavior Model" & Logika Kompleks
for i in range(data_size):
    row = df.iloc[i]
    
    # KONDISI GAGAL FATAL (2)
    if row['action'] == 'kirim_barang' and row['stock'] < 20:
        df.at[i, 'outcome'] = 2 
    elif row['action'] == 'set_harga' and row['user_role'] == 'intern' and row['time'] == 'malam':
        df.at[i, 'outcome'] = 2 # Intern ngantuk = fatal
    elif row['action'] == 'hapus_data' and row['user_role'] != 'admin':
        df.at[i, 'outcome'] = 2 # Security breach
        
    # KONDISI DELAY / PERINGATAN (1)
    elif row['time'] == 'malam' and row['user_role'] == 'staff':
        df.at[i, 'outcome'] = 1 # Staff malam sering lambat (Behavior Model)
    elif row['action'] == 'kirim_barang' and row['stock'] < 100:
        df.at[i, 'outcome'] = 1 # Stok pas-pasan bikin logistik lambat

    # Noise 5% agar data natural
    if random.random() < 0.05:
        df.at[i, 'outcome'] = random.choice([0, 1, 2])

df.to_csv("future_dataset_v2.csv", index=False)
print("✅ Dataset v2 berhasil dibuat! (3 Outcomes)")

print("⏳ Preprocessing...")
encoders = {}
for col in ['action', 'time', 'user_role']:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    encoders[col] = le

X = df.drop("outcome", axis=1)
y = df["outcome"]

print("🧠 Training AI Model (Future Predictor)...")
# Gunakan parameter yang membuat probabilitas lebih smooth
model = RandomForestClassifier(n_estimators=150, max_depth=10, random_state=42)
model.fit(X, y)

joblib.dump(model, "shadow_model_v2.pkl")
joblib.dump(encoders, "encoders_v2.pkl")

print("🚀 BOOM! Model V2 Siap!")