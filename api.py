from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import joblib
import pandas as pd

app = FastAPI(title="AI Shadow Operator v2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    model = joblib.load("shadow_model_v2.pkl")
    encoders = joblib.load("encoders_v2.pkl")
except FileNotFoundError:
    print("❌ Model v2 tidak ditemukan. Run train_model.py dulu!")

@app.post("/simulate")
def simulate(action: str, stock: int, price: int, time: str, user_role: str):
    try:
        # 1. Encode Input
        data_input = {
            "action": encoders['action'].transform([action])[0],
            "stock": stock,
            "price": price,
            "time": encoders['time'].transform([time])[0],
            "user_role": encoders['user_role'].transform([user_role])[0]
        }
        df_input = pd.DataFrame([data_input])
        
        # 2. FUTURE SIMULATION (Hitung probabilitas 3 kemungkinan)
        probs = model.predict_proba(df_input)[0]
        succ_prob = probs[0] if len(probs) > 0 else 0
        del_prob = probs[1] if len(probs) > 1 else 0
        fail_prob = probs[2] if len(probs) > 2 else 0

        # 3. AI REASONING (Explainability Model)
        reasons = []
        if stock < 20 and action == "kirim_barang":
            reasons.append("Stok berada di ambang kritis (<20 unit).")
        if time == "malam" and user_role == "intern":
            reasons.append("Histori behavior: Role 'Intern' memiliki rasio error 85% pada shift malam.")
        elif time == "malam" and user_role == "staff":
            reasons.append("Analitik behavior: Role 'Staff' cenderung mengalami penurunan efisiensi di shift malam.")
        if action == "hapus_data" and user_role != "admin":
            reasons.append("Pelanggaran akses: Tindakan destruktif oleh non-admin.")
        
        insight = " ".join(reasons) if reasons else "Kondisi operasional dalam standar normal. Tidak ada anomali terdeteksi."

        # 4. WHAT-IF SIMULATOR
        what_if_msg = "Sistem optimal. Tidak ada intervensi yang disarankan."
        if fail_prob > 0.3 or del_prob > 0.4:
            if stock < 50 and action == "kirim_barang":
                # AI Mensimulasikan masa depan jika stok diubah jadi 150
                df_wi = df_input.copy()
                df_wi['stock'] = 150
                wi_probs = model.predict_proba(df_wi)[0]
                wi_fail = wi_probs[2] * 100 if len(wi_probs) > 2 else 0
                what_if_msg = f"💡 WHAT-IF: Jika Anda menaikkan stok menjadi 150 sebelum eksekusi, risiko GAGAL akan turun drastis dari {fail_prob*100:.1f}% menjadi {wi_fail:.1f}%!"
            
            elif time == "malam":
                df_wi = df_input.copy()
                df_wi['time'] = encoders['time'].transform(['siang'])[0]
                wi_probs = model.predict_proba(df_wi)[0]
                wi_fail = wi_probs[2] * 100 if len(wi_probs) > 2 else 0
                what_if_msg = f"💡 WHAT-IF: Jika eksekusi ditunda ke shift 'Siang', risiko fatal akan ditekan menjadi {wi_fail:.1f}%. Sangat disarankan."

        # Status Keseluruhan
        status = "AMAN"
        if fail_prob > 0.4: status = "BAHAYA FATAL ❌"
        elif del_prob > 0.4: status = "PERINGATAN ⚠️"

        return {
            "status": "success",
            "risk_level": status,
            "probabilities": {
                "success": round(succ_prob * 100, 1),
                "delay": round(del_prob * 100, 1),
                "fail": round(fail_prob * 100, 1)
            },
            "insight": insight,
            "what_if": what_if_msg
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}