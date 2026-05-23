# ⚡ Thermoelectric Properties Predictor
### TETFund IBR 2024 · Edo State University Uzairue
**PI:** Prof. Akinola S. Olayinka  
**Live URL:** https://thermoelectricpredictor.c2snet.org

---

## Folder structure

```
thermoelectric_app/
├── app.py                        ← Main Streamlit application
├── requirements.txt              ← Pinned Python dependencies
├── README.md
├── .streamlit/
│   └── config.toml              ← Dark theme + server settings
├── assets/
│   ├── TETFUND_logo.png         ← TETFund logo (auto-loaded)
│   └── EDSU_logo.png            ← EDSU logo (auto-loaded)
└── models/
    ├── feature_columns.pkl
    ├── scaler.pkl
    ├── XGBoost_electrical_conductivityS_m_full.pkl
    ├── XGBoost_seebeck_coefficientμV_K_full.pkl
    ├── XGBoost_thermal_conductivityW_mK_full.pkl
    ├── XGBoost_ZT_full.pkl
    └── Gradient_Boosting_power_factorW_mK2_full.pkl
```

---

## Critical: scikit-learn version

The `.pkl` files were saved with **scikit-learn 1.1.3** and **xgboost 1.7.6**.
`requirements.txt` pins these exactly. Using any other version causes the
`__pyx_unpickle_CyHalfSquaredError` error.

If you re-train with a newer sklearn, update the pin to match.

---

## Deploy on Streamlit Community Cloud

1. Push **all files** (including `models/` and `assets/`) to a GitHub repo.
2. If any `.pkl` file exceeds 100 MB, enable **Git LFS**:
   ```bash
   git lfs install
   git lfs track "models/*.pkl"
   git add .gitattributes
   ```
3. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
4. Select your repo, branch `main`, main file `app.py`
5. Click **Deploy** — Streamlit Cloud installs `requirements.txt` automatically.

---

## Run locally

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO
cd YOUR_REPO
pip install -r requirements.txt
streamlit run app.py
```

---

## Admin panel & data retrieval

The app logs every prediction and optional user registration to a local
SQLite database (`thermoelectric_log.db`) created automatically next to `app.py`.

Access via the **🔒 Admin** tab in the app using the admin password.

**Default admin password:** `admin`

**Change it before deployment:**
```python
import hashlib
print(hashlib.sha256(b"YourNewPassword").hexdigest())
```
Paste the output into the `ADMIN_HASH` variable in `app.py`.

On Streamlit Cloud the database resets on each redeployment.
For persistent storage across deployments, replace SQLite with a cloud
database (e.g. Supabase, PlanetScale, or Streamlit's own `st.connection`).

---

## CSV column names (ASCII-safe)

| Column | Property |
|--------|----------|
| `Seebeck_Coefficient_uV/K` | Seebeck coefficient (μV/K) |
| `Electrical_Conductivity_S/m` | Electrical conductivity (S/m) |
| `Thermal_Conductivity_W/mK` | Thermal conductivity (W/mK) |
| `Power_Factor_W/mK2` | Power factor (W/mK²) |
| `ZT_-` | Figure of merit (dimensionless) |
| `Priority_Flag` | `Priority_kappa_lt_1` if κ < 1.0 W/mK |

Plain ASCII headers prevent the encoding corruption (`Î¼`, `Â²`, `â€"`)
seen when Excel opens UTF-8 CSVs with special characters.

---

## User registration

Registration is optional and collapsible. Registered users have their
predictions linked to their email in the database. Anonymous users are
logged as `anonymous`. Both are visible in the Admin panel.

---

## Acknowledgement

This work is supported by the **TETFund Institutional Based Research (IBR) 2024**
grant awarded to Edo State University Uzairue (EDSU).
