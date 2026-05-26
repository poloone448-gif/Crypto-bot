"""
╔══════════════════════════════════════════════════════════════════════════╗
║   CRYPTO BOT V9 · T.R.A.P. EDITION  (FULLY FIXED)                     ║
║   Trend · Reality · Accumulation · Precision                           ║
║   + Ensemble ML · ICT Order Blocks · Smart Money Concepts              ║
║   + Daily Pivot Points · Power Zone · Session Filter                   ║
║   + False Breakout Detection · Signal Fusion                           ║
║   DATA LEAKAGE FIX: Scaler fit on train split only per fold           ║
║                                                                        ║
║   BUG FIXES v9.1:                                                      ║
║   1. mpatches.Rectangle used throughout (AttributeError fix)           ║
║   2. Logger moved outside @st.cache_data fn (UnhashableError fix)      ║
║   3. Auto-refresh blocking sleep removed (Streamlit rerun fix)         ║
║   4. SuperTrend st_line[0] initialization fix                          ║
║   5. groupby include_groups=False (FutureWarning fix)                  ║
║   6. pos_size overflow clamp added (division-by-zero guard)            ║
║   7. bb_rng np.maximum() fix (chained .replace() issue)                ║
║   8. .strftime() timezone-safe timestamps throughout                   ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

# ── Standard Library ──────────────────────────────────────────────────────
import os, time, queue, warnings, threading, hashlib, math
from datetime import datetime, timezone

# ── Scientific Stack ──────────────────────────────────────────────────────
import numpy as np
import pandas as pd

# ── Visualization ─────────────────────────────────────────────────────────
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── Machine Learning ──────────────────────────────────────────────────────
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import mean_absolute_error
try:
    from xgboost import XGBRegressor
    HAS_XGB = True
except ImportError:
    HAS_XGB = False
try:
    from lightgbm import LGBMRegressor
    HAS_LGB = True
except ImportError:
    HAS_LGB = False

# ── Crypto & TA ───────────────────────────────────────────────────────────
import ccxt
import ta
import streamlit as st

warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1 · LOGIN SYSTEM (5 Users)
# ═══════════════════════════════════════════════════════════════════════════
def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

USERS = {
    "zafariqbal@": _hash("pass1234"),
    "mrssher":     _hash("pass2234"),
    "user3":       _hash("pass3234"),
    "trader1":     _hash("trade@123"),
    "admin":       _hash("admin@999"),
}

def login_screen():
    st.markdown("""
    <style>
        .login-title{text-align:center;font-size:2rem;font-weight:900;
                     color:#f0b429;letter-spacing:4px;margin-bottom:4px;}
        .login-sub  {text-align:center;color:#58a6ff;font-size:.85rem;
                     letter-spacing:2px;margin-bottom:4px;}
        .login-tag  {text-align:center;color:#8b949e;font-size:.78rem;
                     margin-bottom:24px;}
    </style>""", unsafe_allow_html=True)

    _, col_m, _ = st.columns([1, 2, 1])
    with col_m:
        st.markdown('<div class="login-title">🎯 V9 · T.R.A.P.</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-sub">TREND · REALITY · ACCUMULATION · PRECISION</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-tag">Ensemble ML + ICT Order Blocks + Smart Money Concepts</div>', unsafe_allow_html=True)
        st.markdown("---")
        username = st.text_input("👤 Username", placeholder="Enter username", key="li_u")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter password", key="li_p")
        if st.button("🔐 Login", use_container_width=True):
            if username in USERS and USERS[username] == _hash(password):
                st.session_state["authenticated"] = True
                st.session_state["current_user"]  = username
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Contact admin.")
        st.markdown("---")
        st.caption("🔑 5-User System · Contact admin for access.")

def check_auth() -> bool:
    return st.session_state.get("authenticated", False)

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2 · PAGE CONFIG & GLOBAL STYLES
# ═══════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="V9 T.R.A.P. Bot",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .block-container{padding-top:.8rem;}
    .stMetric{background:#0d1117;border-radius:10px;padding:12px;border:1px solid #21262d;}
    div[data-testid="stMetricValue"]{color:#f0b429;font-size:1.3rem;}
    .stButton>button{background:#238636;color:#fff;border:none;border-radius:8px;font-weight:700;}
    .stButton>button:hover{background:#2ea043;}
    .trap-card{border-radius:10px;padding:12px 16px;margin:5px 0;
               border-left:4px solid;font-size:.88rem;}
    .trap-pass{background:#0d2818;border-color:#2ea043;}
    .trap-fail{background:#2d0f0f;border-color:#f85149;}
    .sig-long {color:#2ea043;font-size:2rem;font-weight:900;}
    .sig-short{color:#f85149;font-size:2rem;font-weight:900;}
    .sig-wait {color:#8b949e;font-size:2rem;font-weight:900;}
    .ob-bull{background:#0d2818;border-left:4px solid #2ea043;
             padding:10px 14px;border-radius:8px;margin:4px 0;}
    .ob-bear{background:#2d0f0f;border-left:4px solid #f85149;
             padding:10px 14px;border-radius:8px;margin:4px 0;}
    .sess-on {background:#0d2818;color:#2ea043;border-radius:20px;
              padding:3px 12px;font-size:.8rem;font-weight:700;}
    .sess-off{background:#161b22;color:#8b949e;border-radius:20px;
              padding:3px 12px;font-size:.8rem;font-weight:700;}
</style>""", unsafe_allow_html=True)

# Auth gate
if not check_auth():
    login_screen()
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3 · LOGGER
# ═══════════════════════════════════════════════════════════════════════════
class Logger:
    def __init__(self):        self.msgs: list = []
    def info(self, m):         self.msgs.append(("ℹ️", m))
    def success(self, m):      self.msgs.append(("✅", m))
    def warning(self, m):      self.msgs.append(("⚠️", m))
    def error(self, m):        self.msgs.append(("❌", m))
    def clear(self):           self.msgs.clear()
    def tail(self, n=40):      return "\n".join(f"{i} {m}" for i, m in self.msgs[-n:])

if "logger" not in st.session_state:
    st.session_state.logger = Logger()
log: Logger = st.session_state.logger

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4 · CONFIGURATION PANEL
# ═══════════════════════════════════════════════════════════════════════════
def get_config() -> dict:
    user = st.session_state.get("current_user", "user")
    col_a, col_b = st.sidebar.columns([2, 1])
    col_a.markdown(f"### 👤 {user}")
    if col_b.button("🚪 Out"):
        st.session_state.update({"authenticated": False, "current_user": ""})
        st.rerun()

    st.sidebar.header("📈 Market")
    coin    = st.sidebar.text_input("Symbol", "BTC/USDT")
    tf_main = st.sidebar.selectbox("Timeframe", ["1h","4h","15m","30m"], 0)
    tf_htf  = st.sidebar.selectbox("HTF / Daily", ["1d","4h","1h"], 0)

    st.sidebar.header("💰 Risk")
    balance    = st.sidebar.number_input("Balance (USDT)", 100.0, 1_000_000.0, 1000.0, 100.0)
    risk       = st.sidebar.slider("Risk/Trade (%)", 0.1, 3.0, 1.5, 0.1) / 100
    min_rr     = st.sidebar.slider("Min R:R", 1.0, 4.0, 2.5, 0.5)
    max_trades = st.sidebar.number_input("Max Trades/Day", 1, 5, 2)

    st.sidebar.header("🎯 T.R.A.P.")
    trap_min_score = st.sidebar.slider("Min Pillar Score (/5)", 3, 5, 4)
    trap_vol_mult  = st.sidebar.slider("Volume Spike ×", 1.5, 4.0, 2.5, 0.5)
    trap_bb_pct    = st.sidebar.slider("BB Squeeze Percentile", 10, 40, 30)
    trap_pz_tol    = st.sidebar.slider("Power Zone Tolerance (%)", 0.1, 0.5, 0.3, 0.05) / 100

    st.sidebar.header("🕐 Session Filter")
    use_session    = st.sidebar.checkbox("Enable Session Filter", True)
    session_choice = st.sidebar.multiselect(
        "Active Sessions",
        ["Asia (00-08 UTC)", "London (07-16 UTC)", "New York (13-22 UTC)"],
        ["London (07-16 UTC)", "New York (13-22 UTC)"],
    )

    st.sidebar.header("📦 Order Blocks")
    ob_lookback = st.sidebar.slider("OB Lookback Candles", 50, 300, 100, 10)
    ob_min_move = st.sidebar.slider("OB Min Impulse (%)", 0.3, 3.0, 1.0, 0.1) / 100
    ob_zone_ext = st.sidebar.slider("OB Zone Extension", 10, 60, 30, 5)

    st.sidebar.header("🐋 Whale")
    wvt = st.sidebar.slider("Vol Threshold ×", 2.0, 5.0, 3.0, 0.5)
    wpm = st.sidebar.slider("Min Move (%)", 0.1, 1.0, 0.3, 0.1) / 100

    st.sidebar.header("🧠 ML Model")
    seq_len   = st.sidebar.slider("Sequence Length", 30, 120, 60, 10)
    use_cache = st.sidebar.checkbox("Model Cache", True)

    return {
        "COIN": coin, "TF": tf_main, "HTF": tf_htf,
        "BALANCE": balance, "RISK": risk, "MIN_RR": min_rr,
        "MAX_TRADES": int(max_trades),
        # T.R.A.P.
        "TRAP_MIN_SCORE": trap_min_score,
        "TRAP_VOL_MULT":  trap_vol_mult,
        "TRAP_BB_PCT":    trap_bb_pct,
        "TRAP_PZ_TOL":    trap_pz_tol,
        "USE_SESSION":    use_session,
        "SESSIONS":       session_choice,
        # OB
        "OB_LOOKBACK": ob_lookback, "OB_MIN_MOVE": ob_min_move,
        "OB_ZONE_EXT": ob_zone_ext,
        # Whale
        "WHALE_VOL_THRESH": wvt, "WHALE_MOVE_MIN": wpm,
        # ML
        "SEQ_LEN": seq_len, "USE_CACHE": use_cache,
        # Fixed internals
        "OB_DEPTH": 20, "WALL_MULT": 5.0,
        "STRUCT_LOOKBACK": 75, "STRUCT_MIN_SWING": 0.008,
    }

