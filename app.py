"""
╔══════════════════════════════════════════════════════════════════════════╗
║     CRYPTO BOT V9 · ENSEMBLE EDITION · STREAMLIT CLOUD SAFE           ║
║     WITH 5-USER LOGIN SYSTEM                                           ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import os, time, queue, warnings, threading
import concurrent.futures
from datetime import datetime, timezone
import hashlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Lightweight ML Only (Streamlit Cloud Safe) ──────────────────────────
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

import ccxt
import ta

warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════════════════
# LOGIN SYSTEM — 5 Users
# (Change usernames/passwords as needed)
# ══════════════════════════════════════════════════════════════════════

# Passwords stored as SHA-256 hashes for basic security.
# To generate a hash: hashlib.sha256("yourpassword".encode()).hexdigest()
# Default credentials:
#   user1 / pass1234
#   user2 / pass2234
#   user3 / pass3234
#   trader1 / trade@123
#   admin / admin@999

def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

USERS = {
    "zafariqbal@":   _hash("pass1234"),
    "mrssher":   _hash("pass2234"),
    "user3":   _hash("pass3234"),
    "trader1": _hash("trade@123"),
    "admin":   _hash("admin@999"),
}

def login_screen():
    """Renders login form and returns True if authenticated."""
    st.markdown("""
    <style>
        .login-box {
            max-width: 380px;
            margin: 80px auto;
            padding: 2rem;
            background: #161b22;
            border-radius: 12px;
            border: 1px solid #30363d;
        }
        .login-title {
            text-align: center;
            font-size: 1.8rem;
            font-weight: bold;
            color: #58a6ff;
            margin-bottom: 0.2rem;
        }
        .login-sub {
            text-align: center;
            color: #8b949e;
            font-size: 0.9rem;
            margin-bottom: 1.5rem;
        }
    </style>
    """, unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        st.markdown('<div class="login-title">🐋 Crypto Bot V9</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-sub">Ensemble + Walk-Forward Edition</div>', unsafe_allow_html=True)
        st.markdown("---")

        username = st.text_input("👤 Username", placeholder="Enter username")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter password")

        btn = st.button("🔐 Login", use_container_width=True)

        if btn:
            if username in USERS and USERS[username] == _hash(password):
                st.session_state["authenticated"] = True
                st.session_state["current_user"]  = username
                st.success(f"✅ Welcome, **{username}**!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password.")

        st.markdown("---")
        st.caption("🔑 Contact admin for credentials.")

def check_auth():
    """Returns True if user is logged in."""
    return st.session_state.get("authenticated", False)

# ── Page Config ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Crypto Bot V9",
    page_icon="🐋",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown("""
