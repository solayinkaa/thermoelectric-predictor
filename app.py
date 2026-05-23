"""
Thermoelectric Properties Predictor
=====================================
TETFund Institutional Based Research (IBR) 2024
Edo State University Uzairue (EDSU)
Principal Investigator: Prof. Akinola S. Olayinka
Web: https://thermoelectricpredictor.c2snet.org
"""

import re
import os
import csv
import json
import sqlite3
import hashlib
from io import StringIO
from collections import Counter
from datetime import datetime

import numpy as np
import pandas as pd
import joblib
import streamlit as st

# ============================================================
# PAGE CONFIG  — must be first Streamlit call
# ============================================================
st.set_page_config(
    page_title="Thermoelectric Predictor | EDSU · TETFund IBR 2024",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={"About": "TETFund IBR 2024 · Edo State University Uzairue · thermoelectricpredictor.c2snet.org"},
)

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root{
  --bg:#080E1A; --s1:#0F1929; --s2:#162236; --s3:#1D2E47;
  --bd:#243350; --blue:#2E86AB; --amber:#F18F01; --teal:#06A77D;
  --red:#EF4444; --txt:#E4EBF5; --dim:#8494A9;
  --r:10px; --fh:'Playfair Display',Georgia,serif;
  --fb:'Inter',system-ui,sans-serif; --fm:'JetBrains Mono',monospace;
}

/* shell */
.stApp{background:var(--bg)!important;color:var(--txt)!important;font-family:var(--fb)!important}
[data-testid="stSidebar"]{background:var(--s1)!important;border-right:1px solid var(--bd)!important}

/* banner */
.banner{background:linear-gradient(135deg,#060d1a,#0c1e35,#07111f);border:1px solid var(--bd);
  border-radius:var(--r);padding:1.6rem 2rem 1.4rem;position:relative;overflow:hidden;margin-bottom:1rem}
.banner::after{content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse at 20% 55%,rgba(46,134,171,.14) 0%,transparent 55%),
             radial-gradient(ellipse at 85% 20%,rgba(241,143,1,.09) 0%,transparent 45%);pointer-events:none}