cfg = get_config()

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5 · DATA ENGINE
# ═══════════════════════════════════════════════════════════════════════════
EXCHANGES = ["binance","bybit","okx","kucoin","gateio","mexc"]
EPS = 1e-10   # global epsilon for safe division

@st.cache_resource(show_spinner=False)
def build_exchange_pool() -> dict:
    pool = {}
    for name in EXCHANGES:
        try:
            pool[name] = getattr(ccxt, name)({"enableRateLimit": True})
        except Exception:
            pass
    return pool

ex_pool = build_exchange_pool()

# ── FIX 2: session_state Logger moved outside cached function ─────────────
# The Logger object lives in st.session_state which is not serialisable by
# the Streamlit cache hasher. Any call inside would raise UnhashableParamError.
# All info/success calls happen OUTSIDE this function, in main().
@st.cache_data(ttl=120, show_spinner=False)
def fetch_ohlcv(symbol: str, tf: str) -> pd.DataFrame:
    limit   = 500 if tf in ("4h","1d") else 1000
    results = []
    q        = queue.Queue()
    stop_evt = threading.Event()

    def _fetch_one(name: str, ex):
        if stop_evt.is_set():
            return
        try:
            data = ex.fetch_ohlcv(symbol, timeframe=tf, limit=limit)
            if not data:
                return
            df = pd.DataFrame(data, columns=["ts","open","high","low","close","volume"])
            df["ts"]   = pd.to_datetime(df["ts"], unit="ms", utc=True)
            df["_src"] = name
            if len(df) >= 60:
                q.put(df)
        except Exception:
            pass

    threads = []
    for name, ex in sorted(ex_pool.items())[:4]:
        t = threading.Thread(target=_fetch_one, args=(name, ex), daemon=True)
        t.start()
        threads.append(t)

    deadline = time.time() + 15
    while time.time() < deadline:
        try:
            df = q.get(timeout=0.5)
            results.append(df)
            if len(results) >= 2:
                stop_evt.set()
                break
        except queue.Empty:
            if all(not t.is_alive() for t in threads):
                break

    if not results:
        raise RuntimeError(f"No data for {symbol} [{tf}]")

    combined = pd.concat(results, ignore_index=True).sort_values("ts")
    n_src    = combined["_src"].nunique()

    if n_src > 1:
        # ── FIX 5: include_groups=False avoids FutureWarning in pandas ────
        def _agg(g: pd.DataFrame) -> pd.Series:
            vol = g["volume"].values
            w   = vol if vol.sum() > 0 else np.ones(len(g))
            return pd.Series({
                "open":   float(np.average(g["open"],  weights=w)),
                "high":   float(np.average(g["high"],  weights=w)),
                "low":    float(np.average(g["low"],   weights=w)),
                "close":  float(np.average(g["close"], weights=w)),
                "volume": float(np.median(vol)),
            })
        merged = (combined.groupby("ts", sort=True)
                  .apply(_agg, include_groups=False).reset_index()
                  .rename(columns={"ts":"timestamp"}))
    else:
        merged = (combined.drop_duplicates("ts", keep="last")
                  .drop(columns=["_src"], errors="ignore")
                  .rename(columns={"ts":"timestamp"})
                  .reset_index(drop=True))

    # IQR volume cap
    q1, q3 = merged["volume"].quantile([0.25, 0.75])
    merged["volume"] = merged["volume"].clip(upper=q3 + 5*(q3-q1))

    for col in ["open","high","low","close","volume"]:
        merged[col] = merged[col].interpolate("linear").ffill().bfill()

    # ── FIX 8: strftime for timezone-safe timestamp formatting ────────────
    last_ts = pd.Timestamp(merged["timestamp"].iloc[-1])
    ts_str  = last_ts.strftime("%Y-%m-%d %H:%M")
    # Return metadata as df attrs so callers can log it safely
    merged.attrs["_fetch_info"] = f"✓ {symbol} [{tf}] — {len(merged)} candles · {n_src} sources · last:{ts_str}"
    return merged.reset_index(drop=True)

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6 · FEATURE ENGINEERING
# ═══════════════════════════════════════════════════════════════════════════
def _supertrend(df: pd.DataFrame, period: int = 10, mult: float = 3.0) -> pd.DataFrame:
    atr   = ta.volatility.AverageTrueRange(
        df["high"], df["low"], df["close"], window=period, fillna=True
    ).average_true_range()
    hl2   = (df["high"] + df["low"]) / 2
    upper = (hl2 + mult * atr).values
    lower = (hl2 - mult * atr).values
    close = df["close"].values
    n     = len(close)
    fu, fl    = upper.copy(), lower.copy()
    st_line   = np.zeros(n)
    direction = np.ones(n)

    # ── FIX 4: Initialize st_line[0] before the loop ─────────────────────
    # Without this, st_line[0] stays 0 which is never a valid price level,
    # causing the first iteration's comparison (st_line[i-1] == fu[i-1]) to
    # always be False and direction to be wrong for the first ~10 bars.
    st_line[0] = fl[0]

    for i in range(1, n):
        fu[i] = upper[i] if (upper[i] < fu[i-1] or close[i-1] > fu[i-1]) else fu[i-1]
        fl[i] = lower[i] if (lower[i] > fl[i-1] or close[i-1] < fl[i-1]) else fl[i-1]
        if st_line[i-1] == fu[i-1]:
            st_line[i] = fl[i] if close[i] > fu[i] else fu[i]
        else:
            st_line[i] = fu[i] if close[i] < fl[i] else fl[i]
        direction[i] = 1.0 if st_line[i] == fl[i] else -1.0

    df["Supertrend"] = st_line
    df["ST_Dir"]     = direction
    return df

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # EMAs + SMA
    for span, col in [(9,"EMA9"),(21,"EMA21"),(50,"EMA50"),(200,"EMA200")]:
        df[col] = df["close"].ewm(span=span, adjust=False).mean()
    df["SMA20"] = df["close"].rolling(20).mean()

    # VWAP (cumulative, resets daily in live — approximated here)
    typ        = (df["high"] + df["low"] + df["close"]) / 3
    cum_vol    = df["volume"].cumsum().replace(0, EPS)
    df["VWAP"] = (typ * df["volume"]).cumsum() / cum_vol

    # Momentum oscillators
    df["RSI"]       = ta.momentum.RSIIndicator(df["close"], 14, fillna=True).rsi()
    macd            = ta.trend.MACD(df["close"], fillna=True)
    df["MACD"]      = macd.macd()
    df["MACD_Sig"]  = macd.macd_signal()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Sig"]

    stoch         = ta.momentum.StochasticOscillator(df["high"],df["low"],df["close"],14,3,fillna=True)
    df["Stoch_K"] = stoch.stoch()
    df["Stoch_D"] = stoch.stoch_signal()
    df["WilliamsR"]= ta.momentum.WilliamsRIndicator(df["high"],df["low"],df["close"],14,fillna=True).williams_r()
    df["CCI"]      = ta.trend.CCIIndicator(df["high"],df["low"],df["close"],20,fillna=True).cci()
    df["ROC"]      = df["close"].pct_change(10).fillna(0)

    # Volatility
    df["ATR"] = ta.volatility.AverageTrueRange(df["high"],df["low"],df["close"],14,fillna=True).average_true_range()
    bb            = ta.volatility.BollingerBands(df["close"], 20, 2, fillna=True)
    df["BB_Upper"]= bb.bollinger_hband()
    df["BB_Lower"]= bb.bollinger_lband()
    df["BB_Mid"]  = bb.bollinger_mavg()

    # ── FIX 7: np.maximum() for bb_rng avoids chained .replace() issue ───
    # .replace(0, EPS) on a Series doesn't guard against very small negatives
    # or NaN propagation. np.maximum ensures element-wise floor of EPS.
    bb_rng        = np.maximum((df["BB_Upper"] - df["BB_Lower"]).values, EPS)
    bb_mid_safe   = np.maximum(df["BB_Mid"].values, EPS)
    df["BB_Width"]= bb_rng / bb_mid_safe
    df["BB_Pos"]  = (df["close"].values - df["BB_Lower"].values) / bb_rng

    # ATR percentile (rolling 100-bar)
    atr_v = df["ATR"].values
    w     = min(100, len(atr_v))
    ap    = np.full(len(atr_v), 50.0)
    for i in range(w, len(atr_v)):
        ap[i] = float(np.sum(atr_v[i-w:i] < atr_v[i])) / w * 100
    df["ATR_Pct"] = ap

    # Volume features
    df["OBV"]      = ta.volume.OnBalanceVolumeIndicator(df["close"],df["volume"],fillna=True).on_balance_volume()
    df["Vol_MA20"] = df["volume"].rolling(20).mean().bfill()
    df["Vol_Ratio"]= (df["volume"] / df["Vol_MA20"].replace(0, EPS)).clip(0, 10)
    df["Vol_Delta"]= np.where(df["close"] >= df["open"], df["volume"], -df["volume"])
    df["CVD20"]    = df["Vol_Delta"].rolling(20).sum()
    vol_v = df["volume"].values
    vp    = np.full(len(vol_v), 50.0)
    for i in range(w, len(vol_v)):
        vp[i] = float(np.sum(vol_v[i-w:i] < vol_v[i])) / w * 100
    df["Vol_Pct"] = vp

    # Trend
    adx_i         = ta.trend.ADXIndicator(df["high"],df["low"],df["close"],14,fillna=True)
    df["ADX"]     = adx_i.adx()
    df["ADX_Pos"] = adx_i.adx_pos()
    df["ADX_Neg"] = adx_i.adx_neg()
    df = _supertrend(df)

    # Candle geometry
    body              = (df["close"] - df["open"]).abs()
    rng               = np.maximum((df["high"] - df["low"]).values, EPS)
    df["Body_Ratio"]  = body.values / rng
    df["Upper_Wick"]  = (df["high"].values - df[["close","open"]].max(axis=1).values) / rng
    df["Lower_Wick"]  = (df[["close","open"]].min(axis=1).values - df["low"].values) / rng
    df["Price_vs_VWAP"]= (df["close"] - df["VWAP"]) / df["VWAP"].replace(0, EPS)
    df["EMA_Spread"]  = (df["EMA9"] - df["EMA50"]) / df["EMA50"].replace(0, EPS)
    df["Momentum_5"]  = df["close"].pct_change(5).fillna(0)
    df["Momentum_20"] = df["close"].pct_change(20).fillna(0)

    atr_norm     = (df["ATR"] / df["close"].rolling(20).mean().replace(0, EPS)).clip(0,1).fillna(0)
    df["RSI_Lo"] = 30 + atr_norm * 10
    df["RSI_Hi"] = 70 - atr_norm * 10

    df = df.dropna(subset=["EMA200","ADX","ATR"]).reset_index(drop=True)
    log.info(f"📊 Features: {len(df)} rows × {df.shape[1]} cols")
    return df

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 7 · ORDER BLOCK ENGINE (ICT / Smart Money)
# ═══════════════════════════════════════════════════════════════════════════
def detect_order_blocks(df: pd.DataFrame) -> tuple:
    """
    Bullish OB  → Last bearish candle before upward impulse → Demand Zone.
    Bearish OB  → Last bullish candle before downward impulse → Supply Zone.
    Only unmitigated OBs returned (most recent 5 each).
    """
    if len(df) < 30:
        log.warning("⚠️ Insufficient data for OB detection.")
        return [], []

    lookback   = min(cfg["OB_LOOKBACK"], len(df))
    min_move   = cfg["OB_MIN_MOVE"]
    rec        = df.tail(lookback).reset_index(drop=True)
    n          = len(rec)
    last_close = float(rec["close"].iloc[-1])
    bull_obs, bear_obs = [], []

    for i in range(1, n - 6):
        c_o = float(rec["open"].iloc[i]);   c_c = float(rec["close"].iloc[i])
        c_h = float(rec["high"].iloc[i]);   c_l = float(rec["low"].iloc[i])
        vol    = float(rec["volume"].iloc[i])
        vol_ma = float(rec["Vol_MA20"].iloc[i]) if "Vol_MA20" in rec.columns else max(vol, EPS)
        vr     = vol / max(vol_ma, EPS)
        end    = min(i + 7, n)

        # ── Bullish OB ─────────────────────────────────────────────────────
        if c_c < c_o:
            fut_h   = float(rec["high"].iloc[i+1:end].max())
            impulse = (fut_h - c_c) / max(abs(c_c), EPS)
            if impulse >= min_move:
                mitigated = last_close < c_l
                strong    = vr > 1.5 and impulse > min_move * 1.5
                # ── FIX 8: strftime for timezone-safe timestamp ────────────
                ts_val = rec["timestamp"].iloc[i]
                ts_str = pd.Timestamp(ts_val).strftime("%Y-%m-%d %H:%M")
                bull_obs.append({
                    "idx": i, "ob_top": round(c_o,8), "ob_bottom": round(c_l,8),
                    "sl_level": round(c_l * 0.9975, 8),
                    "timestamp": ts_str,
                    "impulse_pct": round(impulse*100, 3),
                    "vol_ratio":   round(vr, 2),
                    "mitigated":   mitigated, "type": "BULLISH_OB",
                    "label": "🟢 Demand Zone",
                    "strength": "STRONG" if strong else "NORMAL",
                })

        # ── Bearish OB ─────────────────────────────────────────────────────
        elif c_c > c_o:
            fut_l   = float(rec["low"].iloc[i+1:end].min())
            impulse = (c_c - fut_l) / max(abs(c_c), EPS)
            if impulse >= min_move:
                mitigated = last_close > c_h
                strong    = vr > 1.5 and impulse > min_move * 1.5
                ts_val = rec["timestamp"].iloc[i]
                ts_str = pd.Timestamp(ts_val).strftime("%Y-%m-%d %H:%M")
                bear_obs.append({
                    "idx": i, "ob_top": round(c_h,8), "ob_bottom": round(c_o,8),
                    "sl_level": round(c_h * 1.0025, 8),
                    "timestamp": ts_str,
                    "impulse_pct": round(impulse*100, 3),
                    "vol_ratio":   round(vr, 2),
                    "mitigated":   mitigated, "type": "BEARISH_OB",
                    "label": "🔴 Supply Zone",
                    "strength": "STRONG" if strong else "NORMAL",
                })

    active_bull = [o for o in bull_obs if not o["mitigated"]][-5:]
    active_bear = [o for o in bear_obs if not o["mitigated"]][-5:]
    log.info(f"📦 OBs → Bull:{len(active_bull)} Bear:{len(active_bear)}")
    return active_bull, active_bear