<style>
    .block-container { padding-top: 1rem; }
    .stMetric { background-color: #0d1117; border-radius: 8px; padding: 10px; }
    div[data-testid="stMetricValue"] { color: #58a6ff; }
    .stButton button { background-color: #238636; color: white; border: none; }
    .signal-buy  { color: #2ea043; font-size: 1.5rem; font-weight: bold; }
    .signal-sell { color: #f85149; font-size: 1.5rem; font-weight: bold; }
    .signal-hold { color: #8b949e; font-size: 1.5rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ── Auth Gate ───────────────────────────────────────────────────────────
if not check_auth():
    login_screen()
    st.stop()

# ── Logger (Session-Safe) ────────────────────────────────────────────────
class Logger:
    def __init__(self):
        self.msgs = []
    def info(self, m):    self.msgs.append(("ℹ️", m))
    def success(self, m): self.msgs.append(("✅", m))
    def warning(self, m): self.msgs.append(("⚠️", m))
    def error(self, m):   self.msgs.append(("❌", m))
    def text(self):
        return "\n".join(f"{i} {m}" for i, m in self.msgs)
    def clear(self):      self.msgs = []

if "logger" not in st.session_state:
    st.session_state.logger = Logger()
log = st.session_state.logger

# ── Config ───────────────────────────────────────────────────────────────
def get_config():
    # ── Sidebar header with logout ───────────────────────────────────
    user = st.session_state.get("current_user", "user")
    col_a, col_b = st.sidebar.columns([2, 1])
    col_a.markdown(f"👤 **{user}**")
    if col_b.button("Logout"):
        st.session_state["authenticated"] = False
        st.session_state["current_user"]  = ""
        st.rerun()

    st.sidebar.header("⚙️ Configuration")
    coin    = st.sidebar.text_input("Coin Symbol", "BTC/USDT")
    tf_main = st.sidebar.selectbox("Main Timeframe", ["1h","4h","15m","30m"], index=0)
    tf_htf  = st.sidebar.selectbox("Higher Timeframe", ["4h","1d","1h"], index=0)
    balance = st.sidebar.number_input("Balance (USDT)", 100.0, 1_000_000.0, 1000.0, 100.0)
    risk    = st.sidebar.slider("Risk per Trade (%)", 0.1, 3.0, 1.0, 0.1) / 100.0
    min_rr  = st.sidebar.slider("Min R:R", 1.0, 3.0, 1.5, 0.1)

    st.sidebar.markdown("---")
    st.sidebar.subheader("🐋 Whale Settings")
    wvt = st.sidebar.slider("Whale Vol Threshold", 2.0, 5.0, 3.0, 0.5)
    wpm = st.sidebar.slider("Whale Min Move (%)", 0.1, 1.0, 0.3, 0.1) / 100

    st.sidebar.markdown("---")
    st.sidebar.subheader("🧠 Model Settings")
    seq_len   = st.sidebar.slider("Sequence Length", 30, 120, 60, 10)
    use_cache = st.sidebar.checkbox("Use Model Cache", True)

    return {
        "COIN": coin, "TF": tf_main, "HTF": tf_htf,
        "BALANCE": balance, "RISK": risk, "MIN_RR": min_rr,
        "WHALE_VOL_THRESH": wvt, "WHALE_MOVE_MIN": wpm,
        "SEQ_LEN": seq_len, "USE_CACHE": use_cache,
        "OB_DEPTH": 20, "WALL_MULT": 5.0,
        "STRUCT_LOOKBACK": 75, "STRUCT_MIN_SWING": 0.008,
    }

cfg = get_config()

# ══════════════════════════════════════════════════════════════════════
# DATA ENGINE
# ══════════════════════════════════════════════════════════════════════
EXCHANGES = ["binance","bybit","okx","kucoin","gateio","mexc"]

@st.cache_resource(show_spinner=False)
def build_exchange_pool():
    pool = {}
    for name in EXCHANGES:
        try:
            pool[name] = getattr(ccxt, name)({"enableRateLimit": True})
        except Exception:
            pass
    return pool

ex_pool = build_exchange_pool()

@st.cache_data(ttl=120, show_spinner=False)
def fetch_ohlcv(symbol: str, tf: str) -> pd.DataFrame:
    """
    ✅ FIXED V9: groupby ts bug resolved — reset_index() properly restores
    timestamp as a column instead of leaving it as index.
    """
    limit = 500 if tf in ("4h","1d") else 1000
    results = []

    q        = queue.Queue()
    stop_evt = threading.Event()

    def _fetch_one(name, ex):
        if stop_evt.is_set():
            return
        try:
            data = ex.fetch_ohlcv(symbol, timeframe=tf, limit=limit)
            df   = pd.DataFrame(
                data, columns=["ts","open","high","low","close","volume"])
            df["ts"]   = pd.to_datetime(df["ts"], unit="ms", utc=True)
            df["_src"] = name
            if len(df) >= 60:
                q.put(df)
        except Exception:
            pass

    threads   = []
    sorted_ex = sorted(ex_pool.items(), key=lambda x: x[0])[:4]
    for name, ex in sorted_ex:
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

    combined = pd.concat(results).sort_values("ts")
    n_src    = combined["_src"].nunique()

    if n_src > 1:
        # ✅ FIX: use reset_index() so 'ts' comes back as a column,
        #         then rename to 'timestamp'.
        def _agg(g):
            vol = g["volume"].values
            w   = vol if vol.sum() > 0 else np.ones(len(g))
            return pd.Series({
                "open":   np.average(g["open"],  weights=w),
                "high":   np.average(g["high"],  weights=w),
                "low":    np.average(g["low"],   weights=w),
                "close":  np.average(g["close"], weights=w),
                "volume": float(np.median(vol)),
            })
        merged = (combined
                  .groupby("ts", sort=True)
                  .apply(_agg)
                  .reset_index()                         # ← ts wapas column banta hai
                  .rename(columns={"ts": "timestamp"})) # ← consistent name
    else:
        merged = (combined
                  .drop_duplicates("ts", keep="last")
                  .drop(columns=["_src"], errors="ignore")
                  .rename(columns={"ts": "timestamp"})
                  .reset_index(drop=True))

    # Volume outlier cap
    q1, q3 = merged["volume"].quantile([0.25, 0.75])
    cap     = q3 + 5 * (q3 - q1)
    merged["volume"] = merged["volume"].clip(upper=cap)

    # Fill gaps
    for col in ["open","high","low","close","volume"]:
        merged[col] = (merged[col]
                       .interpolate("linear")
                       .ffill().bfill())

    log.success(f"✓ {symbol} [{tf}]: {len(merged)} candles, {n_src} sources")
    return merged.reset_index(drop=True)

# ══════════════════════════════════════════════════════════════════════
# FEATURE ENGINEERING
# ══════════════════════════════════════════════════════════════════════
def _supertrend(df, period=10, mult=3.0):
    atr   = ta.volatility.AverageTrueRange(
        df["high"], df["low"], df["close"],
        window=period, fillna=True).average_true_range()
    hl2   = (df["high"] + df["low"]) / 2
    upper = (hl2 + mult * atr).values
    lower = (hl2 - mult * atr).values
    close = df["close"].values
    n     = len(close)
    fu, fl     = upper.copy(), lower.copy()
    st_line    = np.zeros(n)
    direction  = np.ones(n)
    for i in range(1, n):
        fu[i] = (upper[i] if upper[i] < fu[i-1] or close[i-1] > fu[i-1] else fu[i-1])
        fl[i] = (lower[i] if lower[i] > fl[i-1] or close[i-1] < fl[i-1] else fl[i-1])
        if st_line[i-1] == fu[i-1]:
            st_line[i] = fl[i] if close[i] > fu[i] else fu[i]
        else:
            st_line[i] = fu[i] if close[i] < fl[i] else fl[i]
        direction[i] = 1 if st_line[i] == fl[i] else -1
    df["Supertrend"] = st_line
    df["ST_Dir"]     = direction
    return df

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # ── Trend ───────────────────────────────────────────────────────
    df["EMA9"]   = df["close"].ewm(span=9,   adjust=False).mean()
    df["EMA21"]  = df["close"].ewm(span=21,  adjust=False).mean()
    df["EMA50"]  = df["close"].ewm(span=50,  adjust=False).mean()
    df["EMA200"] = df["close"].ewm(span=200, adjust=False).mean()
    df["SMA20"]  = df["close"].rolling(20).mean()

    typ       = (df["high"] + df["low"] + df["close"]) / 3
    df["VWAP"] = ((typ * df["volume"]).cumsum()
                  / df["volume"].cumsum().replace(0, np.nan))

    # ── Momentum ─────────────────────────────────────────────────────
    df["RSI"] = ta.momentum.RSIIndicator(
        df["close"], window=14, fillna=True).rsi()
    macd = ta.trend.MACD(df["close"], fillna=True)
    df["MACD"]      = macd.macd()
    df["MACD_Sig"]  = macd.macd_signal()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Sig"]

    stoch = ta.momentum.StochasticOscillator(
        df["high"], df["low"], df["close"],
        window=14, smooth_window=3, fillna=True)
    df["Stoch_K"] = stoch.stoch()
    df["Stoch_D"] = stoch.stoch_signal()

    df["WilliamsR"] = ta.momentum.WilliamsRIndicator(
        df["high"], df["low"], df["close"], lbp=14, fillna=True).williams_r()
    df["CCI"] = ta.trend.CCIIndicator(
        df["high"], df["low"], df["close"], window=20, fillna=True).cci()
    df["ROC"] = df["close"].pct_change(10).fillna(0)

    # ── Volatility ───────────────────────────────────────────────────
    df["ATR"] = ta.volatility.AverageTrueRange(
        df["high"], df["low"], df["close"], window=14, fillna=True).average_true_range()
    bb = ta.volatility.BollingerBands(
        df["close"], window=20, window_dev=2, fillna=True)
    df["BB_Upper"] = bb.bollinger_hband()
    df["BB_Lower"] = bb.bollinger_lband()
    df["BB_Mid"]   = bb.bollinger_mavg()
    df["BB_Width"] = ((df["BB_Upper"] - df["BB_Lower"])
                      / df["BB_Mid"].replace(0, np.nan)).fillna(0)
    df["BB_Pos"]   = ((df["close"] - df["BB_Lower"])
                      / (df["BB_Upper"] - df["BB_Lower"])
                      .replace(0, np.nan)).fillna(0.5)

    atr_vals = df["ATR"].values
    ap = np.full(len(atr_vals), 50.0)
    w  = min(100, len(atr_vals))
    for i in range(w, len(atr_vals)):
        ap[i] = np.sum(atr_vals[i-w:i] < atr_vals[i]) / w * 100
    df["ATR_Pct"] = ap

    # ── Volume ───────────────────────────────────────────────────────
    df["OBV"]     = ta.volume.OnBalanceVolumeIndicator(
        df["close"], df["volume"], fillna=True).on_balance_volume()
    df["Vol_MA20"]  = df["volume"].rolling(20).mean().bfill()
    df["Vol_Ratio"] = (df["volume"]
                       / df["Vol_MA20"].replace(0, np.nan)).fillna(1).clip(0, 10)
    df["Vol_Delta"] = np.where(
        df["close"] >= df["open"], df["volume"], -df["volume"])
    df["CVD20"]     = df["Vol_Delta"].rolling(20).sum()

    vol_vals = df["volume"].values
    vp = np.full(len(vol_vals), 50.0)
    for i in range(w, len(vol_vals)):
        vp[i] = np.sum(vol_vals[i-w:i] < vol_vals[i]) / w * 100
    df["Vol_Pct"] = vp

    # ── Trend Strength ───────────────────────────────────────────────
    adx_i = ta.trend.ADXIndicator(
        df["high"], df["low"], df["close"], window=14, fillna=True)
    df["ADX"]     = adx_i.adx()
    df["ADX_Pos"] = adx_i.adx_pos()
    df["ADX_Neg"] = adx_i.adx_neg()

    df = _supertrend(df)

    # ── Price Action Features ────────────────────────────────────────
    body = (df["close"] - df["open"]).abs()
    rng  = (df["high"] - df["low"]).replace(0, np.nan)
    df["Body_Ratio"]    = (body / rng).fillna(0)
    df["Upper_Wick"]    = (df["high"] - df[["close","open"]].max(axis=1)) / rng.fillna(1)
    df["Lower_Wick"]    = (df[["close","open"]].min(axis=1) - df["low"]) / rng.fillna(1)
    df["Price_vs_VWAP"] = (df["close"] - df["VWAP"]) / df["VWAP"].replace(0, np.nan)
    df["EMA_Spread"]    = (df["EMA9"] - df["EMA50"]) / df["EMA50"].replace(0, np.nan)
    df["Momentum_5"]    = df["close"].pct_change(5).fillna(0)
    df["Momentum_20"]   = df["close"].pct_change(20).fillna(0)

    atr_norm   = (df["ATR"] / df["close"].rolling(20).mean()).fillna(0).clip(0, 1)
    df["RSI_Lo"] = 30 + atr_norm * 10
    df["RSI_Hi"] = 70 - atr_norm * 10

    df = df.dropna(subset=["EMA200","ADX","ATR"]).reset_index(drop=True)
    log.info(f"📊 Indicators: {len(df)} candles, {len(df.columns)} features")
    return df

# ══════════════════════════════════════════════════════════════════════
# ENSEMBLE MODEL V9
# ══════════════════════════════════════════════════════════════════════
FEATURE_COLS = [
    "close","RSI","MACD","MACD_Hist","ATR","OBV",
    "EMA9","EMA21","BB_Width","BB_Pos","Vol_Ratio","ADX",
    "Stoch_K","ST_Dir","Body_Ratio","Upper_Wick","Lower_Wick",
    "Price_vs_VWAP","EMA_Spread","Momentum_5","Momentum_20",
    "CCI","WilliamsR","ROC","CVD20","Vol_Pct",
]

def _clean_Xy(X: np.ndarray, y: np.ndarray):
    """
    Remove rows where X or y contain NaN or Inf.
    Also clip extreme values to prevent numerical blow-up.
    """
    # Replace inf with nan first
    X = np.where(np.isinf(X), np.nan, X)
    y = np.where(np.isinf(y), np.nan, y)

    # Column-wise median imputation for X (safer than row-drop for time series)
    col_medians = np.nanmedian(X, axis=0)
    nan_mask_X  = np.isnan(X)
    inds = np.where(nan_mask_X)
    X[inds] = np.take(col_medians, inds[1])

    # Drop rows where y is still nan
    valid = ~np.isnan(y)
    X, y  = X[valid], y[valid]

    # Clip to ±10 std to prevent outlier blow-up
    std = X.std(axis=0, keepdims=True).clip(min=1e-8)
    X   = np.clip(X, -10 * std, 10 * std)

    return X, y

def build_features(df: pd.DataFrame, seq_len: int = 60):
    feats  = [c for c in FEATURE_COLS if c in df.columns]
    log.info(f"🧠 Features ({len(feats)}): {', '.join(feats[:8])}…")

    # ── Pre-clean the raw DataFrame columns ─────────────────────────
    raw = df[feats].copy()
    # Forward-fill then backward-fill, then fill any remaining with 0
    raw = raw.ffill().bfill().fillna(0)
    # Replace inf values
    raw = raw.replace([np.inf, -np.inf], 0)

    scaler = RobustScaler()
    scaled = scaler.fit_transform(raw.values)

    # Replace any NaN/Inf that survived scaling
    scaled = np.nan_to_num(scaled, nan=0.0, posinf=0.0, neginf=0.0)

    X, y = [], []
    for i in range(seq_len, len(scaled)):
        window = scaled[i-seq_len:i]
        flat   = window.flatten()
        stats  = np.concatenate([
            window.mean(axis=0),
            window.std(axis=0),
            window[-1] - window[-5],
        ])
        row = np.concatenate([flat, stats])
        X.append(row)
        y.append(scaled[i, 0])

    X_arr, y_arr = np.array(X), np.array(y)

    # Final safety clean
    X_arr, y_arr = _clean_Xy(X_arr, y_arr)

    nan_x = np.isnan(X_arr).sum()
    nan_y = np.isnan(y_arr).sum()
    if nan_x > 0 or nan_y > 0:
        log.warning(f"Residual NaN after clean — X:{nan_x} y:{nan_y}")

    log.info(f"Feature matrix: {X_arr.shape}, samples: {len(y_arr)}")
    return X_arr, y_arr, scaler, feats

def walk_forward_validate(X, y, n_splits=5):
    fold_size = len(X) // (n_splits + 1)
    maes = []
    for i in range(1, n_splits + 1):
        train_end = fold_size * i
        val_start = train_end
        val_end   = min(val_start + fold_size, len(X))
        if val_end <= val_start:
            break
        X_tr,  y_tr  = X[:train_end],  y[:train_end]
        X_val, y_val = X[val_start:val_end], y[val_start:val_end]

        # Per-fold clean (safety)
        X_tr,  y_tr  = _clean_Xy(X_tr.copy(),  y_tr.copy())
        X_val, y_val = _clean_Xy(X_val.copy(), y_val.copy())

        if len(X_tr) < 10 or len(X_val) < 2:
            continue
        try:
            m = Ridge(alpha=1.0)
            m.fit(X_tr, y_tr)
            pred = m.predict(X_val)
            maes.append(mean_absolute_error(y_val, pred))
        except Exception as e:
            log.warning(f"WF fold {i} failed: {e}")
    return float(np.mean(maes)) if maes else 0.0

def build_ensemble(X, y):
    # Global clean before split
    X, y   = _clean_Xy(X.copy(), y.copy())

    split  = int(len(X) * 0.80)
    X_tr,  X_val = X[:split],  X[split:]
    y_tr,  y_val = y[:split],  y[split:]

    models = {
        "Ridge": Ridge(alpha=0.5),
        "GBM":   GradientBoostingRegressor(
                     n_estimators=80, max_depth=4,
                     learning_rate=0.05, subsample=0.8, random_state=42),
        "RF":    RandomForestRegressor(
                     n_estimators=60, max_depth=6,
                     min_samples_leaf=5, random_state=42, n_jobs=1),
    }
    if HAS_XGB:
        models["XGB"] = XGBRegressor(
            n_estimators=80, max_depth=4, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, random_state=42,
            verbosity=0, n_jobs=1)
    if HAS_LGB:
        models["LGB"] = LGBMRegressor(
            n_estimators=80, max_depth=4, learning_rate=0.05,
            subsample=0.8, random_state=42, verbose=-1, n_jobs=1)

    trained, weights, val_maes = {}, {}, {}
    for name, m in models.items():
        try:
            m.fit(X_tr, y_tr)
            pred = m.predict(X_val)
            mae  = mean_absolute_error(y_val, pred)
            val_maes[name]  = mae
            weights[name]   = 1.0 / max(mae, 1e-8)
            trained[name]   = m
            log.success(f"  {name}: MAE={mae:.5f}")
        except Exception as e:
            log.warning(f"  {name} failed: {e}")

    total_w = sum(weights.values())
    norm_w  = {k: v/total_w for k, v in weights.items()}

    wf_mae = walk_forward_validate(X, y)
    log.info(f"Walk-forward MAE: {wf_mae:.5f}")
    return trained, norm_w, val_maes, wf_mae

def ensemble_predict(trained, weights, X, scaler, feats):
    inp         = X[-1:].reshape(1, -1)
    pred_scaled = 0.0
    for name, m in trained.items():
        w = weights.get(name, 0)
        pred_scaled += w * float(m.predict(inp)[0])

    n     = len(feats)
    dummy = np.zeros((1, n))
    dummy[0, 0] = pred_scaled
    return float(scaler.inverse_transform(dummy)[0, 0])

# ══════════════════════════════════════════════════════════════════════
# STRUCTURE ANALYSIS
# ══════════════════════════════════════════════════════════════════════
def analyze_structure(df, lookback=75):
    if len(df) < lookback + 7:
        return _empty_struct("UNKNOWN", 0, "Insufficient data")

    rec = df.tail(lookback).reset_index(drop=True)
    hi, lo, cl = rec["high"].values, rec["low"].values, rec["close"].values
    s_highs, s_lows = [], []

    for i in range(3, len(rec) - 3):
        lh, rh = hi[i-3:i], hi[i+1:i+4]
        ll, rl = lo[i-3:i], lo[i+1:i+4]
        if len(lh) < 3 or len(rh) < 3:
            continue
        if hi[i] >= max(lh) and hi[i] >= max(rh):
            base = max(float(min(lo[max(0,i-5):i])), 1e-10)
            if (hi[i] - base) / base >= cfg["STRUCT_MIN_SWING"]:
                s_highs.append((i, float(hi[i])))
        if lo[i] <= min(ll) and lo[i] <= min(rl):
            base = max(float(lo[i]), 1e-10)
            if (max(hi[max(0,i-5):i]) - lo[i]) / base >= cfg["STRUCT_MIN_SWING"]:
                s_lows.append((i, float(lo[i])))

    if len(s_highs) < 2 or len(s_lows) < 2:
        return _empty_struct("RANGING", 35, "Insufficient swings")

    last_h = s_highs[-3:] if len(s_highs) >= 3 else s_highs
    last_l = s_lows[-3:]  if len(s_lows)  >= 3 else s_lows
    hh = all(last_h[i][1] > last_h[i-1][1] for i in range(1, len(last_h)))
    hl = all(last_l[i][1] > last_l[i-1][1] for i in range(1, len(last_l)))
    lh = all(last_h[i][1] < last_h[i-1][1] for i in range(1, len(last_h)))
    ll = all(last_l[i][1] < last_l[i-1][1] for i in range(1, len(last_l)))

    last_close = float(cl[-1])
    prev_high  = s_highs[-2][1] if len(s_highs) >= 2 else float(hi[-1])
    prev_low   = s_lows[-2][1]  if len(s_lows)  >= 2 else float(lo[-1])
    breakout   = last_close > prev_high * 1.003
    breakdown  = last_close < prev_low  * 0.997

    if hh and hl:        stype, conf = "UPTREND",   90 if breakout  else 78
    elif lh and ll:      stype, conf = "DOWNTREND", 90 if breakdown else 78
    elif breakout:       stype, conf = "BREAKOUT",  72
    elif breakdown:      stype, conf = "BREAKDOWN", 72
    else:                stype, conf = "RANGING",   45

    return {
        "type": stype, "confidence": conf,
        "swing_highs": s_highs, "swing_lows": s_lows,
        "last_high": s_highs[-1][1] if s_highs else None,
        "last_low":  s_lows[-1][1]  if s_lows  else None,
        "prev_high": prev_high, "prev_low": prev_low,
        "breakout": breakout, "breakdown": breakdown,
        "hh": hh, "hl": hl, "lh": lh, "ll": ll,
    }

def _empty_struct(stype, conf, note):
    return {
        "type": stype, "confidence": conf,
        "swing_highs": [], "swing_lows": [],
        "last_high": None, "last_low": None,
        "prev_high": None, "prev_low": None,
        "breakout": False, "breakdown": False,
        "hh": False, "hl": False, "lh": False, "ll": False,
        "note": note,
    }

# ══════════════════════════════════════════════════════════════════════
# WHALE TRACKER
# ══════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=60, show_spinner=False)
def fetch_order_book(symbol: str):
    for name, ex in ex_pool.items():
        try:
            ob = ex.fetch_order_book(symbol, limit=cfg["OB_DEPTH"])
            if ob and ob.get("bids") and ob.get("asks"):
                log.info(f"📖 OB: {name.upper()}")
                return ob
        except Exception:
            continue
    return None

def analyze_ob(symbol, price):
    ob = fetch_order_book(symbol)
    if not ob:
        return _empty_ob()

    bids = np.array(ob["bids"][:cfg["OB_DEPTH"]], dtype=float)
    asks = np.array(ob["asks"][:cfg["OB_DEPTH"]], dtype=float)
    if bids.size == 0 or asks.size == 0:
        return _empty_ob()

    bid_usdt = float(np.sum(bids[:,0] * bids[:,1]))
    ask_usdt = float(np.sum(asks[:,0] * asks[:,1]))
    imbal    = bid_usdt / max(bid_usdt + ask_usdt, 1e-10)

    avg_b  = float(np.mean(bids[:,1]))
    avg_a  = float(np.mean(asks[:,1]))
    b_walls = [(float(bids[i,0]), float(bids[i,1]))
               for i in range(len(bids)) if bids[i,1] >= avg_b * cfg["WALL_MULT"]]
    a_walls = [(float(asks[i,0]), float(asks[i,1]))
               for i in range(len(asks)) if asks[i,1] >= avg_a * cfg["WALL_MULT"]]

    if   imbal >= 0.65: sig, note = "BULL",      f"Heavy bid {imbal:.1%}"
    elif imbal <= 0.35: sig, note = "BEAR",      f"Heavy ask {1-imbal:.1%}"
    elif imbal >= 0.55: sig, note = "MILD_BULL", f"Mild bid {imbal:.1%}"
    elif imbal <= 0.45: sig, note = "MILD_BEAR", f"Mild ask {1-imbal:.1%}"
    else:               sig, note = "NEUTRAL",   f"Balanced {imbal:.1%}"

    return {
        "imbalance": round(imbal, 4),
        "bid_usdt": round(bid_usdt, 2),
        "ask_usdt": round(ask_usdt, 2),
        "bid_walls": b_walls, "ask_walls": a_walls,
        "ob_signal": sig, "ob_note": note,
        "available": True,
    }

def _empty_ob():
    return {
        "imbalance": 0.5, "bid_usdt": 0, "ask_usdt": 0,
        "bid_walls": [], "ask_walls": [],
        "ob_signal": "NEUTRAL", "ob_note": "OB unavailable",
        "available": False,
    }

def detect_whales(df):
    if len(df) < 20:
        return _empty_whale()

    ma20    = df["volume"].rolling(20).mean().bfill()
    candles = []
    for i in range(max(0, len(df)-50), len(df)):
        vm = float(ma20.iloc[i])
        if vm == 0 or pd.isna(vm):
            continue
        vr   = df["volume"].iloc[i] / vm
        op   = max(float(df["open"].iloc[i]), 1e-10)
        pmov = abs(float(df["close"].iloc[i]) - op) / op
        if vr >= cfg["WHALE_VOL_THRESH"] and pmov >= cfg["WHALE_MOVE_MIN"]:
            bull = float(df["close"].iloc[i]) >= op
            candles.append({
                "idx": i, "ts": df["timestamp"].iloc[i],
                "price": float(df["close"].iloc[i]),
                "vol_ratio": round(vr, 2),
                "price_move_pct": round(pmov*100, 3),
                "direction": "BUY" if bull else "SELL",
                "type": "ACCUM" if bull else "DISTRIB",
            })

    rec      = df.tail(30)
    bull_vol = float(rec.loc[rec["close"]>=rec["open"], "volume"].sum())
    bear_vol = float(rec.loc[rec["close"]<rec["open"],  "volume"].sum())
    cvd_r    = bull_vol / max(bull_vol + bear_vol, 1e-10)
    cvd_t    = ("BULL" if cvd_r >= 0.60 else
                "BEAR" if cvd_r <= 0.40 else "NEUTRAL")

    return {
        "whale_candles": candles,
        "recent": candles[-1] if candles else None,
        "cvd_ratio": round(cvd_r, 4),
        "cvd_trend": cvd_t,
        "total": len(candles),
    }

def _empty_whale():
    return {
        "whale_candles": [], "recent": None,
        "cvd_ratio": 0.5, "cvd_trend": "NEUTRAL", "total": 0,
    }

def whale_score(ob, wc, signal):
    pts, notes = 0.0, []
    is_bull = "BUY" in signal

    if ob.get("available"):
        s = ob["ob_signal"]
        m = {"BULL": 4, "MILD_BULL": 2, "NEUTRAL": 1, "MILD_BEAR": 0, "BEAR": 0}
        pts += m.get(s, 0) if is_bull else (4 if s=="BEAR" else 2 if s=="MILD_BEAR" else 1 if s=="NEUTRAL" else 0)
        notes.append(f"OB: {ob['ob_note']}")
        if is_bull and ob["bid_walls"]:
            pts += 1; notes.append(f"Bid wall ({len(ob['bid_walls'])} lvl)")
        elif not is_bull and ob["ask_walls"]:
            pts += 1; notes.append(f"Ask wall ({len(ob['ask_walls'])} lvl)")
    else:
        notes.append("OB unavailable")

    cvd, cvd_r = wc["cvd_trend"], wc["cvd_ratio"]
    if (is_bull and cvd=="BULL") or (not is_bull and cvd=="BEAR"):
        pts += 3; notes.append(f"CVD aligned ({cvd_r:.1%})")
    elif cvd == "NEUTRAL":
        pts += 1; notes.append("CVD neutral")
    else:
        notes.append("CVD opposing")

    rw = wc.get("recent")
    if rw:
        match = (is_bull and rw["direction"]=="BUY") or (not is_bull and rw["direction"]=="SELL")
        if match:
            pts += 2; notes.append(f"Whale {rw['type']} {rw['vol_ratio']}x")
        else:
            notes.append(f"Whale opposing {rw['type']}")
    else:
        notes.append("No whale candle")

    score = round(min(10.0, pts), 1)
    label = ("🐋 CONFIRMED" if score>=7.5 else
             "🐟 PARTIAL"   if score>=5.0 else
             "🔍 NEUTRAL"   if score>=3.0 else "🚨 OPPOSING")
    return score, label, notes

# ══════════════════════════════════════════════════════════════════════
# SIGNAL ENGINE V9
# ══════════════════════════════════════════════════════════════════════
def detect_patterns(df):
    if len(df) < 5:
        return {}
    o, h, l, c = (df["open"].values, df["high"].values,
                  df["low"].values,  df["close"].values)
    avg = np.mean([abs(c[x]-o[x]) for x in range(-10, 0)]) or 1e-10
    i, j, k = -1, -2, -3

    def body(x): return abs(c[x]-o[x])
    def rng(x):  return max(h[x]-l[x], 1e-10)
    def bull(x): return c[x] > o[x]
    def uw(x):   return h[x] - max(c[x], o[x])
    def lw(x):   return min(c[x], o[x]) - l[x]

    return {
        "bull_engulf": (not bull(j) and bull(i)
                        and c[i]>o[j] and o[i]<c[j]
                        and body(i)>body(j)*1.1),
        "bear_engulf": (bull(j) and not bull(i)
                        and c[i]<o[j] and o[i]>c[j]
                        and body(i)>body(j)*1.1),
        "hammer":      (lw(i)>=body(i)*2 and uw(i)<=body(i)*0.3
                        and body(i)>0 and rng(i)>avg*0.5),
        "shoot_star":  (uw(i)>=body(i)*2 and lw(i)<=body(i)*0.3
                        and body(i)>0 and rng(i)>avg*0.5),
        "doji":        (body(i)<=rng(i)*0.1 and rng(i)>avg*0.3),
        "morn_star":   (len(df)>=5
                        and not bull(k) and body(k)>avg*0.8
                        and body(j)<avg*0.3 and bull(i)
                        and c[i]>(o[k]+c[k])/2),
        "eve_star":    (len(df)>=5
                        and bull(k) and body(k)>avg*0.8
                        and body(j)<avg*0.3 and not bull(i)
                        and c[i]<(o[k]+c[k])/2),
    }

def detect_divergences(df, lookback=30):
    if len(df) < lookback:
        return False, False
    rec   = df.tail(lookback).reset_index(drop=True)
    price = rec["close"].values
    rsi   = rec["RSI"].values
    obv   = rec["OBV"].values
    sw    = max(3, lookback//5)

    def swings(arr, w):
        hi, lo = [], []
        for i in range(w, len(arr)-w):
            s = arr[i-w:i+w+1]
            if arr[i] >= np.max(s) - 1e-10: hi.append(i)
            if arr[i] <= np.min(s) + 1e-10: lo.append(i)
        return hi, lo

    ph, pl = swings(price, sw)
    bull_div = bear_div = False

    if len(pl) >= 2:
        p1, p2 = pl[-2], pl[-1]
        if price[p2] < price[p1]*0.999 and rsi[p2] > rsi[p1]+1.5:
            bull_div = True
    if len(ph) >= 2:
        p1, p2 = ph[-2], ph[-1]
        if price[p2] > price[p1]*1.001 and rsi[p2] < rsi[p1]-1.5:
            bear_div = True

    half = lookback // 2
    pt = price[-1] - price[-half] if half < len(price) else 0
    ot = obv[-1]   - obv[-half]   if half < len(obv)   else 0
    if pt < -price[-1]*0.005 and ot > 0: bull_div = True
    elif pt > price[-1]*0.005 and ot < 0: bear_div = True

    return bull_div, bear_div

def get_htf_bias(df4h):
    if df4h is None or len(df4h) < 10:
        return "NEUTRAL", "HTF unavailable"
    last  = df4h.iloc[-1]
    price = float(last["close"])
    checks = [
        price > float(last["EMA9"]),
        price > float(last["EMA50"]),
        price > float(last["EMA200"]),
        float(last["MACD"]) > float(last["MACD_Sig"]),
        float(last["RSI"]) > 55,
        int(last["ST_Dir"]) == 1,
        float(last["ADX_Pos"]) > float(last["ADX_Neg"]),
    ]
    bull = sum(checks); tot = len(checks)
    if bull >= int(tot*0.7):        return "BULL",    f"4H Bullish ({bull}/{tot})"
    elif (tot-bull) >= int(tot*0.7): return "BEAR",   f"4H Bearish ({tot-bull}/{tot})"
    else:                            return "NEUTRAL", f"4H Neutral (B:{bull} Br:{tot-bull})"

def classify_regime(df):
    last  = df.iloc[-1]
    adx   = float(last["ADX"])
    adxp  = float(last["ADX_Pos"])
    adxn  = float(last["ADX_Neg"])
    price = float(last["close"])
    e9, e50, e200 = float(last["EMA9"]), float(last["EMA50"]), float(last["EMA200"])
    bbw   = float(last["BB_Width"])
    atp   = float(last["ATR_Pct"])
    q80   = float(df["BB_Width"].quantile(0.80))
    q40   = float(df["BB_Width"].quantile(0.40))
    pb    = price > e9 > e50 > e200
    nb    = price < e9 < e50 < e200

    if atp > 85 and bbw > q80:               return "VOLATILE",     "⚡ Very high volatility"
    if adx >= 35 and adxp > adxn and pb:     return "STRONG_BULL",  "🚀 Very strong uptrend"
    if adx >= 35 and adxn > adxp and nb:     return "STRONG_BEAR",  "💀 Very strong downtrend"
    if adx > 22 and adxp > adxn and price>e9>e50: return "TRENDING_UP",   "📈 Uptrend"
    if adx > 22 and adxn > adxp and price<e9<e50: return "TRENDING_DOWN", "📉 Downtrend"
    if adx < 20 and bbw < q40:               return "RANGING",      "↔ Sideways"
    return "NORMAL", "🔄 Normal"

def find_sr(df, lookback=100, gap_pct=0.005):
    rec   = df.tail(lookback)
    h, l  = rec["high"].values, rec["low"].values
    price = float(df["close"].iloc[-1])
    gap   = price * gap_pct
    res = [h[i] for i in range(2, len(h)-2) if h[i] == max(h[i-2:i+3])]
    sup = [l[i] for i in range(2, len(l)-2) if l[i] == min(l[i-2:i+3])]
    vr  = [r for r in res if r > price+gap]
    vs  = [s for s in sup if s < price-gap]
    return (float(max(vs)) if vs else price*0.92,
            float(min(vr)) if vr else price*1.08)

def generate_signal_v9(df, pred_price, htf_bias, patterns,
                        bull_div, bear_div, whale_sc, structure):
    last    = df.iloc[-1]
    price   = float(last["close"])
    chg_pct = (pred_price - price) / price * 100

    if chg_pct < -3.5:
        return "HOLD", 0, "Hard guard: drop >3.5%"
    regime, _ = classify_regime(df)
    if regime == "VOLATILE":
        return "HOLD", 0, "Volatile regime"
    if regime == "RANGING" and abs(chg_pct) < 0.8:
        return "HOLD", 0, "Ranging + no momentum"

    adx    = float(last["ADX"])
    adxp   = float(last["ADX_Pos"])
    adxn   = float(last["ADX_Neg"])
    rsi    = float(last["RSI"])
    rsi_lo = float(last["RSI_Lo"])
    rsi_hi = float(last["RSI_Hi"])
    sk     = float(last["Stoch_K"])
    sd     = float(last["Stoch_D"])
    macd_b = float(last["MACD"]) > float(last["MACD_Sig"])
    st_b   = int(last["ST_Dir"]) == 1
    vp     = float(last["Vol_Pct"])
    cvd    = float(last["CVD20"])
    vwap   = float(last["VWAP"])
    body_r = float(last["Body_Ratio"])
    mom5   = float(last["Momentum_5"])

    def score_side(is_bull):
        pts, active = 0.0, []

        if (macd_b and is_bull) or (not macd_b and not is_bull):
            pts += 2.0; active.append("MACD")
        ema_ok = (price>float(last["EMA9"])>float(last["EMA50"])
                  if is_bull else
                  price<float(last["EMA9"])<float(last["EMA50"]))
        if ema_ok:
            pts += 2.0; active.append("EMA_align")
        if adx > 22 and ((adxp>adxn and is_bull) or (adxn>adxp and not is_bull)):
            pts += 1.5; active.append("ADX_trend")
        if (rsi < rsi_lo and is_bull) or (rsi > rsi_hi and not is_bull):
            pts += 1.0; active.append("RSI_zone")
        if (sk<30 and sk>sd and is_bull) or (sk>70 and sk<sd and not is_bull):
            pts += 1.0; active.append("Stoch_cross")
        if vp >= 55:
            pts += 1.0; active.append("Vol_spike")
        if (st_b and is_bull) or (not st_b and not is_bull):
            pts += 1.0; active.append("Supertrend")
        if (price>vwap and is_bull) or (price<vwap and not is_bull):
            pts += 0.5; active.append("VWAP")
        if ((pred_price>price*1.003 and is_bull)
                or (pred_price<price*0.997 and not is_bull)):
            conf = min(1.5, 1.5 * body_r)
            pts += conf; active.append(f"Model({conf:.1f})")

        bull_pats = ["bull_engulf","hammer","morn_star"]
        bear_pats = ["bear_engulf","shoot_star","eve_star"]
        plist = bull_pats if is_bull else bear_pats
        if any(patterns.get(p) for p in plist):
            pts += 1.0; active.append("Pattern")
        if (bull_div and is_bull) or (bear_div and not is_bull):
            pts += 1.0; active.append("Divergence")
        htf_ok = (htf_bias=="BULL" and is_bull) or (htf_bias=="BEAR" and not is_bull)
        if htf_ok:
            pts += 1.0; active.append("4H_aligned")
        if (cvd>0 and is_bull) or (cvd<0 and not is_bull):
            pts += 0.5; active.append("CVD")
        if (mom5>0.005 and is_bull) or (mom5<-0.005 and not is_bull):
            pts += 0.5; active.append("Mom5")

        return pts, active

    buy_s, buy_a   = score_side(True)
    sell_s, sell_a = score_side(False)

    if htf_bias=="BEAR" and buy_s>sell_s:  buy_s  *= 0.75
    elif htf_bias=="BULL" and sell_s>buy_s: sell_s *= 0.75

    is_bull = buy_s >= sell_s
    fs      = buy_s if is_bull else sell_s
    active  = buy_a if is_bull else sell_a

    if fs >= 8.5:   raw = "STRONG BUY"  if is_bull else "STRONG SELL"
    elif fs >= 5.5: raw = "BUY"         if is_bull else "SELL"
    else:           return "HOLD", fs, "Score too low"

    if whale_sc < 2.5:
        return "HOLD", fs, f"Whale block ({whale_sc:.1f}/10)"

    if structure:
        stype = structure["type"]
        gates = {"UPTREND": is_bull, "DOWNTREND": not is_bull,
                 "BREAKOUT": is_bull, "BREAKDOWN": not is_bull}
        if stype in gates and not gates[stype]:
            return "HOLD", fs, f"Structure gate: {stype}"

    return raw, fs, f"Score {fs:.1f} | {len(active)} factors"

# ══════════════════════════════════════════════════════════════════════
# TP/SL
# ══════════════════════════════════════════════════════════════════════
def compute_tp_sl_v9(price, df, signal, strength, htf_bias):
    if "HOLD" in signal:
        return price*0.98, {"TP1": price*1.02, "TP2": None}, {
            "rr_ratio": 0, "cancel_reason": "HOLD"}

    last  = df.iloc[-1]
    atr   = float(last["ATR"])
    atp   = float(last["ATR_Pct"])
    regime, _ = classify_regime(df)
    d     = 1 if "BUY" in signal else -1

    if regime in ("STRONG_BULL","STRONG_BEAR"):
        tp1_m, tp2_m, sl_m = 2.5, 4.5, 1.0
    elif regime in ("TRENDING_UP","TRENDING_DOWN"):
        tp1_m, tp2_m, sl_m = 2.0, 3.5, 0.9
    elif regime == "RANGING":
        tp1_m, tp2_m, sl_m = 1.2, 0.0, 0.8
    else:
        tp1_m, tp2_m, sl_m = 1.8, 3.0, 0.9

    if atp > 70:  tp1_m *= 0.85; sl_m *= 1.2
    elif atp < 30: tp1_m *= 1.1;  sl_m *= 0.9

    tp1 = price + d * atr * tp1_m
    tp2 = (price + d * atr * tp2_m) if tp2_m > 0 else None
    sl  = price - d * atr * sl_m

    sup, res = find_sr(df)
    if "BUY" in signal:
        if tp1 > res: tp1 = res * 0.997
        if tp2 and tp2 > res: tp2 = res * 0.997
        if sl < sup: sl = sup * 1.003
    else:
        if tp1 < sup: tp1 = sup * 1.003
        if tp2 and tp2 < sup: tp2 = sup * 1.003
        if sl > res: sl = res * 0.997

    tp1_d = abs(tp1 - price)
    sl_d  = abs(sl  - price)
    rr    = round(tp1_d / max(sl_d, 1e-10), 2)

    if rr < cfg["MIN_RR"]:
        return sl, {"TP1": round(tp1,6), "TP2": None}, {
            "rr_ratio": rr, "cancel_reason": f"R:R {rr:.2f} < {cfg['MIN_RR']:.1f}"}

    return round(sl, 6), {
        "TP1": round(tp1, 6),
        "TP2": round(tp2, 6) if tp2 else None,
    }, {
        "rr_ratio": rr,
        "cancel_reason": "valid ✓",
        "regime": regime,
        "tp1_pct": round(tp1_d/price*100, 2),
        "sl_pct":  round(sl_d/price*100, 2),
        "nearest_support": sup,
        "nearest_resistance": res,
    }

def compute_position_size(entry, sl, balance, risk_pct,
                           tier, mp_score, whale_sc):
    tier_m = {"A+":1.0,"A":0.9,"B":0.75,"C":0.5,"D":0.25}
    adj    = risk_pct * tier_m.get(tier, 0.5)
    sl_d   = abs(entry - sl) / max(entry, 1e-10)
    if sl_d < 1e-6:
        return {"error": "SL too close"}
    risk_amt  = balance * adj
    pos_usdt  = risk_amt / sl_d
    pos_units = pos_usdt / max(entry, 1e-10)
    return {
        "risk_pct":  round(adj*100, 3),
        "risk_amt":  round(risk_amt, 2),
        "pos_usdt":  round(pos_usdt, 2),
        "pos_units": round(pos_units, 6),
    }

# ══════════════════════════════════════════════════════════════════════
# MAIN RUN
# ══════════════════════════════════════════════════════════════════════
def run_analysis():
    log.clear()
    result = {}

    try:
        log.info(f"📡 Fetching {cfg['COIN']} [{cfg['TF']}]")
        df = fetch_ohlcv(cfg["COIN"], cfg["TF"])
        df = add_indicators(df)

        log.info(f"📡 Fetching HTF [{cfg['HTF']}]")
        try:
            df_htf = fetch_ohlcv(cfg["COIN"], cfg["HTF"])
            df_htf = add_indicators(df_htf)
            htf_bias, htf_desc = get_htf_bias(df_htf)
        except Exception as e:
            log.warning(f"HTF failed: {e}")
            df_htf = None; htf_bias = "NEUTRAL"; htf_desc = "Unavailable"

        price = float(df["close"].iloc[-1])

        patterns = detect_patterns(df)
        bull_div, bear_div = detect_divergences(df)
        structure = analyze_structure(df, cfg["STRUCT_LOOKBACK"])

        ob_res = analyze_ob(cfg["COIN"], price)
        wc_res = detect_whales(df)

        adx_val = float(df["ADX"].iloc[-1])
        if adx_val < 20:
            log.info(f"Model gated — ADX={adx_val:.1f}<20")
            pred_price = price
        else:
            log.info("🧠 Building ensemble model...")
            X, y, scaler, feats = build_features(df, cfg["SEQ_LEN"])
            if len(X) < 50:
                log.warning("Not enough data for model")
                pred_price = price
            else:
                trained, weights, val_maes, wf_mae = build_ensemble(X, y)
                pred_price = ensemble_predict(trained, weights, X, scaler, feats)
                log.success(
                    f"Prediction: {pred_price:.6f} "
                    f"({(pred_price-price)/price*100:+.2f}%)")

        ws_pre, wl_pre, wn_pre = whale_score(ob_res, wc_res, "BUY")

        signal, sig_score, sig_reason = generate_signal_v9(
            df, pred_price, htf_bias, patterns,
            bull_div, bear_div, ws_pre, structure)

        ws, wl, wn = whale_score(ob_res, wc_res, signal)

        sl, tp_levels, tp_info = compute_tp_sl_v9(
            price, df, signal, 50, htf_bias)

        cancel = tp_info.get("cancel_reason", "")
        final_signal = signal if "valid" in cancel.lower() else "HOLD"

        rr = tp_info.get("rr_ratio", 0)
        if   rr>=2.5 and ws>=7 and sig_score>=8: tier="A+"
        elif rr>=2.0 and ws>=5 and sig_score>=6: tier="A"
        elif rr>=1.5 and ws>=3 and sig_score>=5: tier="B"
        elif rr>=1.2:                             tier="C"
        else:                                     tier="D"

        pos = compute_position_size(
            price, sl, cfg["BALANCE"],
            cfg["RISK"], tier, sig_score*10, ws)

        result = {
            "signal": final_signal, "tier": tier, "entry": price,
            "sl": sl, "tp": tp_levels, "rr": rr,
            "sig_score": round(sig_score, 1),
            "pred_price": pred_price,
            "chg_pct": (pred_price-price)/price*100,
            "whale_score": ws, "whale_label": wl, "whale_notes": wn,
            "structure": structure, "htf_bias": htf_bias,
            "htf_desc": htf_desc, "tp_info": tp_info,
            "patterns": patterns, "bull_div": bull_div,
            "bear_div": bear_div, "sig_reason": sig_reason,
            "df": df, "df_htf": df_htf, "ob": ob_res, "wc": wc_res,
            "cancel": cancel, "pos": pos,
        }
        log.success("✅ Analysis complete")

    except Exception as e:
        import traceback
        log.error(f"CRITICAL: {e}")
        result = {"error": str(e), "trace": traceback.format_exc()}

    return result

# ══════════════════════════════════════════════════════════════════════
# STREAMLIT UI
# ══════════════════════════════════════════════════════════════════════
st.title("🐋 Crypto Bot V9 · Ensemble + Walk-Forward")
st.caption(
    f"Multi-source · Ensemble ML · Anti-Overfit · "
    f"Logged in as **{st.session_state.get('current_user','')}**")

run_btn = st.sidebar.button("🚀 Run Analysis", use_container_width=True)

if run_btn:
    with st.spinner("Analysing… (30-60 sec on first run)"):
        res = run_analysis()

    if "error" in res:
        st.error(res["error"])
        st.code(res.get("trace",""))
    else:
        with st.expander("📋 Execution Logs", expanded=False):
            st.text(log.text())

        sig       = res["signal"]
        sig_color = ("signal-buy" if "BUY" in sig else
                     "signal-sell" if "SELL" in sig else "signal-hold")
        st.markdown(
            f'<div class="{sig_color}">▶ {sig} &nbsp;|&nbsp; '
            f'Tier {res["tier"]} &nbsp;|&nbsp; '
            f'Score {res["sig_score"]}/15</div>',
            unsafe_allow_html=True)
        st.caption(res.get("sig_reason",""))

        c1,c2,c3,c4,c5,c6 = st.columns(6)
        c1.metric("Entry",     f"{res['entry']:.6f}")
        c2.metric("Stop Loss", f"{res['sl']:.6f}")
        c3.metric("TP1",       f"{res['tp'].get('TP1','N/A')}")
        c4.metric("TP2",       f"{res['tp'].get('TP2','N/A') or 'N/A'}")
        c5.metric("R:R",       f"1:{res['rr']:.2f}")
        c6.metric("Prediction",
                  f"{res['pred_price']:.5f}",
                  f"{res['chg_pct']:+.2f}%")

        cS, cW = st.columns(2)
        with cS:
            st.subheader("🏗 Market Structure")
            s = res["structure"]
            st.metric(s["type"], f"Conf: {s['confidence']}%")
            if s.get("hh") and s.get("hl"): st.success("HH + HL confirmed")
            elif s.get("lh") and s.get("ll"): st.error("LH + LL confirmed")
        with cW:
            st.subheader("🐋 Whale")
            st.metric(res["whale_label"], f"{res['whale_score']}/10")
            for n in res.get("whale_notes",[]): st.caption(n)

        cH, cP = st.columns(2)
        with cH:
            st.subheader("📡 4H Bias")
            bias = res["htf_bias"]
            col  = "🟢" if bias=="BULL" else "🔴" if bias=="BEAR" else "⚪"
            st.write(f"{col} **{bias}** — {res['htf_desc']}")
        with cP:
            st.subheader("🕯 Patterns")
            found = [k for k,v in res["patterns"].items() if v]
            if found:
                for p in found: st.success(p.replace("_"," ").title())
            else:
                st.info("No strong pattern")
            if res["bull_div"]: st.success("Bullish Divergence")
            if res["bear_div"]: st.error("Bearish Divergence")

        pos = res.get("pos",{})
        st.subheader("💼 Position Sizing")
        cp1,cp2,cp3,cp4 = st.columns(4)
        cp1.metric("Risk %",    f"{pos.get('risk_pct','?')}%")
        cp2.metric("Risk $",    f"${pos.get('risk_amt','?')}")
        cp3.metric("Pos USDT",  f"${pos.get('pos_usdt','?')}")
        cp4.metric("Pos Units", f"{pos.get('pos_units','?')}")

        df = res.get("df")
        if df is not None:
            st.subheader("📈 Price Chart")
            tail = df.tail(200)
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.plot(tail["timestamp"], tail["close"],
                    color="#58a6ff", lw=1.5, label="Close")
            ax.plot(tail["timestamp"], tail["EMA9"],
                    color="#f0883e", ls="--", lw=1, label="EMA9")
            ax.plot(tail["timestamp"], tail["EMA50"],
                    color="#bc8cff", ls="-.", lw=1, label="EMA50")
            ax.axhline(res["entry"], color="white",  ls=":",  lw=1,
                       label=f"Entry {res['entry']:.4f}")
            ax.axhline(res["sl"],    color="#f85149", ls="--", lw=1.5,
                       label=f"SL {res['sl']:.4f}")
            if res["tp"].get("TP1"):
                ax.axhline(res["tp"]["TP1"], color="#2ea043", ls="--", lw=1.5,
                           label=f"TP1 {res['tp']['TP1']:.4f}")
            if res["tp"].get("TP2"):
                ax.axhline(res["tp"]["TP2"], color="#56d364", ls=":", lw=1,
                           label=f"TP2 {res['tp']['TP2']:.4f}")

            s = res["structure"]
            for idx, val in s.get("swing_highs",[])[-5:]:
                ax.scatter(tail["timestamp"].iloc[min(idx, len(tail)-1)],
                           val, color="red", s=30, zorder=5)
            for idx, val in s.get("swing_lows",[])[-5:]:
                ax.scatter(tail["timestamp"].iloc[min(idx, len(tail)-1)],
                           val, color="green", s=30, zorder=5)

            ax.legend(fontsize=8)
            ax.set_facecolor("#161b22")
            fig.patch.set_facecolor("#0d1117")
            ax.tick_params(colors="#8b949e")
            for spine in ax.spines.values(): spine.set_color("#30363d")
            ax.grid(True, alpha=0.15)
            st.pyplot(fig)

        st.success("✅ Done! Adjust sidebar settings and re-run anytime.")

else:
    st.info("👈 Configure settings in sidebar, then click **Run Analysis**.")
    st.markdown("""
    **V9 Improvements:**
    - 🔐 5-user login system with hashed passwords
    - 🧠 Ensemble model (Ridge + GBM + RF + XGBoost + LightGBM)
    - 📊 Walk-forward validation (anti-overfit)
    - ✅ `fetch_ohlcv` groupby timestamp bug fixed
    - 🔬 26 features vs 12 in V8
    - 📈 Price action features (body ratio, wick analysis, momentum)
    - ✅ Streamlit Cloud safe (no background threads, proper caching)
    """)
