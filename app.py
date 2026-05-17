import streamlit as st

# ═══════════════════════════════════════════════════════════════
#  LUXURY LOGIN + UI WRAPPER
# ═══════════════════════════════════════════════════════════════

USERS = {
    "admin":     "admin123",
    "customer1": "pass123",
    "customer2": "trade456",
}

LUXURY_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');

* { box-sizing: border-box; }

.stApp {
    background: #000000 !important;
    background-image:
        radial-gradient(ellipse at 20% 50%, #050510 0%, transparent 60%),
        radial-gradient(ellipse at 80% 20%, #0d0a00 0%, transparent 60%) !important;
}

#MainMenu, footer, header, .stDeployButton { visibility: hidden !important; display: none !important; }

.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image:
        linear-gradient(rgba(0,255,136,0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,136,0.02) 1px, transparent 1px);
    background-size: 60px 60px;
    pointer-events: none;
    z-index: 0;
}

.stTextInput > div > div > input {
    background: #080808 !important;
    border: 1px solid #1a1a1a !important;
    border-bottom: 1px solid #00ff8840 !important;
    border-radius: 2px !important;
    color: #e0e0e0 !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 15px !important;
    letter-spacing: 1px !important;
    padding: 14px 16px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #00ff88 !important;
    box-shadow: 0 0 20px rgba(0,255,136,0.1) !important;
    background: #050f07 !important;
}
.stTextInput > label {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 11px !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    color: #444 !important;
}

.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #00ff88, #00cc6a) !important;
    color: #000000 !important;
    border: none !important;
    border-radius: 2px !important;
    padding: 14px 0 !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 4px !important;
    text-transform: uppercase !important;
    cursor: pointer !important;
    box-shadow: 0 0 30px rgba(0,255,136,0.3) !important;
    margin-top: 8px !important;
    transition: all 0.3s !important;
}
.stButton > button:hover {
    box-shadow: 0 0 50px rgba(0,255,136,0.6) !important;
    transform: translateY(-1px) !important;
}

div[data-testid="metric-container"] {
    background: #080808 !important;
    border: 1px solid #111 !important;
    border-left: 2px solid #00ff8860 !important;
    border-radius: 2px !important;
    padding: 16px !important;
}
div[data-testid="metric-container"] label {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 10px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: #444 !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Orbitron', monospace !important;
    font-size: 16px !important;
    color: #00ff88 !important;
}

.stSelectbox > div > div, .stNumberInput > div > div > input {
    background: #080808 !important;
    border-color: #1a1a1a !important;
    color: #e0e0e0 !important;
    font-family: 'Rajdhani', sans-serif !important;
}

h1, h2, h3 {
    font-family: 'Orbitron', monospace !important;
    letter-spacing: 2px !important;
    color: #ffffff !important;
}