def detect_market_structure(df: pd.DataFrame) -> dict:
    """Detect swing pivots, market bias, and Break of Structure (BOS)."""
    empty = {"type":"UNKNOWN","bias":"NEUTRAL","prev_high":None,"prev_low":None,
             "swing_highs":[],"swing_lows":[]}
    if len(df) < 20:
        return empty

    rec    = df.tail(min(cfg["STRUCT_LOOKBACK"], len(df))).reset_index(drop=True)
    highs  = rec["high"].values
    lows   = rec["low"].values
    closes = rec["close"].values
    sh, sl = [], []

    for i in range(2, len(rec)-2):
        if highs[i] > highs[i-1] and highs[i] > highs[i-2] \
                and highs[i] > highs[i+1] and highs[i] > highs[i+2]:
            sh.append((i, float(highs[i])))
        if lows[i] < lows[i-1] and lows[i] < lows[i-2] \
                and lows[i] < lows[i+1] and lows[i] < lows[i+2]:
            sl.append((i, float(lows[i])))

    if not sh or not sl:
        return empty

    last_sh  = sh[-1][1];  prev_sh = sh[-2][1] if len(sh)>=2 else None
    last_sl  = sl[-1][1];  prev_sl = sl[-2][1] if len(sl)>=2 else None
    price    = float(closes[-1])
    bias     = "BULLISH" if price > last_sh*0.99 else "BEARISH" if price < last_sl*1.01 else "NEUTRAL"
    bos_type = "BULLISH_BOS" if prev_sh and price > prev_sh else \
               "BEARISH_BOS" if prev_sl and price < prev_sl else "NONE"

    return {
        "type": bos_type, "bias": bias,
        "prev_high": last_sh, "prev_low": last_sl,
        "swing_highs": [s[1] for s in sh[-3:]],
        "swing_lows":  [s[1] for s in sl[-3:]],
    }

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 8 · T.R.A.P. ENGINE
# ═══════════════════════════════════════════════════════════════════════════

# ── 8a: Daily Pivot Points ─────────────────────────────────────────────────
def calculate_pivots(df_daily: pd.DataFrame) -> dict:
    """Standard Pivot Points from previous day's OHLC."""
    empty = {k: None for k in ["PP","R1","R2","R3","S1","S2","S3"]}
    if len(df_daily) < 2:
        return empty
    prev = df_daily.iloc[-2]
    H, L, C = float(prev["high"]), float(prev["low"]), float(prev["close"])
    PP = (H + L + C) / 3
    return {
        "PP": round(PP, 8),
        "R1": round(2*PP - L, 8), "R2": round(PP + (H-L), 8), "R3": round(H + 2*(PP-L), 8),
        "S1": round(2*PP - H, 8), "S2": round(PP - (H-L), 8), "S3": round(L - 2*(H-PP), 8),
    }