.banner-title{font-family:var(--fh);font-size:clamp(1.4rem,3vw,2rem);font-weight:700;
  background:linear-gradient(100deg,#e4ebf5 0%,#93c5fd 50%,#fbbf24 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  margin:0 0 .25rem;line-height:1.2}
.banner-sub{font-size:.83rem;color:var(--dim);margin:0;font-weight:300}
.chips{display:flex;flex-wrap:wrap;gap:.35rem;margin-top:.8rem}
.chip{background:rgba(46,134,171,.12);border:1px solid rgba(46,134,171,.28);color:#93c5fd;
  border-radius:20px;padding:.15rem .65rem;font-size:.72rem;font-family:var(--fm);font-weight:500}

/* acknowledgement */
.ack{background:linear-gradient(135deg,rgba(241,143,1,.07),rgba(6,167,125,.05));
  border:1px solid rgba(241,143,1,.25);border-left:4px solid var(--amber);
  border-radius:var(--r);padding:.8rem 1.2rem;font-size:.82rem;color:#c9963a;line-height:1.65;margin-bottom:1rem}
.ack strong{color:var(--amber)}

/* section header */
.sec{font-family:var(--fh);font-size:1.1rem;font-weight:600;color:var(--txt);
  border-bottom:1px solid var(--bd);padding-bottom:.4rem;margin:1.2rem 0 .8rem}

/* model cards */
.mcards{display:grid;grid-template-columns:repeat(5,1fr);gap:.55rem;margin-bottom:1.1rem}
@media(max-width:860px){.mcards{grid-template-columns:repeat(3,1fr)}}
.mcard{background:var(--s2);border:1px solid var(--bd);border-radius:var(--r);
  padding:.75rem .9rem;text-align:center}
.mcard:hover{border-color:var(--blue)}
.mprop{font-size:.66rem;color:var(--dim);font-family:var(--fm);text-transform:uppercase;letter-spacing:.07em}
.malgo{font-size:.78rem;font-weight:600;color:var(--txt);margin:.15rem 0}
.mr2{font-size:1.05rem;font-weight:700;color:var(--teal);font-family:var(--fm)}

/* formula display */
.fbox{background:var(--s2);border:1.5px solid rgba(46,134,171,.4);border-radius:8px;
  padding:.5rem 1rem;font-family:var(--fm);font-size:1.05rem;color:#93c5fd;
  min-height:2.5rem;margin:.3rem 0 .6rem;word-break:break-all}
.fbox-empty{color:var(--dim);font-size:.85rem;font-style:italic}

/* periodic table */
.pt-wrap{max-height:290px;overflow-y:auto;background:var(--s2);border:1px solid var(--bd);
  border-radius:var(--r);padding:.8rem 1rem;margin-bottom:.7rem}
.pt-cat{font-size:.65rem;text-transform:uppercase;letter-spacing:.1em;
  color:var(--dim);font-weight:600;margin:.55rem 0 .25rem}
.pt-row{display:flex;flex-wrap:wrap;gap:.3rem}
.el{background:var(--s1);border:1px solid var(--bd);border-radius:5px;
  padding:.18rem .48rem;font-size:.76rem;font-family:var(--fm);color:var(--txt);
  cursor:pointer;transition:all .13s;user-select:none}
.el:hover{background:rgba(46,134,171,.22);border-color:var(--blue);color:#93c5fd}

/* badges */
.fbad{display:inline-block;background:rgba(239,68,68,.12);border:1px solid rgba(239,68,68,.35);
  color:#f87171;border-radius:10px;padding:.06rem .6rem;font-size:.74rem;font-weight:600;margin:.4rem 0}
.gbad{display:inline-block;background:rgba(6,167,125,.12);border:1px solid rgba(6,167,125,.32);
  color:var(--teal);border-radius:10px;padding:.06rem .6rem;font-size:.74rem;font-weight:600;margin:.4rem 0}

/* widgets */
.stTextInput>div>div>input,
.stNumberInput>div>div>input{
  background:var(--s2)!important;border:1px solid var(--bd)!important;
  color:var(--txt)!important;border-radius:8px!important;font-family:var(--fm)!important}
.stTextInput>div>div>input:focus,
.stNumberInput>div>div>input:focus{border-color:var(--blue)!important;box-shadow:0 0 0 2px rgba(46,134,171,.2)!important}
.stButton>button{background:linear-gradient(135deg,var(--blue),#1d6b8b)!important;
  color:#fff!important;border:none!important;border-radius:8px!important;
  font-family:var(--fb)!important;font-weight:600!important;padding:.5rem 1.3rem!important;width:100%}
.stButton>button:hover{opacity:.84!important;transform:translateY(-1px)!important}
.stTabs [data-baseweb="tab-list"]{background:transparent!important;gap:.2rem}
.stTabs [data-baseweb="tab"]{background:var(--s1)!important;border:1px solid var(--bd)!important;
  border-radius:8px 8px 0 0!important;color:var(--dim)!important;font-family:var(--fb)!important;font-weight:500!important}
.stTabs [aria-selected="true"]{background:var(--s2)!important;color:var(--txt)!important;border-bottom-color:var(--s2)!important}
[data-testid="stMetric"]{background:var(--s2);border:1px solid var(--bd);border-radius:var(--r);padding:.65rem .85rem}
[data-testid="stMetricValue"]{color:var(--blue)!important;font-family:var(--fm)!important;font-size:.98rem!important}
[data-testid="stMetricLabel"]{font-size:.68rem!important;color:var(--dim)!important}
details{background:var(--s1)!important;border:1px solid var(--bd)!important;border-radius:var(--r)!important}
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-track{background:var(--s1)}
::-webkit-scrollbar-thumb{background:var(--bd);border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:var(--blue)}
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATABASE  — SQLite, auto-created next to app.py
# ============================================================
DB_PATH = os.path.join(os.path.dirname(__file__), "thermoelectric_log.db")

def _get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

def init_db():
    conn = _get_conn()
    c = conn.cursor()
    # users table
    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, email TEXT UNIQUE, institution TEXT,
        role TEXT, country TEXT,
        registered_at TEXT DEFAULT (datetime('now'))
    )""")
    # predictions log
    c.execute("""CREATE TABLE IF NOT EXISTS predictions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        formula TEXT, temperature REAL,
        seebeck REAL, elec_cond REAL, therm_cond REAL,
        power_factor REAL, zt REAL, flagged INTEGER,
        mode TEXT,
        predicted_at TEXT DEFAULT (datetime('now'))
    )""")
    conn.commit()
    conn.close()

init_db()

def register_user(name, email, institution, role, country):
    try:
        conn = _get_conn()
        conn.execute(
            "INSERT OR IGNORE INTO users(name,email,institution,role,country) VALUES(?,?,?,?,?)",
            (name, email, institution, role, country)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        return str(e)

def log_prediction(email, formula, temperature, results, mode="single"):
    try:
        conn = _get_conn()
        flagged = 1 if results.get("Thermal Conductivity", 999) < 1.0 else 0
        conn.execute(
            """INSERT INTO predictions
               (user_email,formula,temperature,seebeck,elec_cond,therm_cond,
                power_factor,zt,flagged,mode)
               VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (email or "anonymous",
             formula, temperature,
             results.get("Seebeck Coefficient"),
             results.get("Electrical Conductivity"),
             results.get("Thermal Conductivity"),
             results.get("Power Factor"),
             results.get("ZT"),
             flagged, mode)
        )
        conn.commit()
        conn.close()
    except Exception:
        pass

def fetch_all_predictions() -> pd.DataFrame:
    conn = _get_conn()
    df = pd.read_sql_query("SELECT * FROM predictions ORDER BY predicted_at DESC", conn)
    conn.close()
    return df

def fetch_all_users() -> pd.DataFrame:
    conn = _get_conn()
    df = pd.read_sql_query("SELECT * FROM users ORDER BY registered_at DESC", conn)
    conn.close()
    return df

# ============================================================
# PERIODIC TABLE DATA
# ============================================================
PT_DATA = {
    "Alkali Metals":      ["Li","Na","K","Rb","Cs"],
    "Alkaline Earth":     ["Be","Mg","Ca","Sr","Ba"],
    "Transition Metals":  ["Ti","V","Cr","Mn","Fe","Co","Ni","Cu","Zn",
                           "Zr","Nb","Mo","Ru","Rh","Pd","Ag","Cd",
                           "Hf","Ta","W","Re","Os","Ir","Pt","Au","Hg"],
    "Post-transition":    ["Al","Ga","In","Sn","Tl","Pb","Bi"],
    "Metalloids":         ["B","Si","Ge","As","Sb","Te"],
    "Chalcogens":         ["O","S","Se"],
    "Pnictogens":         ["N","P"],
    "Halogens":           ["F","Cl","Br","I"],
    "Lanthanides":        ["La","Ce","Nd","Sm","Eu","Gd","Dy","Er","Yb","Lu"],
    "Other Nonmetals":    ["H","C"],
}

# ============================================================
# FEATURE ENGINEERING  (mirrors pipeline exactly)
# ============================================================
def parse_formula(formula: str) -> Counter:
    hits = re.findall(r"([A-Z][a-z]*)(\d*)", formula)
    counts: Counter = Counter()
    for elem, cnt in hits:
        if elem:
            counts[elem] += int(cnt) if cnt else 1
    return counts

def build_features(formula: str, temperature: float, feature_columns: list) -> pd.DataFrame:
    counts = parse_formula(formula)
    row = {c: 0.0 for c in feature_columns}

    for elem, cnt in counts.items():
        if elem in row:
            row[elem] = float(cnt)

    total_atoms  = float(sum(counts.values())) or 1.0
    num_elements = float(len(counts))

    row["temperature(K)"]           = float(temperature)
    row["total_atoms"]              = total_atoms
    row["num_elements"]             = num_elements
    row["compositional_complexity"] = num_elements / (total_atoms + 1.0)
    row["temp_squared"]             = float(temperature) ** 2
    row["temp_log"]                 = np.log(float(temperature) + 1.0)
    row["temp_inv"]                 = 1.0 / (float(temperature) + 1.0)

    fracs = {e: c / total_atoms for e, c in counts.items()}
    row["shannon_entropy"]       = -sum(f * np.log(f + 1e-10) for f in fracs.values())
    row["max_element_fraction"]  = max(fracs.values()) if fracs else 0.0
    row["min_element_fraction"]  = min((f for f in fracs.values() if f > 0), default=0.0)
    row["temp_x_complexity"]     = float(temperature) * row["compositional_complexity"]
    row["temp_x_num_elements"]   = float(temperature) * num_elements

    return pd.DataFrame([row])[feature_columns]

# ============================================================
# MODEL LOADING
# ============================================================
PROP_META = {
    "Seebeck Coefficient":     {"unit": "uV/K",  "unit_display": "μV/K",  "r2": 0.787, "algo": "XGBoost",           "log": False},
    "Electrical Conductivity": {"unit": "S/m",   "unit_display": "S/m",   "r2": 0.823, "algo": "XGBoost",           "log": True},
    "Thermal Conductivity":    {"unit": "W/mK",  "unit_display": "W/mK",  "r2": 0.797, "algo": "XGBoost",           "log": False},
    "Power Factor":            {"unit": "W/mK2", "unit_display": "W/mK²", "r2": 0.863, "algo": "Gradient Boosting", "log": False},
    "ZT":                      {"unit": "-",     "unit_display": "—",     "r2": 0.796, "algo": "XGBoost",           "log": False},
}
ORDER = ["Seebeck Coefficient","Electrical Conductivity","Thermal Conductivity","Power Factor","ZT"]

@st.cache_resource(show_spinner="Loading ML models…")
def load_models():
    base = "models"
    try:
        fc  = joblib.load(f"{base}/feature_columns.pkl")
        sc  = joblib.load(f"{base}/scaler.pkl")
        mdl = {
            "Seebeck Coefficient":     joblib.load(f"{base}/XGBoost_seebeck_coefficientμV_K_full.pkl"),
            "Electrical Conductivity": joblib.load(f"{base}/XGBoost_electrical_conductivityS_m_full.pkl"),
            "Thermal Conductivity":    joblib.load(f"{base}/XGBoost_thermal_conductivityW_mK_full.pkl"),
            "Power Factor":            joblib.load(f"{base}/Gradient_Boosting_power_factorW_mK2_full.pkl"),
            "ZT":                      joblib.load(f"{base}/XGBoost_ZT_full.pkl"),
        }
        return fc, sc, mdl, None
    except Exception as exc:
        return None, None, None, str(exc)

# ============================================================
# PREDICTION
# ============================================================
def predict_one(formula, temperature, fc, sc, mdl):
    X  = build_features(formula, float(temperature), fc)
    Xs = sc.transform(X)
    out = {}
    for prop, model in mdl.items():
        val = float(model.predict(Xs)[0])
        if PROP_META[prop]["log"]:
            val = 10.0 ** val
        out[prop] = val
    return out

def results_to_df(formula, temperature, results):
    """Build a clean DataFrame with ASCII-safe column headers for CSV export."""
    row = {"Formula": formula, "Temperature_K": float(temperature)}
    for prop in ORDER:
        col = f"{prop}_{PROP_META[prop]['unit']}"
        row[col] = round(results[prop], 6)
    row["Priority_Flag"] = "Priority_kappa_lt_1" if results["Thermal Conductivity"] < 1.0 else ""
    return pd.DataFrame([row])

def batch_predict(df_in, fc, sc, mdl):
    rows = []
    for _, r in df_in.iterrows():
        try:
            p   = predict_one(str(r["Formula"]), float(r["temperature_K"]), fc, sc, mdl)
            row = {"Formula": r["Formula"], "Temperature_K": r["temperature_K"]}
            for prop in ORDER:
                row[f"{prop}_{PROP_META[prop]['unit']}"] = round(p[prop], 6)
            row["Priority_Flag"] = "Priority_kappa_lt_1" if p["Thermal Conductivity"] < 1.0 else ""
            rows.append(row)
        except Exception as e:
            rows.append({"Formula": r["Formula"], "Error": str(e)})
    return pd.DataFrame(rows)

# ============================================================
# SESSION STATE
# ============================================================
for _k, _v in [
    ("pt_elems", {}),
    ("single_result", None),
    ("pt_result", None),
    ("user_email", ""),
    ("user_name", ""),
    ("registered", False),
]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ============================================================
# LOGO PATHS
# ============================================================
TETFUND_LOGO = "assets/TETFUND_logo.png"
EDSU_LOGO    = "assets/EDSU_logo.png"

# ============================================================
# HEADER
# ============================================================
cl, cm, cr = st.columns([1, 6, 1])
with cl:
    if os.path.exists(TETFUND_LOGO):
        st.image(TETFUND_LOGO, use_container_width=True)
    else:
        st.markdown("<p style='text-align:center;color:#8494A9;font-size:.7rem;margin-top:1rem'>TETFUND<br>logo</p>",
                    unsafe_allow_html=True)
with cm:
    st.markdown("""
<div class="banner">
  <p class="banner-title">Thermoelectric Properties Predictor</p>
  <p class="banner-sub">
    AI-driven prediction · Edo State University Uzairue ·
    <a href="https://thermoelectricpredictor.c2snet.org" style="color:#93c5fd;text-decoration:none">
      thermoelectricpredictor.c2snet.org</a>
  </p>
  <div class="chips">
    <span class="chip">5 Properties</span>
    <span class="chip">88-Feature Pipeline</span>
    <span class="chip">XGBoost · Gradient Boosting</span>
    <span class="chip">Single &amp; Batch Mode</span>
    <span class="chip">TETFund IBR 2024</span>
  </div>
</div>
""", unsafe_allow_html=True)
with cr:
    if os.path.exists(EDSU_LOGO):
        st.image(EDSU_LOGO, use_container_width=True)
    else:
        st.markdown("<p style='text-align:center;color:#8494A9;font-size:.7rem;margin-top:1rem'>EDSU<br>logo</p>",
                    unsafe_allow_html=True)

# Acknowledgement
st.markdown("""
<div class="ack">
  <strong>Acknowledgement</strong> — This research is funded by the
  <strong>TETFund Institutional Based Research (IBR) 2024</strong> grant,
  Edo State University Uzairue (EDSU). PI: <strong>Prof. Akinola S. Olayinka</strong>.
  Compounds with predicted thermal conductivity κ &lt; 1.0 W/mK are automatically
  flagged as priority candidates for experimental validation and future model retraining.
</div>
""", unsafe_allow_html=True)

# Model cards
st.markdown('<div class="sec">Best-performing models deployed</div>', unsafe_allow_html=True)
st.markdown("""
<div class="mcards">
  <div class="mcard"><div class="mprop">Seebeck Coeff.</div>
    <div class="malgo">XGBoost</div><div class="mr2">R² 0.787</div></div>
  <div class="mcard"><div class="mprop">Elec. Conductivity</div>
    <div class="malgo">XGBoost</div><div class="mr2">R² 0.823</div></div>
  <div class="mcard"><div class="mprop">Thermal Conductivity</div>
    <div class="malgo">XGBoost</div><div class="mr2">R² 0.797</div></div>
  <div class="mcard"><div class="mprop">Power Factor</div>
    <div class="malgo">Gradient Boost.</div><div class="mr2">R² 0.863</div></div>
  <div class="mcard"><div class="mprop">Figure of Merit ZT</div>
    <div class="malgo">XGBoost</div><div class="mr2">R² 0.796</div></div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# LOAD MODELS
# ============================================================
fc, sc, mdl, load_err = load_models()

if load_err:
    st.error(
        f"**Model loading failed:** {load_err}\n\n"
        "• Ensure `models/` folder contains all 7 `.pkl` files.\n"
        "• Check `requirements.txt` — must use `scikit-learn==1.1.3` and `xgboost==1.7.6`."
    )

st.markdown("---")

# ============================================================
# USER REGISTRATION (optional, collapsible)
# ============================================================
with st.expander("👤  Optional: Register to track your predictions", expanded=False):
    st.markdown(
        "Registration is **optional and free**. It lets you retrieve your prediction history "
        "and helps us understand who is using this tool across the research community."
    )
    rc1, rc2 = st.columns(2)
    with rc1:
        r_name  = st.text_input("Full name",        key="r_name")
        r_email = st.text_input("Email address",     key="r_email")
        r_inst  = st.text_input("Institution",        key="r_inst")
    with rc2:
        r_role    = st.selectbox("Role", ["Researcher","Lecturer","PhD Student",
                                          "MSc Student","Engineer","Other"], key="r_role")
        r_country = st.text_input("Country",          key="r_country")

    if st.button("Register / Update", key="reg_btn"):
        if r_name and r_email:
            res = register_user(r_name, r_email, r_inst, r_role, r_country)
            if res is True:
                st.session_state["user_email"] = r_email
                st.session_state["user_name"]  = r_name
                st.session_state["registered"] = True
                st.success(f"✅ Welcome, {r_name}! Your predictions will be linked to {r_email}.")
            else:
                st.warning(str(res))
        else:
            st.warning("Please enter at least your name and email.")

    if st.session_state["registered"]:
        st.info(f"Logged in as **{st.session_state['user_name']}** ({st.session_state['user_email']})")

st.markdown("")

# ============================================================
# MAIN TABS
# ============================================================
tab_type, tab_pt, tab_batch, tab_about, tab_admin = st.tabs([
    "✏️  Type Formula",
    "🔬  Periodic Table Builder",
    "📂  Batch Upload",
    "ℹ️  About",
    "🔒  Admin",
])

# ──────────────────────────────────────────────────────────────
# TAB 1 — Type formula
# ──────────────────────────────────────────────────────────────
with tab_type:
    st.markdown('<div class="sec">Single Compound — Type Formula</div>', unsafe_allow_html=True)
    st.markdown("Enter a chemical formula and temperature, then click **Predict**.")

    col_f, col_t = st.columns([3, 2])
    with col_f:
        formula_typed = st.text_input(
            "Chemical formula",
            placeholder="e.g.  Bi2Te3   PbTe   CoSb3   Cu2Se   GeTe",
            help="Type element symbols followed by stoichiometry numbers.",
            key="formula_typed",
        )
        st.caption("Examples: `Bi2Te3` · `PbTe` · `CoSb3` · `Cu2Se` · `GeTe` · `SnSe`")
    with col_t:
        temp_typed = st.number_input(
            "Temperature (K)",
            min_value=50, max_value=2000, value=300, step=25,
            key="temp_typed",
        )

    # Live formula preview
    if formula_typed.strip():
        parsed = parse_formula(formula_typed.strip())
        preview = "  ·  ".join(f"{e}<sub>{n}</sub>" if n > 1 else e
                                for e, n in sorted(parsed.items()))
        st.markdown(
            f'<div class="fbox">🔬 <strong>{formula_typed.strip()}</strong>'
            f'<span style="font-size:.78rem;color:#8494A9"> → {preview}</span></div>',
            unsafe_allow_html=True)
    else:
        st.markdown('<div class="fbox fbox-empty">Formula preview appears here…</div>',
                    unsafe_allow_html=True)

    btn_type = st.button(
        "⚡  Predict all 5 properties",
        key="btn_type",
        disabled=(not formula_typed.strip() or load_err is not None),
    )

    if btn_type and formula_typed.strip():
        with st.spinner("Running 5 models simultaneously…"):
            try:
                r = predict_one(formula_typed.strip(), temp_typed, fc, sc, mdl)
                st.session_state["single_result"]  = r
                st.session_state["single_formula"] = formula_typed.strip()
                st.session_state["single_temp"]    = temp_typed
                log_prediction(st.session_state["user_email"],
                               formula_typed.strip(), temp_typed, r, "single")
            except Exception as exc:
                st.error(f"Prediction error: {exc}")

    if st.session_state.get("single_result"):
        r   = st.session_state["single_result"]
        fm  = st.session_state["single_formula"]
        tp  = st.session_state["single_temp"]
        tc  = r["Thermal Conductivity"]

        st.success(f"✅  Results for **{fm}** at **{tp} K**")
        cols = st.columns(5)
        for i, prop in enumerate(ORDER):
            cols[i].metric(
                f"{prop} ({PROP_META[prop]['unit_display']})",
                f"{r[prop]:.4g}",
                help=f"Algorithm: {PROP_META[prop]['algo']} · R²={PROP_META[prop]['r2']}"
            )

        if tc < 1.0:
            st.markdown(f'<div class="fbad">⚑ κ = {tc:.4g} W/mK — Priority candidate (κ &lt; 1.0 W/mK)</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="gbad">✓ κ = {tc:.4g} W/mK — Above screening threshold</div>',
                        unsafe_allow_html=True)

        csv_out = results_to_df(fm, tp, r).to_csv(index=False, encoding="utf-8")
        st.download_button(
            "⬇ Download result (CSV)",
            csv_out.encode("utf-8"),
            file_name=f"thermo_{fm}_{int(tp)}K.csv",
            mime="text/csv",
            key="dl_type",
        )

# ──────────────────────────────────────────────────────────────
# TAB 2 — Periodic Table Builder
# ──────────────────────────────────────────────────────────────
with tab_pt:
    st.markdown('<div class="sec">Single Compound — Periodic Table Builder</div>',
                unsafe_allow_html=True)
    st.markdown(
        "Browse the periodic table below as a **reference**, then use the controls "
        "to add elements and build your formula."
    )

    # Render periodic table (visual reference)
    pt_html = ['<div class="pt-wrap">']
    for cat, elems in PT_DATA.items():
        pt_html.append(f'<div class="pt-cat">{cat}</div><div class="pt-row">')
        for e in elems:
            pt_html.append(f'<span class="el" title="{e}">{e}</span>')
        pt_html.append('</div>')
    pt_html.append('</div>')
    st.markdown("".join(pt_html), unsafe_allow_html=True)

    # Controls
    st.markdown("**Add elements to your formula:**")
    pa, pb, pc, pd_ = st.columns([2, 1, 1, 1])
    with pa:
        new_sym = st.text_input(
            "Element symbol (e.g. Bi, Te, Pb)",
            key="pt_sym",
            label_visibility="collapsed",
            placeholder="Element symbol  e.g. Bi",
        )
    with pb:
        new_cnt = st.number_input(
            "Count", min_value=1, max_value=30, value=2,
            key="pt_cnt", label_visibility="collapsed",
        )
    with pc:
        if st.button("➕ Add", key="pt_add_btn"):
            sym = new_sym.strip().capitalize()
            if re.match(r"^[A-Z][a-z]?$", sym):
                st.session_state["pt_elems"][sym] = new_cnt
                st.rerun()
            elif sym:
                st.warning("Enter a valid element symbol (e.g. Bi, Te, Pb, Se).")
    with pd_:
        if st.button("🗑 Clear", key="pt_clear_btn"):
            st.session_state["pt_elems"] = {}
            st.rerun()

    # Show composition + formula
    if st.session_state["pt_elems"]:
        elems_d = st.session_state["pt_elems"]
        formula_pt = "".join(
            f"{e}{n if n > 1 else ''}" for e, n in elems_d.items()
        )
        comp_str = "  ·  ".join(f"**{e}** ×{n}" for e, n in elems_d.items())
        st.markdown(f"**Composition:** {comp_str}")
        st.markdown(
            f'<div class="fbox">🔬 <strong>{formula_pt}</strong></div>',
            unsafe_allow_html=True
        )

        # Remove individual elements
        with st.expander("Remove an element"):
            rm_cols = st.columns(min(len(elems_d), 6))
            for i, sym in enumerate(list(elems_d.keys())):
                with rm_cols[i % 6]:
                    if st.button(f"✕ {sym}", key=f"rm_{sym}"):
                        del st.session_state["pt_elems"][sym]
                        st.rerun()
    else:
        formula_pt = ""
        st.markdown('<div class="fbox fbox-empty">No elements added yet.</div>',
                    unsafe_allow_html=True)

    temp_pt = st.number_input(
        "Temperature (K)",
        min_value=50, max_value=2000, value=300, step=25, key="temp_pt",
    )

    btn_pt = st.button(
        "⚡  Predict all 5 properties",
        key="btn_pt",
        disabled=(not formula_pt or load_err is not None),
    )

    if btn_pt and formula_pt:
        with st.spinner("Running 5 models simultaneously…"):
            try:
                r_pt = predict_one(formula_pt, temp_pt, fc, sc, mdl)
                st.session_state["pt_result"]  = r_pt
                st.session_state["pt_formula"] = formula_pt
                st.session_state["pt_temp"]    = temp_pt
                log_prediction(st.session_state["user_email"],
                               formula_pt, temp_pt, r_pt, "periodic_table")
            except Exception as exc:
                st.error(f"Prediction error: {exc}")

    if st.session_state.get("pt_result"):
        r_pt = st.session_state["pt_result"]
        fm_pt = st.session_state["pt_formula"]
        tp_pt = st.session_state["pt_temp"]
        tc_pt = r_pt["Thermal Conductivity"]

        st.success(f"✅  Results for **{fm_pt}** at **{tp_pt} K**")
        cols_pt = st.columns(5)
        for i, prop in enumerate(ORDER):
            cols_pt[i].metric(
                f"{prop} ({PROP_META[prop]['unit_display']})",
                f"{r_pt[prop]:.4g}",
                help=f"Algorithm: {PROP_META[prop]['algo']} · R²={PROP_META[prop]['r2']}"
            )

        if tc_pt < 1.0:
            st.markdown(f'<div class="fbad">⚑ κ = {tc_pt:.4g} W/mK — Priority candidate (κ &lt; 1.0 W/mK)</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="gbad">✓ κ = {tc_pt:.4g} W/mK — Above screening threshold</div>',
                        unsafe_allow_html=True)

        csv_pt = results_to_df(fm_pt, tp_pt, r_pt).to_csv(index=False, encoding="utf-8")
        st.download_button(
            "⬇ Download result (CSV)",
            csv_pt.encode("utf-8"),
            file_name=f"thermo_{fm_pt}_{int(tp_pt)}K.csv",
            mime="text/csv",
            key="dl_pt",
        )

# ──────────────────────────────────────────────────────────────
# TAB 3 — Batch Upload
# ──────────────────────────────────────────────────────────────
with tab_batch:
    st.markdown('<div class="sec">Batch Screening — Upload Excel or CSV</div>',
                unsafe_allow_html=True)
    st.markdown("""
Upload a file with **Formula** and **temperature_K** columns.
All 5 properties are predicted per row. Compounds with κ &lt; 1.0 W/mK are flagged automatically.

| Formula | temperature_K |
|---------|--------------|
| Bi2Te3  | 300          |
| PbTe    | 500          |
| CoSb3   | 700          |
""")

    # Template download
    tpl = pd.DataFrame({
        "Formula":        ["Bi2Te3","PbTe","CoSb3","Cu2Se","GeTe","SnSe","In4Se3"],
        "temperature_K":  [300, 500, 700, 300, 600, 800, 400],
    })
    st.download_button(
        "⬇ Download CSV template",
        tpl.to_csv(index=False, encoding="utf-8").encode("utf-8"),
        file_name="thermoelectric_batch_template.csv",
        mime="text/csv",
        key="dl_tpl",
    )

    uploaded = st.file_uploader(
        "Upload your CSV or Excel file",
        type=["csv","xlsx"],
        key="batch_up",
    )

    if uploaded:
        try:
            raw = (pd.read_excel(uploaded) if uploaded.name.lower().endswith(".xlsx")
                   else pd.read_csv(uploaded))
            raw.columns = [c.strip() for c in raw.columns]

            # Flexible column detection
            lc = {c.lower().replace(" ","").replace("(","").replace(")","").replace("_",""): c
                  for c in raw.columns}
            f_col = next((lc[k] for k in lc if "formula" in k), None)
            t_col = next((lc[k] for k in lc if "temp" in k), None)

            if not f_col or not t_col:
                st.error("Cannot find 'Formula' and 'temperature_K' columns. "
                         "Please download and use the template above.")
            else:
                df_in = raw[[f_col, t_col]].rename(
                    columns={f_col: "Formula", t_col: "temperature_K"})
                df_in = df_in.dropna(subset=["Formula","temperature_K"])

                st.info(f"📋 **{len(df_in)} compounds** loaded. Preview:")
                st.dataframe(df_in.head(8), use_container_width=True)

                if st.button(
                    f"⚡  Predict all 5 properties for {len(df_in)} compounds",
                    key="btn_batch",
                    disabled=(load_err is not None),
                ):
                    prog = st.progress(0, text="Starting…")
                    batch_rows = []
                    for idx, row in df_in.iterrows():
                        try:
                            p = predict_one(str(row["Formula"]), float(row["temperature_K"]),
                                            fc, sc, mdl)
                            entry = {"Formula": row["Formula"], "Temperature_K": row["temperature_K"]}
                            for prop in ORDER:
                                entry[f"{prop}_{PROP_META[prop]['unit']}"] = round(p[prop], 6)
                            entry["Priority_Flag"] = ("Priority_kappa_lt_1"
                                                      if p["Thermal Conductivity"] < 1.0 else "")
                            batch_rows.append(entry)
                            log_prediction(st.session_state["user_email"],
                                           str(row["Formula"]), float(row["temperature_K"]),
                                           p, "batch")
                        except Exception as e:
                            batch_rows.append({"Formula": row["Formula"], "Error": str(e)})
                        prog.progress((len(batch_rows)) / len(df_in),
                                      text=f"Predicted {len(batch_rows)}/{len(df_in)}…")

                    prog.empty()
                    df_out = pd.DataFrame(batch_rows)
                    n_flag = (df_out.get("Priority_Flag","") == "Priority_kappa_lt_1").sum()

                    st.success(f"✅ **{len(df_out)} predictions** · {n_flag} priority flag(s)")
                    st.dataframe(df_out, use_container_width=True)

                    st.download_button(
                        "⬇ Download batch predictions (CSV)",
                        df_out.to_csv(index=False, encoding="utf-8").encode("utf-8"),
                        file_name=f"thermo_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key="dl_batch",
                    )

        except Exception as exc:
            st.error(f"File error: {exc}")

# ──────────────────────────────────────────────────────────────
# TAB 4 — About
# ──────────────────────────────────────────────────────────────
with tab_about:
    st.markdown('<div class="sec">About the Models & Pipeline</div>', unsafe_allow_html=True)
    st.markdown("""
### Predictive Framework

Five regression models — four XGBoost and one Gradient Boosting — were selected from a
comprehensive benchmark as the best performers across an 88-feature engineered representation
of thermoelectric materials data.

### Feature Engineering (88 features)

Each chemical formula is automatically parsed and transformed into:

- **Element-count features** — stoichiometric counts for every element in the training corpus
- **Structural descriptors** — total atoms, number of elements, compositional complexity, Shannon entropy
- **Elemental fractions** — maximum and minimum element mole fractions
- **Temperature features** — T, T², log(T+1), 1/(T+1)
- **Cross-features** — T × compositional complexity, T × number of elements

All features are scaled with a pre-fitted Robust Scaler before inference.

### Electrical Conductivity Transformation

EC spans many orders of magnitude; the model predicts log₁₀(EC).  
Predictions are automatically back-transformed (10ˣ) before display.

### Priority Flag (κ < 1.0 W/mK)

Compounds with predicted thermal conductivity below 1.0 W/mK — a widely accepted
threshold for strong phonon scattering — are flagged for priority experimental validation.

### CSV Column Headers

Download columns use plain ASCII names to avoid encoding issues in Excel:

| CSV column | Meaning |
|---|---|
| `Seebeck_Coefficient_uV/K` | Seebeck coefficient in μV/K |
| `Electrical_Conductivity_S/m` | Electrical conductivity in S/m |
| `Thermal_Conductivity_W/mK` | Thermal conductivity in W/mK |
| `Power_Factor_W/mK2` | Power factor in W/mK² |
| `ZT_-` | Dimensionless figure of merit |
| `Priority_Flag` | `Priority_kappa_lt_1` if κ < 1.0 W/mK |

### Live URL
🌐 [https://thermoelectricpredictor.c2snet.org](https://thermoelectricpredictor.c2snet.org)

### Funding & Citation
**TETFund Institutional Based Research (IBR) 2024**  
Principal Investigator: **Prof. Akinola S. Olayinka**  
Edo State University Uzairue, Nigeria
akinola.olayinka@edouniversity.edu.ng |
akinola.olayinka@colororado.edu

""")

# ──────────────────────────────────────────────────────────────
# TAB 5 — Admin (password protected)
# ──────────────────────────────────────────────────────────────
with tab_admin:
    st.markdown('<div class="sec">🔒 Admin — Data Retrieval</div>', unsafe_allow_html=True)
    st.markdown(
        "This panel is for the research team to download logged predictions and user registrations."
    )

    admin_pw = st.text_input("Admin password", type="password", key="admin_pw")
    # Hash the entered password and compare — change the hash below to your own
    # Generate with: import hashlib; print(hashlib.sha256(b"YourPassword").hexdigest())
    ADMIN_HASH = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"
    # ↑ Default password is:  admin   — CHANGE THIS before deployment

    if admin_pw:
        entered_hash = hashlib.sha256(admin_pw.encode()).hexdigest()
        if entered_hash == ADMIN_HASH:
            st.success("✅ Access granted")

            st.markdown("### Prediction Log")
            df_preds = fetch_all_predictions()
            st.metric("Total predictions logged", len(df_preds))
            if not df_preds.empty:
                n_flag  = df_preds["flagged"].sum()
                n_anon  = (df_preds["user_email"] == "anonymous").sum()
                c1, c2, c3 = st.columns(3)
                c1.metric("Priority-flagged (κ<1)", int(n_flag))
                c2.metric("Anonymous queries",       int(n_anon))
                c3.metric("Registered-user queries", int(len(df_preds) - n_anon))
                st.dataframe(df_preds, use_container_width=True)
                st.download_button(
                    "⬇ Download all predictions (CSV)",
                    df_preds.to_csv(index=False, encoding="utf-8").encode("utf-8"),
                    file_name=f"all_predictions_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    key="dl_admin_preds",
                )

            st.markdown("### Registered Users")
            df_users = fetch_all_users()
            st.metric("Registered users", len(df_users))
            if not df_users.empty:
                st.dataframe(df_users, use_container_width=True)
                st.download_button(
                    "⬇ Download user list (CSV)",
                    df_users.to_csv(index=False, encoding="utf-8").encode("utf-8"),
                    file_name=f"registered_users_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    key="dl_admin_users",
                )

            # Priority compounds
            if not df_preds.empty and df_preds["flagged"].sum() > 0:
                st.markdown("### Priority Compounds (κ < 1.0 W/mK)")
                df_flag = df_preds[df_preds["flagged"] == 1][
                    ["formula","temperature","therm_cond","zt","user_email","predicted_at"]
                ].sort_values("therm_cond")
                st.dataframe(df_flag, use_container_width=True)
                st.download_button(
                    "⬇ Download priority compounds (CSV)",
                    df_flag.to_csv(index=False, encoding="utf-8").encode("utf-8"),
                    file_name=f"priority_compounds_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    key="dl_priority",
                )
        else:
            st.error("Incorrect password.")

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#8494A9;font-size:.76rem;line-height:2">
  <strong style="color:#E4EBF5">Thermoelectric Properties Predictor</strong> &nbsp;·&nbsp;
  TETFund Institutional Based Research (IBR) 2024 &nbsp;·&nbsp;
  Edo State University Uzairue &nbsp;·&nbsp;
  PI: Prof. Akinola S. Olayinka<br>
  <a href="https://thermoelectricpredictor.c2snet.org"
     style="color:#2E86AB;text-decoration:none">thermoelectricpredictor.c2snet.org</a>
</div>
""", unsafe_allow_html=True)