::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: #000; }
::-webkit-scrollbar-thumb { background: #00ff8830; }

.stProgress > div > div { background: #00ff88 !important; }
hr { border-color: #111 !important; }

.stSpinner > div { border-top-color: #00ff88 !important; }
</style>
"""

def show_login():
    st.markdown(LUXURY_CSS, unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align:center; padding:60px 0 30px 0;'>
        <div style='font-size:60px; filter:drop-shadow(0 0 40px rgba(0,255,136,0.7));'>⚡</div>
        <div style='font-family:Orbitron,monospace; font-size:28px; font-weight:900;
                    color:#fff; letter-spacing:8px; margin:16px 0 6px;'>
            CRYPTO <span style='color:#00ff88;'>BOT</span>
        </div>
        <div style='font-family:Rajdhani,sans-serif; font-size:11px; color:#2a2a2a;
                    letter-spacing:5px; text-transform:uppercase;'>
            v11 · Self-Evolving Regime Brain
        </div>
        <div style='width:60px; height:1px; background:linear-gradient(90deg,transparent,#00ff88,transparent);
                    margin:20px auto;'></div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("IDENTIFIER", placeholder="username")
            password = st.text_input("ACCESS KEY", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("⚡  AUTHENTICATE")
            if submitted:
                if username in USERS and USERS[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.user = username
                    st.rerun()
                else:
                    st.error("⛔ ACCESS DENIED")

    st.markdown("""
    <div style='text-align:center; margin-top:50px;'>
        <div style='font-family:Rajdhani,sans-serif; font-size:10px; color:#1a1a1a; letter-spacing:4px;'>
            SECURED · ENCRYPTED · REAL-TIME ANALYSIS
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_result(result):
    signal  = result.get("signal", "HOLD")
    sig_col = "#00ff88" if "BUY" in signal else "#ff3333" if "SELL" in signal else "#ffd700"
    sig_cls = "buy" if "BUY" in signal else "sell" if "SELL" in signal else "hold"

    # Signal Banner
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,{sig_col}08,{sig_col}15);
                border:1px solid {sig_col}40; border-top:3px solid {sig_col};
                border-radius:4px; padding:32px; text-align:center; margin:20px 0;
                box-shadow:0 0 60px {sig_col}15;'>
        <div style='font-family:Orbitron,monospace; font-size:36px; font-weight:900;
                    color:{sig_col}; letter-spacing:6px;'>{signal}</div>
        <div style='font-family:Rajdhani,sans-serif; font-size:13px; color:#444;
                    letter-spacing:3px; margin-top:8px; text-transform:uppercase;'>
            Grade: {result.get("tier","N/A")} &nbsp;·&nbsp;
            Regime: {result.get("regime","N/A")} &nbsp;·&nbsp;
            Quality: {result.get("quality",0)}/10
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Metrics
    tp  = result.get("tp_levels", {})
    pos = result.get("position",  {})
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("ENTRY",    f"{result.get('entry',0):.6f}")
    col2.metric("R:R",      f"1:{result.get('rr',0):.2f}")
    col3.metric("STRENGTH", f"{result.get('strength',0)}/100")
    col4.metric("WHALE",    f"{result.get('whale_score',0):.1f}/10")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Price Levels
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style='font-family:Orbitron,monospace; font-size:11px; color:#444;
                    letter-spacing:3px; margin-bottom:12px;'>PRICE LEVELS</div>
        """, unsafe_allow_html=True)
        levels = [
            ("ENTRY",       result.get("entry",0),        "#58a6ff"),
            ("STOP LOSS",   result.get("sl",0),           "#ff3333"),
            ("TP1",         tp.get("TP1",0),              "#00ff88"),
            ("TP2",         tp.get("TP2","N/A"),          "#7ee787"),
            ("TP3",         tp.get("TP3","N/A"),          "#56d364"),
        ]
        for label, val, col in levels:
            val_str = f"{val:.6f}" if isinstance(val, float) else str(val)
            st.markdown(f"""
            <div style='display:flex; justify-content:space-between; align-items:center;
                        padding:10px 0; border-bottom:1px solid #0f0f0f;'>
                <span style='font-family:Rajdhani,sans-serif; font-size:11px;
                             color:#333; letter-spacing:2px;'>{label}</span>
                <span style='font-family:Orbitron,monospace; font-size:13px;
                             color:{col}; font-weight:700;'>{val_str}</span>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='font-family:Orbitron,monospace; font-size:11px; color:#444;
                    letter-spacing:3px; margin-bottom:12px;'>ANALYSIS</div>
        """, unsafe_allow_html=True)
        analysis = [
            ("REGIME",      result.get("regime","N/A"),         "#bc8cff"),
            ("4H BIAS",     result.get("htf_bias","N/A"),       "#00ff88" if result.get("htf_bias")=="BULL" else "#ff3333" if result.get("htf_bias")=="BEAR" else "#ffd700"),
            ("STRUCTURE",   result.get("structure","N/A"),      "#58a6ff"),
            ("TRANSITION",  result.get("transition","N/A"),     "#8b949e"),
            ("ENTRY TYPE",  result.get("entry_type","N/A"),     "#ffd700"),
        ]
        for label, val, col in analysis:
            st.markdown(f"""
            <div style='display:flex; justify-content:space-between; align-items:center;
                        padding:10px 0; border-bottom:1px solid #0f0f0f;'>
                <span style='font-family:Rajdhani,sans-serif; font-size:11px;
                             color:#333; letter-spacing:2px;'>{label}</span>
                <span style='font-family:Rajdhani,sans-serif; font-size:13px;
                             color:{col}; font-weight:700;'>{val}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Scores + Position
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style='font-family:Orbitron,monospace; font-size:11px; color:#444;
                    letter-spacing:3px; margin-bottom:12px;'>SCORES</div>
        """, unsafe_allow_html=True)
        scores = [
            ("MARKET POWER",  f"{result.get('market_power',0):.0f}/100", "#00ff88"),
            ("WHALE SCORE",   f"{result.get('whale_score',0):.1f}/10",   "#00ff88"),
            ("ADDON SCORE",   f"{result.get('addon_score',0):.1f}/10",   "#00ff88"),
            ("QUALITY",       f"{result.get('quality',0):.1f}/10",       "#ffd700"),
            ("LSTM SIGMA",    f"±{result.get('lstm_sigma',0):.5f}",      "#8b949e"),
        ]
        for label, val, col in scores:
            st.markdown(f"""
            <div style='display:flex; justify-content:space-between; align-items:center;
                        padding:10px 0; border-bottom:1px solid #0f0f0f;'>
                <span style='font-family:Rajdhani,sans-serif; font-size:11px;
                             color:#333; letter-spacing:2px;'>{label}</span>
                <span style='font-family:Orbitron,monospace; font-size:13px;
                             color:{col}; font-weight:700;'>{val}</span>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='font-family:Orbitron,monospace; font-size:11px; color:#444;
                    letter-spacing:3px; margin-bottom:12px;'>POSITION</div>
        """, unsafe_allow_html=True)
        positions = [
            ("BALANCE",    f"${pos.get('balance',0):,.2f}",       "#e6edf3"),
            ("RISK %",     f"{pos.get('risk_pct',0):.3f}%",       "#ff3333"),
            ("RISK AMT",   f"${pos.get('risk_amt',0):.2f}",       "#ff3333"),
            ("POSITION",   f"${pos.get('pos_usdt',0):,.2f}",      "#00ff88"),
            ("UNITS",      f"{pos.get('pos_units',0):.6f}",       "#58a6ff"),
        ]
        for label, val, col in positions:
            st.markdown(f"""
            <div style='display:flex; justify-content:space-between; align-items:center;
                        padding:10px 0; border-bottom:1px solid #0f0f0f;'>
                <span style='font-family:Rajdhani,sans-serif; font-size:11px;
                             color:#333; letter-spacing:2px;'>{label}</span>
                <span style='font-family:Orbitron,monospace; font-size:13px;
                             color:{col}; font-weight:700;'>{val}</span>
            </div>
            """, unsafe_allow_html=True)

    # TP Units
    if pos.get("tp1_units", 0) > 0:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("TP1 UNITS", f"{pos.get('tp1_units',0):.6f}")
        c2.metric("TP2 UNITS", f"{pos.get('tp2_units',0):.6f}" if pos.get('tp2_units',0) > 0 else "N/A")
        c3.metric("TP3 UNITS", f"{pos.get('tp3_units',0):.6f}" if pos.get('tp3_units',0) > 0 else "N/A")

    # Addon Scores
    addon = result.get("addon_score", 0)
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='font-family:Orbitron,monospace; font-size:11px; color:#444;
                letter-spacing:3px; margin-bottom:12px;'>ADDON MODULES</div>
    """, unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("ORDER BLOCK",  result.get("ptp_tp1_type","N/A"))
    c2.metric("ADDON GATE",   result.get("addon_gate","N/A"))
    c3.metric("ADDON LABEL",  result.get("addon_label","N/A"))
    c4.metric("TP1 TYPE",     result.get("ptp_tp1_type","N/A"))

    # Final Action
    action_map = {
        "STRONG BUY":  ("⚡ EXECUTE STRONG BUY",  "#00ff88"),
        "BUY":         ("✅ EXECUTE BUY ORDER",    "#00ff88"),
        "STRONG SELL": ("⚡ EXECUTE STRONG SELL",  "#ff3333"),
        "SELL":        ("✅ EXECUTE SELL ORDER",   "#ff3333"),
        "HOLD":        ("⏳ HOLD — WAIT",          "#ffd700"),
    }
    action_text, action_col = action_map.get(signal, ("⏳ HOLD", "#ffd700"))
    st.markdown(f"""
    <div style='background:{action_col}08; border:1px solid {action_col}40;
                border-top:3px solid {action_col}; border-radius:4px;
                padding:24px; text-align:center; margin:24px 0;
                box-shadow:0 0 40px {action_col}10;'>
        <div style='font-family:Orbitron,monospace; font-size:18px; font-weight:900;
                    color:{action_col}; letter-spacing:4px;'>{action_text}</div>
        <div style='font-family:Rajdhani,sans-serif; font-size:13px; color:#333;
                    letter-spacing:2px; margin-top:8px;'>
            SL: {result.get("sl",0):.6f} &nbsp;|&nbsp;
            TP1: {tp.get("TP1",0):.6f} &nbsp;|&nbsp;
            R:R 1:{result.get("rr",0):.2f}
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_dashboard():
    st.markdown(LUXURY_CSS, unsafe_allow_html=True)
    user = st.session_state.user

    # Header
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"""
        <div style='padding:8px 0 16px;'>
            <span style='font-family:Orbitron,monospace; font-size:20px;
                         font-weight:900; color:#fff; letter-spacing:4px;'>
                ⚡ CRYPTO <span style='color:#00ff88;'>BOT</span>
                <span style='font-size:11px; color:#333; letter-spacing:3px;'>v11</span>
            </span>
            <span style='font-family:Rajdhani,sans-serif; font-size:11px;
                         color:#00ff88; letter-spacing:2px; margin-left:12px;'>● LIVE</span>
            <div style='font-family:Rajdhani,sans-serif; font-size:12px;
                        color:#2a2a2a; letter-spacing:2px; margin-top:4px;'>
                WELCOME BACK — <span style='color:#444;'>{user.upper()}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("LOGOUT"):
            st.session_state.logged_in = False
            st.rerun()

    st.markdown("<hr style='border-color:#0f0f0f; margin:0 0 20px;'>", unsafe_allow_html=True)

    # Input
    st.markdown("""
    <div style='font-family:Orbitron,monospace; font-size:11px; color:#444;
                letter-spacing:3px; margin-bottom:16px;'>MARKET ANALYSIS</div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        symbol = st.text_input("TRADING PAIR", value="XRP/USDT", placeholder="BTC/USDT, ETH/USDT...")
    with col2:
        balance = st.number_input("BALANCE (USDT)", min_value=10.0, value=1000.0, step=100.0)
    with col3:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        run = st.button("⚡  RUN ANALYSIS")

    if run:
        with st.spinner("🧠 Regime Brain Analyzing..."):
            try:
                result = run_bot(symbol, balance)
                # ---- یہ تین لائنیں شامل کی ہیں ----
                st.write("🔎 Result keys:", list(result.keys()) if result else "None")
                if result and result.get("signal"):
                    show_result(result)
                else:
                    st.error("⛔ Bot returned no result or HOLD with zero values")
            except Exception as e:
                st.error(f"⛔ Error: {str(e)}")
                st.exception(e)   # پوری traceback دکھائے گا

# ═══════════════════════════════════════════════════════════════
#  PASTE YOUR ENTIRE ORIGINAL V11 CODE BELOW THIS LINE
#  (Everything from your original file — with required changes!)
# ═══════════════════════════════════════════════════════════════

# ↓↓↓ MODIFIED V11 CODE STARTS HERE ↓↓↓

#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║  CRYPTO TRADING BOT  v11  ·  Self-Evolving Regime Brain                        ║
║  ─────────────────────────────────────────────────────────────────────────────  ║
║  RegimeBrain×9 · Adaptive Router · Markov Memory · MetaFusion · AdaptiveTP     ║
║  ─────────────────────────────────────────────────────────────────────────────  ║
║  Built on v10 (FIX-A/B/C preserved). All regime logic added ON TOP.            ║
║  FIXED: TensorFlow replaced with sklearn ensemble (Streamlit Cloud Free Tier) ║
╚══════════════════════════════════════════════════════════════════════════════════╝
"""

# ── Standard library ──────────────────────────────────────────────────────────
import os, sys, time, json, queue, hashlib, pickle, traceback, warnings, threading
import concurrent.futures
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

warnings.filterwarnings("ignore")

# ── Third-party ───────────────────────────────────────────────────────────────
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches

# Scikit-learn imports (replace TensorFlow/Keras)
from sklearn.ensemble import GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler
import joblib

import ccxt
import ta

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                        TERMINAL COLOR HELPERS                              ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

class C:
    RST  = "\033[0m";  BOLD = "\033[1m";  DIM  = "\033[2m"
    RED  = "\033[91m"; GREEN= "\033[92m"; YEL  = "\033[93m"
    BLUE = "\033[94m"; MAG  = "\033[95m"; CYAN = "\033[96m"
    WHITE= "\033[97m"; GREY = "\033[90m"

    @staticmethod
    def r(s):    return f"{C.RED}{s}{C.RST}"
    @staticmethod
    def g(s):    return f"{C.GREEN}{s}{C.RST}"
    @staticmethod
    def y(s):    return f"{C.YEL}{s}{C.RST}"
    @staticmethod
    def b(s):    return f"{C.BLUE}{s}{C.RST}"
    @staticmethod
    def m(s):    return f"{C.MAG}{s}{C.RST}"
    @staticmethod
    def c(s):    return f"{C.CYAN}{s}{C.RST}"
    @staticmethod
    def w(s):    return f"{C.WHITE}{C.BOLD}{s}{C.RST}"
    @staticmethod
    def dim(s):  return f"{C.DIM}{s}{C.RST}"


def section(title, icon=""):
    sep = C.dim("┄" * max(0, 66 - len(title)))
    return f"\n {C.CYAN}{C.BOLD}{icon}  {title} {sep}{C.RST}"

def row(label, value, indent=4, label_w=20):
    return f"{' '*indent}{C.dim(f'{label:<{label_w}}')} {value}"


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                            CONFIGURATION                                   ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

COIN_SYMBOL       = "XRP/USDT"
MIN_RISK_REWARD   = 1.5
TIMEFRAME_MAIN    = "1h"
TIMEFRAME_HIGHER  = "4h"
MODEL_CACHE_DIR   = "/tmp/model_cache_v11"
JOURNAL_FILE      = "/tmp/trade_journal_v11.json"
REGIME_MEMORY_FILE= "/tmp/regime_memory_v11.json"
USE_MODEL_CACHE   = True
ACCOUNT_BALANCE   = 1_000.0
RISK_PER_TRADE    = 0.01            # 1%

# ── Whale ─────────────────────────────────────────────────────────────────────
WHALE_VOL_THRESHOLD  = 3.0
WHALE_PRICE_MOVE_MIN = 0.003
ORDER_BOOK_DEPTH     = 20
WALL_MULT            = 5.0
WHALE_SIZE_WEIGHT    = 0.15

# ── Structure ─────────────────────────────────────────────────────────────────
STRUCTURE_LOOKBACK = 75

# ── Addon ─────────────────────────────────────────────────────────────────────
ADDON_WEIGHTS = {
    "order_block":     0.30,
    "breakout_retest": 0.25,
    "liquidity_grab":  0.25,
    "oi_funding":      0.20,
}
ADDON_HARD_BLOCK     = 2.0
ADDON_SOFT_DOWNGRADE = 3.5
ADDON_SIZE_WEIGHT    = 0.40
ADDON_UNAVAIL_FLOOR  = 3.0

# ── Sklearn Ensemble ──────────────────────────────────────────────────────────
SKLEARN_N_MODELS = 3
SEQUENCE_LENGTH = 30      # Reduced from 60 for memory optimization

# ── Probability TP Engine ─────────────────────────────────────────────────────
PTP_ATR_MIN      = 0.3
PTP_ATR_MAX      = 5.0
PTP_MIN_SCORE    = 4.0
PTP_ROUND_DIGS   = 2

# ── Regime Brain (new) ────────────────────────────────────────────────────────
REGIME_MIN_SAMPLES   = 15
REGIME_HURST_WINDOW  = 50
REGIME_TRANSITION_LOOKBACK = 20
TRAIL_ACTIVATION_ATR = 1.0
TRAIL_DISTANCE_ATR   = 1.5
QUALITY_SCORE_FLOOR  = 6.0

# ── Futures exchanges ─────────────────────────────────────────────────────────
FUTURES_EXCHANGES = ["binance", "bybit", "okx"]

os.makedirs(MODEL_CACHE_DIR, exist_ok=True)


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                      BOOT BANNER  (no TF)                                  ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def _boot_banner():
    hw = C.y("✓ CPU mode – sklearn ensemble")
    print(f"""
{C.CYAN}{C.BOLD}╔══════════════════════════════════════════════════════════════════════════╗
║  CRYPTO BOT v11  ·  Self-Evolving Regime Brain (sklearn)                  ║
║  RegimeBrain×9 · Adaptive Router · Markov Memory                           ║
║  MetaFusion · AdaptiveTP · 11-Panel Chart                                  ║
╚══════════════════════════════════════════════════════════════════════════╝{C.RST}
  {hw}
  {C.dim('TF:')} {TIMEFRAME_MAIN}  {C.dim('HTF:')} {TIMEFRAME_HIGHER}  {C.dim('Balance:')} ${ACCOUNT_BALANCE:,.0f}  {C.dim('Risk:')} {RISK_PER_TRADE*100:.1f}%
""")

_boot_banner()


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                          TRADE JOURNAL  (v10 — Self-Improvement)          ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

class TradeJournal:
    MIN_SAMPLES = 20

    def __init__(self, path: str = JOURNAL_FILE):
        self.path = path
        self._data: dict = self._load()

    def _load(self) -> dict:
        try:
            with open(self.path) as f:
                return json.load(f)
        except Exception:
            return {"trades": [], "stats": {}, "version": "v10"}

    def _save(self):
        try:
            with open(self.path, "w") as f:
                json.dump(self._data, f, indent=2, default=str)
        except Exception as e:
            print(C.y(f"  ⚠ Journal save fail: {e}"))

    def record(self, entry: float, signal: str, sl: float, tp1: float,
               tp2, tp3, regime: str, addon_score: float,
               strength: float, whale_score: float, symbol: str = COIN_SYMBOL):
        trade = {
            "id":          len(self._data["trades"]) + 1,
            "timestamp":   datetime.now(timezone.utc).isoformat(),
            "symbol":      symbol,
            "signal":      signal,
            "entry":       round(entry, 6),
            "sl":          round(sl, 6),
            "tp1":         round(tp1, 6),
            "tp2":         round(tp2, 6) if tp2 else None,
            "tp3":         round(tp3, 6) if tp3 else None,
            "regime":      regime,
            "addon_score": round(addon_score, 2),
            "strength":    round(strength, 1),
            "whale_score": round(whale_score, 1),
            "outcome":     "OPEN",
            "exit_price":  None,
            "pnl_pct":     None,
        }
        self._data["trades"].append(trade)
        self._save()
        print(C.dim(f"  📓 Trade #{trade['id']} recorded in journal"))
        return trade["id"]

    def update_outcome(self, trade_id: int, outcome: str, exit_price: float):
        for t in self._data["trades"]:
            if t["id"] == trade_id:
                t["outcome"]    = outcome
                t["exit_price"] = round(exit_price, 6)
                pnl_dir         = 1 if "BUY" in t["signal"] else -1
                t["pnl_pct"]    = round((exit_price - t["entry"]) / t["entry"] * 100 * pnl_dir, 3)
                self._data["trades"][self._data["trades"].index(t)] = t
                self._save()
                col = C.g if t["pnl_pct"] > 0 else C.r
                print(col(f"  📓 Trade #{trade_id} closed → {outcome}  PnL:{t['pnl_pct']:+.2f}%"))
                return
        print(C.y(f"  ⚠ Trade #{trade_id} not found in journal"))

    def compute_stats(self) -> dict:
        closed = [t for t in self._data["trades"] if t["outcome"] != "OPEN"]
        n      = len(closed)
        if n < 1:
            return {"n": 0}

        wins    = [t for t in closed if t["pnl_pct"] is not None and t["pnl_pct"] > 0]
        win_r   = len(wins) / n
        tp1_hits = sum(1 for t in closed if t["outcome"] in ("TP1","TP2","TP3")) / max(n, 1)
        tp2_hits = sum(1 for t in closed if t["outcome"] in ("TP2","TP3"))       / max(n, 1)
        tp3_hits = sum(1 for t in closed if t["outcome"] == "TP3")               / max(n, 1)

        regimes = {}
        for t in closed:
            r = t.get("regime", "NORMAL")
            regimes.setdefault(r, {"n": 0, "wins": 0})
            regimes[r]["n"] += 1
            if t.get("pnl_pct", 0) > 0:
                regimes[r]["wins"] += 1
        regime_wr = {r: round(v["wins"]/v["n"], 3) for r, v in regimes.items() if v["n"] >= 3}

        sigs = {}
        for t in closed:
            s = t.get("signal", "HOLD")
            sigs.setdefault(s, {"n": 0, "wins": 0})
            sigs[s]["n"] += 1
            if t.get("pnl_pct", 0) > 0:
                sigs[s]["wins"] += 1
        sig_wr = {s: round(v["wins"]/v["n"], 3) for s, v in sigs.items() if v["n"] >= 3}

        avg_pnl = np.mean([t["pnl_pct"] for t in closed if t["pnl_pct"] is not None])

        stats = {
            "n":          n,
            "win_rate":   round(win_r, 3),
            "avg_pnl":    round(float(avg_pnl), 3),
            "tp1_rate":   round(tp1_hits, 3),
            "tp2_rate":   round(tp2_hits, 3),
            "tp3_rate":   round(tp3_hits, 3),
            "regime_wr":  regime_wr,
            "signal_wr":  sig_wr,
        }
        self._data["stats"] = stats
        self._save()
        return stats

    def adaptive_signal_threshold(self, signal: str, default: float = 5.0) -> float:
        stats = self._data.get("stats", {})
        n     = stats.get("n", 0)
        if n < self.MIN_SAMPLES:
            return default

        sig_wr = stats.get("signal_wr", {})
        key    = "BUY" if "BUY" in signal else "SELL" if "SELL" in signal else signal
        wr     = sig_wr.get(key, sig_wr.get(signal, None))

        if wr is None:
            return default

        adj = 0.0
        if   wr < 0.40: adj = +default * 0.10
        elif wr > 0.65: adj = -default * 0.10

        return round(max(2.0, default + adj), 2)

    def print_summary(self):
        stats = self.compute_stats()
        if stats.get("n", 0) < 1:
            print(C.dim("  📓 Journal: no closed trades yet"))
            return
        print(section("Trade Journal  (Self-Improvement)", "📓"))
        print(row("Closed trades",  C.c(str(stats["n"]))))
        col = C.g if stats["win_rate"] >= 0.55 else C.y if stats["win_rate"] >= 0.45 else C.r
        print(row("Win Rate",       col(f"{stats['win_rate']:.1%}")))
        print(row("Avg PnL",        (C.g if stats["avg_pnl"] > 0 else C.r)(f"{stats['avg_pnl']:+.2f}%")))
        print(row("TP1 Hit Rate",   C.g(f"{stats['tp1_rate']:.1%}")))
        print(row("TP2 Hit Rate",   C.dim(f"{stats['tp2_rate']:.1%}")))
        print(row("TP3 Hit Rate",   C.dim(f"{stats['tp3_rate']:.1%}")))
        if stats.get("regime_wr"):
            for r, wr in stats["regime_wr"].items():
                col2 = C.g if wr >= 0.55 else C.y if wr >= 0.45 else C.r
                print(row(f"  {r}", col2(f"{wr:.1%}")))


_journal = TradeJournal(JOURNAL_FILE)


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                         MARKET DATA ENGINE                                 ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

class MarketDataEngine:
    EXCHANGES = ["binance", "bybit", "okx", "kucoin", "gateio", "mexc"]

    def __init__(self, workers: int = 8):
        self.pool: dict = {}
        for name in self.EXCHANGES:
            try:
                self.pool[name] = getattr(ccxt, name)({"enableRateLimit": True})
            except Exception:
                pass
        self._scores   = {ex: 1.0 for ex in self.pool}
        self._cache: dict    = {}
        self._cache_ts: dict = {}
        self._ttl      = 120
        self._exec     = concurrent.futures.ThreadPoolExecutor(max_workers=workers)

    def fetch(self, symbol: str, timeframe: str = "1h",
              timeout: int = 12, need: int = 2) -> pd.DataFrame:
        key = f"{symbol}_{timeframe}"
        now = time.time()
        if key in self._cache and now - self._cache_ts.get(key, 0) < self._ttl:
            print(C.dim(f"  ⚡ cache hit [{symbol} {timeframe}]"))
            return self._cache[key]

        print(section(f"Fetching {symbol} [{timeframe}]", "📡"))
        q, stop = queue.Queue(), threading.Event()
        limit   = 500 if timeframe in ("4h", "1d") else 1500

        def _one(name: str):
            if stop.is_set(): return
            try:
                t0    = time.time()
                ohlcv = self.pool[name].fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
                df    = pd.DataFrame(ohlcv, columns=["timestamp","open","high","low","close","volume"])
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
                df["_src"]      = name
                elapsed = time.time() - t0
                if len(df) >= 60:
                    self._scores[name] = max(0.1, 1.0 / max(elapsed, 0.01))
                    q.put(df)
                    print(C.g(f"    ✓ {name.upper():<8}") + C.dim(f" {len(df)} candles ({elapsed:.1f}s)"))
                else:
                    print(C.y(f"    ⚠ {name.upper():<8} only {len(df)} candles"))
            except Exception as e:
                self._scores[name] = self._scores.get(name, 1.0) * 0.8
                print(C.r(f"    ✗ {name.upper():<8}") + C.dim(f" {str(e)[:55]}"))

        sorted_ex = sorted(self.pool, key=lambda x: self._scores.get(x, 1.0), reverse=True)
        threads   = [threading.Thread(target=_one, args=(ex,), daemon=True) for ex in sorted_ex[:5]]
        for t in threads: t.start()

        results, deadline = [], time.time() + timeout
        while time.time() < deadline:
            try:
                results.append(q.get(timeout=0.5))
                if len(results) >= need:
                    stop.set()
                    break
            except queue.Empty:
                if all(not t.is_alive() for t in threads): break

        if not results:
            raise RuntimeError(f"All exchanges failed for {symbol} [{timeframe}]")

        merged = self._merge(results)
        self._cache[key]    = merged
        self._cache_ts[key] = now
        return merged

    def get_spread(self, symbol: str) -> dict:
        spreads = {}
        for name in list(self.pool)[:3]:
            try:
                t = self.pool[name].fetch_ticker(symbol)
                if t.get("bid") and t.get("ask"):
                    spreads[name] = {
                        "bid": t["bid"], "ask": t["ask"],
                        "spread_pct": round((t["ask"] - t["bid"]) / t["bid"] * 100, 5),
                    }
            except Exception:
                continue
        return spreads

    def cleanup(self):
        self._exec.shutdown(wait=False)

    def _merge(self, frames: list) -> pd.DataFrame:
        combined = pd.concat(frames, ignore_index=True).sort_values("timestamp")
        n_src    = combined["_src"].nunique() if "_src" in combined.columns else 1

        if n_src > 1:
            def _agg(g: pd.DataFrame) -> pd.Series:
                vol = g["volume"].values
                w   = vol if vol.sum() > 0 else np.ones(len(g))
                return pd.Series({
                    "timestamp":      g["timestamp"].iloc[0],
                    "open":           np.average(g["open"].values,  weights=w),
                    "high":           np.average(g["high"].values,  weights=w),
                    "low":            np.average(g["low"].values,   weights=w),
                    "close":          np.average(g["close"].values, weights=w),
                    "volume":         float(np.median(vol)),
                    "source":         "multi_vwap",
                    "volume_quality": "multi_median",
                    "n_sources":      len(g),
                })
            agg = combined.groupby("timestamp", sort=True).apply(_agg).reset_index(drop=True)
        else:
            combined = combined.drop_duplicates(subset=["timestamp"], keep="last")
            combined = combined.rename(columns={"_src": "source"}) if "_src" in combined.columns else combined
            if "source" not in combined.columns: combined["source"] = "single"
            combined["volume_quality"] = "single"
            combined["n_sources"]      = 1
            agg = combined.reset_index(drop=True)

        for col in ["open", "high", "low", "close", "volume"]:
            agg[col] = agg[col].interpolate(method="linear").ffill().bfill()

        q1, q3 = agg["volume"].quantile(0.25), agg["volume"].quantile(0.75)
        cap     = q3 + 5.0 * (q3 - q1)
        clipped = int((agg["volume"] > cap).sum())
        agg["volume"] = agg["volume"].clip(upper=cap)
        if clipped:
            print(C.y(f"  🔧 Volume clipped {clipped} outlier(s) (>{cap:.2f})"))

        print(C.dim(f"  📊 Merged: {len(agg)} candles  sources:{n_src}  vol:{agg['volume_quality'].iloc[0]}"))
        return agg.reset_index(drop=True)


_engine = MarketDataEngine(workers=8)


def get_data(symbol: str = COIN_SYMBOL, tf: str = "1h") -> pd.DataFrame:
    try:
        df = _engine.fetch(symbol, tf, timeout=12, need=2)
        if df.empty or len(df) < 60:
            raise ValueError("Insufficient candles")
        return df
    except Exception as e:
        print(C.y(f"  ⚠ Primary fetch failed: {e} → fallback"))
        return _fallback_fetch(symbol, tf)


def _fallback_fetch(symbol: str, tf: str) -> pd.DataFrame:
    limit = 500 if tf in ("4h", "1d") else 1500
    for name in MarketDataEngine.EXCHANGES:
        try:
            ex    = getattr(ccxt, name)({"enableRateLimit": True})
            ohlcv = ex.fetch_ohlcv(symbol, timeframe=tf, limit=limit)
            df    = pd.DataFrame(ohlcv, columns=["timestamp","open","high","low","close","volume"])
            df["timestamp"]      = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
            df["source"]         = name
            df["volume_quality"] = "single"
            df["n_sources"]      = 1
            df = df.dropna()
            if len(df) >= 60:
                print(C.g(f"  ✓ Fallback {name}: {len(df)} candles"))
                return df
        except Exception:
            continue
    raise RuntimeError(f"All exchanges failed for {symbol} [{tf}]")


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                   TECHNICAL INDICATORS  (v10 + MFI)                        ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def _supertrend(df: pd.DataFrame, period=10, mult=3.0) -> pd.DataFrame:
    atr   = ta.volatility.AverageTrueRange(df["high"], df["low"], df["close"],
                                           window=period, fillna=True).average_true_range()
    hl2   = (df["high"] + df["low"]) / 2
    upper = (hl2 + mult * atr).values
    lower = (hl2 - mult * atr).values
    close = df["close"].values
    n     = len(close)
    fu, fl, st, di = upper.copy(), lower.copy(), np.zeros(n), np.ones(n)
    for i in range(1, n):
        fu[i] = upper[i] if upper[i] < fu[i-1] or close[i-1] > fu[i-1] else fu[i-1]
        fl[i] = lower[i] if lower[i] > fl[i-1] or close[i-1] < fl[i-1] else fl[i-1]
        st[i] = fu[i] if (st[i-1]==fu[i-1] and close[i]<=fu[i]) else \
                (fl[i] if (st[i-1]==fu[i-1] and close[i]>fu[i]) else
                (fl[i] if close[i]>=fl[i] else fu[i]))
        di[i] = -1 if st[i] == fu[i] else 1
    df["Supertrend"]   = st
    df["ST_Direction"] = di
    return df


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    print(section("Computing Indicators", "📊"))

    df["EMA_9"]   = df["close"].ewm(span=9,   adjust=False).mean()
    df["SMA_20"]  = df["close"].rolling(20).mean()
    df["EMA_50"]  = df["close"].ewm(span=50,  adjust=False).mean()
    df["EMA_200"] = df["close"].ewm(span=200, adjust=False).mean()

    typical   = (df["high"] + df["low"] + df["close"]) / 3
    df["VWAP"] = (typical * df["volume"]).cumsum() / df["volume"].cumsum().replace(0, np.nan)

    df["RSI_14"] = ta.momentum.RSIIndicator(df["close"], window=14, fillna=True).rsi()

    try:
        df["MFI_14"] = ta.volume.MFIIndicator(
            df["high"], df["low"], df["close"], df["volume"], window=14, fillna=True
        ).money_flow_index()
    except Exception:
        df["MFI_14"] = df["RSI_14"]

    macd              = ta.trend.MACD(df["close"], window_slow=26, window_fast=12, fillna=True)
    df["MACD"]        = macd.macd()
    df["MACD_Signal"] = macd.macd_signal()
    df["MACD_Hist"]   = df["MACD"] - df["MACD_Signal"]

    df["ATR"] = ta.volatility.AverageTrueRange(
        df["high"], df["low"], df["close"], window=14, fillna=True
    ).average_true_range()

    atr_arr = df["ATR"].values
    wp      = min(100, len(atr_arr))
    ap      = np.full(len(atr_arr), 50.0)
    for i in range(wp, len(atr_arr)):
        ap[i] = np.sum(atr_arr[i-wp:i] < atr_arr[i]) / wp * 100
    df["ATR_Percentile"] = ap

    df["OBV"] = ta.volume.OnBalanceVolumeIndicator(
        df["close"], df["volume"], fillna=True).on_balance_volume()

    bb = ta.volatility.BollingerBands(df["close"], window=20, window_dev=2, fillna=True)
    df["BB_Upper"] = bb.bollinger_hband()
    df["BB_Lower"] = bb.bollinger_lband()
    df["BB_Mid"]   = bb.bollinger_mavg()
    df["BB_Width"] = ((df["BB_Upper"] - df["BB_Lower"]) / df["BB_Mid"]).fillna(0)

    adx_i         = ta.trend.ADXIndicator(df["high"], df["low"], df["close"], window=14, fillna=True)
    df["ADX"]     = adx_i.adx()
    df["ADX_Pos"] = adx_i.adx_pos()
    df["ADX_Neg"] = adx_i.adx_neg()

    stoch         = ta.momentum.StochasticOscillator(
        df["high"], df["low"], df["close"], window=14, smooth_window=3, fillna=True)
    df["Stoch_K"] = stoch.stoch()
    df["Stoch_D"] = stoch.stoch_signal()

    atr_vol = (df["ATR"] / df["close"].rolling(20).mean()).fillna(0).clip(0, 1)
    df["Dynamic_RSI_Lower"] = 30 + atr_vol * 10
    df["Dynamic_RSI_Upper"] = 70 - atr_vol * 10

    df["Williams_R"] = ta.momentum.WilliamsRIndicator(
        df["high"], df["low"], df["close"], lbp=14, fillna=True).williams_r()
    df["CCI"]        = ta.trend.CCIIndicator(
        df["high"], df["low"], df["close"], window=20, fillna=True).cci()

    df["Volume_MA20"]      = df["volume"].rolling(20).mean().bfill()
    vol_arr                = df["volume"].values
    roll100                = min(100, len(vol_arr))
    vp_arr                 = np.full(len(vol_arr), 50.0)
    for i in range(roll100, len(vol_arr)):
        vp_arr[i] = np.sum(vol_arr[i-roll100:i] < vol_arr[i]) / roll100 * 100
    df["Volume_Percentile"] = vp_arr
    df["Volume_Ratio"]      = (df["volume"] / df["Volume_MA20"].replace(0, np.nan)).fillna(1.0).clip(0, 10)
    df["Volume_Delta"]      = np.where(df["close"] >= df["open"], df["volume"], -df["volume"])
    df["CVD_20"]            = df["Volume_Delta"].rolling(20).sum()

    df = _supertrend(df)
    df = df.dropna(subset=["EMA_200", "ADX", "ATR"]).reset_index(drop=True)

    last = df.iloc[-1]
    print(C.dim(f"  Shape: {df.shape}"))
    print(row("ADX",    C.c(f"{last['ADX']:.1f}")))
    print(row("MFI",    C.dim(f"{last['MFI_14']:.1f}")))
    print(row("BB_W",   C.dim(f"{last['BB_Width']:.4f}")))
    print(row("ST",     C.g("BULL") if last["ST_Direction"] == 1 else C.r("BEAR")))
    return df


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                  PROBABILITY TP ENGINE  (v10 — FIXED)                      ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def _default_ai() -> dict:
    return {
        "cancel_reason":        "N/A",
        "rr_ratio":             0.0,
        "sl_dist_pct":          0.0,
        "sl_mult_used":         0.0,
        "tp1_score":            0.0,
        "tp1_type":             "N/A",
        "tp1_pct":              0.0,
        "tp2_pct":              None,
        "tp3_pct":              None,
        "vol_zone":             "N/A",
        "regime":               "N/A",
        "levels_scored":        [],
        "nearest_support":      None,
        "nearest_resistance":   None,
        "min_rr_used":          MIN_RISK_REWARD,
    }


class ProbabilityTPEngine:
    FIB_RATIOS  = [0.236, 0.382, 0.500, 0.618, 0.786, 1.000, 1.272, 1.618]
    ROUND_STEPS = [0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 500.0]

    def _swing_levels(self, df: pd.DataFrame, lookback: int = 75) -> list:
        rec  = df.tail(lookback)
        hi, lo = rec["high"].values, rec["low"].values
        lvls = []
        for i in range(3, len(rec) - 3):
            if hi[i] >= max(hi[max(0,i-3):i]) and hi[i] >= max(hi[i+1:i+4]):
                lvls.append({"price": float(hi[i]), "type": "SWING_HIGH", "base_score": 3.0})
            if lo[i] <= min(lo[max(0,i-3):i]) and lo[i] <= min(lo[i+1:i+4]):
                lvls.append({"price": float(lo[i]), "type": "SWING_LOW",  "base_score": 3.0})
        return lvls

    def _ob_edges(self, obs: list) -> list:
        lvls = []
        for o in obs:
            lvls.append({"price": float(o["ob_high"]), "type": "OB_HIGH", "base_score": 4.0})
            lvls.append({"price": float(o["ob_low"]),  "type": "OB_LOW",  "base_score": 4.0})
        return lvls

    def _eq_levels(self, eq_hi: list, eq_lo: list) -> list:
        lvls = []
        for p in eq_hi:
            lvls.append({"price": float(p), "type": "EQ_HIGH", "base_score": 3.5})
        for p in eq_lo:
            lvls.append({"price": float(p), "type": "EQ_LOW",  "base_score": 3.5})
        return lvls

    def _fibonacci_levels(self, df: pd.DataFrame, lookback: int = 100) -> list:
        rec    = df.tail(lookback)
        hi_val = float(rec["high"].max())
        lo_val = float(rec["low"].min())
        rng    = hi_val - lo_val
        if rng < 1e-10:
            return []
        lvls = []
        for r in self.FIB_RATIOS:
            score = 2.5 if r in (0.382, 0.500, 0.618) else 1.5
            lvls.append({"price": round(lo_val + r * rng, 8), "type": f"FIB_{r:.3f}", "base_score": score})
            lvls.append({"price": round(hi_val - r * rng, 8), "type": f"FIB_INV_{r:.3f}", "base_score": score})
        return lvls

    def _round_numbers(self, price: float, atr: float) -> list:
        lvls = []
        step = next((s for s in self.ROUND_STEPS if s > atr * 0.2), 1.0)
        p0   = round(price / step) * step
        for mult in range(-15, 16):
            lvl = round(p0 + mult * step, 8)
            if lvl > 0:
                lvls.append({"price": lvl, "type": "ROUND", "base_score": 2.0})
        return lvls

    def _prev_day_hl(self, df: pd.DataFrame) -> list:
        if "timestamp" not in df.columns or len(df) < 48:
            return []
        rec = df.tail(48)
        day_slice = rec.iloc[:-24] if len(rec) >= 48 else rec
        if day_slice.empty:
            return []
        return [
            {"price": float(day_slice["high"].max()), "type": "PREV_DAY_HIGH", "base_score": 2.0},
            {"price": float(day_slice["low"].min()),  "type": "PREV_DAY_LOW",  "base_score": 2.0},
        ]

    def _vwap_levels(self, df: pd.DataFrame) -> list:
        if "VWAP" not in df.columns:
            return []
        vwap = float(df["VWAP"].iloc[-1])
        return [{"price": vwap, "type": "VWAP", "base_score": 1.5}]

    def _bb_levels(self, df: pd.DataFrame) -> list:
        last = df.iloc[-1]
        return [
            {"price": float(last.get("BB_Upper", 0)), "type": "BB_UPPER", "base_score": 1.0},
            {"price": float(last.get("BB_Lower", 0)), "type": "BB_LOWER", "base_score": 1.0},
        ]

    def _volume_bonus(self, candidate_price: float, df: pd.DataFrame, atr: float) -> float:
        rec = df.tail(50)
        vp  = rec.get("Volume_Percentile", pd.Series(dtype=float)) if "Volume_Percentile" in rec.columns else pd.Series(dtype=float)
        for i in range(len(rec)):
            close_ = float(rec["close"].iloc[i])
            vp_val = float(vp.iloc[i]) if len(vp) > i else 50.0
            if vp_val >= 75 and abs(close_ - candidate_price) <= atr * 0.3:
                return 0.5
        return 0.0

    def _score_level(self, lvl: dict, price: float, atr: float, df: pd.DataFrame) -> float:
        s   = lvl["base_score"]
        s  += self._volume_bonus(lvl["price"], df, atr)
        dist_atr = abs(lvl["price"] - price) / max(atr, 1e-10)
        if dist_atr <= 1.0:
            s += 0.5
        return round(s, 2)

    def compute(self, price: float, df: pd.DataFrame, signal: str,
                obs: list | None = None,
                eq_hi: list | None = None, eq_lo: list | None = None,
                min_rr: float = MIN_RISK_REWARD) -> tuple:
        # (sl, tp_levels, regime, ai) — overridden in AdaptiveTPEngine below
        if "HOLD" in signal:
            ai = _default_ai()
            ai.update({
                "cancel_reason": "HOLD — no entry",
                "rr_ratio":      0.0,
                "sl_dist_pct":   round(abs(price * 0.02) / price * 100, 3),
                "sl_mult_used":  1.2,
                "tp1_pct":       round(abs(price * 1.02 - price) / price * 100, 3),
                "tp1_type":      "HOLD_DEFAULT",
                "tp1_score":     0.0,
                "vol_zone":      "N/A",
                "regime":        "HOLD",
                "levels_scored": [],
            })
            return (round(price * 0.98, 6),
                    {"TP1": round(price * 1.02, 6), "TP2": None, "TP3": None},
                    "HOLD", ai)

        last     = df.iloc[-1]
        atr      = float(last["ATR"])
        atp      = float(last["ATR_Percentile"])
        is_bull  = "BUY" in signal
        d        = 1 if is_bull else -1
        regime   = classify_regime(df)[0]

        candidates = []
        candidates.extend(self._swing_levels(df))
        candidates.extend(self._fibonacci_levels(df))
        candidates.extend(self._round_numbers(price, atr))
        candidates.extend(self._prev_day_hl(df))
        candidates.extend(self._vwap_levels(df))
        candidates.extend(self._bb_levels(df))
        if obs:
            candidates.extend(self._ob_edges(obs))
        if eq_hi:
            candidates.extend(self._eq_levels(eq_hi, eq_lo or []))

        min_dist = atr * PTP_ATR_MIN
        max_dist = atr * PTP_ATR_MAX

        if is_bull:
            valid = [c for c in candidates
                     if c["price"] > price + min_dist
                     and c["price"] <= price + max_dist]
        else:
            valid = [c for c in candidates
                     if c["price"] < price - min_dist
                     and c["price"] >= price - max_dist]

        if not valid:
            tp1     = price + d * atr * 2.0
            sl_raw  = price - d * atr * 1.2
            sl_dist = abs(sl_raw - price)
            rr      = round(abs(tp1 - price) / max(sl_dist, 1e-10), 2)
            ai      = _default_ai()
            ai.update({
                "cancel_reason": "No candidate levels — ATR fallback",
                "rr_ratio":      rr,
                "sl_dist_pct":   round(sl_dist / price * 100, 3),
                "sl_mult_used":  1.2,
                "tp1_pct":       round(abs(tp1 - price) / price * 100, 3),
                "tp1_type":      "ATR_FALLBACK",
                "tp1_score":     0.0,
                "vol_zone":      "low" if atp < 30 else "high" if atp > 70 else "normal",
                "regime":        regime,
                "levels_scored": [],
            })
            return round(sl_raw, 6), {"TP1": round(tp1, 6), "TP2": None, "TP3": None}, regime, ai

        scored = []
        seen   = set()
        for c in valid:
            p = round(c["price"], 8)
            if p in seen:
                continue
            seen.add(p)
            s = self._score_level(c, price, atr, df)
            if s >= PTP_MIN_SCORE * 0.5:
                scored.append({**c, "score": s, "dist_atr": round(abs(p - price) / atr, 2)})

        scored.sort(key=lambda x: abs(x["price"] - price))

        sup, res = find_sr(df, signal)
        atp_vz   = "low" if atp < 30 else "high" if atp > 70 else "normal"
        sl_mult  = {"low": 0.9, "normal": 1.2, "high": 1.6}[atp_vz]
        if regime == "RANGING":
            sl_mult *= 0.85
        sl = price - d * atr * sl_mult
        if is_bull and sl < sup:
            sl = sup * 1.003
        elif not is_bull and sl > res:
            sl = res * 0.997

        sl_dist = abs(sl - price)

        tp_hits   = []
        for lvl in scored:
            lp = lvl["price"]
            rr = abs(lp - price) / max(sl_dist, 1e-10)
            if len(tp_hits) == 0 and rr < min_rr:
                continue
            tp_hits.append({**lvl, "rr": round(rr, 2)})
            if len(tp_hits) >= 3:
                break

        if not tp_hits:
            tp1 = price + d * atr * 2.0
            rr  = round(abs(tp1 - price) / max(sl_dist, 1e-10), 2)
            ai  = _default_ai()
            ai.update({
                "cancel_reason": f"R:R {rr:.2f} < {min_rr} even at ATR fallback",
                "rr_ratio":      rr,
                "sl_dist_pct":   round(sl_dist / price * 100, 3),
                "sl_mult_used":  sl_mult,
                "tp1_pct":       round(abs(tp1 - price) / price * 100, 3),
                "tp1_type":      "ATR_FALLBACK",
                "tp1_score":     0.0,
                "vol_zone":      atp_vz,
                "regime":        regime,
                "levels_scored": scored[:5],
            })
            return round(sl, 6), {"TP1": round(tp1, 6), "TP2": None, "TP3": None}, regime, ai

        tp1_p = tp_hits[0]["price"]
        tp2_p = tp_hits[1]["price"] if len(tp_hits) >= 2 else None
        tp3_p = tp_hits[2]["price"] if len(tp_hits) >= 3 else None
        rr1   = tp_hits[0]["rr"]

        ai = _default_ai()
        ai.update({
            "cancel_reason":       "None — valid ✓",
            "rr_ratio":            rr1,
            "sl_dist_pct":         round(sl_dist / price * 100, 3),
            "sl_mult_used":        sl_mult,
            "tp1_score":           tp_hits[0].get("score", 0),
            "tp1_type":            tp_hits[0].get("type", "N/A"),
            "tp1_pct":             round(abs(tp1_p - price) / price * 100, 3),
            "tp2_pct":             round(abs(tp2_p - price) / price * 100, 3) if tp2_p else None,
            "tp3_pct":             round(abs(tp3_p - price) / price * 100, 3) if tp3_p else None,
            "vol_zone":            atp_vz,
            "regime":              regime,
            "levels_scored":       scored[:8],
            "nearest_support":     sup,
            "nearest_resistance":  res,
            "min_rr_used":         min_rr,
        })

        return (round(sl, 6),
                {"TP1": round(tp1_p, 6),
                 "TP2": round(tp2_p, 6) if tp2_p else None,
                 "TP3": round(tp3_p, 6) if tp3_p else None},
                regime, ai)


_ptp_engine = ProbabilityTPEngine()


def find_sr(df: pd.DataFrame, signal: str,
            lookback: int = 100, gap_pct: float = 0.005) -> tuple:
    rec   = df.tail(lookback)
    h, l  = rec["high"].values, rec["low"].values
    price = float(df["close"].iloc[-1])
    gap   = price * gap_pct
    res   = [h[i] for i in range(2, len(h)-2) if h[i] == max(h[i-2:i+3])]
    sup   = [l[i] for i in range(2, len(l)-2) if l[i] == min(l[i-2:i+3])]
    vr    = [r for r in res if r > price + gap]
    vs    = [s for s in sup if s < price - gap]
    return (float(max(vs)) if vs else price * 0.92,
            float(min(vr)) if vr else price * 1.08)


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                          WHALE TRACKER                                     ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

class WhaleTracker:
    CVD_WINDOW = 50

    def __init__(self, pool: dict):
        self.pool    = pool
        self._ob: dict    = {}
        self._ob_ts: dict = {}
        self._ob_ttl = 60

    def fetch_ob(self, symbol: str) -> dict | None:
        key = f"ob_{symbol}"
        now = time.time()
        if key in self._ob and now - self._ob_ts.get(key, 0) < self._ob_ttl:
            return self._ob[key]
        for name, ex in self.pool.items():
            try:
                ob = ex.fetch_order_book(symbol, limit=ORDER_BOOK_DEPTH)
                if ob and ob.get("bids") and ob.get("asks"):
                    self._ob[key] = ob; self._ob_ts[key] = now
                    return ob
            except Exception:
                continue
        print(C.y("  ⚠ OB: all exchanges failed"))
        return None

    def analyze_ob(self, symbol: str, price: float) -> dict:
        ob = self.fetch_ob(symbol)
        if not ob:
            return self._empty_ob()
        bids = np.array(ob["bids"][:ORDER_BOOK_DEPTH], dtype=float)
        asks = np.array(ob["asks"][:ORDER_BOOK_DEPTH], dtype=float)
        if bids.size == 0 or asks.size == 0:
            return self._empty_ob()
        bid_px, bid_sz = bids[:, 0], bids[:, 1]
        ask_px, ask_sz = asks[:, 0], asks[:, 1]
        bid_usdt = float(np.sum(bid_px * bid_sz))
        ask_usdt = float(np.sum(ask_px * ask_sz))
        imbal    = bid_usdt / max(bid_usdt + ask_usdt, 1e-10)
        avg_b    = float(np.mean(bid_sz)) if len(bid_sz) else 1.0
        avg_a    = float(np.mean(ask_sz)) if len(ask_sz) else 1.0
        b_walls  = [(float(bid_px[i]), float(bid_sz[i])) for i in range(len(bid_sz))
                    if bid_sz[i] >= avg_b * WALL_MULT]
        a_walls  = [(float(ask_px[i]), float(ask_sz[i])) for i in range(len(ask_sz))
                    if ask_sz[i] >= avg_a * WALL_MULT]
        if   imbal >= 0.65: sig = "BULL";      note = f"Heavy bid ({imbal:.1%})"
        elif imbal <= 0.35: sig = "BEAR";      note = f"Heavy ask ({1-imbal:.1%})"
        elif imbal >= 0.55: sig = "MILD_BULL"; note = f"Mild bid ({imbal:.1%})"
        elif imbal <= 0.45: sig = "MILD_BEAR"; note = f"Mild ask ({1-imbal:.1%})"
        else:               sig = "NEUTRAL";   note = f"Balanced ({imbal:.1%})"
        return {"imbalance": round(imbal, 4), "bid_usdt": round(bid_usdt, 2),
                "ask_usdt": round(ask_usdt, 2), "bid_walls": b_walls, "ask_walls": a_walls,
                "ob_signal": sig, "ob_note": note, "available": True}

    def detect_whales(self, df: pd.DataFrame) -> dict:
        if len(df) < 20:
            return self._empty_whale()
        ma20    = df["volume"].rolling(20).mean().bfill()
        candles = []
        for i in range(max(0, len(df) - 50), len(df)):
            vm  = ma20.iloc[i]
            if vm == 0 or pd.isna(vm): continue
            vr   = df["volume"].iloc[i] / vm
            op   = max(float(df["open"].iloc[i]), 1e-10)
            pmov = abs(float(df["close"].iloc[i]) - op) / op
            if vr >= WHALE_VOL_THRESHOLD and pmov >= WHALE_PRICE_MOVE_MIN:
                bull = float(df["close"].iloc[i]) >= op
                candles.append({"idx": i, "price": float(df["close"].iloc[i]),
                                "vol_ratio": round(vr, 2), "price_move": round(pmov*100, 3),
                                "direction": "BUY" if bull else "SELL",
                                "type": "ACCUMULATION" if bull else "DISTRIBUTION"})
        win      = min(self.CVD_WINDOW, len(df))
        rec      = df.tail(win)
        bull_vol = float(rec.loc[rec["close"] >= rec["open"], "volume"].sum())
        bear_vol = float(rec.loc[rec["close"] <  rec["open"], "volume"].sum())
        cvd_r    = bull_vol / max(bull_vol + bear_vol, 1e-10)
        cvd_t    = "BULL" if cvd_r >= 0.60 else "BEAR" if cvd_r <= 0.40 else "NEUTRAL"
        return {"whale_candles": candles, "recent_whale": candles[-1] if candles else None,
                "cvd_ratio": round(cvd_r, 4), "cvd_trend": cvd_t,
                "bull_vol": round(bull_vol, 2), "bear_vol": round(bear_vol, 2),
                "total_detected": len(candles)}

    def score(self, ob: dict, wc: dict, signal: str) -> tuple:
        pts, notes, is_bull = 0.0, [], "BUY" in signal
        if ob.get("available"):
            s = ob["ob_signal"]
            if   (is_bull  and s == "BULL"):        pts += 4; notes.append(f"OB BULL aligned  — {ob['ob_note']}")
            elif (not is_bull and s == "BEAR"):      pts += 4; notes.append(f"OB BEAR aligned  — {ob['ob_note']}")
            elif (is_bull  and s == "MILD_BULL"):    pts += 2; notes.append(f"OB mild BULL     — {ob['ob_note']}")
            elif (not is_bull and s == "MILD_BEAR"): pts += 2; notes.append(f"OB mild BEAR     — {ob['ob_note']}")
            elif s == "NEUTRAL":                     pts += 1; notes.append(f"OB neutral       — {ob['ob_note']}")
            else:                                              notes.append(f"OB against       — {ob['ob_note']}")
            if   is_bull  and ob["bid_walls"]:  pts += 1; notes.append(f"Bid whale wall ({len(ob['bid_walls'])} lvl)")
            elif not is_bull and ob["ask_walls"]: pts += 1; notes.append(f"Ask whale wall ({len(ob['ask_walls'])} lvl)")
        else:
            pts += 2.5; notes.append("OB unavailable — neutral 2.5 (FIX 2)")
        cvd = wc.get("cvd_trend", "NEUTRAL"); cvd_r = wc.get("cvd_ratio", 0.5)
        if   (is_bull  and cvd == "BULL"):   pts += 3; notes.append(f"CVD bull ({self.CVD_WINDOW}b) ({cvd_r:.1%})")
        elif (not is_bull and cvd == "BEAR"): pts += 3; notes.append(f"CVD bear ({self.CVD_WINDOW}b) ({cvd_r:.1%})")
        elif cvd == "NEUTRAL":               pts += 1; notes.append(f"CVD neutral ({cvd_r:.1%})")
        else:                                           notes.append(f"CVD opposing ({cvd_r:.1%})")
        rw = wc.get("recent_whale")
        if rw:
            match = (is_bull and rw["direction"] == "BUY") or (not is_bull and rw["direction"] == "SELL")
            if match: pts += 2; notes.append(f"Whale {rw['type']} {rw['vol_ratio']:.1f}× vol")
            else:               notes.append(f"Whale opposing {rw['type']}")
        else:
            notes.append("No whale candle in last 50 bars")
        final = round(min(10.0, pts), 1)
        label = ("🐋 CONFIRMED" if final >= 7.5 else "🐟 PARTIAL" if final >= 5.0 else
                 "🔍 NEUTRAL"   if final >= 3.0 else "🚨 OPPOSING")
        return final, label, notes

    @staticmethod
    def _empty_ob() -> dict:
        return {"imbalance": 0.5, "bid_usdt": 0, "ask_usdt": 0,
                "bid_walls": [], "ask_walls": [], "ob_signal": "NEUTRAL",
                "ob_note": "OB unavailable", "available": False}

    @staticmethod
    def _empty_whale() -> dict:
        return {"whale_candles": [], "recent_whale": None, "cvd_ratio": 0.5,
                "cvd_trend": "NEUTRAL", "bull_vol": 0.0, "bear_vol": 0.0, "total_detected": 0}


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                ADDON MODULE 1 — BREAKOUT RETEST ANALYZER                  ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

class BreakoutRetestAnalyzer:
    LOOKBACK=50; RETEST_WIN=20; LEVEL_TOL=0.005
    MIN_VOL_PCT=60; MIN_ATR_MULT=0.8; CLUSTER_PCT=0.003

    def _key_levels(self, df: pd.DataFrame) -> dict:
        rec = df.tail(self.LOOKBACK).reset_index(drop=True)
        hi, lo = rec["high"].values, rec["low"].values
        res, sup = [], []
        for i in range(2, len(rec)-2):
            if hi[i] >= max(hi[i-2:i]) and hi[i] >= max(hi[i+1:i+3]): res.append(float(hi[i]))
            if lo[i] <= min(lo[i-2:i]) and lo[i] <= min(lo[i+1:i+3]): sup.append(float(lo[i]))
        def _cluster(lvls):
            if not lvls: return []
            lvls = sorted(set(lvls)); out = [lvls[0]]
            for v in lvls[1:]:
                if (v - out[-1]) / max(out[-1], 1e-10) > self.CLUSTER_PCT: out.append(v)
            return out
        price = float(rec["close"].iloc[-1])
        rc, sc = _cluster(res), _cluster(sup)
        return {"resistances": rc, "supports": sc,
                "nearest_res": float(min([r for r in rc if r > price*1.001], default=0)) or None,
                "nearest_sup": float(max([s for s in sc if s < price*0.999], default=0)) or None}

    def _find_breakouts(self, df: pd.DataFrame, levels: dict) -> list:
        rec = df.tail(30+self.RETEST_WIN).reset_index(drop=True)
        atr = float(df["ATR"].iloc[-1]); bos = []
        all_lvls = [("resistance", r) for r in levels["resistances"]] + \
                   [("support", s) for s in levels["supports"]]
        for i in range(5, len(rec)):
            close = float(rec["close"].iloc[i])
            vp    = float(rec["Volume_Percentile"].iloc[i]) if "Volume_Percentile" in rec.columns else 50.0
            for ltype, lvl in all_lvls:
                move = abs(close - lvl)
                if ltype == "resistance" and close > lvl*(1+self.LEVEL_TOL*0.5):
                    if move >= atr*self.MIN_ATR_MULT and vp >= self.MIN_VOL_PCT:
                        prev = rec["close"].iloc[max(0,i-5):i].values
                        if all(c <= lvl*1.002 for c in prev):
                            bos.append({"idx":i,"level":lvl,"ltype":ltype,"dir":"BULLISH",
                                        "close":close,"vol_pct":vp,"atr_mult":round(move/max(atr,1e-10),2)})
                elif ltype == "support" and close < lvl*(1-self.LEVEL_TOL*0.5):
                    if move >= atr*self.MIN_ATR_MULT and vp >= self.MIN_VOL_PCT:
                        prev = rec["close"].iloc[max(0,i-5):i].values
                        if all(c >= lvl*0.998 for c in prev):
                            bos.append({"idx":i,"level":lvl,"ltype":ltype,"dir":"BEARISH",
                                        "close":close,"vol_pct":vp,"atr_mult":round(move/max(atr,1e-10),2)})
        return bos

    def _find_retest(self, df: pd.DataFrame, bo: dict) -> dict:
        rec  = df.tail(self.RETEST_WIN+5).reset_index(drop=True)
        lvl  = bo["level"]; atr = float(df["ATR"].iloc[-1]); zone = atr*0.5
        info = {"found":False,"confirmed":False,"candles_ago":None}
        for i in range(len(rec)-1, max(0, len(rec)-self.RETEST_WIN), -1):
            lo_ = float(rec["low"].iloc[i]); hi_ = float(rec["high"].iloc[i])
            cl_ = float(rec["close"].iloc[i])
            if bo["dir"]=="BULLISH":
                if lvl-zone <= lo_ <= lvl+zone:
                    info.update({"found":True,"candles_ago":len(rec)-1-i})
                    if cl_ > lvl: info.update({"confirmed":True,"retest_close":cl_})
                    break
            else:
                if lvl-zone <= hi_ <= lvl+zone:
                    info.update({"found":True,"candles_ago":len(rec)-1-i})
                    if cl_ < lvl: info.update({"confirmed":True,"retest_close":cl_})
                    break
        return info

    def score(self, df: pd.DataFrame, signal: str) -> tuple:
        try:
            lvls = self._key_levels(df); bos = self._find_breakouts(df, lvls)
            if not bos:
                return 0.0,"⬜ NO_BREAKOUT",{"levels":lvls,"breakout":None,"retest":None,
                                               "notes":["No valid breakout in last 30 candles"]}
            recent  = max(bos, key=lambda x: x["idx"])
            retest  = self._find_retest(df, recent)
            is_bull = "BUY" in signal; aligned = (recent["dir"]=="BULLISH") == is_bull
            if not aligned:
                return 2.0,"⚠ OPPOSING_BO",{"levels":lvls,"breakout":recent,"retest":retest,
                                               "notes":[f"BO {recent['dir']} ≠ signal {signal}"]}
            pts, notes = 3.0, []
            notes.append(f"BO {recent['dir']} @ {recent['level']:.5f} vol:{recent['vol_pct']:.0f}th {recent['atr_mult']}× ATR")
            if   recent["vol_pct"] >= 85: pts+=1.5; notes.append("Strong vol on BO +1.5")
            elif recent["vol_pct"] >= 70: pts+=1.0; notes.append("Good vol on BO +1.0")
            if recent["atr_mult"] >= 2.0: pts+=1.0; notes.append(f"Powerful BO {recent['atr_mult']}× ATR +1.0")
            if retest["found"] and retest["confirmed"]: pts+=3.5; notes.append(f"✓ RETEST CONFIRMED {retest['candles_ago']} c ago")
            elif retest["found"]:                       pts+=1.5; notes.append(f"⚡ Retest in progress")
            else:                                                  notes.append("No retest yet")
            pts = min(10.0, pts)
            lbl = ("🟢 CONFIRMED_RETEST" if pts>=7.5 else "🟡 PARTIAL_RETEST" if pts>=5.0 else
                   "🔵 BREAKOUT_ONLY"    if pts>=3.0 else "⬜ WEAK_BO")
            return round(pts,1), lbl, {"levels":lvls,"breakout":recent,"retest":retest,"notes":notes}
        except Exception as e:
            return 0.0,"⬜ ERROR",{"notes":[f"BreakoutRetest: {e}"]}


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                 ADDON MODULE 2 — LIQUIDITY GRAB DETECTOR                  ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

class LiquidityGrabDetector:
    SWEEP_LOOKBACK=20; MIN_WICK_RATIO=1.5; MIN_SWEEP_DIST=0.001
    EQ_TOL=0.002; CONF_WINDOW=3

    def _pools(self, df: pd.DataFrame) -> dict:
        rec = df.tail(self.SWEEP_LOOKBACK+5).reset_index(drop=True)
        hi, lo = rec["high"].values, rec["low"].values
        bsl, ssl = [], []
        for i in range(2, len(rec)-1):
            if hi[i] > hi[i-1] and hi[i] > hi[i-2] and hi[i] >= hi[i+1]: bsl.append({"idx":i,"price":float(hi[i])})
            if lo[i] < lo[i-1] and lo[i] < lo[i-2] and lo[i] <= lo[i+1]: ssl.append({"idx":i,"price":float(lo[i])})
        eq_hi = []
        for i in range(len(bsl)):
            for j in range(i+1, len(bsl)):
                p1,p2 = bsl[i]["price"],bsl[j]["price"]
                if abs(p1-p2)/max(p1,1e-10) < self.EQ_TOL:
                    mid = (p1+p2)/2
                    if not any(abs(mid-e)/max(mid,1e-10) < self.EQ_TOL for e in eq_hi):
                        eq_hi.append(round(mid,8))
        eq_lo = []
        for i in range(len(ssl)):
            for j in range(i+1, len(ssl)):
                p1,p2 = ssl[i]["price"],ssl[j]["price"]
                if abs(p1-p2)/max(p1,1e-10) < self.EQ_TOL:
                    mid = (p1+p2)/2
                    if not any(abs(mid-e)/max(mid,1e-10) < self.EQ_TOL for e in eq_lo):
                        eq_lo.append(round(mid,8))
        return {"bsl":bsl,"ssl":ssl,"eq_hi":eq_hi,"eq_lo":eq_lo}

    def _detect_sweep(self, df: pd.DataFrame, pools: dict) -> dict:
        rec = df.tail(8).reset_index(drop=True); atr = float(df["ATR"].iloc[-1]); hits = []
        for i in range(1, len(rec)):
            o=float(rec["open"].iloc[i]); h=float(rec["high"].iloc[i])
            l=float(rec["low"].iloc[i]);  c=float(rec["close"].iloc[i])
            body=abs(c-o) or 1e-10; uw=h-max(c,o); lw=min(c,o)-l
            vp=float(rec["Volume_Percentile"].iloc[i]) if "Volume_Percentile" in rec.columns else 50.0
            for pvl,ptype in [(p["price"],"BSL") for p in pools["bsl"]]+[(p,"BSL_EQ") for p in pools["eq_hi"]]:
                if h>pvl*(1+self.MIN_SWEEP_DIST) and c<pvl*1.001 and uw>=body*self.MIN_WICK_RATIO and uw>=atr*0.25:
                    hits.append({"sweep_type":"BSL","dir":"BEARISH","pool_price":pvl,"pool_type":ptype,
                                  "idx":i,"cago":len(rec)-1-i,"wick":round(uw,6),"wick_ratio":round(uw/body,2),"vol_pct":vp})
            for pvl,ptype in [(p["price"],"SSL") for p in pools["ssl"]]+[(p,"SSL_EQ") for p in pools["eq_lo"]]:
                if l<pvl*(1-self.MIN_SWEEP_DIST) and c>pvl*0.999 and lw>=body*self.MIN_WICK_RATIO and lw>=atr*0.25:
                    hits.append({"sweep_type":"SSL","dir":"BULLISH","pool_price":pvl,"pool_type":ptype,
                                  "idx":i,"cago":len(rec)-1-i,"wick":round(lw,6),"wick_ratio":round(lw/body,2),"vol_pct":vp})
        return max(hits, key=lambda x: x["idx"]) if hits else {}

    def _confirmed(self, df: pd.DataFrame, sweep: dict) -> bool:
        cag = sweep.get("cago",99)
        if cag == 0: return False
        tail = df.tail(cag+2).reset_index(drop=True)
        if len(tail) < 2: return False
        last=tail.iloc[-1]; pvl=sweep["pool_price"]
        if sweep["dir"]=="BULLISH": return float(last["close"])>float(last["open"]) and float(last["close"])>pvl
        else:                       return float(last["close"])<float(last["open"]) and float(last["close"])<pvl

    def score(self, df: pd.DataFrame, signal: str) -> tuple:
        try:
            pools=self._pools(df); sweep=self._detect_sweep(df,pools)
            pool_summary=f"BSL:{len(pools['bsl'])}(eq:{len(pools['eq_hi'])}) SSL:{len(pools['ssl'])}(eq:{len(pools['eq_lo'])})"
            if not sweep:
                return 0.0,"⬜ NO_SWEEP",{"pools":pools,"sweep":None,"confirmed":False,
                                           "notes":[f"No recent sweep | {pool_summary}"]}
            is_bull="BUY" in signal; aligned=(sweep["dir"]=="BULLISH")==is_bull
            if not aligned:
                return 1.0,"⚠ OPPOSING_SWEEP",{"pools":pools,"sweep":sweep,"confirmed":False,
                                                  "notes":[f"Sweep {sweep['dir']} ≠ signal | {pool_summary}"]}
            conf=self._confirmed(df,sweep); pts,notes=3.0,[]
            notes.append(f"{sweep['sweep_type']} sweep pool:{sweep['pool_price']:.5f} wick:{sweep['wick_ratio']:.1f}× {sweep['cago']} cago")
            if "EQ" in sweep.get("pool_type",""): pts+=1.5; notes.append("EQ highs/lows swept +1.5")
            vp=sweep.get("vol_pct",50)
            if   vp>=80: pts+=2.0; notes.append(f"Vol spike {vp:.0f}th +2.0")
            elif vp>=65: pts+=1.0; notes.append(f"Vol elevated {vp:.0f}th +1.0")
            if   sweep["wick_ratio"]>=3.0: pts+=1.5; notes.append(f"Wick dominant {sweep['wick_ratio']:.1f}× +1.5")
            elif sweep["wick_ratio"]>=2.0: pts+=0.5; notes.append(f"Wick ok {sweep['wick_ratio']:.1f}× +0.5")
            if conf: pts+=2.0; notes.append("✓ Reversal candle CONFIRMED +2.0")
            else:    notes.append("⚡ Awaiting reversal candle")
            if sweep["cago"]<=1: pts+=0.5; notes.append("Fresh sweep ≤1 bar +0.5")
            pts=min(10.0,pts)
            lbl=("🎯 CONF_SWEEP" if pts>=7.5 else "⚡ PART_SWEEP" if pts>=5.0 else
                 "🔵 WEAK_SWEEP" if pts>=3.0 else "⬜ MIN_SWEEP")
            return round(pts,1),lbl,{"pools":pools,"sweep":sweep,"confirmed":conf,"notes":notes}
        except Exception as e:
            return 0.0,"⬜ ERROR",{"notes":[f"LiqGrab: {e}"]}


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                  ADDON MODULE 3 — ORDER BLOCK ENGINE                       ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

class OrderBlockEngine:
    LOOKBACK=100; MAX_OB_AGE=50; IMPULSE_MULT=1.5; IMPULSE_CONSEC=2; PROX_ATR=1.5

    def _avg_body(self, df: pd.DataFrame, n: int=14) -> float:
        return float(np.mean(abs(df["close"]-df["open"]).tail(n).values)) or 1e-10

    def detect(self, df: pd.DataFrame) -> list:
        rec=df.tail(self.LOOKBACK).reset_index(drop=True); avg=self._avg_body(rec); obs=[]
        for i in range(1, len(rec)-self.IMPULSE_CONSEC-1):
            o=float(rec["open"].iloc[i]); h=float(rec["high"].iloc[i])
            l=float(rec["low"].iloc[i]);  c=float(rec["close"].iloc[i])
            body=abs(c-o); bull=(c>o); bear=(c<o)
            n1o=float(rec["open"].iloc[i+1]); n1c=float(rec["close"].iloc[i+1]); n1b=abs(n1c-n1o)
            large_bull=n1c>n1o and n1b>=avg*self.IMPULSE_MULT
            large_bear=n1c<n1o and n1b>=avg*self.IMPULSE_MULT
            end=min(len(rec),i+1+self.IMPULSE_CONSEC)
            seq_bull=all(float(rec["close"].iloc[j])>float(rec["open"].iloc[j]) for j in range(i+1,end))
            seq_bear=all(float(rec["close"].iloc[j])<float(rec["open"].iloc[j]) for j in range(i+1,end))
            age=len(rec)-1-i
            if age > self.MAX_OB_AGE: continue
            bhi_b=max(o,c); blo_b=min(o,c); mit_end=min(len(rec),i+1+self.MAX_OB_AGE)
            def _mit(ob_blo,ob_bhi,direction):
                for j in range(i+1,mit_end):
                    fc=float(rec["close"].iloc[j]); fl=float(rec["low"].iloc[j]); fh=float(rec["high"].iloc[j])
                    if direction=="BULLISH":
                        if ob_blo<=fc<=ob_bhi or fl<ob_blo: return True
                    else:
                        if ob_blo<=fc<=ob_bhi or fh>ob_bhi: return True
                return False
            if bear and (large_bull or seq_bull) and not _mit(blo_b,bhi_b,"BULLISH"):
                obs.append({"type":"BULLISH_OB","idx":i,"age":age,"ob_high":round(h,6),"ob_low":round(l,6),
                             "body_hi":round(bhi_b,6),"body_lo":round(blo_b,6),"body_sz":round(body,6),
                             "impulse":round(n1b/max(avg,1e-10),2),"mitigated":False})
            if bull and (large_bear or seq_bear) and not _mit(blo_b,bhi_b,"BEARISH"):
                obs.append({"type":"BEARISH_OB","idx":i,"age":age,"ob_high":round(h,6),"ob_low":round(l,6),
                             "body_hi":round(bhi_b,6),"body_lo":round(blo_b,6),"body_sz":round(body,6),
                             "impulse":round(n1b/max(avg,1e-10),2),"mitigated":False})
        return sorted(obs, key=lambda x: x["age"])

    def score(self, df: pd.DataFrame, signal: str) -> tuple:
        try:
            obs=self.detect(df); price=float(df["close"].iloc[-1]); atr=float(df["ATR"].iloc[-1])
            bull_n=sum(1 for o in obs if o["type"]=="BULLISH_OB")
            bear_n=sum(1 for o in obs if o["type"]=="BEARISH_OB")
            notes=[f"Unmitigated OBs — bull:{bull_n} bear:{bear_n}"]
            target="BULLISH_OB" if "BUY" in signal else "BEARISH_OB"
            cands=[o for o in obs if o["type"]==target]
            if not cands:
                return 0.0,"⬜ NO_OB",{"all_obs":obs,"active":None,"prox":"NONE","notes":notes}
            active=min(cands,key=lambda x: abs((x["ob_high"]+x["ob_low"])/2-price))
            mid=((active["ob_high"]+active["ob_low"])/2); dist=abs(price-mid)
            if   active["ob_low"]<=price<=active["ob_high"]: prox="INSIDE"
            elif dist<=atr*self.PROX_ATR:                    prox="APPROACHING"
            elif dist<=atr*3.0:                               prox="NEARBY"
            else:                                             prox="FAR"
            if prox=="FAR":
                return 0.5,"⬜ OB_FAR",{"all_obs":obs,"active":active,"prox":prox,"notes":notes}
            pts=2.0
            notes.append(f"Active {active['type']} [{active['ob_low']:.5f}–{active['ob_high']:.5f}] age:{active['age']} impulse:{active['impulse']:.1f}×")
            if   prox=="INSIDE":      pts+=4.0; notes.append("✓ Price INSIDE OB +4.0")
            elif prox=="APPROACHING": pts+=2.5; notes.append("⚡ Approaching OB +2.5")
            elif prox=="NEARBY":      pts+=1.0; notes.append("Price nearby OB +1.0")
            if   active["impulse"]>=3.0: pts+=2.0; notes.append(f"Impulse {active['impulse']:.1f}× +2.0")
            elif active["impulse"]>=2.0: pts+=1.0; notes.append(f"Impulse {active['impulse']:.1f}× +1.0")
            if   active["age"]<=10: pts+=1.0; notes.append(f"Fresh OB {active['age']} bars +1.0")
            elif active["age"]<=25: pts+=0.5; notes.append(f"Recent OB {active['age']} bars +0.5")
            pts=min(10.0,pts)
            lbl=("🎯 OB_INSIDE" if prox=="INSIDE" and pts>=7.0 else
                 "⚡ OB_APPROACHING" if prox=="APPROACHING" else
                 "🔵 OB_NEARBY"   if pts>=3.0 else "⬜ OB_FAR")
            return round(pts,1),lbl,{"all_obs":obs,"active":active,"prox":prox,"notes":notes}
        except Exception as e:
            return 0.0,"⬜ ERROR",{"notes":[f"OrderBlock: {e}"]}


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║              ADDON MODULE 4 — OPEN INTEREST + FUNDING RATE                 ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

class OpenInterestEngine:
    FR_EXTREME_LONG=0.0010; FR_CROWDED_LONG=0.0005
    FR_NEUTRAL_HI=0.0003;   FR_NEUTRAL_LO=-0.0001
    FR_CROWDED_SHORT=-0.0003; FR_EXTREME_SHORT=-0.0005
    OI_STRONG_CHG=0.05; OI_MOD_CHG=0.02; _TTL=300

    def __init__(self, pool: dict):
        self.pool=pool; self._cache: dict={}; self._cache_t: dict={}

    def _futures_ex(self, name: str):
        try:
            cls=getattr(ccxt,name); return cls({"enableRateLimit":True,"options":{"defaultType":"future"}})
        except Exception: return None

    def _sym_f(self, symbol: str) -> str:
        return symbol.replace("/USDT","/USDT:USDT")

    def fetch_oi(self, symbol: str) -> dict:
        key=f"oi_{symbol}"
        if key in self._cache and time.time()-self._cache_t.get(key,0)<self._TTL:
            return self._cache[key]
        fsym=self._sym_f(symbol)
        for name in FUTURES_EXCHANGES:
            try:
                ex=self._futures_ex(name)
                if not ex: continue
                oi=ex.fetch_open_interest(fsym)
                if not oi: continue
                val=float(oi.get("openInterest",0) or 0); usd=float(oi.get("openInterestValue",val) or val)
                if val>0:
                    res={"available":True,"oi":val,"oi_usd":usd,"exchange":name}
                    self._cache[key]=res; self._cache_t[key]=time.time(); return res
            except Exception as e:
                print(C.dim(f"  OI {name}: {str(e)[:50]}"))
        return {"available":False,"oi":0,"oi_usd":0}

    def fetch_oi_hist(self, symbol: str, n: int=12) -> list:
        fsym=self._sym_f(symbol)
        for name in FUTURES_EXCHANGES:
            try:
                ex=self._futures_ex(name)
                if not ex or not ex.has.get("fetchOpenInterestHistory"): continue
                hist=ex.fetch_open_interest_history(fsym,"1h",limit=n)
                if hist and len(hist)>=3:
                    return [float(h.get("openInterest",0) or 0) for h in hist]
            except Exception: continue
        return []

    def fetch_funding(self, symbol: str) -> dict:
        key=f"fr_{symbol}"
        if key in self._cache and time.time()-self._cache_t.get(key,0)<self._TTL:
            return self._cache[key]
        fsym=self._sym_f(symbol)
        for name in FUTURES_EXCHANGES:
            try:
                ex=self._futures_ex(name)
                if not ex: continue
                fr=ex.fetch_funding_rate(fsym)
                if not fr: continue
                rate=float(fr.get("fundingRate",0) or 0)
                res={"available":True,"rate":rate,"rate_pct":round(rate*100,5),"exchange":name}
                self._cache[key]=res; self._cache_t[key]=time.time(); return res
            except Exception as e:
                print(C.dim(f"  FR {name}: {str(e)[:50]}"))
        return {"available":False,"rate":0.0,"rate_pct":0.0}

    def _oi_trend(self, hist: list) -> dict:
        if len(hist)<4: return {"trend":"UNKNOWN","chg_pct":0}
        n=len(hist); recent=float(np.mean(hist[max(0,n-3):])); older=float(np.mean(hist[max(0,n-9):max(0,n-3)])) if n>=6 else float(hist[0])
        chg=(recent-older)/max(abs(older),1e-10)
        if   chg>=self.OI_STRONG_CHG:  trend="RISING_STRONG"
        elif chg>=self.OI_MOD_CHG:     trend="RISING"
        elif chg<=-self.OI_STRONG_CHG: trend="FALLING_STRONG"
        elif chg<=-self.OI_MOD_CHG:    trend="FALLING"
        else:                           trend="NEUTRAL"
        return {"trend":trend,"chg_pct":round(chg*100,2),"recent":round(recent,2),"older":round(older,2)}

    def _fr_class(self, rate: float) -> tuple:
        if   rate>=self.FR_EXTREME_LONG:  return "EXTREME_LONG","Longs severely crowded"
        elif rate>=self.FR_CROWDED_LONG:  return "CROWDED_LONG","Longs moderately crowded"
        elif rate<=self.FR_EXTREME_SHORT: return "EXTREME_SHORT","Shorts severely crowded"
        elif rate<=self.FR_CROWDED_SHORT: return "CROWDED_SHORT","Shorts moderately crowded"
        else:                             return "NEUTRAL","Funding balanced"

    def score(self, symbol: str, df: pd.DataFrame, signal: str) -> tuple:
        try:
            is_bull="BUY" in signal; oi_now=self.fetch_oi(symbol)
            oi_hist=self.fetch_oi_hist(symbol); fr_data=self.fetch_funding(symbol)
            if not oi_now.get("available") and not fr_data.get("available"):
                return 5.0,"⬜ NO_FUTURES",{"oi":oi_now,"fr":fr_data,"notes":["Futures unavailable — neutral 5.0"]}
            oi_tr=self._oi_trend(oi_hist); rate=fr_data.get("rate",0.0)
            frcls,frnote=self._fr_class(rate); pts,notes=0.0,[]
            p_up=float(df["close"].iloc[-1])>float(df["close"].iloc[-5]) if len(df)>=5 else True
            ot=oi_tr["trend"]
            if ot!="UNKNOWN":
                rising="RISING" in ot; falling="FALLING" in ot; strong="STRONG" in ot
                if is_bull:
                    if   rising  and p_up:     pts+=4.0 if strong else 2.5; notes.append(f"OI↑+Price↑ {oi_tr['chg_pct']:+.1f}%")
                    elif falling and p_up:     pts+=0.5; notes.append(f"OI↓+Price↑ {oi_tr['chg_pct']:+.1f}%")
                    elif rising  and not p_up: pts+=1.0; notes.append(f"OI↑+Price↓ {oi_tr['chg_pct']:+.1f}%")
                    else:                      pts+=1.5; notes.append(f"OI neutral {oi_tr['chg_pct']:+.1f}%")
                else:
                    if   falling and not p_up: pts+=4.0 if strong else 2.5; notes.append(f"OI↓+Price↓ {oi_tr['chg_pct']:+.1f}%")
                    elif rising  and not p_up: pts+=3.0 if strong else 2.0; notes.append(f"OI↑+Price↓ {oi_tr['chg_pct']:+.1f}%")
                    elif falling and p_up:     pts+=0.5; notes.append(f"OI↓+Price↑ {oi_tr['chg_pct']:+.1f}%")
                    else:                      pts+=1.5; notes.append(f"OI neutral {oi_tr['chg_pct']:+.1f}%")
            else:
                pts+=2.0; notes.append("OI history unavailable")
            if fr_data.get("available"):
                notes.append(f"FR:{rate*100:.4f}% — {frcls} | {frnote}")
                if is_bull:
                    if   frcls=="EXTREME_LONG":  pts-=2.0
                    elif frcls=="CROWDED_LONG":  pts+=1.0
                    elif frcls=="EXTREME_SHORT": pts+=3.0
                    elif frcls=="CROWDED_SHORT": pts+=2.0
                    else:                        pts+=1.5
                else:
                    if   frcls=="EXTREME_SHORT": pts-=2.0
                    elif frcls=="CROWDED_SHORT": pts+=1.0
                    elif frcls=="EXTREME_LONG":  pts+=3.0
                    elif frcls=="CROWDED_LONG":  pts+=2.0
                    else:                        pts+=1.5
            else:
                pts+=1.5; notes.append("Funding unavailable")
            pts=round(min(10.0,max(0.0,pts)),1)
            lbl=("🚀 OI_SQUEEZE" if pts>=8.0 else "💪 OI_CONFIRMED" if pts>=6.0 else
                 "🟡 OI_PARTIAL" if pts>=4.0 else "⚠ OI_WEAK"      if pts>=2.0 else "🚨 OI_OPPOSING")
            return pts,lbl,{"oi_now":oi_now,"oi_trend":oi_tr,"fr":fr_data,"fr_class":frcls,"notes":notes}
        except Exception as e:
            return 5.0,"⬜ ERROR",{"notes":[f"OI/Funding: {e}"]}


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                         MASTER ADDON ENGINE                                ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

class AddonEngine:
    def __init__(self, pool: dict):
        self.br = BreakoutRetestAnalyzer()
        self.lg = LiquidityGrabDetector()
        self.ob = OrderBlockEngine()
        self.oi = OpenInterestEngine(pool)

    def run_all(self, df: pd.DataFrame, symbol: str, signal: str, weights_override: dict | None = None) -> dict:
        w = weights_override if weights_override else ADDON_WEIGHTS
        print(section("ADDON  —  4 Extra Logics", "🔬"))

        print(C.dim("  [1/4] Breakout Retest ..."))
        br_s,br_l,br_i = self.br.score(df, signal)
        print(row("BR Score", (C.g if br_s>=6 else C.y if br_s>=3 else C.r)(f"{br_s:.1f}/10")))
        for n in br_i.get("notes",[])[:2]: print(C.dim(f"    · {n}"))

        print(C.dim("  [2/4] Liquidity Grab ..."))
        lg_s,lg_l,lg_i = self.lg.score(df, signal)
        print(row("LG Score", (C.g if lg_s>=6 else C.y if lg_s>=3 else C.r)(f"{lg_s:.1f}/10")))
        for n in lg_i.get("notes",[])[:2]: print(C.dim(f"    · {n}"))

        print(C.dim("  [3/4] Order Block ..."))
        ob_s,ob_l,ob_i = self.ob.score(df, signal)
        print(row("OB Score", (C.g if ob_s>=6 else C.y if ob_s>=3 else C.r)(f"{ob_s:.1f}/10")))
        for n in ob_i.get("notes",[])[:2]: print(C.dim(f"    · {n}"))

        print(C.dim("  [4/4] Open Interest + Funding ..."))
        oi_s,oi_l,oi_i = self.oi.score(symbol, df, signal)
        print(row("OI Score", (C.g if oi_s>=6 else C.y if oi_s>=3 else C.r)(f"{oi_s:.1f}/10")))
        for n in oi_i.get("notes",[])[:2]: print(C.dim(f"    · {n}"))

        comb = round(br_s*w["breakout_retest"] + lg_s*w["liquidity_grab"] +
                     ob_s*w["order_block"]     + oi_s*w["oi_funding"], 2)

        if br_s==0 and lg_s==0 and ob_s==0 and oi_s==5.0:
            comb = max(comb, ADDON_UNAVAIL_FLOOR)
            print(C.y(f"  ⚠  All addon zero — floor {ADDON_UNAVAIL_FLOOR} applied (FIX 3)"))

        lbl = ("🏆 ADDON_SUPREME" if comb>=8.0 else "💪 ADDON_STRONG" if comb>=6.0 else
               "🟡 ADDON_MODERATE" if comb>=4.0 else "⚠ ADDON_WEAK" if comb>=2.0 else "🚨 ADDON_OPPOSING")

        print(section(f"ADDON Combined  {comb:.1f}/10  —  {lbl}", "🔬"))

        gate_action = "ALLOW"; gate_reason = "All addon checks passed"
        if comb < ADDON_HARD_BLOCK and signal != "HOLD":
            gate_action="HARD_BLOCK"; gate_reason=f"Addon {comb:.1f} < {ADDON_HARD_BLOCK}"
            print(C.r(f"  🚫 HARD BLOCK: {gate_reason}"))
        elif ADDON_HARD_BLOCK <= comb < ADDON_SOFT_DOWNGRADE and "STRONG" in signal:
            gate_action="SOFT_DOWNGRADE"; gate_reason=f"Addon {comb:.1f} STRONG downgraded"
            print(C.y(f"  ⚠  SOFT DOWNGRADE: {gate_reason}"))
        elif comb >= 6.0:
            print(C.g("  ✓  Addon fully confirms signal"))

        size_mult = round(max(0.80, min(1.20, 0.80 + (comb/10)*ADDON_SIZE_WEIGHT)), 3)

        return {"combined_score":comb,"combined_label":lbl,"gate_action":gate_action,
                "gate_reason":gate_reason,"size_mult":size_mult,
                "breakout_retest":{"score":br_s,"label":br_l,"info":br_i},
                "liquidity_grab": {"score":lg_s,"label":lg_l,"info":lg_i},
                "order_block":    {"score":ob_s,"label":ob_l,"info":ob_i},
                "oi_funding":     {"score":oi_s,"label":oi_l,"info":oi_i}}


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                     MARKET STRUCTURE ANALYZER                              ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def analyze_structure(df: pd.DataFrame, lookback: int = STRUCTURE_LOOKBACK) -> dict:
    if len(df) < lookback + 7:
        return _empty_structure("UNKNOWN", 0, "Insufficient data")
    rec=df.tail(lookback).reset_index(drop=True)
    hi,lo,cl=rec["high"].values,rec["low"].values,rec["close"].values
    atr_val=float(rec["ATR"].iloc[-1]) if "ATR" in rec.columns else 0
    price_ref=float(cl[-1]) if cl[-1]>0 else 1.0
    min_swing=max(0.005, 0.5*atr_val/price_ref)
    s_highs,s_lows=[],[]
    for i in range(3,len(rec)-3):
        lh,rh=hi[i-3:i],hi[i+1:i+4]; ll,rl=lo[i-3:i],lo[i+1:i+4]
        if len(lh)<3 or len(rh)<3: continue
        if hi[i]>=max(lh) and hi[i]>=max(rh):
            local_lo=lo[max(0,i-5):i]
            if len(local_lo)>0 and (hi[i]-max(float(min(local_lo)),1e-10))/max(float(min(local_lo)),1e-10)>=min_swing:
                s_highs.append((i,float(hi[i])))
        if lo[i]<=min(ll) and lo[i]<=min(rl):
            local_hi=hi[max(0,i-5):i]
            if len(local_hi)>0 and (max(local_hi)-lo[i])/max(float(lo[i]),1e-10)>=min_swing:
                s_lows.append((i,float(lo[i])))
    notes=[f"{len(s_highs)} swing highs | {len(s_lows)} swing lows (lookback:{lookback} min_swing:{min_swing:.3%})"]
    if len(s_highs)<2 or len(s_lows)<2:
        return _empty_structure("RANGING",35,"Insufficient swings — choppy market",s_highs,s_lows)
    last_h=s_highs[-3:] if len(s_highs)>=3 else s_highs
    last_l=s_lows[-3:]  if len(s_lows)>=3  else s_lows
    hh=all(last_h[i][1]>last_h[i-1][1] for i in range(1,len(last_h)))
    hl=all(last_l[i][1]>last_l[i-1][1] for i in range(1,len(last_l)))
    lh=all(last_h[i][1]<last_h[i-1][1] for i in range(1,len(last_h)))
    ll=all(last_l[i][1]<last_l[i-1][1] for i in range(1,len(last_l)))
    last_close=float(cl[-1]); prev_high=s_highs[-2][1] if len(s_highs)>=2 else float(hi[-1])
    prev_low=s_lows[-2][1]   if len(s_lows)>=2  else float(lo[-1])
    breakout=last_close>prev_high*1.003; breakdown=last_close<prev_low*0.997
    if hh and hl:       stype="UPTREND";   conf=90 if breakout else 78; notes.append("HH+HL confirmed")
    elif lh and ll:     stype="DOWNTREND"; conf=90 if breakdown else 78; notes.append("LH+LL confirmed")
    elif breakout:      stype="BREAKOUT";  conf=72; notes.append(f"Breakout above {prev_high:.5f}")
    elif breakdown:     stype="BREAKDOWN"; conf=72; notes.append(f"Breakdown below {prev_low:.5f}")
    else:               stype="RANGING";   conf=45; notes.append("Mixed/ranging structure")
    return {"type":stype,"confidence":conf,"swing_highs":s_highs,"swing_lows":s_lows,
            "last_high":s_highs[-1][1] if s_highs else None,"last_low":s_lows[-1][1] if s_lows else None,
            "prev_high":prev_high,"prev_low":prev_low,"breakout":breakout,"breakdown":breakdown,
            "hh":hh,"hl":hl,"lh":lh,"ll":ll,"min_swing_used":round(min_swing,5),"notes":notes}


def _empty_structure(stype,conf,note,sh=None,sl=None) -> dict:
    return {"type":stype,"confidence":conf,"swing_highs":sh or [],"swing_lows":sl or [],
            "last_high":None,"last_low":None,"prev_high":None,"prev_low":None,
            "breakout":False,"breakdown":False,"hh":False,"hl":False,"lh":False,"ll":False,
            "min_swing_used":0.008,"notes":[note]}


def structure_gate(structure: dict, signal: str) -> tuple:
    stype=structure.get("type","RANGING"); conf=structure.get("confidence",0); is_bull="BUY" in signal
    if signal=="HOLD": return True,"HOLD — no gate applied"
    rules={"UPTREND":(True if is_bull else False,"UPTREND"),"DOWNTREND":(True if not is_bull else False,"DOWNTREND"),
           "BREAKOUT":(True if is_bull else False,"BREAKOUT"),"BREAKDOWN":(True if not is_bull else False,"BREAKDOWN")}
    if stype in rules:
        allowed,label=rules[stype]
        if allowed: return True,f"✓ Structure {label} supports signal (conf:{conf}%)"
        return False,f"✗ BLOCKED — {label} structure forbids {'BUY' if is_bull else 'SELL'} (conf:{conf}%)"
    return True,f"⚠ RANGING structure — signal allowed with caution (conf:{conf}%)"


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                           REGIME CLASSIFIER (original v10 kept)            ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def classify_regime(df: pd.DataFrame) -> tuple:
    last=df.iloc[-1]; adx=float(last["ADX"]); bbw=float(last["BB_Width"])
    atp=float(last["ATR_Percentile"]); price=float(last["close"])
    e9=float(last["EMA_9"]); e50=float(last["EMA_50"]); e200=float(last["EMA_200"])
    adxp=float(last["ADX_Pos"]); adxn=float(last["ADX_Neg"])
    pb=price>e9>e50>e200; nb=price<e9<e50<e200; ub=price>e9>e50; db=price<e9<e50
    q80=float(df["BB_Width"].quantile(0.80)); q40=float(df["BB_Width"].quantile(0.40))
    if atp>85 and bbw>q80:            return "VOLATILE",     "⚡ Very high volatility"
    if adx>=35 and adxp>adxn and pb:  return "STRONG_BULL",  "🚀 Very strong uptrend"
    if adx>=35 and adxn>adxp and nb:  return "STRONG_BEAR",  "💀 Very strong downtrend"
    if adx>22  and adxp>adxn and ub:  return "TRENDING_UP",  "📈 Uptrend"
    if adx>22  and adxn>adxp and db:  return "TRENDING_DOWN","📉 Downtrend"
    if adx<20  and bbw<q40:           return "RANGING",      "↔ Sideways"
    return "NORMAL","🔄 Normal"


# ───────────────────────────────────────────────────────────────────────────────
#  NEW MODULE 1: RegimeBrain (Master Controller)
# ───────────────────────────────────────────────────────────────────────────────

@dataclass
class RegimeState:
    primary: str
    secondary: str
    confidence: float
    volatility_tier: str
    trend_strength: float
    momentum_bias: str
    regime_age: int
    transition_prob: float


class RegimeBrain:
    def __init__(self):
        self._last_regime = None
        self._regime_start_idx = 0
        self._regime_age = 0

    def _volatility_dna(self, df: pd.DataFrame) -> dict:
        last = df.iloc[-1]
        atr_pct = float(last["ATR_Percentile"])
        bb_w = float(last["BB_Width"])
        bb_hist = df["BB_Width"].dropna().tail(200)
        bb_percentile = (bb_hist < bb_w).mean() * 100 if len(bb_hist) else 50
        closes = df["close"].tail(50)
        rv10 = closes.pct_change().tail(10).std() * np.sqrt(24) if len(closes)>10 else 0
        rv20 = closes.pct_change().tail(20).std() * np.sqrt(24) if len(closes)>20 else 0
        rv50 = closes.pct_change().tail(50).std() * np.sqrt(24) if len(closes)>50 else 0
        high_low = np.log(df["high"] / df["low"]).tail(50)
        open_close = np.log(df["close"] / df["open"].shift(1)).tail(50)
        close_open = np.log(df["open"] / df["close"].shift(1)).tail(50)
        hl_avg = (high_low**2).mean() * 0.5 if len(high_low) else 0
        oc_avg = (open_close**2).mean() if len(open_close) else 0
        co_avg = (close_open**2).mean() if len(close_open) else 0
        yz_vol = np.sqrt(hl_avg + 0.164*oc_avg + 0.836*co_avg) * np.sqrt(24) if hl_avg>0 else 0
        vol_tier = "LOW" if atr_pct < 25 else "MEDIUM" if atr_pct < 50 else "HIGH" if atr_pct < 75 else "EXTREME"
        return {"atr_pct": atr_pct, "bb_pct": bb_percentile, "rv10": rv10, "rv20": rv20, "rv50": rv50,
                "yz_vol": yz_vol, "tier": vol_tier}

    def _trend_dna(self, df: pd.DataFrame) -> dict:
        last = df.iloc[-1]
        adx_val = float(last["ADX"])
        adx_series = df["ADX"].tail(10).values
        adx_slope = np.polyfit(np.arange(len(adx_series)), adx_series, 1)[0] if len(adx_series)>=5 else 0
        e9 = float(last["EMA_9"]); e50 = float(last["EMA_50"]); e200 = float(last["EMA_200"])
        price = float(last["close"])
        sep = abs(e9 - e200) / price * 100
        pos_score = sum([price > e9, price > e50, price > e200, e9 > e50, e50 > e200, e9 > e200])
        st_dir = df["ST_Direction"].values
        streak = 0
        for i in range(len(st_dir)-1, -1, -1):
            if st_dir[i] == st_dir[-1]:
                streak += 1
            else:
                break
        trend_strength = min(100, (adx_val * 1.5 + pos_score * 8 + streak * 1.5))
        momentum = "BULL" if price > e50 and e9 > e50 else "BEAR" if price < e50 and e9 < e50 else "NEUTRAL"
        return {"adx": adx_val, "adx_slope": adx_slope, "ema_sep_pct": sep,
                "pos_score": pos_score, "st_streak": streak, "trend_strength": trend_strength,
                "momentum": momentum}

    def _volume_dna(self, df: pd.DataFrame) -> dict:
        last = df.iloc[-1]
        cvd_20 = float(last["CVD_20"]) if "CVD_20" in last.index else 0
        obv = df["OBV"].values
        obv_ema5 = pd.Series(obv).ewm(span=5).mean().iloc[-1] if len(obv) else 0
        obv_ema20 = pd.Series(obv).ewm(span=20).mean().iloc[-1] if len(obv) else 0
        obv_momentum = obv_ema5 - obv_ema20
        vol_ratio = float(last["Volume_Ratio"])
        vol_expanding = vol_ratio > 1.2
        return {"cvd_20": cvd_20, "obv_momentum": obv_momentum, "vol_expanding": vol_expanding}

    def _microstructure_dna(self, df: pd.DataFrame, structure: dict | None = None) -> dict:
        if structure is None:
            structure = analyze_structure(df)
        sh = structure.get("swing_highs", [])
        if len(sh) >= 3:
            recent_highs = [h for _, h in sh[-3:]]
            spread = (max(recent_highs) - min(recent_highs)) / min(recent_highs) * 100 if min(recent_highs) > 0 else 0
        else:
            spread = 0
        closes = df["close"].tail(REGIME_HURST_WINDOW).values
        if len(closes) >= REGIME_HURST_WINDOW:
            log_prices = np.log(closes)
            L = REGIME_HURST_WINDOW
            mean = np.mean(log_prices)
            cum_dev = np.cumsum(log_prices - mean)
            R = max(cum_dev) - min(cum_dev)
            S = np.std(log_prices)
            hurst = np.log(R / S) / np.log(L) if S > 0 else 0.5
        else:
            hurst = 0.5
        return {"swing_spread": spread, "hurst": hurst, "structure": structure}

    def detect(self, df1h: pd.DataFrame, df4h: pd.DataFrame | None = None, structure: dict | None = None) -> RegimeState:
        try:
            vol = self._volatility_dna(df1h)
            trd = self._trend_dna(df1h)
            vold = self._volume_dna(df1h)
            micro = self._microstructure_dna(df1h, structure=structure)

            last = df1h.iloc[-1]
            price = float(last["close"])
            atr_pct = vol["atr_pct"]
            bb_pct = vol["bb_pct"]
            adx = trd["adx"]
            adx_slope = trd["adx_slope"]
            momentum = trd["momentum"]
            trend_strength = trd["trend_strength"]

            primary = "NORMAL"
            secondary = ""
            confidence = 50

            if atr_pct > 85 or bb_pct > 85:
                primary = "VOLATILE_SPIKE"
                confidence = max(85, atr_pct)
            elif atr_pct < 25 and bb_pct < 25:
                primary = "RANGING_TIGHT"
                confidence = 70
            elif atr_pct < 50 and bb_pct < 40:
                primary = "RANGING_WIDE"
                confidence = 60
            else:
                if adx >= 35:
                    if momentum == "BULL":
                        primary = "STRONG_BULL"
                        confidence = 85
                    elif momentum == "BEAR":
                        primary = "STRONG_BEAR"
                        confidence = 85
                elif adx > 22:
                    if momentum == "BULL":
                        primary = "TRENDING_UP"
                        confidence = 75
                    elif momentum == "BEAR":
                        primary = "TRENDING_DOWN"
                        confidence = 75

            if primary in ("NORMAL",):
                primary = "RANGING_TIGHT" if adx < 20 else "TRENDING_UP" if momentum=="BULL" else "TRENDING_DOWN"
                confidence = 50

            bb_squeeze = bb_pct < 15
            adx_rising = adx_slope > 0.2
            vol_spike = vold["vol_expanding"]
            if bb_squeeze and adx_rising and vol_spike:
                if momentum == "BULL":
                    secondary = "BREAKOUT_IMMINENT"
                elif momentum == "BEAR":
                    secondary = "BREAKDOWN_IMMINENT"

            if primary != self._last_regime:
                self._last_regime = primary
                self._regime_start_idx = len(df1h) - 1
            self._regime_age = len(df1h) - self._regime_start_idx

            transition_prob = 0.1
            if trd["ema_sep_pct"] < 1.0 and adx_slope < -0.1:
                transition_prob = 0.4
            elif trd["ema_sep_pct"] < 0.5 and adx_slope < -0.2:
                transition_prob = 0.65

            return RegimeState(
                primary=primary,
                secondary=secondary if secondary else primary,
                confidence=confidence,
                volatility_tier=vol["tier"],
                trend_strength=trend_strength,
                momentum_bias=momentum,
                regime_age=self._regime_age,
                transition_prob=transition_prob
            )
        except Exception as e:
            print(C.y(f"  ⚠ RegimeBrain error: {e} — using V10 classify_regime"))
            regime, _ = classify_regime(df1h)
            return RegimeState(primary=regime, secondary=regime, confidence=50,
                               volatility_tier="MEDIUM", trend_strength=50,
                               momentum_bias="NEUTRAL", regime_age=0, transition_prob=0.1)


# ───────────────────────────────────────────────────────────────────────────────
#  NEW MODULE 2: AdaptiveStrategyRouter
# ───────────────────────────────────────────────────────────────────────────────

REGIME_CONFIGS = {
    "STRONG_BULL": {
        "min_rr": 1.2, "sl_atr_mult": 1.0, "tp_style": "SCALED_OUT",
        "signal_threshold": 4.5, "allowed_signals": ["BUY", "STRONG BUY"],
        "forbidden_signals": ["SELL", "STRONG SELL"], "position_size_mult": 1.20,
        "addon_weight_override": {
            "order_block": 0.15, "breakout_retest": 0.40,
            "liquidity_grab": 0.25, "oi_funding": 0.20,
        },
        "lstm_trust": 0.9, "tp_split": (0.4, 0.35, 0.25),
    },
    "TRENDING_UP": {
        "min_rr": 1.5, "sl_atr_mult": 1.1, "tp_style": "TRAIL",
        "signal_threshold": 5.0, "allowed_signals": ["BUY", "STRONG BUY"],
        "forbidden_signals": ["SELL", "STRONG SELL"], "position_size_mult": 1.10,
        "addon_weight_override": {
            "order_block": 0.20, "breakout_retest": 0.30,
            "liquidity_grab": 0.25, "oi_funding": 0.25,
        },
        "lstm_trust": 0.75, "tp_split": (1.0, 0.0, 0.0),
    },
    "BREAKOUT_IMMINENT": {
        "min_rr": 1.8, "sl_atr_mult": 0.9, "tp_style": "WAIT_AND_POUNCE",
        "signal_threshold": 7.0, "allowed_signals": ["BUY", "STRONG BUY"],
        "forbidden_signals": ["SELL", "STRONG SELL"], "position_size_mult": 0.90,
        "addon_weight_override": {
            "order_block": 0.30, "breakout_retest": 0.35,
            "liquidity_grab": 0.25, "oi_funding": 0.10,
        },
        "lstm_trust": 0.6, "tp_split": (1.0, 0.0, 0.0),
    },
    "STRONG_BEAR": {
        "min_rr": 1.2, "sl_atr_mult": 1.0, "tp_style": "SCALED_OUT",
        "signal_threshold": 4.5, "allowed_signals": ["SELL", "STRONG SELL"],
        "forbidden_signals": ["BUY", "STRONG BUY"], "position_size_mult": 1.20,
        "addon_weight_override": {
            "order_block": 0.15, "breakout_retest": 0.40,
            "liquidity_grab": 0.25, "oi_funding": 0.20,
        },
        "lstm_trust": 0.9, "tp_split": (0.4, 0.35, 0.25),
    },
    "TRENDING_DOWN": {
        "min_rr": 1.5, "sl_atr_mult": 1.1, "tp_style": "TRAIL",
        "signal_threshold": 5.0, "allowed_signals": ["SELL", "STRONG SELL"],
        "forbidden_signals": ["BUY", "STRONG BUY"], "position_size_mult": 1.10,
        "addon_weight_override": {
            "order_block": 0.20, "breakout_retest": 0.30,
            "liquidity_grab": 0.25, "oi_funding": 0.25,
        },
        "lstm_trust": 0.75, "tp_split": (1.0, 0.0, 0.0),
    },
    "BREAKDOWN_IMMINENT": {
        "min_rr": 1.8, "sl_atr_mult": 0.9, "tp_style": "WAIT_AND_POUNCE",
        "signal_threshold": 7.0, "allowed_signals": ["SELL", "STRONG SELL"],
        "forbidden_signals": ["BUY", "STRONG BUY"], "position_size_mult": 0.90,
        "addon_weight_override": {
            "order_block": 0.30, "breakout_retest": 0.35,
            "liquidity_grab": 0.25, "oi_funding": 0.10,
        },
        "lstm_trust": 0.6, "tp_split": (1.0, 0.0, 0.0),
    },
    "RANGING_TIGHT": {
        "min_rr": 2.5, "sl_atr_mult": 0.7, "tp_style": "FIXED",
        "signal_threshold": 8.0, "allowed_signals": ["BUY", "SELL"],
        "forbidden_signals": ["STRONG BUY", "STRONG SELL"], "position_size_mult": 0.60,
        "addon_weight_override": {
            "order_block": 0.40, "breakout_retest": 0.10,
            "liquidity_grab": 0.35, "oi_funding": 0.15,
        },
        "lstm_trust": 0.3, "tp_split": (1.0, 0.0, 0.0),
    },
    "RANGING_WIDE": {
        "min_rr": 2.0, "sl_atr_mult": 0.8, "tp_style": "FIXED",
        "signal_threshold": 7.0, "allowed_signals": ["BUY", "SELL"],
        "forbidden_signals": ["STRONG BUY", "STRONG SELL"], "position_size_mult": 0.70,
        "addon_weight_override": {
            "order_block": 0.35, "breakout_retest": 0.15,
            "liquidity_grab": 0.30, "oi_funding": 0.20,
        },
        "lstm_trust": 0.4, "tp_split": (1.0, 0.0, 0.0),
    },
    "VOLATILE_SPIKE": {
        "min_rr": 0.0, "sl_atr_mult": 0.0, "tp_style": "NONE",
        "signal_threshold": 999, "allowed_signals": [],
        "forbidden_signals": ["BUY","SELL","STRONG BUY","STRONG SELL"],
        "position_size_mult": 0.0, "lstm_trust": 0.0, "tp_split": (0.0, 0.0, 0.0),
    },
    "NORMAL": {
        "min_rr": 1.5, "sl_atr_mult": 1.2, "tp_style": "TRAIL",
        "signal_threshold": 5.0, "allowed_signals": ["BUY","SELL","STRONG BUY","STRONG SELL"],
        "forbidden_signals": [], "position_size_mult": 1.0,
        "addon_weight_override": {}, "lstm_trust": 0.5, "tp_split": (1.0, 0.0, 0.0),
    },
}


class AdaptiveStrategyRouter:
    @staticmethod
    def route(regime_state: RegimeState, signal: str, df: pd.DataFrame) -> dict:
        regime = regime_state.primary
        config = REGIME_CONFIGS.get(regime, REGIME_CONFIGS["NORMAL"])
        return {
            "regime": regime,
            "min_rr": config["min_rr"],
            "sl_atr_mult": config["sl_atr_mult"],
            "tp_style": config["tp_style"],
            "signal_threshold": config["signal_threshold"],
            "allowed_signals": config["allowed_signals"],
            "forbidden_signals": config["forbidden_signals"],
            "position_size_mult": config["position_size_mult"],
            "addon_weights": config.get("addon_weight_override", ADDON_WEIGHTS),
            "lstm_trust": config["lstm_trust"],
            "tp_split": config.get("tp_split", (1.0, 0.0, 0.0)),
        }


# ───────────────────────────────────────────────────────────────────────────────
#  NEW MODULE 3: RegimeMemory (Self-Evolving Core)
# ───────────────────────────────────────────────────────────────────────────────

class RegimeMemory:
    def __init__(self, path: str = REGIME_MEMORY_FILE):
        self.path = path
        self.data = self._load()

    def _load(self):
        try:
            with open(self.path) as f:
                return json.load(f)
        except Exception:
            return {
                "regime_performance": {},
                "transition_matrix": {},
                "last_50_regimes": [],
                "meta_version": "v11"
            }

    def _save(self):
        try:
            with open(self.path, "w") as f:
                json.dump(self.data, f, indent=2, default=str)
        except Exception as e:
            print(C.y(f"  ⚠ RegimeMemory save fail: {e}"))

    def record_regime_entry(self, regime: str, timestamp, price: float):
        self.data["last_50_regimes"].append({"regime": regime, "ts": str(timestamp), "price": price})
        if len(self.data["last_50_regimes"]) > 50:
            self.data["last_50_regimes"] = self.data["last_50_regimes"][-50:]
        if len(self.data["last_50_regimes"]) >= 2:
            prev = self.data["last_50_regimes"][-2]["regime"]
            curr = regime
            key = f"{prev}->{curr}"
            self.data["transition_matrix"][key] = self.data["transition_matrix"].get(key, 0) + 1
        self._save()

    def record_trade_outcome(self, regime: str, signal: str, sl_mult: float, outcome: str, pnl_pct: float):
        perf = self.data["regime_performance"].setdefault(regime, {
            "total_trades": 0, "wins": 0, "win_rate": 0, "avg_rr_achieved": 0,
            "best_addon_combo": [], "worst_signal": "", "optimal_threshold": 5.0,
            "sl_mult_performance": {}, "best_sl_mult": 1.2,
            "regime_transition_accuracy": 0,
        })
        perf["total_trades"] += 1
        if pnl_pct > 0:
            perf["wins"] += 1
        perf["win_rate"] = round(perf["wins"] / perf["total_trades"], 3) if perf["total_trades"] > 0 else 0
        sl_key = str(round(sl_mult, 1))
        slm = perf["sl_mult_performance"].setdefault(sl_key, {"trades": 0, "win_rate": 0})
        slm["trades"] += 1
        if pnl_pct > 0:
            slm["win_rate"] = round((slm["win_rate"] * (slm["trades"]-1) + 1) / slm["trades"], 3)
        else:
            slm["win_rate"] = round(slm["win_rate"] * (slm["trades"]-1) / slm["trades"], 3)
        self._save()

    def evolve_thresholds(self) -> dict:
        evolved = {}
        for regime, perf in self.data["regime_performance"].items():
            if perf["total_trades"] < REGIME_MIN_SAMPLES:
                continue
            wr = perf["win_rate"]
            cfg = REGIME_CONFIGS.get(regime, REGIME_CONFIGS["NORMAL"]).copy()
            if wr < 0.40:
                cfg["signal_threshold"] = min(999, cfg["signal_threshold"] * 1.05)
            elif wr > 0.65:
                cfg["signal_threshold"] = max(1.0, cfg["signal_threshold"] * 0.97)
                best_sl = max(perf["sl_mult_performance"].items(), key=lambda x: x[1]["win_rate"])[0] if perf["sl_mult_performance"] else "1.2"
                cfg["sl_atr_mult"] = float(best_sl)
                cfg["best_sl_mult"] = float(best_sl)
                evolved[regime] = cfg
        return evolved

    def predict_next_regime(self, current_regime: str) -> tuple:
        tm = self.data.get("transition_matrix", {})
        candidates = {k: v for k, v in tm.items() if k.startswith(f"{current_regime}->")}
        if not candidates:
            return current_regime, 0.0
        total = sum(candidates.values())
        next_reg, count = max(candidates.items(), key=lambda x: x[1])
        prob = round(count / total, 3) if total > 0 else 0.0
        return next_reg.split("->")[1], prob

    def get_optimal_config(self, regime: str) -> dict:
        evolved = self.evolve_thresholds()
        return evolved.get(regime, REGIME_CONFIGS.get(regime, REGIME_CONFIGS["NORMAL"]))

    def win_rate_gate(self, regime: str) -> bool:
        perf = self.data["regime_performance"].get(regime, {})
        if perf.get("total_trades", 0) < REGIME_MIN_SAMPLES:
            return True
        return perf["win_rate"] >= 0.38

_regime_memory = RegimeMemory()


# ───────────────────────────────────────────────────────────────────────────────
#  NEW MODULE 4: RegimeTransitionDetector
# ───────────────────────────────────────────────────────────────────────────────

@dataclass
class TransitionAlert:
    from_regime: str
    likely_to: str
    confidence: float
    bars_until: int
    action: str
    reason: str


class RegimeTransitionDetector:
    def __init__(self):
        self._prev_regime = None

    def check(self, df1h: pd.DataFrame, regime_state: RegimeState) -> TransitionAlert:
        primary = regime_state.primary
        bb_width = df1h["BB_Width"].values
        bb_pct = (bb_width[-1] < np.percentile(bb_width[-200:], 10)) if len(bb_width) >= 200 else False
        adx_rising = regime_state.trend_strength > 60 and np.polyfit(np.arange(5), df1h["ADX"].tail(5).values, 1)[0] > 0.2
        vol_spike = df1h["Volume_Ratio"].iloc[-1] > 1.5

        if primary.startswith("RANGING") and bb_pct and adx_rising and vol_spike:
            likely = "BREAKOUT_IMMINENT" if regime_state.momentum_bias == "BULL" else "BREAKDOWN_IMMINENT"
            return TransitionAlert(from_regime=primary, likely_to=likely, confidence=0.7,
                                   bars_until=2, action="HOLD", reason="Breakout imminent — wait for confirmation")

        if "TREND" in primary or "BULL" in primary or "BEAR" in primary:
            adx_series = df1h["ADX"].tail(10).values
            adx_peak = np.max(adx_series)
            adx_falling = adx_series[-1] < adx_peak * 0.8
            ema_sep = abs(df1h["EMA_9"].iloc[-1] - df1h["EMA_200"].iloc[-1]) / df1h["close"].iloc[-1] * 100
            vol_shrinking = df1h["Volume_Ratio"].iloc[-1] < 0.8
            if adx_falling and ema_sep < 2 and vol_shrinking:
                return TransitionAlert(from_regime=primary, likely_to="RANGING_WIDE", confidence=0.6,
                                       bars_until=3, action="REDUCE_SIZE", reason="Trend exhaustion detected")

        atr_pct = df1h["ATR_Percentile"].iloc[-1]
        chg_2bars = abs(df1h["close"].iloc[-1] / df1h["close"].iloc[-3] - 1) * 100 if len(df1h) >= 3 else 0
        if atr_pct > 95 or chg_2bars > 6:
            return TransitionAlert(from_regime=primary, likely_to="VOLATILE_SPIKE", confidence=0.9,
                                   bars_until=0, action="HOLD", reason="Extreme volatility spike")

        price = df1h["close"].iloc[-1]
        ema200 = df1h["EMA_200"].iloc[-1]
        if price < ema200 and "BULL" in primary:
            return TransitionAlert(from_regime=primary, likely_to="TRENDING_DOWN", confidence=0.5,
                                   bars_until=4, action="HOLD", reason="Potential regime flip: price below EMA200")

        return TransitionAlert(from_regime=primary, likely_to=primary, confidence=0.2,
                               bars_until=99, action="ALLOW", reason="Stable regime")

    @staticmethod
    def should_skip(alert: TransitionAlert) -> bool:
        return alert.action == "HOLD" or alert.bars_until <= 1


# ───────────────────────────────────────────────────────────────────────────────
#  NEW MODULE 5: MetaSignalFusion
# ───────────────────────────────────────────────────────────────────────────────

@dataclass
class FusedSignal:
    signal: str
    confidence: float
    entry_price: float
    entry_type: str
    quality_score: float
    skip_reason: str
    regime_override: bool
    size_modifier: float
    tp_strategy: str
    trail_activation: float
    trail_distance_atr: float
    tp_split: tuple = (1.0, 0.0, 0.0)


class MetaSignalFusion:
    def __init__(self):
        pass

    def fuse(self, raw_signal: str, regime_state: RegimeState,
             addon_result: dict, whale_score: float,
             lstm_pred: float, structure: dict,
             transition_alert: TransitionAlert,
             htf_bias: str, patterns: dict,
             divergences: tuple, regime_memory: RegimeMemory,
             price: float, df: pd.DataFrame) -> FusedSignal:

        if transition_alert.action == "HOLD" and transition_alert.confidence >= 0.80:
            return FusedSignal(signal="HOLD", confidence=0, entry_price=price, entry_type="NONE",
                               quality_score=0, skip_reason=f"Regime transition: {transition_alert.reason}",
                               regime_override=True, size_modifier=0, tp_strategy="NONE",
                               trail_activation=0, trail_distance_atr=0)

        regime_config = regime_memory.get_optimal_config(regime_state.primary)

        if not regime_memory.win_rate_gate(regime_state.primary):
            return FusedSignal(signal="HOLD", confidence=0, entry_price=price, entry_type="NONE",
                               quality_score=0, skip_reason=f"Regime memory veto: {regime_state.primary} win<38%",
                               regime_override=True, size_modifier=0, tp_strategy="NONE",
                               trail_activation=0, trail_distance_atr=0)

        addon_score = addon_result.get("combined_score", 5.0)
        structure_conf = structure.get("confidence", 50) / 100
        htf_alignment = 1.0 if (htf_bias == "BULL" and "BUY" in raw_signal) or (htf_bias == "BEAR" and "SELL" in raw_signal) else 0.5
        lstm_trust = regime_config.get("lstm_trust", 0.5)
        if lstm_pred:
            pct_diff = abs(lstm_pred - price) / max(price, 1e-10)
            lstm_pred_confidence = min(1.0, pct_diff * 20)
        else:
            lstm_pred_confidence = 0.5

        quality = (regime_state.confidence/100 * 0.2 +
                   addon_score/10 * 0.25 +
                   whale_score/10 * 0.15 +
                   structure_conf * 0.15 +
                   htf_alignment * 0.15 +
                   lstm_trust * lstm_pred_confidence * 0.10) * 10
        quality = round(min(10, quality), 1)

        if quality < QUALITY_SCORE_FLOOR:
            return FusedSignal(signal="HOLD", confidence=0, entry_price=price, entry_type="NONE",
                               quality_score=quality, skip_reason=f"Quality score {quality} < {QUALITY_SCORE_FLOOR}",
                               regime_override=False, size_modifier=0, tp_strategy="NONE",
                               trail_activation=0, trail_distance_atr=0)

        allowed = regime_config.get("allowed_signals", [])
        forbidden = regime_config.get("forbidden_signals", [])
        if raw_signal not in allowed or raw_signal in forbidden:
            return FusedSignal(signal="HOLD", confidence=0, entry_price=price, entry_type="NONE",
                               quality_score=0, skip_reason=f"Signal {raw_signal} forbidden in {regime_state.primary}",
                               regime_override=True, size_modifier=0, tp_strategy="NONE",
                               trail_activation=0, trail_distance_atr=0)

        entry_type = "MARKET"
        addon_ob = addon_result.get("order_block", {}).get("info", {})
        ob_prox = addon_ob.get("prox", "FAR")
        if ob_prox == "INSIDE":
            entry_type = "MARKET"
        elif "TREND" in regime_state.primary:
            entry_type = "LIMIT"
        elif regime_state.primary.startswith("RANGING") and "BREAK" in regime_state.secondary:
            entry_type = "WAIT_RETEST"

        tp_style = regime_config.get("tp_style", "TRAIL")
        tp_split = regime_config.get("tp_split", (1.0, 0.0, 0.0))
        trail_activation = price + (float(df["ATR"].iloc[-1]) * TRAIL_ACTIVATION_ATR) if tp_style == "TRAIL" else 0
        trail_dist_atr = TRAIL_DISTANCE_ATR if tp_style == "TRAIL" else 0

        return FusedSignal(signal=raw_signal, confidence=quality*10, entry_price=price,
                           entry_type=entry_type, quality_score=quality, skip_reason="",
                           regime_override=False, size_modifier=regime_config.get("position_size_mult", 1.0),
                           tp_strategy=tp_style, trail_activation=trail_activation, trail_distance_atr=trail_dist_atr,
                           tp_split=tp_split)


# ───────────────────────────────────────────────────────────────────────────────
#  NEW MODULE 6: AdaptiveTPEngine (upgrade ProbabilityTPEngine)
# ───────────────────────────────────────────────────────────────────────────────

class AdaptiveTPEngine(ProbabilityTPEngine):
    def compute(self, price: float, df: pd.DataFrame, signal: str,
                obs: list | None = None,
                eq_hi: list | None = None, eq_lo: list | None = None,
                min_rr: float = MIN_RISK_REWARD,
                regime_config: dict | None = None,
                fused_signal: FusedSignal | None = None,
                regime_name: str = "") -> tuple:

        if fused_signal is None or fused_signal.signal == "HOLD":
            return super().compute(price, df, signal, obs=obs, eq_hi=eq_hi, eq_lo=eq_lo, min_rr=min_rr)

        tp_strategy = fused_signal.tp_strategy
        atr = float(df["ATR"].iloc[-1])
        sl_mult = regime_config.get("sl_atr_mult", 1.2) if regime_config else 1.2
        is_bull = "BUY" in signal
        d = 1 if is_bull else -1
        sl = price - d * atr * sl_mult

        if tp_strategy == "SCALED_OUT":
            base_tp1 = price + d * atr * 1.5
            candidates = super()._swing_levels(df) + super()._fibonacci_levels(df)
            valid = [c for c in candidates if (is_bull and c["price"] > price + atr*0.5) or (not is_bull and c["price"] < price - atr*0.5)]
            valid.sort(key=lambda x: abs(x["price"] - price))
            tp2 = valid[0]["price"] if len(valid) > 0 else None
            tp3 = valid[1]["price"] if len(valid) > 1 else None
            tp_levels = {"TP1": round(base_tp1, 6), "TP2": round(tp2, 6) if tp2 else None, "TP3": round(tp3, 6) if tp3 else None}
        elif tp_strategy == "TRAIL":
            base_tp = price + d * atr * 2.0
            tp_levels = {"TP1": round(base_tp, 6), "TP2": None, "TP3": None}
        elif tp_strategy == "FIXED":
            bb_upper = float(df["BB_Upper"].iloc[-1])
            bb_lower = float(df["BB_Lower"].iloc[-1])
            tp = bb_upper if is_bull else bb_lower
            tp_levels = {"TP1": round(tp, 6), "TP2": None, "TP3": None}
        elif tp_strategy == "WAIT_AND_POUNCE":
            bb_width = float(df["BB_Width"].iloc[-1])
            squeeze_range = bb_width * price
            tp = price + d * squeeze_range * 2
            tp_levels = {"TP1": round(tp, 6), "TP2": None, "TP3": None}
        else:
            tp_levels = {"TP1": price, "TP2": None, "TP3": None}

        ai = _default_ai()
        ai.update({"regime": regime_name, "tp_strategy": tp_strategy,
                   "tp1_type": tp_strategy, "sl_mult_used": sl_mult,
                   "rr_ratio": round(abs(tp_levels["TP1"] - price) / max(abs(sl - price), 1e-10), 2)})
        return sl, tp_levels, regime_name, ai


_adaptive_tp = AdaptiveTPEngine()


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                      CANDLESTICK PATTERNS                                  ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def detect_patterns(df: pd.DataFrame) -> dict:
    if len(df) < 5: return {}
    o,h,l,c=(df["open"].values,df["high"].values,df["low"].values,df["close"].values)
    def body(i): return abs(c[i]-o[i])
    def rng(i):  return max(h[i]-l[i],1e-10)
    def bull(i): return c[i]>o[i]
    def bear(i): return c[i]<o[i]
    def uw(i):   return h[i]-max(c[i],o[i])
    def lw(i):   return min(c[i],o[i])-l[i]
    avg=np.mean([body(x) for x in range(-min(10,len(df)),0)]) or 1e-10
    i,j,k=-1,-2,-3
    pats={"bullish_engulfing":bool(bear(j) and bull(i) and c[i]>o[j] and o[i]<c[j] and body(i)>body(j)*1.1),
          "bearish_engulfing":bool(bull(j) and bear(i) and c[i]<o[j] and o[i]>c[j] and body(i)>body(j)*1.1),
          "hammer":           bool(lw(i)>=body(i)*2 and uw(i)<=body(i)*0.3 and body(i)>0 and rng(i)>avg*0.5),
          "shooting_star":    bool(uw(i)>=body(i)*2 and lw(i)<=body(i)*0.3 and body(i)>0 and rng(i)>avg*0.5),
          "doji":             bool(body(i)<=rng(i)*0.1 and rng(i)>avg*0.3),
          "morning_star":     len(df)>=5 and bool(bear(k) and body(k)>avg*0.8 and body(j)<avg*0.3 and bull(i) and c[i]>(o[k]+c[k])/2),
          "evening_star":     len(df)>=5 and bool(bull(k) and body(k)>avg*0.8 and body(j)<avg*0.3 and bear(i) and c[i]<(o[k]+c[k])/2)}
    active=[k_ for k_,v in pats.items() if v]
    print(C.m(f"\n  🕯  Patterns: {', '.join(active)}") if active else C.dim("  🕯  No patterns detected"))
    return pats


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                       DIVERGENCE DETECTOR                                  ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def detect_divergences(df: pd.DataFrame, lookback: int = 30) -> tuple:
    if len(df) < lookback: return False,False,["Insufficient data"]
    rec=df.tail(lookback).reset_index(drop=True)
    price,rsi,obv=rec["close"].values,rec["RSI_14"].values,rec["OBV"].values
    sw=max(3,lookback//5); notes=[]
    def swings(arr,w):
        hi,lo=[],[]
        for i in range(w,len(arr)-w):
            s=arr[i-w:i+w+1]
            if arr[i]>=np.max(s)-1e-10: hi.append(i)
            if arr[i]<=np.min(s)+1e-10: lo.append(i)
        return hi,lo
    ph,pl=swings(price,sw); bull_div=bear_div=False
    if len(pl)>=2:
        p1,p2=pl[-2],pl[-1]
        if price[p2]<price[p1]*0.999 and rsi[p2]>rsi[p1]+1.5:
            bull_div=True; notes.append("Bullish RSI divergence (price↓ RSI↑)")
    if len(ph)>=2:
        p1,p2=ph[-2],ph[-1]
        if price[p2]>price[p1]*1.001 and rsi[p2]<rsi[p1]-1.5:
            bear_div=True; notes.append("Bearish RSI divergence (price↑ RSI↓)")
    half=lookback//2; pt=price[-1]-price[-half] if half<len(price) else 0
    ot=obv[-1]-obv[-half] if half<len(obv) else 0
    if pt<-price[-1]*0.005 and ot>0: bull_div=True; notes.append("Bullish OBV divergence")
    elif pt>price[-1]*0.005 and ot<0: bear_div=True; notes.append("Bearish OBV divergence")
    for n in notes: print(C.b(f"  ↕  {n}"))
    if not notes: print(C.dim("  ↕  No divergences detected"))
    return bull_div,bear_div,notes


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                      MULTI-TIMEFRAME BIAS                                  ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def get_htf_bias(df4: pd.DataFrame | None) -> tuple:
    if df4 is None or df4.empty or len(df4) < 10: return "NEUTRAL","4H unavailable"
    last=df4.iloc[-1]; price=float(last["close"])
    checks=[price>float(last["EMA_9"]),price>float(last["EMA_50"]),price>float(last["EMA_200"]),
            float(last["MACD"])>float(last["MACD_Signal"]),float(last["RSI_14"])>55,
            int(last["ST_Direction"])==1,float(last["ADX_Pos"])>float(last["ADX_Neg"])]
    bull=sum(checks); tot=len(checks)
    if   bull>=int(tot*0.7): return "BULL",f"4H Bullish ({bull}/{tot}) ADX={last['ADX']:.1f}"
    elif tot-bull>=int(tot*0.7): return "BEAR",f"4H Bearish ({tot-bull}/{tot}) ADX={last['ADX']:.1f}"
    return "NEUTRAL",f"4H Neutral B={bull} Br={tot-bull} ADX={last['ADX']:.1f}"


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                         MARKET POWER ENGINE                                ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def market_power(df: pd.DataFrame, htf_bias: str="NEUTRAL",
                 strength_score: float=50, signal: str="HOLD") -> tuple:
    last=df.iloc[-1]; score=0.0; max_s=0.0; log=[]; is_bull="BUY" in signal
    def _add(pts,mx,label): nonlocal score,max_s; score+=pts; max_s+=mx; log.append((pts,mx,label))
    adx=float(last["ADX"])
    pts=25 if adx>=50 else 22 if adx>=40 else 18 if adx>=30 else 12 if adx>=22 else 5 if adx>=15 else 0
    _add(pts,25,f"ADX {adx:.1f}")
    p,e9,e50,e200=(float(last["close"]),float(last["EMA_9"]),float(last["EMA_50"]),float(last["EMA_200"]))
    if is_bull: pts=20 if p>e9>e50>e200 else 14 if p>e9>e50 else 7 if p>e9 else 0
    else:       pts=20 if p<e9<e50<e200 else 14 if p<e9<e50 else 7 if p<e9 else 0
    _add(pts,20,"EMA alignment")
    if (htf_bias=="BULL" and is_bull) or (htf_bias=="BEAR" and not is_bull): pts=15
    elif htf_bias=="NEUTRAL": pts=6
    else: pts=0
    _add(pts,15,f"4H bias {htf_bias}")
    st_ok=(float(last["ST_Direction"])==1 and is_bull) or (float(last["ST_Direction"])==-1 and not is_bull)
    _add(10 if st_ok else 0,10,"Supertrend")
    mh=float(last["MACD_Hist"]); sl_v=mh-(float(df["MACD_Hist"].iloc[-2]) if len(df)>=2 else 0)
    mb=float(last["MACD"])>float(last["MACD_Signal"])
    if   (is_bull and mb and sl_v>0) or (not is_bull and not mb and sl_v<0): pts=10
    elif (is_bull and mb) or (not is_bull and not mb):                         pts=6
    else:                                                                       pts=0
    _add(pts,10,"MACD")
    vp=float(last["Volume_Percentile"]) if "Volume_Percentile" in last.index else 50.0
    pts=10 if vp>=90 else 8 if vp>=75 else 5 if vp>=55 else 2 if vp>=30 else 0
    _add(pts,10,f"Vol pct {vp:.0f}th")
    rsi=float(last["RSI_14"]); r_lo=float(last["Dynamic_RSI_Lower"]); r_hi=float(last["Dynamic_RSI_Upper"])
    if   is_bull and r_lo<=rsi<=r_lo+10:     pts=5
    elif not is_bull and r_hi-10<=rsi<=r_hi: pts=5
    elif 45<=rsi<=55:                         pts=1
    else:                                     pts=2
    _add(pts,5,f"RSI {rsi:.1f}")
    mfi=float(last["MFI_14"]) if "MFI_14" in last.index else 50.0
    if   is_bull and mfi<30:    pts=5; _add(pts,5,f"MFI oversold {mfi:.0f}")
    elif not is_bull and mfi>70:pts=5; _add(pts,5,f"MFI overbought {mfi:.0f}")
    elif 40<=mfi<=60:            pts=2; _add(pts,5,f"MFI neutral {mfi:.0f}")
    else:                        pts=1; _add(pts,5,f"MFI {mfi:.0f}")
    _add(min(5,round(strength_score/20)),5,"Strength carry")
    final=round(min(100.0,(score/max(max_s,0.01))*100),1)
    if   final>=86: label,tier="🚀 SUPREME",6
    elif final>=71: label,tier="🔥 V.STRONG",5
    elif final>=56: label,tier="💪 STRONG",4
    elif final>=41: label,tier="🟡 MODERATE",3
    elif final>=26: label,tier="⚠  WEAK",2
    else:           label,tier="🚨 RISKY",1
    print(section(f"Market Power  {final:.0f}/100  —  {label}","⚡"))
    for pts_,mx_,lbl_ in log:
        col=C.g if pts_>=mx_*0.7 else C.y if pts_>=mx_*0.4 else C.r
        print(f"    {lbl_:<25} {col(f'{pts_:>2}/{mx_}')}")
    return final,label,tier


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                        STRENGTH SCORE                                      ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def compute_strength(df: pd.DataFrame, predicted_price: float | None=None,
                     pred_sigma: float=0.0, patterns: dict | None=None,
                     bull_div: bool=False, bear_div: bool=False,
                     htf_bias: str="NEUTRAL", whale_score: float=5.0,
                     structure: dict | None=None) -> tuple:
    if patterns is None: patterns={}
    last=df.iloc[-1]; price=float(last["close"]); comps={}; notes=[]
    def _c(name,pts,mx,note): comps[name]=(pts,mx); notes.append(note)
    e9,e50,e200=float(last["EMA_9"]),float(last["EMA_50"]),float(last["EMA_200"])
    if   price>e9>e50>e200: _c("EMA",2.5,2.5,"EMA perfect bull +2.5")
    elif price>e9>e50:       _c("EMA",1.8,2.5,"EMA partial bull +1.8")
    elif price>e9:            _c("EMA",0.8,2.5,"EMA above EMA9 +0.8")
    elif price<e9<e50<e200:  _c("EMA",2.5,2.5,"EMA perfect bear +2.5")
    elif price<e9<e50:        _c("EMA",1.8,2.5,"EMA partial bear +1.8")
    else:                     _c("EMA",0.8,2.5,"EMA below EMA9 +0.8")
    adx=float(last["ADX"])
    if   adx>=40: _c("ADX",2.0,2.0,f"ADX monster {adx:.1f} +2.0")
    elif adx>=30: _c("ADX",1.5,2.0,f"ADX v.strong {adx:.1f} +1.5")
    elif adx>=25: _c("ADX",1.0,2.0,f"ADX strong {adx:.1f} +1.0")
    elif adx>=18: _c("ADX",0.4,2.0,f"ADX weak {adx:.1f} +0.4")
    else:         _c("ADX",0.0,2.0,f"ADX no-trend {adx:.1f} +0")
    vp=float(last["Volume_Percentile"]) if "Volume_Percentile" in last.index else 50.0
    if   vp>=90: _c("Volume",2.0,2.0,f"Vol extreme pct={vp:.0f} +2.0")
    elif vp>=75: _c("Volume",1.5,2.0,f"Vol strong pct={vp:.0f} +1.5")
    elif vp>=55: _c("Volume",1.0,2.0,f"Vol above avg pct={vp:.0f} +1.0")
    elif vp>=30: _c("Volume",0.4,2.0,f"Vol normal pct={vp:.0f} +0.4")
    else:        _c("Volume",0.0,2.0,f"Vol low pct={vp:.0f} +0")
    rsi=float(last["RSI_14"]); r_lo=float(last["Dynamic_RSI_Lower"]); r_hi=float(last["Dynamic_RSI_Upper"])
    mid_lo=r_lo+(r_hi-r_lo)*0.25; mid_hi=r_hi-(r_hi-r_lo)*0.25
    if   r_lo<=rsi<=mid_lo:    _c("RSI",1.5,1.5,f"RSI buy zone {rsi:.1f} +1.5")
    elif mid_hi<=rsi<=r_hi:    _c("RSI",1.5,1.5,f"RSI sell zone {rsi:.1f} +1.5")
    elif rsi<r_lo or rsi>r_hi: _c("RSI",0.3,1.5,f"RSI extreme {rsi:.1f} +0.3")
    else:                       _c("RSI",0.7,1.5,f"RSI neutral {rsi:.1f} +0.7")
    mfi=float(last["MFI_14"]) if "MFI_14" in last.index else 50.0
    adx_bull=float(last["ADX_Pos"])>float(last["ADX_Neg"])
    if   adx_bull and mfi<35:    _c("MFI",1.0,1.0,f"MFI OS confirm {mfi:.0f} +1.0")
    elif not adx_bull and mfi>65:_c("MFI",1.0,1.0,f"MFI OB confirm {mfi:.0f} +1.0")
    elif 45<=mfi<=55:             _c("MFI",0.3,1.0,f"MFI neutral {mfi:.0f} +0.3")
    else:                         _c("MFI",0.5,1.0,f"MFI trending {mfi:.0f} +0.5")
    mh=float(last["MACD_Hist"]); sl_v=mh-(float(df["MACD_Hist"].iloc[-2]) if len(df)>=3 else 0)
    if   (mh>0 and sl_v>0) or (mh<0 and sl_v<0): _c("MACD",1.0,1.0,"MACD accelerating +1.0")
    elif mh!=0:                                    _c("MACD",0.4,1.0,"MACD weak +0.4")
    else:                                          _c("MACD",0.0,1.0,"MACD flat +0")
    sk,sd=float(last["Stoch_K"]),float(last["Stoch_D"])
    if   sk<25 and sk>sd: _c("Stoch",1.0,1.0,f"Stoch bull cross {sk:.1f} +1.0")
    elif sk>75 and sk<sd: _c("Stoch",1.0,1.0,f"Stoch bear cross {sk:.1f} +1.0")
    elif 40<=sk<=60:       _c("Stoch",0.3,1.0,f"Stoch mid {sk:.1f} +0.3")
    else:                  _c("Stoch",0.5,1.0,f"Stoch trending {sk:.1f} +0.5")
    st_ok=(float(last["ST_Direction"])==1 and adx_bull) or (float(last["ST_Direction"])==-1 and not adx_bull)
    _c("Supertrend",1.0 if st_ok else 0.0,1.0,"Supertrend aligned +1.0" if st_ok else "Supertrend opposing +0")
    lstm_confirms=False
    if predicted_price is not None:
        pct=(predicted_price-price)/price*100; conf_ok=pred_sigma<abs(pct)*0.5 if pred_sigma>0 else True
        if adx_bull and pct>0.3 and conf_ok:
            _c("LSTM",1.5,1.5,f"LSTM ensemble BUY {pct:+.2f}% σ={pred_sigma:.3f} +1.5"); lstm_confirms=True
        elif not adx_bull and pct<-0.3 and conf_ok:
            _c("LSTM",1.5,1.5,f"LSTM ensemble SELL {pct:+.2f}% σ={pred_sigma:.3f} +1.5"); lstm_confirms=True
        else:
            _c("LSTM",0.0,1.5,f"LSTM no confirm {pct:+.2f}% σ={pred_sigma:.3f} +0")
    bull_pats=["bullish_engulfing","hammer","morning_star"]
    bear_pats=["bearish_engulfing","shooting_star","evening_star"]
    found_pat=next((p for p in bull_pats+bear_pats if patterns.get(p)),None)
    _c("Pattern",1.0 if found_pat else 0.0,1.0,f"Candle: {found_pat} +1.0" if found_pat else "Candle: none +0")
    if   bull_div: _c("Diverge",1.0,1.0,"Divergence: bullish +1.0")
    elif bear_div: _c("Diverge",1.0,1.0,"Divergence: bearish +1.0")
    else:          _c("Diverge",0.0,1.0,"Divergence: none +0")
    if (htf_bias=="BULL" and adx_bull) or (htf_bias=="BEAR" and not adx_bull): _c("4H",1.0,1.0,"4H bias aligned +1.0")
    elif htf_bias=="NEUTRAL": _c("4H",0.3,1.0,"4H bias neutral +0.3")
    else:                     _c("4H",0.0,1.0,"4H bias against +0")
    if   whale_score>=7.5: _c("Whale",1.0,1.0,f"Whale confirmed {whale_score:.1f}/10 +1.0")
    elif whale_score>=5.0: _c("Whale",0.6,1.0,f"Whale partial {whale_score:.1f}/10 +0.6")
    elif whale_score>=3.0: _c("Whale",0.3,1.0,f"Whale neutral {whale_score:.1f}/10 +0.3")
    else:                  _c("Whale",0.0,1.0,f"Whale opposing {whale_score:.1f}/10 +0")
    if structure:
        stype=structure.get("type","RANGING"); sconf=structure.get("confidence",0)
        if (stype=="UPTREND" and adx_bull) or (stype=="DOWNTREND" and not adx_bull):
            pts=min(1.0,sconf/100); _c("Structure",pts,1.0,f"Structure aligned {stype} {sconf}% +{pts:.2f}")
        elif stype in ("BREAKOUT","BREAKDOWN"): _c("Structure",0.5,1.0,f"Structure {stype} +0.5")
        else:                                   _c("Structure",0.0,1.0,f"Structure ranging +0")
    earned=sum(v[0] for v in comps.values()); total=sum(v[1] for v in comps.values())
    final=round(min(100.0,(earned/max(total,0.1))*100),1)
    lbl=("🔥 MONSTER" if final>=80 else "💪 STRONG" if final>=65 else "🟡 MODERATE" if final>=45 else "😐 WEAK")
    print(section(f"Strength Score  {final}/100  —  {lbl}","🎯"))
    for n in notes: print(C.dim(f"    {n}"))
    return final,lbl,notes,lstm_confirms


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                        SIGNAL GENERATION  (v10)                            ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def generate_signal(df: pd.DataFrame, actual_price_chg_pct: float,
                    predicted_price: float | None=None, htf_bias: str="NEUTRAL",
                    patterns: dict | None=None, bull_div: bool=False, bear_div: bool=False,
                    whale_score: float=5.0, whale_label: str="", structure: dict | None=None,
                    addon_score: float=5.0, regime: str="NORMAL",
                    threshold_override: float | None = None) -> tuple:
    if patterns is None: patterns={}
    if actual_price_chg_pct < -3.5:
        return "HOLD",[],0.0,f"Hard guard: actual drop {actual_price_chg_pct:.1f}% > 3.5%"
    if regime=="VOLATILE_SPIKE":
        return "HOLD",[],0.0,"Regime: VOLATILE_SPIKE — skip entry"
    if regime.startswith("RANGING") and abs(actual_price_chg_pct) < 0.8:
        return "HOLD",[],0.0,"Regime: RANGING — no momentum"

    last=df.iloc[-1]; adx=float(last["ADX"]); adxp=float(last["ADX_Pos"]); adxn=float(last["ADX_Neg"])
    rsi=float(last["RSI_14"]); r_lo=float(last["Dynamic_RSI_Lower"]); r_hi=float(last["Dynamic_RSI_Upper"])
    sk,sd=float(last["Stoch_K"]),float(last["Stoch_D"]); close=float(last["close"])
    vp=float(last["Volume_Percentile"]) if "Volume_Percentile" in last.index else 50.0
    vwap=float(last["VWAP"]) if "VWAP" in last.index else close
    cvd20=float(df["CVD_20"].iloc[-1]) if "CVD_20" in df.columns else 0.0
    macd_b=float(last["MACD"])>float(last["MACD_Signal"]); st_bull=int(last["ST_Direction"])==1
    mfi=float(last["MFI_14"]) if "MFI_14" in last.index else 50.0

    def side_score(weights):
        t,a=0.0,[]
        for name,(cond,w) in weights.items():
            if cond: t+=w; a.append(name)
        return t,a

    buy_w={"macd_cross":(macd_b,2.0),"ema_align":(close>float(last["EMA_9"])>float(last["EMA_50"]),2.0),
           "adx_bull":(adx>22 and adxp>adxn,1.5),"rsi_zone":(rsi<r_lo,1.0),"mfi_os":(mfi<35,1.0),
           "stoch_bull":(sk<30 and sk>sd,1.0),"vol_spike":(vp>=55,1.0),"supertrend":(st_bull,1.0),
           "vwap_above":(close>vwap,0.5),"lstm_bull":(predicted_price is not None and predicted_price>close*1.003,1.5),
           "bull_pat":(any(patterns.get(p,False) for p in ["bullish_engulfing","hammer","morning_star"]),1.0),
           "bull_div":(bull_div,1.0),"htf_bull":(htf_bias=="BULL",1.0),"cvd_bull":(cvd20>0,0.5)}
    sell_w={"macd_cross":(not macd_b,2.0),"ema_align":(close<float(last["EMA_9"])<float(last["EMA_50"]),2.0),
            "adx_bear":(adx>22 and adxn>adxp,1.5),"rsi_zone":(rsi>r_hi,1.0),"mfi_ob":(mfi>65,1.0),
            "stoch_bear":(sk>70 and sk<sd,1.0),"vol_spike":(vp>=55,1.0),"supertrend":(not st_bull,1.0),
            "vwap_below":(close<vwap,0.5),"lstm_bear":(predicted_price is not None and predicted_price<close*0.997,1.5),
            "bear_pat":(any(patterns.get(p,False) for p in ["bearish_engulfing","shooting_star","evening_star"]),1.0),
            "bear_div":(bear_div,1.0),"htf_bear":(htf_bias=="BEAR",1.0),"cvd_bear":(cvd20<0,0.5)}

    buy_s,buy_a=side_score(buy_w); sell_s,sell_a=side_score(sell_w)
    max_pts=sum(w for _,w in buy_w.values())

    if htf_bias=="BEAR" and buy_s>sell_s:   buy_s*=0.75
    elif htf_bias=="BULL" and sell_s>buy_s: sell_s*=0.75

    print(section("Signal Scoring","⚖"))
    print(row("BUY  score", C.g(f"{buy_s:.1f}")))
    print(row("SELL score", C.r(f"{sell_s:.1f}")))

    if regime.startswith("RANGING"): strong_threshold=8.0; normal_threshold=6.0
    else:                             strong_threshold=7.5; normal_threshold=5.0

    if threshold_override is not None:
        normal_threshold = threshold_override
    else:
        normal_threshold = _journal.adaptive_signal_threshold("BUY", normal_threshold)

    if buy_s>sell_s:
        fs=buy_s; active=buy_a
        raw=("STRONG BUY" if fs>=strong_threshold else "BUY" if fs>=normal_threshold else "HOLD")
    else:
        fs=sell_s; active=sell_a
        raw=("STRONG SELL" if fs>=strong_threshold else "SELL" if fs>=normal_threshold else "HOLD")

    if raw=="HOLD": return "HOLD",[],max(buy_s,sell_s),f"Score too low (B:{buy_s:.1f} S:{sell_s:.1f})"

    if whale_score<2.5:
        return "HOLD",[],0.0,f"BLOCKED: whale {whale_score:.1f} opposing"
    if structure:
        allowed,sreason=structure_gate(structure,raw)
        if not allowed: return "HOLD",[],0.0,f"BLOCKED: {sreason}"
        print(C.g(f"  ✓  Structure: {sreason}"))
    if addon_score<ADDON_HARD_BLOCK:
        return "HOLD",[],0.0,f"BLOCKED: addon {addon_score:.1f} < {ADDON_HARD_BLOCK}"
    if ADDON_HARD_BLOCK<=addon_score<ADDON_SOFT_DOWNGRADE and raw in ("STRONG BUY","STRONG SELL"):
        raw=raw.replace("STRONG ",""); print(C.y(f"  ⚠  ADDON DOWNGRADE → {raw}"))
    final_sig=raw
    if 2.5<=whale_score<3.5 and raw in ("STRONG BUY","STRONG SELL"):
        final_sig=raw.replace("STRONG ",""); print(C.y(f"  ⚠  Whale downgrade → {final_sig}"))

    return final_sig,active,fs,f"Score {fs:.1f} | addon:{addon_score:.1f} | adaptive_thr:{normal_threshold:.1f}"


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                     CONFIDENCE TIER                                        ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def confidence_tier(w_score,strength,rr,htf_bias,signal,mp=50,whale=5.0,struct_conf=0,addon_score=5.0) -> tuple:
    pts=0
    if   w_score>=9.0: pts+=3
    elif w_score>=7.5: pts+=2
    elif w_score>=5.5: pts+=1
    if   strength>=75: pts+=3
    elif strength>=60: pts+=2
    elif strength>=45: pts+=1
    if   rr>=3.0: pts+=2
    elif rr>=2.0: pts+=1
    if signal!="HOLD":
        d="BULL" if "BUY" in signal else "BEAR"
        if   htf_bias==d:          pts+=2
        elif htf_bias=="NEUTRAL":  pts+=1
    if   mp>=70: pts+=2
    elif mp>=50: pts+=1
    if whale>=7.5:      pts+=1
    if struct_conf>=75: pts+=1
    if   addon_score>=8.5: pts+=3
    elif addon_score>=7.5: pts+=2
    elif addon_score>=5.0: pts+=1
    if   pts>=15: return "A+","🏆 Supreme setup"
    elif pts>=12: return "A","🏆 Premium confidence"
    elif pts>=8:  return "B","✅ Good — above average"
    elif pts>=5:  return "C","🟡 Moderate — trade with caution"
    else:         return "D","🚫 Weak — consider skipping"


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                        POSITION SIZING                                     ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def position_size(entry: float, sl: float, balance: float=ACCOUNT_BALANCE,
                  risk_pct: float=RISK_PER_TRADE, tier: str="B",
                  mp: float=50, whale: float=5.0, addon_score: float=5.0) -> dict:
    tier_m={"A+":1.0,"A":1.0,"B":0.75,"C":0.5,"D":0.25}
    pow_m=round(max(0.5,min(1.0,mp/100)),3)
    whl_m=round(max(0.85,min(1.15,0.85+(whale/10)*WHALE_SIZE_WEIGHT*2)),3)
    addon_m=round(max(0.80,min(1.20,0.80+(addon_score/10)*ADDON_SIZE_WEIGHT)),3)
    adj=risk_pct*tier_m.get(tier,0.5)*pow_m*whl_m*addon_m
    sl_dist=abs(entry-sl)/max(entry,1e-10)
    if sl_dist<1e-6: return {"error":"SL too close to entry"}
    risk_amt=balance*adj; pos_usdt=risk_amt/sl_dist; pos_unit=pos_usdt/max(entry,1e-10)
    return {"balance":round(balance,2),"risk_pct":round(adj*100,3),"risk_amt":round(risk_amt,2),
            "pos_usdt":round(pos_usdt,2),"pos_units":round(pos_unit,6),"entry":round(entry,6),
            "sl":round(sl,6),"sl_dist":round(sl_dist*100,2),
            "pow_mult":pow_m,"whl_mult":whl_m,"addon_mult":addon_m}


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                SKLEARN ENSEMBLE  (MLP + GradientBoosting + ExtraTrees)    ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def prepare_sequences(df: pd.DataFrame, seq_len: int = SEQUENCE_LENGTH) -> tuple:
    feats = [c for c in ["close","RSI_14","MACD","MACD_Hist","ATR","OBV",
                         "EMA_9","BB_Width","Volume_Ratio","ADX","Stoch_K","ST_Direction","MFI_14"]
             if c in df.columns]
    print(C.dim(f"  Sklearn features ({len(feats)}): {', '.join(feats[:7])}{'…' if len(feats)>7 else ''}"))

    scaler = MinMaxScaler((0,1))
    scaled = scaler.fit_transform(df[feats])

    X, y = [], []
    for i in range(seq_len, len(scaled)):
        X.append(scaled[i-seq_len:i].flatten())
        y.append(scaled[i, 0])

    X = np.array(X)
    y = np.array(y)
    close_scaler = MinMaxScaler((0,1)).fit(df[["close"]])
    return X, y, scaler, close_scaler, feats


def _cache_key_sklearn(X: np.ndarray, model_name: str) -> str:
    h = hashlib.sha256(X.astype(np.float32).tobytes()).hexdigest()[:14]
    return f"{COIN_SYMBOL.replace('/','_')}_{h}_{model_name}"


def train_sklearn_ensemble(X, y) -> tuple:
    models = []
    mlp = MLPRegressor(
        hidden_layer_sizes=(128, 64, 32),
        activation='relu',
        solver='adam',
        alpha=1e-4,
        batch_size=64,
        learning_rate_init=0.001,
        max_iter=200,
        early_stopping=True,
        validation_fraction=0.15,
        random_state=42,
        verbose=False
    )
    gbr = GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.8,
        random_state=43,
        verbose=0
    )
    etr = ExtraTreesRegressor(
        n_estimators=200,
        max_depth=10,
        min_samples_split=5,
        random_state=44,
        n_jobs=-1,
        verbose=0
    )

    model_list = [
        ("MLP", mlp),
        ("GBR", gbr),
        ("ETR", etr),
    ]

    for name, mdl in model_list:
        ck = _cache_key_sklearn(X, name)
        cp = os.path.join(MODEL_CACHE_DIR, f"m_{ck}.joblib")
        if USE_MODEL_CACHE and os.path.exists(cp):
            try:
                mdl = joblib.load(cp)
                print(C.dim(f"  [{name}] cache hit"))
                models.append(mdl)
                continue
            except Exception:
                pass

        print(C.dim(f"  [{name}] training..."))
        t0 = time.time()
        mdl.fit(X, y)
        print(C.g(f"  [{name}] trained in {time.time()-t0:.0f}s"))

        if USE_MODEL_CACHE:
            try:
                joblib.dump(mdl, cp)
            except Exception as e:
                print(C.y(f"  Cache save fail: {e}"))
        models.append(mdl)

    hist_obj = type("H", (), {"history": {"loss": [0.0], "mae": [0.0], "val_loss": [0.0]}})()
    return models, hist_obj


def _predict_sklearn_ensemble(models, X, scaler, feats) -> tuple:
    last_seq = X[-1].reshape(1, -1)
    preds = []
    for mdl in models:
        pred = mdl.predict(last_seq)[0]
        dum = np.zeros((1, len(feats)))
        dum[0, 0] = pred
        price_pred = scaler.inverse_transform(dum)[0, 0]
        preds.append(price_pred)

    median_pred = float(np.median(preds))
    sigma = float(np.std(preds))
    print(C.dim(f"  Ensemble: {[f'{p:.5f}' for p in preds]}  median:{median_pred:.5f}  σ:{sigma:.5f}"))
    return median_pred, sigma


def pre_screen(df: pd.DataFrame) -> tuple:
    last=df.iloc[-1]; fails=[]
    if float(last["ADX"])<15:                  fails.append(f"ADX={last['ADX']:.1f}<15")
    if float(last["BB_Width"])<float(df["BB_Width"].quantile(0.20)): fails.append("BB_Width<20th")
    vp=float(last["Volume_Percentile"]) if "Volume_Percentile" in last.index else 50.0
    if vp<20:                                  fails.append(f"VolPct={vp:.0f}<20")
    if 48<=float(last["RSI_14"])<=52:          fails.append(f"RSI_flat({last['RSI_14']:.1f})")
    if abs(float(last["MACD_Hist"]))<float(last["ATR"])*0.01: fails.append("MACD_Hist≈0")
    if len(fails)>=3:
        reason=", ".join(fails); print(C.y(f"  ⚡ Pre-screen HOLD: {reason}")); return True,f"Pre-screened: {reason}"
    return False,"Training required"


def _skip_history():
    return type("H",(),{"history":{"loss":[0.0],"mae":[0.0],"val_loss":[0.0]}})()


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                          MAIN RUN BOT  (v11 integrated, now with args)     ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def run_bot(symbol: str = None, balance: float = None) -> dict:
    sym = symbol if symbol else COIN_SYMBOL
    bal = balance if balance else ACCOUNT_BALANCE

    wt     = WhaleTracker(_engine.pool)
    result = {}
    regime_brain = RegimeBrain()
    transition_detector = RegimeTransitionDetector()
    fusion_engine = MetaSignalFusion()

    try:
        _journal.print_summary()

        df1h = get_data(sym, TIMEFRAME_MAIN)
        spreads = _engine.get_spread(sym)
        if spreads:
            print(section("Market Spreads","💰"))
            for ex,d in list(spreads.items())[:3]:
                print(row(ex.upper(), C.dim(f"Bid={d['bid']:.5f} Ask={d['ask']:.5f} Spr={d['spread_pct']:.4f}%")))

        print(section("4H Higher Timeframe","📡"))
        try:
            df4h               = get_data(sym, TIMEFRAME_HIGHER)
            df4h               = compute_indicators(df4h)
            htf_bias,htf_desc  = get_htf_bias(df4h)
        except Exception as e:
            print(C.y(f"  ⚠ 4H failed: {e}")); df4h=None; htf_bias="NEUTRAL"; htf_desc="Unavailable"
        print(row("4H Bias", C.g(htf_bias) if htf_bias=="BULL" else C.r(htf_bias) if htf_bias=="BEAR" else C.y(htf_bias)))

        df1h = compute_indicators(df1h)
        current_price  = float(df1h["close"].iloc[-1])
        prev_close     = float(df1h["close"].iloc[-2]) if len(df1h)>=2 else current_price
        actual_chg_pct = (current_price-prev_close)/max(prev_close,1e-10)*100

        structure = analyze_structure(df1h)

        print(section("Regime Brain (v11)","🧠"))
        regime_state = regime_brain.detect(df1h, df4h, structure=structure)
        print(row("Primary",      C.w(regime_state.primary)))
        print(row("Secondary",    C.dim(regime_state.secondary)))
        print(row("Confidence",   f"{regime_state.confidence:.0f}%"))
        print(row("Vol Tier",     regime_state.volatility_tier))
        print(row("Trend Str",    f"{regime_state.trend_strength:.0f}"))
        print(row("Momentum",     regime_state.momentum_bias))
        print(row("Age",          f"{regime_state.regime_age} bars"))
        print(row("Trans Prob",   f"{regime_state.transition_prob:.0%}"))

        transition_alert = transition_detector.check(df1h, regime_state)
        print(section("Regime Transition","🔮"))
        print(row("From → To",  C.y(f"{transition_alert.from_regime} → {transition_alert.likely_to}")))
        print(row("Action",     C.r(transition_alert.action) if transition_alert.action!="ALLOW" else C.g(transition_alert.action)))
        print(row("Reason",     transition_alert.reason))
        if regime_state.transition_prob > 0.85 or transition_alert.action == "HOLD" or transition_alert.bars_until <= 0.85):
            print(C.r("  🚫 REGIME GATE: transition imminent — skip signal"))
            result = {"signal": "HOLD", "reason": "Regime transition gate",
                      "transition": f"{transition_alert.from_regime}→{transition_alert.likely_to}",
                      "entry_type": "N/A"}
            return result

        route_config = AdaptiveStrategyRouter.route(regime_state, "", df1h)
        print(section("Adaptive Router","🧭"))
        print(row("TP Style", route_config["tp_style"]))
        print(row("Signal Thr", f"{route_config['signal_threshold']:.1f}"))
        print(row("Size Mult", f"{route_config['position_size_mult']:.2f}x"))
        print(row("TP Split", str(route_config.get("tp_split", (1,0,0)))))

        print(section("Patterns & Divergences","🕯"))
        patterns             = detect_patterns(df1h)
        bull_div,bear_div,_  = detect_divergences(df1h)

        print(section("Market Structure","🏗"))
        sc_ = C.g if structure["type"] in ("UPTREND","BREAKOUT") else C.r if structure["type"] in ("DOWNTREND","BREAKDOWN") else C.y
        print(row("Type",     sc_(f"{structure['type']} ({structure['confidence']}%)")))
        print(row("HH/HL",    C.dim(f"{structure['hh']} / {structure['hl']}")))
        print(row("LH/LL",    C.dim(f"{structure['lh']} / {structure['ll']}")))

        print(section("Whale Tracker","🐋"))
        ob_res = wt.analyze_ob(sym, current_price)
        wc_res = wt.detect_whales(df1h)
        print(row("OB Signal",  C.g(ob_res["ob_note"]) if "BULL" in ob_res["ob_signal"]
                                 else C.r(ob_res["ob_note"]) if "BEAR" in ob_res["ob_signal"]
                                 else C.dim(ob_res["ob_note"])))
        print(row("CVD Trend",  C.g(wc_res["cvd_trend"]) if wc_res["cvd_trend"]=="BULL"
                                 else C.r(wc_res["cvd_trend"]) if wc_res["cvd_trend"]=="BEAR"
                                 else C.y(wc_res["cvd_trend"])))

        last_adx   = float(df1h["ADX"].iloc[-1])
        sklearn_gated = last_adx < 20 or regime_state.primary in ("RANGING_TIGHT", "RANGING_WIDE", "VOLATILE_SPIKE")
        skip,skip_reason = pre_screen(df1h)

        print(section("Sklearn Ensemble (MLP+GBR+ETR)","🧠"))
        pred_price=current_price; pred_sigma=0.0; chg_pct=0.0
        feats=["close"]; hist_obj=_skip_history(); X=np.zeros((1, SEQUENCE_LENGTH, 1)); models_list=[]

        if sklearn_gated:
            print(C.y(f"  ⚡ Sklearn GATED — regime {regime_state.primary} / ADX={last_adx:.1f}<20"))
            skip=True; skip_reason=f"Sklearn gated regime={regime_state.primary}"
        elif skip:
            print(C.y(f"  ⚡ Pre-screened: {skip_reason}"))
        else:
            X,y,scaler,cs,feats=prepare_sequences(df1h, SEQUENCE_LENGTH)
            models_list,hist_obj=train_sklearn_ensemble(X,y)
            if models_list:
                pred_price,pred_sigma=_predict_sklearn_ensemble(models_list,X,scaler,feats)
                chg_pct=(pred_price-current_price)/current_price*100

        print(row("Current",   C.w(f"{current_price:.6f} USDT")))
        print(row("Predicted", (C.g if chg_pct>0 else C.r)(f"{pred_price:.6f} ({chg_pct:+.3f}%)")))
        print(row("σ",         C.dim(f"{pred_sigma:.5f} USDT")))

        signal_threshold_override = route_config["signal_threshold"]
        sig_pre,_,_,_ = generate_signal(
            df1h, actual_chg_pct,
            predicted_price=pred_price if not skip else None,
            htf_bias=htf_bias, patterns=patterns, bull_div=bull_div, bear_div=bear_div,
            whale_score=5.0, structure=structure,
            addon_score=5.0, regime=regime_state.primary,
            threshold_override=signal_threshold_override)

        whale_score,whale_label,whale_notes = wt.score(ob_res,wc_res, sig_pre)
        addon_engine = AddonEngine(_engine.pool)
        addon_weights_override = route_config.get("addon_weights", ADDON_WEIGHTS)
        addon_result = addon_engine.run_all(df1h, sym, sig_pre, weights_override=addon_weights_override)
        addon_score = addon_result["combined_score"]

        signal,active,w_score,sig_reason = generate_signal(
            df1h, actual_chg_pct,
            predicted_price=pred_price if not skip else None,
            htf_bias=htf_bias, patterns=patterns, bull_div=bull_div, bear_div=bear_div,
            whale_score=whale_score, whale_label=whale_label, structure=structure,
            addon_score=addon_score, regime=regime_state.primary,
            threshold_override=signal_threshold_override)

        fused = fusion_engine.fuse(
            raw_signal=signal,
            regime_state=regime_state,
            addon_result=addon_result,
            whale_score=whale_score,
            lstm_pred=pred_price if not skip else current_price,
            structure=structure,
            transition_alert=transition_alert,
            htf_bias=htf_bias,
            patterns=patterns,
            divergences=(bull_div,bear_div),
            regime_memory=_regime_memory,
            price=current_price,
            df=df1h
        )
        print(section("Meta Signal Fusion","🔀"))
        print(row("Fused Signal", C.w(fused.signal)))
        print(row("Quality",      C.g(f"{fused.quality_score:.1f}") if fused.quality_score>=QUALITY_SCORE_FLOOR else C.r(f"{fused.quality_score:.1f}")))
        print(row("Entry Type",   fused.entry_type))
        print(row("TP Strategy",  fused.tp_strategy))
        print(row("TP Split",     f"{fused.tp_split[0]:.0%}/{fused.tp_split[1]:.0%}/{fused.tp_split[2]:.0%}"))
        if fused.skip_reason:
            print(row("Skip Reason", C.r(fused.skip_reason)))

        final_signal = fused.signal
        if final_signal == "HOLD":
            result = {"signal": "HOLD", "reason": fused.skip_reason,
                      "transition": f"{transition_alert.from_regime}→{transition_alert.likely_to}",
                      "entry_type": fused.entry_type}
            return result

        strength,s_lbl,s_notes,lstm_confirms = compute_strength(
            df1h, predicted_price=pred_price if not skip else None,
            pred_sigma=pred_sigma, patterns=patterns, bull_div=bull_div, bear_div=bear_div,
            htf_bias=htf_bias, whale_score=whale_score, structure=structure)

        cached_mp = market_power(df1h, htf_bias, strength, final_signal)
        mp_val,mp_label,mp_tier = cached_mp

        ob_module_info = addon_result.get("order_block",{}).get("info",{})
        all_obs = ob_module_info.get("all_obs",[])
        lg_module_info = addon_result.get("liquidity_grab",{}).get("info",{})
        pools = lg_module_info.get("pools",{})
        eq_hi = pools.get("eq_hi",[])
        eq_lo = pools.get("eq_lo",[])

        regime_config = _regime_memory.get_optimal_config(regime_state.primary)
        stop_loss, tp_levels, regime, ai = _adaptive_tp.compute(
            current_price, df1h, final_signal,
            obs=all_obs if final_signal!="HOLD" else [],
            eq_hi=eq_hi, eq_lo=eq_lo,
            min_rr=route_config["min_rr"],
            regime_config=regime_config,
            fused_signal=fused,
            regime_name=regime_state.primary)

        rr = ai.get("rr_ratio",0)
        tier,tier_desc = confidence_tier(w_score, strength, rr, htf_bias, final_signal,
                                        mp_val, whale_score, structure.get("confidence",0), addon_score)
        pos = position_size(current_price, stop_loss, bal, RISK_PER_TRADE,
                            tier, mp_val, whale_score, addon_score=addon_score)

        tp_split = fused.tp_split if fused else (1.0, 0.0, 0.0)
        if final_signal != "HOLD" and tp_split[0] < 1.0:
            total_units = pos["pos_units"]
            pos["tp1_units"] = round(total_units * tp_split[0], 6)
            pos["tp2_units"] = round(total_units * tp_split[1], 6) if tp_levels.get("TP2") else 0
            pos["tp3_units"] = round(total_units * tp_split[2], 6) if tp_levels.get("TP3") else 0
        else:
            pos["tp1_units"] = pos["pos_units"]
            pos["tp2_units"] = 0
            pos["tp3_units"] = 0

        _regime_memory.record_regime_entry(regime_state.primary, datetime.now(timezone.utc), current_price)

        result = {"signal":final_signal,"tier":tier,"entry":current_price,"sl":stop_loss,
                  "tp_levels":tp_levels,"rr":rr,"strength":strength,"market_power":mp_val,
                  "whale_score":whale_score,"whale_label":whale_label,
                  "structure":structure["type"],"structure_conf":structure["confidence"],
                  "addon_score":addon_score,"addon_label":addon_result["combined_label"],
                  "addon_gate":addon_result["gate_action"],"lstm_sigma":pred_sigma,"position":pos,
                  "ptp_tp1_type":ai.get("tp1_type","N/A"),"ptp_tp1_score":ai.get("tp1_score",0),
                  "regime": regime_state.primary, "quality": fused.quality_score,
                  "transition": f"{transition_alert.from_regime}→{transition_alert.likely_to}",
                  "entry_type": fused.entry_type,
                  "tp_split": f"{tp_split[0]:.0%}/{tp_split[1]:.0%}/{tp_split[2]:.0%}"}

    except Exception as e:
        print(C.r(f"\n  CRITICAL ERROR: {e}")); traceback.print_exc()
    finally:
        _engine.cleanup(); print(C.dim("\n  Engine cleaned up."))

    return result


# ═══════════════════════════════════════════════════
#  STREAMLIT ENTRY POINT — At the very bottom
# ═══════════════════════════════════════════════════

st.set_page_config(
    page_title="CRYPTO BOT v11",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    show_login()
else:
    show_dashboard()