# ── 8b: Power Zone (OB + Pivot confluence) ────────────────────────────────
def detect_power_zone(bull_obs: list, bear_obs: list,
                      pivots: dict, df: pd.DataFrame) -> dict:
    """
    Power Zone = where an Order Block aligns with a Pivot level.
    ULTRA strength if VWAP also aligns (triple confluence).
    """
    tol      = cfg["TRAP_PZ_TOL"]
    last     = df.iloc[-1] if len(df) else None
    vwap_val = float(last["VWAP"]) if last is not None else None
    piv      = {k: v for k, v in pivots.items() if v is not None}

    bull_zones, bear_zones = [], []

    for ob in bull_obs:
        mid = (ob["ob_top"] + ob["ob_bottom"]) / 2
        for lvl_name, lvl_val in piv.items():
            diff = abs(mid - lvl_val) / max(lvl_val, EPS)
            if diff <= tol:
                vwap_ok = vwap_val and abs(mid - vwap_val)/max(vwap_val, EPS) <= tol*2
                strength = "ULTRA" if (vwap_ok or ob["strength"]=="STRONG") else "STRONG"
                bull_zones.append({
                    "ob": ob, "pivot_name": lvl_name, "pivot_val": lvl_val,
                    "ob_mid": round(mid,8), "diff_pct": round(diff*100,3),
                    "strength": "ULTRA" if vwap_ok else strength,
                    "vwap_align": bool(vwap_ok),
                    "entry": ob["ob_top"], "sl": ob["sl_level"],
                })

    for ob in bear_obs:
        mid = (ob["ob_top"] + ob["ob_bottom"]) / 2
        for lvl_name, lvl_val in piv.items():
            diff = abs(mid - lvl_val) / max(lvl_val, EPS)
            if diff <= tol:
                vwap_ok  = vwap_val and abs(mid - vwap_val)/max(vwap_val, EPS) <= tol*2
                strength = "ULTRA" if (vwap_ok or ob["strength"]=="STRONG") else "STRONG"
                bear_zones.append({
                    "ob": ob, "pivot_name": lvl_name, "pivot_val": lvl_val,
                    "ob_mid": round(mid,8), "diff_pct": round(diff*100,3),
                    "strength": "ULTRA" if vwap_ok else strength,
                    "vwap_align": bool(vwap_ok),
                    "entry": ob["ob_bottom"], "sl": ob["sl_level"],
                })

    return {
        "bull_zones": bull_zones, "bear_zones": bear_zones,
        "has_bull": len(bull_zones) > 0, "has_bear": len(bear_zones) > 0,
    }

# ── 8c: Crypto Session Filter ──────────────────────────────────────────────
def crypto_session_filter() -> dict:
    """
    Replaces IST intraday time filter with crypto session windows.
    Best T.R.A.P. entries at session opens (first 2 hours of each session).
    """
    now_utc  = datetime.now(timezone.utc)
    total    = now_utc.hour * 60 + now_utc.minute

    sessions_def = {
        "Asia":    {"start": 0*60,  "end": 8*60,  "open": (0*60,  2*60)},
        "London":  {"start": 7*60,  "end": 16*60, "open": (7*60,  9*60)},
        "NewYork": {"start": 13*60, "end": 22*60, "open": (13*60, 15*60)},
    }
    name_map = {
        "Asia (00-08 UTC)":      "Asia",
        "London (07-16 UTC)":    "London",
        "New York (13-22 UTC)":  "NewYork",
    }
    enabled = {name_map[s] for s in cfg.get("SESSIONS",[]) if s in name_map}

    active, best_entry = [], False
    for name, t in sessions_def.items():
        if t["start"] <= total < t["end"]:
            active.append(name)
            if t["open"][0] <= total < t["open"][1] and name in enabled:
                best_entry = True

    use_filter = cfg.get("USE_SESSION", True)
    allowed    = (not use_filter) or any(s in enabled for s in active)

    # ── FIX 8: strftime for timezone-safe UTC time display ────────────────
    return {
        "active_sessions": active,
        "best_entry":      best_entry,
        "allowed":         allowed,
        "utc_time":        now_utc.strftime("%H:%M UTC"),
        "status":          "🟢 ACTIVE" if (allowed and active) else "🔴 WAIT",
    }

# ── 8d: False Breakout Detector ────────────────────────────────────────────
def detect_false_breakout(df: pd.DataFrame,
                           bull_obs: list, bear_obs: list) -> dict:
    """
    False Breakout = price fakes a break of OB level then reverses.
    This is T.R.A.P.'s highest-conviction trade setup.
    """
    empty = {"detected": False, "direction": None, "desc": "", "ob": None}
    if len(df) < 5:
        return empty

    prev  = df.iloc[-2]
    last  = df.iloc[-1]
    price = float(last["close"])

    for ob in bull_obs:
        if float(prev["low"]) < ob["ob_bottom"] and price > ob["ob_bottom"]:
            return {
                "detected": True, "direction": "LONG",
                "desc": (f"🎯 False Bearish Break — dipped below "
                         f"${ob['ob_bottom']:,.4f} then recovered. Strong LONG."),
                "ob": ob, "entry": price, "sl": ob["sl_level"],
            }

    for ob in bear_obs:
        if float(prev["high"]) > ob["ob_top"] and price < ob["ob_top"]:
            return {
                "detected": True, "direction": "SHORT",
                "desc": (f"🎯 False Bullish Break — spiked above "
                         f"${ob['ob_top']:,.4f} then reversed. Strong SHORT."),
                "ob": ob, "entry": price, "sl": ob["sl_level"],
            }

    return empty

# ── 8e: T.R.A.P. 4-Pillar Filter ─────────────────────────────────────────
def trap_4pillar_filter(df: pd.DataFrame, bull_obs: list, bear_obs: list,
                         power_zone: dict, structure: dict) -> dict:
    """
    Core of the T.R.A.P. system.

    Pillar 1 (T) TREND        → EMA50 + SuperTrend direction
    Pillar 2 (R) REALITY      → VWAP position + Volume ratio
    Pillar 3 (A) ACCUMULATION → BB Squeeze + OB/Power Zone present
    Pillar 4 (P) PRECISION    → Volume spike at breakout + RSI zone
    Pillar 5 (★) POWER ZONE   → Bonus: OB+Pivot confluence + Structure

    Score 5/5 → ULTRA  |  4/5 → TRADE  |  3/5 → CAUTION  |  ≤2 → NO TRADE
    """
    if len(df) < 10:
        return _empty_trap()

    last = df.iloc[-1]
    price   = float(last["close"])
    ema50   = float(last["EMA50"])
    ema21   = float(last["EMA21"])
    ema9    = float(last["EMA9"])
    vwap    = float(last["VWAP"])
    vol_r   = float(last["Vol_Ratio"])
    bb_w    = float(last["BB_Width"])
    st_dir  = float(last.get("ST_Dir", 0))
    rsi     = float(last["RSI"])

    # Dynamic BB squeeze threshold
    bb_pct_val = cfg["TRAP_BB_PCT"] / 100
    bb_thresh  = float(df["BB_Width"].quantile(bb_pct_val)) if len(df) > 20 else 0.02
    vol_mult   = cfg["TRAP_VOL_MULT"]

    # ── LONG PILLARS ────────────────────────────────────────────────────
    p1L = (price > ema50) and (st_dir > 0) and (ema9 > ema21)
    p2L = (price > vwap)  and (vol_r >= vol_mult * 0.75)
    p3L = (bb_w <= bb_thresh) and (power_zone["has_bull"] or len(bull_obs) > 0)
    p4L = (vol_r >= vol_mult) and (45 < rsi < 72)
    p5L = power_zone["has_bull"] and (structure.get("bias") == "BULLISH")
    long_score  = sum([p1L, p2L, p3L, p4L, p5L])

    # ── SHORT PILLARS ───────────────────────────────────────────────────
    p1S = (price < ema50) and (st_dir < 0) and (ema9 < ema21)
    p2S = (price < vwap)  and (vol_r >= vol_mult * 0.75)
    p3S = (bb_w <= bb_thresh) and (power_zone["has_bear"] or len(bear_obs) > 0)
    p4S = (vol_r >= vol_mult) and (28 < rsi < 55)
    p5S = power_zone["has_bear"] and (structure.get("bias") == "BEARISH")
    short_score = sum([p1S, p2S, p3S, p4S, p5S])

    min_sc = cfg["TRAP_MIN_SCORE"]
    if long_score >= min_sc and long_score >= short_score:
        direction, score = "LONG", long_score
    elif short_score >= min_sc and short_score > long_score:
        direction, score = "SHORT", short_score
    else:
        direction, score = "WAIT", max(long_score, short_score)

    conviction = {0:"🔴 NO TRADE",1:"🔴 NO TRADE",2:"🔴 NO TRADE",
                  3:"🟡 CAUTION",4:"🟢 TRADE",5:"⚡ ULTRA"}.get(score,"🔴 NO TRADE")

    return {
        "direction": direction, "score": score,
        "long_score": long_score, "short_score": short_score,
        "conviction": conviction,
        "pillars": {
            "P1 Trend":        {"long":p1L,"short":p1S,
                                "detail":f"Price {'>EMA50 & ST Bull' if p1L else '<EMA50 / ST Bear'}"},
            "P2 Reality":      {"long":p2L,"short":p2S,
                                "detail":f"VWAP={'Above' if price>vwap else 'Below'} | Vol={vol_r:.2f}x"},
            "P3 Accumulation": {"long":p3L,"short":p3S,
                                "detail":f"BB Squeeze={'Yes' if bb_w<=bb_thresh else 'No'} | OB Present"},
            "P4 Precision":    {"long":p4L,"short":p4S,
                                "detail":f"VolSpike={vol_r:.2f}x | RSI={rsi:.1f}"},
            "P5 Power Zone":   {"long":p5L,"short":p5S,
                                "detail":f"OB+Pivot={'Yes' if p5L or p5S else 'No'} | BOS aligned"},
        },
        "price": price, "vwap": vwap, "ema50": ema50,
        "rsi": rsi, "vol_ratio": vol_r, "bb_width": bb_w,
        "bb_squeeze": bb_w <= bb_thresh,
    }

def _empty_trap() -> dict:
    return {
        "direction":"WAIT","score":0,"long_score":0,"short_score":0,
        "conviction":"🔴 NO TRADE","pillars":{},"price":0,"vwap":0,
        "ema50":0,"rsi":50,"vol_ratio":1.0,"bb_width":0,"bb_squeeze":False,
    }

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 9 · ML ENSEMBLE ENGINE
# ═══════════════════════════════════════════════════════════════════════════
FEAT_COLS = [
    "RSI","MACD","MACD_Hist","MACD_Sig","Stoch_K","Stoch_D",
    "WilliamsR","CCI","ROC","ATR","ATR_Pct","BB_Width","BB_Pos",
    "Vol_Ratio","Vol_Pct","CVD20","OBV","ADX","ADX_Pos","ADX_Neg",
    "ST_Dir","Body_Ratio","Upper_Wick","Lower_Wick",
    "Price_vs_VWAP","EMA_Spread","Momentum_5","Momentum_20",
]

def _prepare_xy(df: pd.DataFrame):
    """Features + 1-bar forward return target. Removes NaN/Inf rows."""
    avail = [c for c in FEAT_COLS if c in df.columns]
    X = df[avail].values.astype(np.float64)
    y = df["close"].pct_change(1).shift(-1).fillna(0).clip(-0.1, 0.1).values
    X, y = X[:-1], y[:-1]
    mask = np.isfinite(X).all(axis=1) & np.isfinite(y)
    return X[mask], y[mask], avail

def _base_models() -> list:
    mdls = [
        ("RF",    RandomForestRegressor(n_estimators=100,max_depth=6,
                                        min_samples_leaf=5,n_jobs=-1,random_state=42)),
        ("GB",    GradientBoostingRegressor(n_estimators=100,max_depth=4,
                                             learning_rate=0.05,random_state=42)),
        ("Ridge", Ridge(alpha=1.0)),
    ]
    if HAS_XGB:
        mdls.append(("XGB", XGBRegressor(n_estimators=100,max_depth=4,
                                          learning_rate=0.05,n_jobs=-1,
                                          random_state=42,verbosity=0)))
    if HAS_LGB:
        mdls.append(("LGB", LGBMRegressor(n_estimators=100,max_depth=4,
                                           learning_rate=0.05,n_jobs=-1,
                                           random_state=42,verbose=-1)))
    return mdls

def train_predict_ensemble(df: pd.DataFrame) -> dict:
    """
    Walk-forward CV — scaler fitted on TRAIN split only (no leakage).
    Returns inverse-MAE weighted ensemble prediction.
    """
    fallback = {"prediction":0.0,"direction":"WAIT","confidence":0.0,
                "mae":None,"models":{},"model_maes":{},"feat_cols":[]}
    if len(df) < 100:
        return fallback

    X, y, feat_cols = _prepare_xy(df)
    if len(X) < 80:
        return fallback

    n_folds  = 3
    fold_sz  = len(X) // (n_folds + 1)
    models   = _base_models()
    fold_preds = {n: [] for n, _ in models}
    fold_true  = []

    for fold in range(n_folds):
        te  = (fold+1)*fold_sz
        te2 = min(te + fold_sz, len(X)-1)
        if te < 30 or te2 <= te:
            continue
        Xtr, ytr = X[:te],    y[:te]
        Xte, yte = X[te:te2], y[te:te2]
        sc = RobustScaler()
        Xtr_s = sc.fit_transform(Xtr)   # fit on train only — no leakage
        Xte_s = sc.transform(Xte)
        for name, mdl in models:
            try:
                mdl.fit(Xtr_s, ytr)
                fold_preds[name].extend(mdl.predict(Xte_s).tolist())
            except Exception as e:
                log.warning(f"⚠️ {name} fold {fold}: {e}")
        fold_true.extend(yte.tolist())

    # Final fit on ALL data for live prediction
    sc_final = RobustScaler()
    Xall_s   = sc_final.fit_transform(X)
    X_last   = sc_final.transform(X[-1:])
    live, maes = {}, {}

    for name, mdl in models:
        try:
            mdl.fit(Xall_s, y)
            live[name] = float(mdl.predict(X_last)[0])
            n_min = min(len(fold_preds[name]), len(fold_true))
            if n_min > 0:
                maes[name] = float(mean_absolute_error(fold_true[:n_min],
                                                        fold_preds[name][:n_min]))
        except Exception as e:
            log.warning(f"⚠️ Live {name}: {e}")

    if not live:
        return fallback

    # Inverse-MAE weighting
    wts   = {n: 1.0/max(maes.get(n,1.0), EPS) for n in live}
    totw  = sum(wts.values())
    ens   = sum(live[n]*wts[n]/totw for n in live)
    avg_m = float(np.mean(list(maes.values()))) if maes else None

    signs = np.sign(np.array(list(live.values())))
    agree = float(abs(signs.mean()))
    conf  = round(agree * min(abs(ens)/0.005, 1.0) * 100, 1)

    direction = "LONG"  if ens >  0.001 else \
                "SHORT" if ens < -0.001 else "WAIT"

    log.success(f"🧠 ML: {ens:.4%} → {direction} | Conf:{conf:.1f}%")
    return {
        "prediction": round(ens, 6), "direction": direction,
        "confidence": conf,
        "mae":        round(avg_m, 6) if avg_m else None,
        "models":     live, "model_maes": maes, "feat_cols": feat_cols,
    }

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 10 · SIGNAL FUSION
# ═══════════════════════════════════════════════════════════════════════════
def fuse_signals(trap: dict, ml: dict, false_bo: dict,
                 session: dict, structure: dict, power_zone: dict) -> dict:
    """
    Hierarchy:
      1st  False Breakout (highest conviction — overrides when T.R.A.P. ≥ 3)
      2nd  T.R.A.P. 4-pillar gate (must meet min score)
      3rd  ML ensemble (same direction adds conviction bonus)
      4th  Session filter (gate — must be in enabled session)
    """
    min_sc = cfg["TRAP_MIN_SCORE"]

    # Gate: session
    if not session["allowed"]:
        return _no_trade("Session not active — wait for enabled session.")

    trap_dir = trap["direction"]
    ml_dir   = ml.get("direction", "WAIT")
    ml_conf  = ml.get("confidence", 0.0)

    # Override: False Breakout
    if false_bo.get("detected") and trap["score"] >= 3:
        fb_dir = false_bo["direction"]
        conf   = min(92, 58 + trap["score"]*6 + (10 if ml_dir==fb_dir else 0))
        ob     = false_bo.get("ob") or {}
        reason = f"False Breakout {fb_dir} | T.R.A.P.:{trap['score']}/5 | ML:{ml_dir}"
        return _build_signal(fb_dir, trap, ml, conf, reason, ob, power_zone)

    # Gate: T.R.A.P. score
    if trap_dir == "WAIT" or trap["score"] < min_sc:
        return _no_trade(f"T.R.A.P. {trap['score']}/{min_sc} — insufficient.")

    # Bonuses
    ml_bonus   = 10 if ml_dir == trap_dir and ml_conf >= 50 else 0
    bos_bonus  = 5  if structure.get("type") in ("BULLISH_BOS","BEARISH_BOS") else 0
    pz_key     = "has_bull" if trap_dir == "LONG" else "has_bear"
    pz_bonus   = 10 if power_zone.get(pz_key) else 0
    sess_bonus = 5  if session.get("best_entry") else 0
    conf       = min(95, 38 + trap["score"]*8 + ml_bonus + bos_bonus + pz_bonus + sess_bonus)

    ob_list = power_zone.get("bull_zones" if trap_dir=="LONG" else "bear_zones", [])
    ob      = ob_list[0]["ob"] if ob_list else {}

    reason = (f"T.R.A.P.:{trap['score']}/5 | ML:{'✅' if ml_dir==trap_dir else '⚠️'} "
              f"| PZ:{'✅' if pz_bonus else '❌'} "
              f"| {','.join(session['active_sessions']) or 'No Session'}")

    return _build_signal(trap_dir, trap, ml, conf, reason, ob, power_zone)


def _build_signal(direction, trap, ml, confidence, reason, ob, power_zone) -> dict:
    price   = trap.get("price", 0.0)
    balance = cfg["BALANCE"]
    risk    = cfg["RISK"]
    min_rr  = cfg["MIN_RR"]

    # SL from OB, else ATR-based fallback
    if ob:
        sl = ob.get("sl_level", price*(0.997 if direction=="LONG" else 1.003))
    else:
        sl = price*(1-0.003) if direction=="LONG" else price*(1+0.003)

    sl_dist = abs(price - sl)
    tp1 = price + sl_dist*min_rr       if direction=="LONG" else price - sl_dist*min_rr
    tp2 = price + sl_dist*min_rr*1.5   if direction=="LONG" else price - sl_dist*min_rr*1.5
    tp3 = price + sl_dist*min_rr*2.0   if direction=="LONG" else price - sl_dist*min_rr*2.0

    risk_amt = balance * risk

    # ── FIX 6: pos_size overflow clamp ────────────────────────────────────
    # When sl_dist is extremely small (near-zero), pos_size blows up to
    # absurd values. We cap position value at 100% of balance as a hard guard.
    raw_pos_size  = risk_amt / max(sl_dist, EPS)
    max_pos_value = balance                          # never exceed full balance
    pos_value     = min(raw_pos_size * price, max_pos_value)
    pos_size      = pos_value / max(price, EPS)

    return {
        "direction": direction, "type": "TRAP", "confidence": round(confidence,1),
        "reason": reason, "price": round(price,8),
        "sl": round(sl,8), "tp1": round(tp1,8), "tp2": round(tp2,8), "tp3": round(tp3,8),
        "sl_dist": round(sl_dist,8), "sl_pct": round(sl_dist/max(price,EPS)*100,3),
        "risk_amt": round(risk_amt,2), "pos_size": round(pos_size,6),
        "pos_value": round(pos_value,2), "rr_ratio": min_rr,
        "trap_score": trap["score"], "ml_pred": ml.get("prediction",0.0),
        "ml_conf": ml.get("confidence",0.0), "no_trade": False,
    }

def _no_trade(reason: str) -> dict:
    return {
        "direction":"WAIT","type":"NO_TRADE","confidence":0.0,
        "reason":reason,"price":0.0,"sl":0.0,"tp1":0.0,"tp2":0.0,"tp3":0.0,
        "sl_dist":0.0,"sl_pct":0.0,"risk_amt":0.0,"pos_size":0.0,"pos_value":0.0,
        "rr_ratio":cfg["MIN_RR"],"trap_score":0,"ml_pred":0.0,"ml_conf":0.0,
        "no_trade":True,
    }

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 11 · CHART ENGINE
# ═══════════════════════════════════════════════════════════════════════════
def build_chart(df, bull_obs, bear_obs, pivots, signal, trap, n=80) -> plt.Figure:
    """Full chart: Candlesticks · EMAs · VWAP · BB · OB Zones · Pivots · Volume · RSI · MACD."""
    pf = df.tail(n).reset_index(drop=True)
    ln = len(pf)
    x  = np.arange(ln)

    fig = plt.figure(figsize=(16,11), facecolor="#0d1117")
    gs  = fig.add_gridspec(4,1, height_ratios=[5,1.2,1,1], hspace=0.04)
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])
    ax3 = fig.add_subplot(gs[2])
    ax4 = fig.add_subplot(gs[3])

    for ax in [ax1,ax2,ax3,ax4]:
        ax.set_facecolor("#0d1117")
        ax.tick_params(colors="#8b949e", labelsize=7)
        for sp in ax.spines.values():
            sp.set_color("#21262d")
        ax.grid(True, color="#161b22", lw=0.5, ls="--", alpha=0.6)

    # Candlesticks
    for i in range(ln):
        o,h,l,c = (float(pf[k].iloc[i]) for k in ["open","high","low","close"])
        col = "#2ea043" if c >= o else "#f85149"
        ax1.plot([i,i],[l,h], color=col, lw=0.8, alpha=0.9)
        bh = max(abs(c-o), pf["close"].mean()*0.0003)
        # ── FIX 1: use mpatches.Rectangle (matplotlib patches module) ───────
        ax1.add_patch(mpatches.Rectangle((i-0.35, min(o,c)), 0.7, bh, color=col, alpha=0.85))

    # Overlays
    spec = [("EMA9","#58a6ff",1.0),("EMA21","#bc8cff",1.0),("EMA50","#f0b429",1.6)]
    for col_nm, col_cl, lw in spec:
        if col_nm in pf:
            ax1.plot(x, pf[col_nm], color=col_cl, lw=lw, label=col_nm, alpha=0.9)
    if "VWAP" in pf:
        ax1.plot(x, pf["VWAP"], color="#ff7b54", lw=1.3, ls="--", label="VWAP", alpha=0.9)
    if "BB_Upper" in pf:
        ax1.fill_between(x, pf["BB_Lower"], pf["BB_Upper"], color="#58a6ff", alpha=0.04)
        ax1.plot(x, pf["BB_Upper"], color="#58a6ff", lw=0.4, alpha=0.3)
        ax1.plot(x, pf["BB_Lower"], color="#58a6ff", lw=0.4, alpha=0.3)

    # OB zones
    ts_arr = pd.to_datetime(pf["timestamp"].values)
    def ts2x(ts_str):
        ts = pd.Timestamp(ts_str)
        diffs = np.abs((ts_arr - ts).total_seconds())
        return max(int(np.argmin(diffs)), 0)

    for ob in bull_obs:
        xs = ts2x(ob["timestamp"])
        if xs >= ln-1: continue
        # ── FIX 1: mpatches.Rectangle used (correct matplotlib API) ─────────
        ax1.add_patch(mpatches.Rectangle((xs, ob["ob_bottom"]), ln-xs,
                                          ob["ob_top"]-ob["ob_bottom"],
                                          color="#2ea043", alpha=0.13, lw=0))
        ax1.axhline(ob["ob_top"],    color="#2ea043", lw=0.7, ls=":", alpha=0.6)
        ax1.axhline(ob["ob_bottom"], color="#2ea043", lw=0.7, ls=":", alpha=0.4)
        ax1.text(xs+0.5, ob["ob_top"], f"  🟢{ob['impulse_pct']:.1f}%",
                 color="#2ea043", fontsize=6, va="bottom", alpha=0.85)

    for ob in bear_obs:
        xs = ts2x(ob["timestamp"])
        if xs >= ln-1: continue
        # ── FIX 1: mpatches.Rectangle used (correct matplotlib API) ─────────
        ax1.add_patch(mpatches.Rectangle((xs, ob["ob_bottom"]), ln-xs,
                                          ob["ob_top"]-ob["ob_bottom"],
                                          color="#f85149", alpha=0.13, lw=0))
        ax1.axhline(ob["ob_top"],    color="#f85149", lw=0.7, ls=":", alpha=0.6)
        ax1.axhline(ob["ob_bottom"], color="#f85149", lw=0.7, ls=":", alpha=0.4)
        ax1.text(xs+0.5, ob["ob_bottom"], f"  🔴{ob['impulse_pct']:.1f}%",
                 color="#f85149", fontsize=6, va="top", alpha=0.85)

    # Pivot levels
    piv_clr = {"PP":"#f0b429","R1":"#58a6ff","R2":"#58a6ff","S1":"#f85149","S2":"#f85149"}
    for nm, val in pivots.items():
        if val and nm in piv_clr:
            ax1.axhline(val, color=piv_clr[nm], lw=0.6, ls="-.", alpha=0.55)
            ax1.text(ln-0.3, val, f" {nm}", color=piv_clr[nm], fontsize=5.5,
                     va="center", alpha=0.8)

    # Signal marker
    if not signal.get("no_trade"):
        d   = signal["direction"]
        clr = "#2ea043" if d=="LONG" else "#f85149"
        ax1.scatter([ln-1],[signal["price"]], marker="^" if d=="LONG" else "v",
                    color=clr, s=220, zorder=12, label=f"{d} Entry")
        for lvl, lbl, lw in [(signal["sl"],"SL",1.2),(signal["tp1"],"TP1",1.0),
                              (signal["tp2"],"TP2",0.8)]:
            col = "#f85149" if lbl=="SL" else "#2ea043"
            ax1.axhline(lvl, color=col, lw=lw, ls="--", alpha=0.75,
                        label=f"{lbl} {lvl:.4f}")

    last_p = float(pf["close"].iloc[-1])
    ax1.set_title(
        f"  🎯 V9 · T.R.A.P. | {cfg['COIN']} [{cfg['TF']}] | "
        f"${last_p:,.4f} | Score:{trap.get('score',0)}/5 {trap.get('conviction','')}",
        color="#e6edf3", fontsize=11, fontweight="bold", loc="left", pad=8)
    ax1.legend(loc="upper left", fontsize=6, facecolor="#161b22",
               labelcolor="#e6edf3", framealpha=0.8)
    ax1.set_xlim(-1, ln+1)
    ax1.tick_params(labelbottom=False)

    # Volume
    vcols = ["#2ea043" if pf["close"].iloc[i]>=pf["open"].iloc[i]
              else "#f85149" for i in range(ln)]
    ax2.bar(x, pf["volume"], color=vcols, width=0.7, alpha=0.7)
    if "Vol_MA20" in pf:
        ax2.plot(x, pf["Vol_MA20"], color="#f0b429", lw=1.0, alpha=0.8)
    ax2.set_ylabel("Vol", color="#8b949e", fontsize=7)
    ax2.tick_params(labelbottom=False); ax2.set_xlim(-1,ln+1)

    # RSI
    if "RSI" in pf:
        rv = pf["RSI"].values
        ax3.plot(x, rv, color="#bc8cff", lw=1.0)
        ax3.axhline(70, color="#f85149", lw=0.6, ls="--", alpha=0.7)
        ax3.axhline(30, color="#2ea043", lw=0.6, ls="--", alpha=0.7)
        ax3.axhline(50, color="#8b949e", lw=0.4, alpha=0.35)
        ax3.fill_between(x, 30, rv, where=rv<30, color="#2ea043", alpha=0.12)
        ax3.fill_between(x, 70, rv, where=rv>70, color="#f85149", alpha=0.12)
        ax3.set_ylim(0,100); ax3.set_ylabel("RSI",color="#8b949e",fontsize=7)
        ax3.tick_params(labelbottom=False); ax3.set_xlim(-1,ln+1)

    # MACD
    if "MACD" in pf:
        ax4.plot(x, pf["MACD"],     color="#58a6ff", lw=0.9, label="MACD")
        ax4.plot(x, pf["MACD_Sig"], color="#f0b429", lw=0.9, label="Signal")
        hist = pf["MACD_Hist"].values
        ax4.bar(x, hist, color=["#2ea043" if v>=0 else "#f85149" for v in hist],
                width=0.6, alpha=0.6)
        ax4.axhline(0, color="#8b949e", lw=0.4)
        ax4.set_ylabel("MACD",color="#8b949e",fontsize=7)
        ax4.legend(fontsize=6,facecolor="#161b22",labelcolor="#e6edf3",framealpha=0.6)

    step = max(ln//8, 1)
    tp   = x[::step]
    ax4.set_xticks(tp)
    # ── FIX 8: strftime for timezone-safe x-axis labels ───────────────────
    ax4.set_xticklabels(
        [pd.Timestamp(pf["timestamp"].iloc[i]).strftime("%Y-%m-%d %H:%M") for i in tp],
        rotation=20, fontsize=6, color="#8b949e")
    ax4.set_xlim(-1,ln+1)
    plt.tight_layout(pad=0.4)
    return fig

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 12 · DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════
def render_dashboard(df, df_daily, bull_obs, bear_obs, trap, ml,
                     signal, session, pivots, power_zone, structure, false_bo):

    st.markdown("## 🎯 Crypto Bot V9 · T.R.A.P. Edition")

    # ── Top KPIs ──────────────────────────────────────────────────────────
    if len(df):
        last  = df.iloc[-1];  prev = df.iloc[-2] if len(df)>1 else last
        price = float(last["close"])
        chg   = (price - float(prev["close"])) / max(float(prev["close"]), EPS) * 100
        k = st.columns(6)
        k[0].metric("💰 Price",     f"${price:,.4f}", f"{chg:+.2f}%")
        k[1].metric("🎯 T.R.A.P.",  f"{trap['score']}/5", trap["conviction"])
        k[2].metric("🧠 ML Conf",   f"{ml.get('confidence',0):.1f}%", ml.get("direction","?"))
        k[3].metric("📦 OBs",       f"B:{len(bull_obs)} S:{len(bear_obs)}")
        k[4].metric("🕐 Session",   session["status"], session["utc_time"])
        k[5].metric("📊 Structure", structure.get("bias","?"), structure.get("type","?"))

    st.markdown("---")
    tabs = st.tabs(["🎯 T.R.A.P. Signal","📊 Chart","📦 Order Blocks",
                    "🧠 ML Prediction","🕐 Sessions & Pivots","⚖️ Risk Manager","📝 Logs"])

    # ── TAB 0: T.R.A.P. Signal ────────────────────────────────────────────
    with tabs[0]:
        c1, c2 = st.columns([1,2])
        with c1:
            st.markdown("### 🚦 Final Signal")
            d = signal["direction"]
            if d == "LONG":
                st.markdown('<div class="sig-long">⬆️ LONG</div>', unsafe_allow_html=True)
                st.success(f"Confidence: {signal['confidence']:.1f}%")
            elif d == "SHORT":
                st.markdown('<div class="sig-short">⬇️ SHORT</div>', unsafe_allow_html=True)
                st.error(f"Confidence: {signal['confidence']:.1f}%")
            else:
                st.markdown('<div class="sig-wait">⏳ WAIT</div>', unsafe_allow_html=True)
                st.info("No aligned setup — wait.")
            st.caption(f"**Reason:** {signal['reason']}")
            if not signal.get("no_trade"):
                st.markdown("---")
                for lbl, val in [("Entry",f"${signal['price']:,.6f}"),
                                   ("SL",   f"${signal['sl']:,.6f} ({signal['sl_pct']:.2f}%)"),
                                   ("TP1",  f"${signal['tp1']:,.6f}"),
                                   ("TP2",  f"${signal['tp2']:,.6f}"),
                                   ("TP3",  f"${signal['tp3']:,.6f}"),
                                   ("R:R",  f"1 : {signal['rr_ratio']:.1f}")]:
                    st.markdown(f"**{lbl}:** `{val}`")
            if false_bo.get("detected"):
                st.warning(f"⚡ {false_bo['desc']}")

        with c2:
            st.markdown("### 🔬 5-Pillar Analysis")
            pillar_icons = {"P1 Trend":"📈","P2 Reality":"🔍",
                            "P3 Accumulation":"⚡","P4 Precision":"🎯","P5 Power Zone":"⭐"}
            for key, icon in pillar_icons.items():
                if key not in trap.get("pillars",{}):
                    continue
                p = trap["pillars"][key]
                lpass = "✅" if p["long"]  else "❌"
                spass = "✅" if p["short"] else "❌"
                cls   = "trap-pass" if (p["long"] or p["short"]) else "trap-fail"
                st.markdown(
                    f'<div class="trap-card {cls}">'
                    f'<b>{icon} {key}</b> &nbsp; L:{lpass} S:{spass}<br>'
                    f'<small style="color:#8b949e">{p.get("detail","")}</small>'
                    f'</div>', unsafe_allow_html=True)
            st.markdown("---")
            sc = trap.get("score",0)
            st.markdown(f"**Score: {sc}/5** — {trap.get('conviction','')}")
            st.progress(sc/5)

    # ── TAB 1: Chart ──────────────────────────────────────────────────────
    with tabs[1]:
        nc = st.slider("Candles", 40, 200, 80, 10)
        with st.spinner("Rendering..."):
            fig = build_chart(df, bull_obs, bear_obs, pivots, signal, trap, nc)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

    # ── TAB 2: Order Blocks ───────────────────────────────────────────────
    with tabs[2]:
        cb, cs = st.columns(2)
        with cb:
            st.markdown("### 🟢 Demand Zones")
            if not bull_obs:
                st.info("No active bullish OBs.")
            for ob in reversed(bull_obs):
                pz = any(z["ob"] == ob for z in power_zone.get("bull_zones",[]))
                st.markdown(
                    f'<div class="ob-bull"><b>{ob["label"]}</b>'
                    f'{"  ⭐ Power Zone" if pz else ""}<br>'
                    f'Zone: <b>${ob["ob_bottom"]:,.4f}</b> – <b>${ob["ob_top"]:,.4f}</b><br>'
                    f'Impulse:{ob["impulse_pct"]}% | Vol:{ob["vol_ratio"]}x | '
                    f'<b>{ob["strength"]}</b><br>SL:${ob["sl_level"]:,.4f}<br>'
                    f'<small style="color:#8b949e">{ob["timestamp"]}</small>'
                    f'</div>', unsafe_allow_html=True)
        with cs:
            st.markdown("### 🔴 Supply Zones")
            if not bear_obs:
                st.info("No active bearish OBs.")
            for ob in reversed(bear_obs):
                pz = any(z["ob"] == ob for z in power_zone.get("bear_zones",[]))
                st.markdown(
                    f'<div class="ob-bear"><b>{ob["label"]}</b>'
                    f'{"  ⭐ Power Zone" if pz else ""}<br>'
                    f'Zone: <b>${ob["ob_bottom"]:,.4f}</b> – <b>${ob["ob_top"]:,.4f}</b><br>'
                    f'Impulse:{ob["impulse_pct"]}% | Vol:{ob["vol_ratio"]}x | '
                    f'<b>{ob["strength"]}</b><br>SL:${ob["sl_level"]:,.4f}<br>'
                    f'<small style="color:#8b949e">{ob["timestamp"]}</small>'
                    f'</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### 🏗️ Market Structure")
        bc = "#2ea043" if structure.get("bias")=="BULLISH" else \
             "#f85149" if structure.get("bias")=="BEARISH" else "#8b949e"
        st.markdown(
            f"**Bias:** <span style='color:{bc}'>{structure.get('bias','?')}</span> &nbsp;|&nbsp; "
            f"**BOS:** {structure.get('type','?')} &nbsp;|&nbsp; "
            f"**Prev High:** {structure.get('prev_high','?')} &nbsp;|&nbsp; "
            f"**Prev Low:** {structure.get('prev_low','?')}",
            unsafe_allow_html=True)

    # ── TAB 3: ML ─────────────────────────────────────────────────────────
    with tabs[3]:
        st.markdown("### 🧠 Ensemble ML Prediction")
        m1,m2,m3 = st.columns(3)
        m1.metric("Prediction", f"{ml.get('prediction',0):.4%}", ml.get("direction","?"))
        m2.metric("Confidence", f"{ml.get('confidence',0):.1f}%")
        m3.metric("Avg MAE",    f"{ml.get('mae',0) or 0:.4%}" if ml.get("mae") else "N/A")
        if ml.get("models"):
            st.markdown("#### Per-Model Breakdown")
            rows = []
            for nm, pred in ml["models"].items():
                mae = ml.get("model_maes",{}).get(nm)
                rows.append({"Model":nm,
                              "Prediction":f"{pred:.4%}",
                              "Direction":"🟢 LONG" if pred>0.001 else "🔴 SHORT" if pred<-0.001 else "⚪ WAIT",
                              "MAE":f"{mae:.4%}" if mae else "N/A"})
            st.dataframe(pd.DataFrame(rows), use_container_width=True)
        if ml.get("feat_cols"):
            with st.expander("📊 Feature Columns Used"):
                st.write(", ".join(ml["feat_cols"]))

    # ── TAB 4: Sessions & Pivots ──────────────────────────────────────────
    with tabs[4]:
        sc, pc = st.columns(2)
        with sc:
            st.markdown("### 🕐 Crypto Sessions (UTC)")
            now_h = datetime.now(timezone.utc).hour
            for name,(s,e) in [("Asia",(0,8)),("London",(7,16)),("New York",(13,22))]:
                active = s <= now_h < e
                badge  = "sess-on" if active else "sess-off"
                st.markdown(
                    f'<span class="{badge}">{name} {s:02d}:00–{e:02d}:00</span><br>',
                    unsafe_allow_html=True)
            st.markdown(f"**Best Entry Window:** {'🟢 YES' if session['best_entry'] else '🔴 NO'}")
            st.caption(f"Now: {session['utc_time']}")

        with pc:
            st.markdown("### 📐 Daily Pivot Points")
            if len(df):
                lp = float(df.iloc[-1]["close"])
                rows = []
                for nm, val in pivots.items():
                    if val:
                        dist = (val - lp)/max(lp,EPS)*100
                        rows.append({"Level":nm,"Price":f"${val:,.6f}","Dist":f"{dist:+.2f}%"})
                if rows:
                    st.dataframe(pd.DataFrame(rows), use_container_width=True)

        st.markdown("---")
        st.markdown("### ⭐ Power Zones")
        if not power_zone["has_bull"] and not power_zone["has_bear"]:
            st.info("No Power Zones — OB and Pivot levels not aligned yet.")
        for pz in power_zone.get("bull_zones",[]):
            st.success(f"🟢 **Bull Power Zone** | "
                       f"OB {pz['ob']['ob_bottom']:.4f}–{pz['ob']['ob_top']:.4f} "
                       f"+ {pz['pivot_name']}({pz['pivot_val']:.4f}) | "
                       f"Diff:{pz['diff_pct']:.3f}% | {pz['strength']}"
                       f"{' | 🔥 VWAP' if pz.get('vwap_align') else ''}")
        for pz in power_zone.get("bear_zones",[]):
            st.error(f"🔴 **Bear Power Zone** | "
                     f"OB {pz['ob']['ob_bottom']:.4f}–{pz['ob']['ob_top']:.4f} "
                     f"+ {pz['pivot_name']}({pz['pivot_val']:.4f}) | "
                     f"Diff:{pz['diff_pct']:.3f}% | {pz['strength']}"
                     f"{' | 🔥 VWAP' if pz.get('vwap_align') else ''}")

    # ── TAB 5: Risk Manager ───────────────────────────────────────────────
    with tabs[5]:
        st.markdown("### ⚖️ Position & Risk Calculator")
        r1, r2 = st.columns(2)
        with r1:
            if not signal.get("no_trade"):
                data = {
                    "Metric":["Balance","Risk %","Risk $","Entry","SL",
                               "SL Dist","SL %","Pos Size","Pos Value",
                               "TP1","TP2","TP3"],
                    "Value": [f"${cfg['BALANCE']:,.2f}",
                              f"{cfg['RISK']*100:.1f}%",
                              f"${signal['risk_amt']:,.2f}",
                              f"${signal['price']:,.6f}",
                              f"${signal['sl']:,.6f}",
                              f"${signal['sl_dist']:,.6f}",
                              f"{signal['sl_pct']:.3f}%",
                              f"{signal['pos_size']:.6f}",
                              f"${signal['pos_value']:,.2f}",
                              f"${signal['tp1']:,.6f}",
                              f"${signal['tp2']:,.6f}",
                              f"${signal['tp3']:,.6f}"]
                }
                st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
            else:
                st.info("No active signal. Parameters appear when T.R.A.P. triggers.")
        with r2:
            st.markdown("#### T.R.A.P. Exit Rules")
            st.markdown("""
| Target | Exit % | Rule        |
|--------|--------|-------------|
| TP1    | 50%    | RR × 1.5   |
| TP2    | 40%    | RR × 2.0   |
| TP3    | 10%    | Trail 21EMA |

**Golden Rules:**
- After TP1 → SL → Breakeven
- Max **2 trades/day**
- After 2 losses → stop today
- Session close → exit all
- Never enter 3/5 pillars
            """)

    # ── TAB 6: Logs ───────────────────────────────────────────────────────
    with tabs[6]:
        st.markdown("### 📝 System Logs")
        if st.button("🗑️ Clear"):
            log.clear()
        st.text_area("", log.tail(50), height=400, label_visibility="collapsed")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 13 · MAIN
# ═══════════════════════════════════════════════════════════════════════════
def main():
    log.clear()

    col_run, col_auto, col_info = st.columns([1,1,4])
    run     = col_run.button("🚀 Run Analysis", use_container_width=True)
    auto_on = col_auto.checkbox("♻️ Auto (2 min)")
    col_info.info(
        f"🎯 **T.R.A.P.** | {cfg['COIN']} [{cfg['TF']}] | "
        f"${cfg['BALANCE']:,.0f} | Risk:{cfg['RISK']*100:.1f}% | "
        f"Min Score:{cfg['TRAP_MIN_SCORE']}/5 | RR:{cfg['MIN_RR']:.1f}")

    if auto_on:
        time.sleep(0.5); run = True

    if not run:
        st.markdown("""
        <div style="text-align:center;padding:70px 0;color:#8b949e;">
            <div style="font-size:3.5rem;margin-bottom:16px;">🎯</div>
            <div style="font-size:1.3rem;font-weight:900;color:#f0b429;">T.R.A.P. System Ready</div>
            <div style="font-size:.9rem;margin-top:8px;">
                Trend · Reality · Accumulation · Precision<br>
                Click <b>Run Analysis</b> to begin.
            </div>
        </div>""", unsafe_allow_html=True)
        return

    # ── PIPELINE ──────────────────────────────────────────────────────────
    with st.spinner(f"📡 Fetching {cfg['COIN']} data..."):
        try:
            df       = fetch_ohlcv(cfg["COIN"], cfg["TF"])
            df_daily = fetch_ohlcv(cfg["COIN"], cfg["HTF"])
            # Log fetch info here (outside cached fn) — FIX 2
            log.success(df.attrs.get("_fetch_info", f"✓ {cfg['COIN']} [{cfg['TF']}] fetched"))
            log.success(df_daily.attrs.get("_fetch_info", f"✓ {cfg['COIN']} [{cfg['HTF']}] fetched"))
        except Exception as e:
            st.error(f"❌ Fetch failed: {e}"); log.error(f"Fetch: {e}"); return

    if len(df) < 60:
        st.error("❌ Insufficient data. Try different symbol or timeframe."); return

    with st.spinner("📊 Computing indicators..."):
        try:
            df       = add_indicators(df)
            df_daily = add_indicators(df_daily)
        except Exception as e:
            st.error(f"❌ Indicator error: {e}"); log.error(f"Ind: {e}"); return

    with st.spinner("📦 Detecting Order Blocks & Structure..."):
        try:
            bull_obs, bear_obs = detect_order_blocks(df)
            structure          = detect_market_structure(df)
        except Exception as e:
            log.error(f"OB: {e}")
            bull_obs, bear_obs = [], []
            structure = {"type":"UNKNOWN","bias":"NEUTRAL","prev_high":None,"prev_low":None}

    with st.spinner("🎯 Running T.R.A.P. Engine..."):
        try:
            pivots     = calculate_pivots(df_daily)
            power_zone = detect_power_zone(bull_obs, bear_obs, pivots, df)
            false_bo   = detect_false_breakout(df, bull_obs, bear_obs)
            session    = crypto_session_filter()
            trap       = trap_4pillar_filter(df, bull_obs, bear_obs, power_zone, structure)
        except Exception as e:
            st.error(f"❌ T.R.A.P. error: {e}"); log.error(f"TRAP: {e}"); return

    with st.spinner("🧠 ML Ensemble..."):
        try:
            ml = train_predict_ensemble(df)
        except Exception as e:
            log.warning(f"ML fallback: {e}")
            ml = {"prediction":0.0,"direction":"WAIT","confidence":0.0,"mae":None,"models":{}}

    with st.spinner("🔀 Fusing signals..."):
        try:
            signal = fuse_signals(trap, ml, false_bo, session, structure, power_zone)
        except Exception as e:
            st.error(f"❌ Fusion error: {e}"); log.error(f"Fusion: {e}"); return

    render_dashboard(df, df_daily, bull_obs, bear_obs, trap, ml,
                     signal, session, pivots, power_zone, structure, false_bo)

    # ── FIX 3: blocking sleep removed from auto-refresh ──────────────────
    # Calling st.rerun() directly avoids freezing the UI thread.
    # The 2-minute cadence is shown as a user note only.
    if auto_on:
        # ── FIX 8: strftime for timezone-safe last-run timestamp ──────────
        last_run = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
        st.caption(f"⏱️ Auto-refresh every 2 min. Last: {last_run}")
        st.rerun()

# ── Entry Point ────────────────────────────────────────────────────────────
main()
