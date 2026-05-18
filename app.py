"""
╔══════════════════════════════════════════════════════════════════════════╗
║          CRYPTO TRADING BOT  v8  ·  STREAMLIT DASHBOARD                ║
║  Structure + Whale Edition  ·  Market Power Engine  ·  Anti-Overfit    ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import os, sys, time, queue, hashlib, pickle, traceback, warnings, threading
import concurrent.futures
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ── PyTorch (replaces TensorFlow/Keras) ────────────────────────────────
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

import ccxt
import ta
from sklearn.preprocessing import MinMaxScaler

warnings.filterwarnings("ignore")

# ── Streamlit Page Config & Dark Theme ─────────────────────────────────
st.set_page_config(
    page_title="Crypto Bot V8",
    page_icon="🐋",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(
    """
<style>
    .block-container { padding-top: 1rem; }
    .stMetric { background-color: #0d1117; border-radius: 8px; padding: 10px; }
    div[data-testid="stMetricValue"] { color: #58a6ff; }
    .stButton button { background-color: #238636; color: white; border: none; }
    .stButton button:hover { background-color: #2ea043; }
</style>
""",
    unsafe_allow_html=True,
)

# ── Logger ──────────────────────────────────────────────────────────────
class StreamlitLogger:
    def __init__(self):
        self.messages = []
    def info(self, msg):
        self.messages.append(("ℹ️", msg))
    def success(self, msg):
        self.messages.append(("✅", msg))
    def warning(self, msg):
        self.messages.append(("⚠️", msg))
    def error(self, msg):
        self.messages.append(("❌", msg))
    def get_text(self):
        return "\n".join(f"{icon} {msg}" for icon, msg in self.messages)

logger = StreamlitLogger()

# ── Config from Sidebar ─────────────────────────────────────────────────
def get_config():
    st.sidebar.header("⚙️ Configuration")
    coin = st.sidebar.text_input("Coin Symbol", "OP/USDT")
    tf_main = st.sidebar.selectbox("Main Timeframe", ["1h", "4h", "15m", "30m"], index=0)
    tf_higher = st.sidebar.selectbox("Higher Timeframe", ["4h", "1d", "1h"], index=0)
    balance = st.sidebar.number_input("Account Balance (USDT)", 100.0, 1_000_000.0, 1000.0, 100.0)
    risk = st.sidebar.slider("Risk per Trade (%)", 0.1, 5.0, 1.0, 0.1) / 100.0
    min_rr = st.sidebar.slider("Min Risk:Reward", 1.0, 3.0, 1.5, 0.1)
    whale_vol_thresh = st.sidebar.slider("Whale Vol Threshold (x avg)", 2.0, 5.0, 3.0, 0.5)
    whale_price_move = st.sidebar.slider("Whale Min Price Move (%)", 0.1, 1.0, 0.3, 0.1) / 100.0
    structure_lookback = st.sidebar.slider("Structure Lookback (bars)", 20, 200, 75, 5)
    return {
        "COIN_SYMBOL": coin,
        "TIMEFRAME_MAIN": tf_main,
        "TIMEFRAME_HIGHER": tf_higher,
        "ACCOUNT_BALANCE": balance,
        "RISK_PER_TRADE": risk,
        "MIN_RISK_REWARD": min_rr,
        "WHALE_VOL_THRESHOLD": whale_vol_thresh,
        "WHALE_PRICE_MOVE_MIN": whale_price_move,
        "STRUCTURE_LOOKBACK": structure_lookback,
        "MODEL_CACHE_DIR": "/tmp/model_cache_v8",
        "USE_MODEL_CACHE": True,
        "ORDER_BOOK_DEPTH": 20,
        "WALL_MULT": 5.0,
        "WHALE_SIZE_WEIGHT": 0.15,
        "STRUCTURE_MIN_SWING": 0.008,
        "WORKERS": 8,
    }

cfg = get_config()

# ── Market Data Engine (Cached) ─────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_engine():
    return MarketDataEngine(workers=cfg["WORKERS"])

class MarketDataEngine:
    EXCHANGES = ["binance", "bybit", "okx", "kucoin", "gateio", "mexc"]

    def __init__(self, workers=8):
        self.pool = {}
        for name in self.EXCHANGES:
            try:
                self.pool[name] = getattr(ccxt, name)({"enableRateLimit": True})
            except Exception:
                pass
        self._scores = {ex: 1.0 for ex in self.pool}
        self._cache = {}
        self._cache_ts = {}
        self._ttl = 120
        self._exec = concurrent.futures.ThreadPoolExecutor(max_workers=workers)

    def fetch(self, symbol, timeframe="1h", timeout=12, need=2):
        key = f"{symbol}_{timeframe}"
        now = time.time()
        if key in self._cache and now - self._cache_ts.get(key, 0) < self._ttl:
            logger.info(f"⚡ cache hit [{symbol} {timeframe}]")
            return self._cache[key]

        logger.info(f"📡 Fetching {symbol} [{timeframe}]")
        q, stop, limit = queue.Queue(), threading.Event(), (500 if timeframe in ("4h","1d") else 1500)

        def _one(name):
            if stop.is_set(): return
            try:
                t0 = time.time()
                ohlcv = self.pool[name].fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
                df = pd.DataFrame(ohlcv, columns=["timestamp","open","high","low","close","volume"])
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
                df["_src"] = name
                elapsed = time.time() - t0
                if len(df) >= 60:
                    self._scores[name] = max(0.1, 1.0 / max(elapsed, 0.01))
                    q.put(df)
                    logger.success(f"✓ {name.upper():<8} {len(df)} candles ({elapsed:.1f}s)")
                else:
                    logger.warning(f"⚠ {name.upper():<8} only {len(df)} candles")
            except Exception as e:
                self._scores[name] = self._scores.get(name, 1.0) * 0.8
                logger.error(f"✗ {name.upper():<8} {str(e)[:55]}")

        sorted_ex = sorted(self.pool, key=lambda x: self._scores.get(x, 1.0), reverse=True)
        threads = [threading.Thread(target=_one, args=(ex,), daemon=True) for ex in sorted_ex[:5]]
        for t in threads: t.start()

        results, deadline = [], time.time() + timeout
        while time.time() < deadline:
            try:
                results.append(q.get(timeout=0.5))
                if len(results) >= need:
                    stop.set()
                    logger.info(f"⚡ {need} responses collected – proceeding")
                    break
            except queue.Empty:
                if all(not t.is_alive() for t in threads):
                    break
        if not results:
            raise RuntimeError(f"All exchanges failed for {symbol} [{timeframe}]")

        merged = self._merge(results)
        self._cache[key] = merged
        self._cache_ts[key] = now
        return merged

    def _merge(self, frames):
        combined = pd.concat(frames, ignore_index=True).sort_values("timestamp")
        n_src = combined["_src"].nunique() if "_src" in combined.columns else 1
        if n_src > 1:
            def _agg(g):
                vol = g["volume"].values
                w = vol if vol.sum() > 0 else np.ones(len(g))
                return pd.Series({
                    "timestamp": g["timestamp"].iloc[0],
                    "open": np.average(g["open"].values, weights=w),
                    "high": np.average(g["high"].values, weights=w),
                    "low": np.average(g["low"].values, weights=w),
                    "close": np.average(g["close"].values, weights=w),
                    "volume": float(np.median(vol)),
                    "source": "multi_vwap",
                    "volume_quality": "multi_median",
                    "n_sources": len(g),
                })
            agg = combined.groupby("timestamp", sort=True).apply(_agg).reset_index(drop=True)
        else:
            combined = combined.drop_duplicates(subset=["timestamp"], keep="last")
            if "_src" in combined.columns:
                combined = combined.rename(columns={"_src": "source"})
            combined["volume_quality"] = "single"
            combined["n_sources"] = 1
            agg = combined.reset_index(drop=True)

        for col in ["open","high","low","close","volume"]:
            agg[col] = agg[col].interpolate(method="linear").ffill().bfill()

        q1, q3 = agg["volume"].quantile(0.25), agg["volume"].quantile(0.75)
        cap = q3 + 5.0 * (q3 - q1)
        clipped = int((agg["volume"] > cap).sum())
        agg["volume"] = agg["volume"].clip(upper=cap)
        if clipped:
            logger.warning(f"🔧 Volume fix: clipped {clipped} outlier(s) (>{cap:.2f})")

        q_label = agg["volume_quality"].iloc[0] if "volume_quality" in agg.columns else "?"
        logger.info(f"📊 Merged: {len(agg)} candles  sources:{n_src}  vol:{q_label}")
        return agg.reset_index(drop=True)

    def get_spread(self, symbol):
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

_engine = get_engine()

def get_data(symbol, tf):
    try:
        return _engine.fetch(symbol, tf, timeout=12, need=2)
    except Exception as e:
        logger.warning(f"Primary fetch failed: {e} → fallback sequential")
        return _fallback_fetch(symbol, tf)

def _fallback_fetch(symbol, tf):
    limit = 500 if tf in ("4h","1d") else 1500
    for name in MarketDataEngine.EXCHANGES:
        try:
            ex = getattr(ccxt, name)({"enableRateLimit": True})
            ohlcv = ex.fetch_ohlcv(symbol, timeframe=tf, limit=limit)
            df = pd.DataFrame(ohlcv, columns=["timestamp","open","high","low","close","volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
            df["source"] = name
            df["volume_quality"] = "single"
            df["n_sources"] = 1
            df = df.dropna()
            if len(df) >= 60:
                logger.success(f"✓ Fallback {name.upper()}: {len(df)} candles")
                return df
        except Exception:
            continue
    raise RuntimeError(f"All exchanges failed for {symbol} [{tf}]")

# ── Whale Tracker ───────────────────────────────────────────────────────
class WhaleTracker:
    def __init__(self, pool):
        self.pool = pool
        self._ob = {}
        self._ob_ts = {}
        self._ob_ttl = 60

    def fetch_ob(self, symbol):
        key = f"ob_{symbol}"
        now = time.time()
        if key in self._ob and now - self._ob_ts.get(key, 0) < self._ob_ttl:
            return self._ob[key]
        for name, ex in self.pool.items():
            try:
                ob = ex.fetch_order_book(symbol, limit=cfg["ORDER_BOOK_DEPTH"])
                if ob and ob.get("bids") and ob.get("asks"):
                    self._ob[key] = ob; self._ob_ts[key] = now
                    logger.info(f"📖 OB: {name.upper()} ({len(ob['bids'])} bid levels)")
                    return ob
            except Exception:
                continue
        logger.warning("⚠ OB: all exchanges failed")
        return None

    def analyze_ob(self, symbol, price):
        ob = self.fetch_ob(symbol)
        if not ob: return self._empty_ob()
        bids = np.array(ob["bids"][:cfg["ORDER_BOOK_DEPTH"]], dtype=float)
        asks = np.array(ob["asks"][:cfg["ORDER_BOOK_DEPTH"]], dtype=float)
        if bids.size == 0 or asks.size == 0: return self._empty_ob()
        bid_px, bid_sz = bids[:, 0], bids[:, 1]
        ask_px, ask_sz = asks[:, 0], asks[:, 1]
        bid_usdt = float(np.sum(bid_px * bid_sz))
        ask_usdt = float(np.sum(ask_px * ask_sz))
        imbal = bid_usdt / max(bid_usdt + ask_usdt, 1e-10)
        avg_b = float(np.mean(bid_sz))
        avg_a = float(np.mean(ask_sz))
        b_walls = [(float(bid_px[i]), float(bid_sz[i])) for i in range(len(bid_sz)) if bid_sz[i] >= avg_b * cfg["WALL_MULT"]]
        a_walls = [(float(ask_px[i]), float(ask_sz[i])) for i in range(len(ask_sz)) if ask_sz[i] >= avg_a * cfg["WALL_MULT"]]
        bwd = ((price - b_walls[0][0]) / price * 100) if b_walls else None
        awd = ((a_walls[0][0] - price) / price * 100) if a_walls else None
        if imbal >= 0.65: sig = "BULL"; note = f"Heavy bid ({imbal:.1%})"
        elif imbal <= 0.35: sig = "BEAR"; note = f"Heavy ask ({1-imbal:.1%})"
        elif imbal >= 0.55: sig = "MILD_BULL"; note = f"Mild bid ({imbal:.1%})"
        elif imbal <= 0.45: sig = "MILD_BEAR"; note = f"Mild ask ({1-imbal:.1%})"
        else: sig = "NEUTRAL"; note = f"Balanced ({imbal:.1%})"
        return {
            "imbalance": round(imbal, 4), "bid_usdt": round(bid_usdt, 2),
            "ask_usdt": round(ask_usdt, 2),
            "bid_walls": b_walls, "ask_walls": a_walls,
            "bid_wall_dist_pct": round(bwd, 3) if bwd is not None else None,
            "ask_wall_dist_pct": round(awd, 3) if awd is not None else None,
            "ob_signal": sig, "ob_note": note, "available": True,
        }

    def detect_whales(self, df):
        if len(df) < 20: return self._empty_whale()
        ma20 = df["volume"].rolling(20).mean().bfill()
        candles = []
        for i in range(max(0, len(df) - 50), len(df)):
            vm = ma20.iloc[i]
            if vm == 0 or pd.isna(vm): continue
            vr = df["volume"].iloc[i] / vm
            op = max(float(df["open"].iloc[i]), 1e-10)
            pmov = abs(float(df["close"].iloc[i]) - op) / op
            if vr >= cfg["WHALE_VOL_THRESHOLD"] and pmov >= cfg["WHALE_PRICE_MOVE_MIN"]:
                bull = float(df["close"].iloc[i]) >= op
                candles.append({
                    "idx": i, "timestamp": df["timestamp"].iloc[i],
                    "price": float(df["close"].iloc[i]),
                    "vol_ratio": round(vr, 2),
                    "price_move": round(pmov * 100, 3),
                    "direction": "BUY" if bull else "SELL",
                    "type": "ACCUMULATION" if bull else "DISTRIBUTION",
                })
        rec = df.tail(30)
        bull_vol = float(rec.loc[rec["close"] >= rec["open"], "volume"].sum())
        bear_vol = float(rec.loc[rec["close"] < rec["open"], "volume"].sum())
        cvd_r = bull_vol / max(bull_vol + bear_vol, 1e-10)
        cvd_t = "BULL" if cvd_r >= 0.60 else "BEAR" if cvd_r <= 0.40 else "NEUTRAL"
        return {
            "whale_candles": candles,
            "recent_whale": candles[-1] if candles else None,
            "cvd_ratio": round(cvd_r, 4),
            "cvd_trend": cvd_t,
            "bull_vol": round(bull_vol, 2),
            "bear_vol": round(bear_vol, 2),
            "total_detected": len(candles),
        }

    def score(self, ob, wc, signal):
        pts = 0.0; notes = []
        is_bull = "BUY" in signal
        if ob.get("available"):
            s = ob["ob_signal"]
            if is_bull and s == "BULL": pts += 4; notes.append(f"OB BULL aligned – {ob['ob_note']}")
            elif not is_bull and s == "BEAR": pts += 4; notes.append(f"OB BEAR aligned – {ob['ob_note']}")
            elif is_bull and s == "MILD_BULL": pts += 2; notes.append(f"OB mild BULL – {ob['ob_note']}")
            elif not is_bull and s == "MILD_BEAR": pts += 2; notes.append(f"OB mild BEAR – {ob['ob_note']}")
            elif s == "NEUTRAL": pts += 1; notes.append(f"OB neutral – {ob['ob_note']}")
            else: notes.append(f"OB against – {ob['ob_note']}")
            if is_bull and ob["bid_walls"]: pts += 1; notes.append(f"Bid whale wall ({len(ob['bid_walls'])} lvl)")
            elif not is_bull and ob["ask_walls"]: pts += 1; notes.append(f"Ask whale wall ({len(ob['ask_walls'])} lvl)")
        else:
            notes.append("OB unavailable – skipped")
        cvd = wc.get("cvd_trend", "NEUTRAL")
        cvd_r = wc.get("cvd_ratio", 0.5)
        if is_bull and cvd == "BULL": pts += 3; notes.append(f"CVD bull ({cvd_r:.1%})")
        elif not is_bull and cvd == "BEAR": pts += 3; notes.append(f"CVD bear ({cvd_r:.1%})")
        elif cvd == "NEUTRAL": pts += 1; notes.append(f"CVD neutral ({cvd_r:.1%})")
        else: notes.append(f"CVD opposing ({cvd_r:.1%})")
        rw = wc.get("recent_whale")
        if rw:
            match = (is_bull and rw["direction"] == "BUY") or (not is_bull and rw["direction"] == "SELL")
            if match:
                pts += 2
                notes.append(f"Whale {rw['type']:<14} {rw['vol_ratio']}× vol {rw['price_move']}% move")
            else:
                notes.append(f"Whale opposing {rw['type']} {rw['vol_ratio']}×")
        else:
            notes.append("No whale candle in last 50 bars")
        final = round(min(10.0, pts), 1)
        label = ("🐋 CONFIRMED" if final >= 7.5 else
                 "🐟 PARTIAL" if final >= 5.0 else
                 "🔍 NEUTRAL" if final >= 3.0 else "🚨 OPPOSING")
        return final, label, notes

    @staticmethod
    def _empty_ob():
        return {"imbalance": 0.5, "bid_usdt": 0, "ask_usdt": 0,
                "bid_walls": [], "ask_walls": [],
                "bid_wall_dist_pct": None, "ask_wall_dist_pct": None,
                "ob_signal": "NEUTRAL", "ob_note": "OB unavailable", "available": False}

    @staticmethod
    def _empty_whale():
        return {"whale_candles": [], "recent_whale": None,
                "cvd_ratio": 0.5, "cvd_trend": "NEUTRAL",
                "bull_vol": 0.0, "bear_vol": 0.0, "total_detected": 0}

# ── Technical Indicators ────────────────────────────────────────────────
def _supertrend(df, period=10, mult=3.0):
    atr = ta.volatility.AverageTrueRange(df["high"], df["low"], df["close"], window=period, fillna=True).average_true_range()
    hl2 = (df["high"] + df["low"]) / 2
    upper = (hl2 + mult * atr).values
    lower = (hl2 - mult * atr).values
    close = df["close"].values
    n = len(close)
    fu, fl, st, di = upper.copy(), lower.copy(), np.zeros(n), np.ones(n)
    for i in range(1, n):
        fu[i] = upper[i] if upper[i] < fu[i-1] or close[i-1] > fu[i-1] else fu[i-1]
        fl[i] = lower[i] if lower[i] > fl[i-1] or close[i-1] < fl[i-1] else fl[i-1]
        st[i] = fu[i] if (st[i-1]==fu[i-1] and close[i]<=fu[i]) else \
                (fl[i] if (st[i-1]==fu[i-1] and close[i]>fu[i]) else
                (fl[i] if close[i]>=fl[i] else fu[i]))
        di[i] = -1 if st[i] == fu[i] else 1
    df["Supertrend"] = st
    df["ST_Direction"] = di
    return df

def compute_indicators(df):
    df = df.copy()
    logger.info("📊 Computing indicators")
    df["EMA_9"]   = df["close"].ewm(span=9, adjust=False).mean()
    df["SMA_20"]  = df["close"].rolling(20).mean()
    df["EMA_50"]  = df["close"].ewm(span=50, adjust=False).mean()
    df["EMA_200"] = df["close"].ewm(span=200, adjust=False).mean()
    typical = (df["high"] + df["low"] + df["close"]) / 3
    df["VWAP"] = (typical * df["volume"]).cumsum() / df["volume"].cumsum().replace(0, np.nan)
    df["RSI_14"] = ta.momentum.RSIIndicator(df["close"], window=14, fillna=True).rsi()
    macd = ta.trend.MACD(df["close"], window_slow=26, window_fast=12, fillna=True)
    df["MACD"] = macd.macd()
    df["MACD_Signal"] = macd.macd_signal()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]
    df["ATR"] = ta.volatility.AverageTrueRange(df["high"], df["low"], df["close"], window=14, fillna=True).average_true_range()
    atr_arr = df["ATR"].values
    wp = min(100, len(atr_arr))
    ap = np.full(len(atr_arr), 50.0)
    for i in range(wp, len(atr_arr)):
        ap[i] = np.sum(atr_arr[i-wp:i] < atr_arr[i]) / wp * 100
    df["ATR_Percentile"] = ap
    df["OBV"] = ta.volume.OnBalanceVolumeIndicator(df["close"], df["volume"], fillna=True).on_balance_volume()
    bb = ta.volatility.BollingerBands(df["close"], window=20, window_dev=2, fillna=True)
    df["BB_Upper"] = bb.bollinger_hband()
    df["BB_Lower"] = bb.bollinger_lband()
    df["BB_Mid"] = bb.bollinger_mavg()
    df["BB_Width"] = ((df["BB_Upper"] - df["BB_Lower"]) / df["BB_Mid"]).fillna(0)
    adx_i = ta.trend.ADXIndicator(df["high"], df["low"], df["close"], window=14, fillna=True)
    df["ADX"] = adx_i.adx()
    df["ADX_Pos"] = adx_i.adx_pos()
    df["ADX_Neg"] = adx_i.adx_neg()
    stoch = ta.momentum.StochasticOscillator(df["high"], df["low"], df["close"], window=14, smooth_window=3, fillna=True)
    df["Stoch_K"] = stoch.stoch()
    df["Stoch_D"] = stoch.stoch_signal()
    atr_vol = (df["ATR"] / df["close"].rolling(20).mean()).fillna(0).clip(0, 1)
    df["Dynamic_RSI_Lower"] = 30 + atr_vol * 10
    df["Dynamic_RSI_Upper"] = 70 - atr_vol * 10
    df["Williams_R"] = ta.momentum.WilliamsRIndicator(df["high"], df["low"], df["close"], lbp=14, fillna=True).williams_r()
    df["CCI"] = ta.trend.CCIIndicator(df["high"], df["low"], df["close"], window=20, fillna=True).cci()
    df["Volume_MA20"] = df["volume"].rolling(20).mean().bfill()
    vol_arr = df["volume"].values
    roll100 = min(100, len(vol_arr))
    vp_arr = np.full(len(vol_arr), 50.0)
    for i in range(roll100, len(vol_arr)):
        vp_arr[i] = np.sum(vol_arr[i-roll100:i] < vol_arr[i]) / roll100 * 100
    df["Volume_Percentile"] = vp_arr
    df["Volume_Ratio"] = (df["volume"] / df["Volume_MA20"].replace(0, np.nan)).fillna(1.0).clip(0, 10)
    df["Volume_Delta"] = np.where(df["close"] >= df["open"], df["volume"], -df["volume"])
    df["CVD_20"] = df["Volume_Delta"].rolling(20).sum()
    df = _supertrend(df)
    df = df.dropna(subset=["EMA_200", "ADX", "ATR"]).reset_index(drop=True)
    return df

# ── Structure Analyzer ──────────────────────────────────────────────────
def analyze_structure(df, lookback=75):
    if len(df) < lookback + 7:
        return _empty_structure("UNKNOWN", 0, "Insufficient data")
    rec = df.tail(lookback).reset_index(drop=True)
    hi, lo = rec["high"].values, rec["low"].values
    cl = rec["close"].values
    s_highs, s_lows = [], []
    for i in range(3, len(rec) - 3):
        lh, rh = hi[i-3:i], hi[i+1:i+4]
        ll, rl = lo[i-3:i], lo[i+1:i+4]
        if len(lh) < 3 or len(rh) < 3: continue
        if hi[i] >= max(lh) and hi[i] >= max(rh):
            local_lo = lo[max(0, i-5):i]
            if len(local_lo) > 0:
                base = max(float(min(local_lo)), 1e-10)
                if (hi[i] - base) / base >= cfg["STRUCTURE_MIN_SWING"]:
                    s_highs.append((i, float(hi[i])))
        if lo[i] <= min(ll) and lo[i] <= min(rl):
            local_hi = hi[max(0, i-5):i]
            if len(local_hi) > 0:
                base = max(float(lo[i]), 1e-10)
                if (max(local_hi) - lo[i]) / base >= cfg["STRUCTURE_MIN_SWING"]:
                    s_lows.append((i, float(lo[i])))
    notes = [f"{len(s_highs)} swing highs | {len(s_lows)} swing lows (lookback {lookback})"]
    if len(s_highs) < 2 or len(s_lows) < 2:
        return _empty_structure("RANGING", 35, "Insufficient swings – ranging/choppy market", s_highs, s_lows)
    last_h = s_highs[-3:] if len(s_highs) >= 3 else s_highs
    last_l = s_lows[-3:] if len(s_lows) >= 3 else s_lows
    hh = all(last_h[i][1] > last_h[i-1][1] for i in range(1, len(last_h)))
    hl = all(last_l[i][1] > last_l[i-1][1] for i in range(1, len(last_l)))
    lh = all(last_h[i][1] < last_h[i-1][1] for i in range(1, len(last_h)))
    ll = all(last_l[i][1] < last_l[i-1][1] for i in range(1, len(last_l)))
    last_close = float(cl[-1])
    prev_high = s_highs[-2][1] if len(s_highs) >= 2 else float(hi[-1])
    prev_low = s_lows[-2][1] if len(s_lows) >= 2 else float(lo[-1])
    breakout = last_close > prev_high * 1.003
    breakdown = last_close < prev_low * 0.997
    if hh and hl:
        stype = "UPTREND"; conf = 90 if breakout else 78; notes.append("HH + HL confirmed")
    elif lh and ll:
        stype = "DOWNTREND"; conf = 90 if breakdown else 78; notes.append("LH + LL confirmed")
    elif breakout:
        stype = "BREAKOUT"; conf = 72; notes.append(f"Breakout above {prev_high:.5f}")
    elif breakdown:
        stype = "BREAKDOWN"; conf = 72; notes.append(f"Breakdown below {prev_low:.5f}")
    else:
        stype = "RANGING"; conf = 45; notes.append("Mixed / ranging structure")
    return {
        "type": stype, "confidence": conf,
        "swing_highs": s_highs, "swing_lows": s_lows,
        "last_high": s_highs[-1][1] if s_highs else None,
        "last_low": s_lows[-1][1] if s_lows else None,
        "prev_high": prev_high, "prev_low": prev_low,
        "breakout": breakout, "breakdown": breakdown,
        "hh": hh, "hl": hl, "lh": lh, "ll": ll,
        "notes": notes,
    }

def _empty_structure(stype, conf, note, sh=None, sl=None):
    return {
        "type": stype, "confidence": conf,
        "swing_highs": sh or [], "swing_lows": sl or [],
        "last_high": None, "last_low": None,
        "prev_high": None, "prev_low": None,
        "breakout": False, "breakdown": False,
        "hh": False, "hl": False, "lh": False, "ll": False,
        "notes": [note],
    }

def structure_gate(structure, signal):
    stype = structure.get("type", "RANGING")
    conf = structure.get("confidence", 0)
    is_bull = "BUY" in signal
    if signal == "HOLD": return True, "HOLD – no gate applied"
    rules = {
        "UPTREND": (True if is_bull else False, "UPTREND"),
        "DOWNTREND": (True if not is_bull else False, "DOWNTREND"),
        "BREAKOUT": (True if is_bull else False, "BREAKOUT"),
        "BREAKDOWN": (True if not is_bull else False, "BREAKDOWN"),
    }
    if stype in rules:
        allowed, label = rules[stype]
        if allowed:
            return True, f"✓ Structure {label} supports signal (conf:{conf}%)"
        else:
            side = "BUY" if is_bull else "SELL"
            return False, f"✗ BLOCKED – {label} structure forbids {side} (conf:{conf}%)"
    return True, f"⚠ RANGING structure – signal allowed with caution (conf:{conf}%)"

# ── Pattern & Divergence ────────────────────────────────────────────────
def detect_patterns(df):
    if len(df) < 5: return {}
    o, h, l, c = (df["open"].values, df["high"].values,
                  df["low"].values, df["close"].values)
    def body(i): return abs(c[i] - o[i])
    def rng(i): return max(h[i] - l[i], 1e-10)
    def is_bull(i): return c[i] > o[i]
    def is_bear(i): return c[i] < o[i]
    def uw(i): return h[i] - max(c[i], o[i])
    def lw(i): return min(c[i], o[i]) - l[i]
    avg = np.mean([body(x) for x in range(-min(10, len(df)), 0)]) or 1e-10
    i, j, k = -1, -2, -3
    pats = {
        "bullish_engulfing": bool(is_bear(j) and is_bull(i) and c[i]>o[j] and o[i]<c[j] and body(i)>body(j)*1.1),
        "bearish_engulfing": bool(is_bull(j) and is_bear(i) and c[i]<o[j] and o[i]>c[j] and body(i)>body(j)*1.1),
        "hammer": bool(lw(i)>=body(i)*2 and uw(i)<=body(i)*0.3 and body(i)>0 and rng(i)>avg*0.5),
        "shooting_star": bool(uw(i)>=body(i)*2 and lw(i)<=body(i)*0.3 and body(i)>0 and rng(i)>avg*0.5),
        "doji": bool(body(i)<=rng(i)*0.1 and rng(i)>avg*0.3),
        "morning_star": len(df)>=5 and bool(is_bear(k) and body(k)>avg*0.8 and body(j)<avg*0.3 and is_bull(i) and c[i]>(o[k]+c[k])/2),
        "evening_star": len(df)>=5 and bool(is_bull(k) and body(k)>avg*0.8 and body(j)<avg*0.3 and is_bear(i) and c[i]<(o[k]+c[k])/2),
    }
    return pats

def detect_divergences(df, lookback=30):
    if len(df) < lookback: return False, False, ["Insufficient data"]
    rec = df.tail(lookback).reset_index(drop=True)
    price, rsi, obv = rec["close"].values, rec["RSI_14"].values, rec["OBV"].values
    sw = max(3, lookback // 5)
    notes = []
    def swings(arr, w):
        hi, lo = [], []
        for i in range(w, len(arr) - w):
            s = arr[i-w:i+w+1]
            if arr[i] >= np.max(s) - 1e-10: hi.append(i)
            if arr[i] <= np.min(s) + 1e-10: lo.append(i)
        return hi, lo
    ph, pl = swings(price, sw)
    bull_div = bear_div = False
    if len(pl) >= 2:
        p1, p2 = pl[-2], pl[-1]
        if price[p2] < price[p1] * 0.999 and rsi[p2] > rsi[p1] + 1.5:
            bull_div = True; notes.append("Bullish RSI divergence (price ↓ RSI ↑)")
    if len(ph) >= 2:
        p1, p2 = ph[-2], ph[-1]
        if price[p2] > price[p1] * 1.001 and rsi[p2] < rsi[p1] - 1.5:
            bear_div = True; notes.append("Bearish RSI divergence (price ↑ RSI ↓)")
    half = lookback // 2
    pt = price[-1] - price[-half] if half < len(price) else 0
    ot = obv[-1] - obv[-half] if half < len(obv) else 0
    if pt < -price[-1]*0.005 and ot > 0:
        bull_div = True; notes.append("Bullish OBV divergence (price ↓ OBV ↑)")
    elif pt > price[-1]*0.005 and ot < 0:
        bear_div = True; notes.append("Bearish OBV divergence (price ↑ OBV ↓)")
    return bull_div, bear_div, notes

# ── HTF Bias, Regime, Market Power, Strength, Signals, TP/SL, etc. ─────
def get_htf_bias(df4):
    if df4 is None or df4.empty or len(df4) < 10:
        return "NEUTRAL", "4H unavailable"
    last = df4.iloc[-1]
    price = float(last["close"])
    checks = [
        price > float(last["EMA_9"]),
        price > float(last["EMA_50"]),
        price > float(last["EMA_200"]),
        float(last["MACD"]) > float(last["MACD_Signal"]),
        float(last["RSI_14"]) > 55,
        int(last["ST_Direction"]) == 1,
        float(last["ADX_Pos"]) > float(last["ADX_Neg"]),
    ]
    bull = sum(checks)
    bear = len(checks) - bull
    tot = len(checks)
    if bull >= int(tot * 0.7): return "BULL", f"4H Bullish ({bull}/{tot}) ADX={last['ADX']:.1f}"
    elif bear >= int(tot * 0.7): return "BEAR", f"4H Bearish ({bear}/{tot}) ADX={last['ADX']:.1f}"
    else: return "NEUTRAL", f"4H Neutral B={bull} Br={bear} ADX={last['ADX']:.1f}"

def classify_regime(df):
    last = df.iloc[-1]
    adx, bbw, atp = float(last["ADX"]), float(last["BB_Width"]), float(last["ATR_Percentile"])
    price, e9, e50, e200 = float(last["close"]), float(last["EMA_9"]), float(last["EMA_50"]), float(last["EMA_200"])
    adxp, adxn = float(last["ADX_Pos"]), float(last["ADX_Neg"])
    pb = price > e9 > e50 > e200
    nb = price < e9 < e50 < e200
    ub = price > e9 > e50
    db = price < e9 < e50
    q80 = float(df["BB_Width"].quantile(0.80))
    q40 = float(df["BB_Width"].quantile(0.40))
    if atp > 85 and bbw > q80: return "VOLATILE", "⚡ Very high volatility"
    if adx >= 35 and adxp > adxn and pb: return "STRONG_BULL", "🚀 Very strong uptrend"
    if adx >= 35 and adxn > adxp and nb: return "STRONG_BEAR", "💀 Very strong downtrend"
    if adx > 22 and adxp > adxn and ub: return "TRENDING_UP", "📈 Uptrend"
    if adx > 22 and adxn > adxp and db: return "TRENDING_DOWN", "📉 Downtrend"
    if adx < 20 and bbw < q40: return "RANGING", "↔ Sideways"
    return "NORMAL", "🔄 Normal"

def find_sr(df, signal, lookback=100, gap_pct=0.005):
    rec = df.tail(lookback)
    h, l = rec["high"].values, rec["low"].values
    price = float(df["close"].iloc[-1])
    gap = price * gap_pct
    res = [h[i] for i in range(2, len(h)-2) if h[i] == max(h[i-2:i+3])]
    sup = [l[i] for i in range(2, len(l)-2) if l[i] == min(l[i-2:i+3])]
    vr = [r for r in res if r > price + gap]
    vs = [s for s in sup if s < price - gap]
    return (float(max(vs)) if vs else price * 0.92,
            float(min(vr)) if vr else price * 1.08)

def market_power(df, htf_bias="NEUTRAL", strength_score=50, signal="HOLD"):
    last = df.iloc[-1]
    score, max_s, log = 0.0, 0.0, []
    is_bull = "BUY" in signal
    def _add(pts, mx, label):
        nonlocal score, max_s
        score += pts; max_s += mx
        log.append((pts, mx, label))
    adx = float(last["ADX"])
    pts = 25 if adx>=50 else 22 if adx>=40 else 18 if adx>=30 else 12 if adx>=22 else 5 if adx>=15 else 0
    _add(pts, 25, f"ADX {adx:.1f}")
    p, e9, e50, e200 = (float(last["close"]), float(last["EMA_9"]),
                        float(last["EMA_50"]), float(last["EMA_200"]))
    if is_bull: pts = 20 if p>e9>e50>e200 else 14 if p>e9>e50 else 7 if p>e9 else 0
    else: pts = 20 if p<e9<e50<e200 else 14 if p<e9<e50 else 7 if p<e9 else 0
    _add(pts, 20, "EMA alignment")
    if (htf_bias=="BULL" and is_bull) or (htf_bias=="BEAR" and not is_bull): pts=15
    elif htf_bias=="NEUTRAL": pts=6
    else: pts=0
    _add(pts, 15, f"4H bias {htf_bias}")
    st_ok = (float(last["ST_Direction"])==1 and is_bull) or (float(last["ST_Direction"])==-1 and not is_bull)
    _add(10 if st_ok else 0, 10, "Supertrend")
    mh = float(last["MACD_Hist"])
    sl_mh = mh - (float(df["MACD_Hist"].iloc[-2]) if len(df)>=2 else 0)
    mb = float(last["MACD"]) > float(last["MACD_Signal"])
    if (is_bull and mb and sl_mh>0) or (not is_bull and not mb and sl_mh<0): pts=10
    elif (is_bull and mb) or (not is_bull and not mb): pts=6
    else: pts=0
    _add(pts, 10, "MACD")
    vp = float(last["Volume_Percentile"]) if "Volume_Percentile" in last.index else 50.0
    pts = 10 if vp>=90 else 8 if vp>=75 else 5 if vp>=55 else 2 if vp>=30 else 0
    _add(pts, 10, f"Vol pct {vp:.0f}th")
    rsi = float(last["RSI_14"])
    r_lo = float(last["Dynamic_RSI_Lower"])
    r_hi = float(last["Dynamic_RSI_Upper"])
    if is_bull and r_lo<=rsi<=r_lo+10: pts=5
    elif not is_bull and r_hi-10<=rsi<=r_hi: pts=5
    elif 45<=rsi<=55: pts=1
    else: pts=2
    _add(pts, 5, f"RSI {rsi:.1f}")
    _add(min(5, round(strength_score/20)), 5, "Strength carry")
    final = round(min(100.0, (score / max(max_s, 0.01)) * 100), 1)
    if final>=86: label, tier = "🚀 SUPREME", 6
    elif final>=71: label, tier = "🔥 V.STRONG", 5
    elif final>=56: label, tier = "💪 STRONG", 4
    elif final>=41: label, tier = "🟡 MODERATE", 3
    elif final>=26: label, tier = "⚠ WEAK", 2
    else: label, tier = "🚨 RISKY", 1
    return final, label, tier

def compute_strength(df, predicted_price=None, patterns=None, bull_div=False, bear_div=False,
                     htf_bias="NEUTRAL", whale_score=5.0, structure=None):
    if patterns is None: patterns = {}
    last = df.iloc[-1]; price = float(last["close"])
    comps = {}; notes = []
    def _c(name, pts, mx, note):
        comps[name] = (pts, mx); notes.append(note)
    e9, e50, e200 = float(last["EMA_9"]), float(last["EMA_50"]), float(last["EMA_200"])
    if price>e9>e50>e200: _c("EMA", 2.5, 2.5, "EMA perfect bull +2.5")
    elif price>e9>e50: _c("EMA", 1.8, 2.5, "EMA partial bull +1.8")
    elif price>e9: _c("EMA", 0.8, 2.5, "EMA above EMA9 +0.8")
    elif price<e9<e50<e200: _c("EMA", 2.5, 2.5, "EMA perfect bear +2.5")
    elif price<e9<e50: _c("EMA", 1.8, 2.5, "EMA partial bear +1.8")
    else: _c("EMA", 0.8, 2.5, "EMA below EMA9 +0.8")
    adx = float(last["ADX"])
    if adx>=40: _c("ADX", 2.0, 2.0, f"ADX monster {adx:.1f} +2.0")
    elif adx>=30: _c("ADX", 1.5, 2.0, f"ADX v.strong {adx:.1f} +1.5")
    elif adx>=25: _c("ADX", 1.0, 2.0, f"ADX strong {adx:.1f} +1.0")
    elif adx>=18: _c("ADX", 0.4, 2.0, f"ADX weak {adx:.1f} +0.4")
    else: _c("ADX", 0.0, 2.0, f"ADX no-trend {adx:.1f} +0")
    vp = float(last["Volume_Percentile"]) if "Volume_Percentile" in last.index else 50.0
    if vp>=90: _c("Volume", 2.0, 2.0, f"Vol extreme pct={vp:.0f} +2.0")
    elif vp>=75: _c("Volume", 1.5, 2.0, f"Vol strong pct={vp:.0f} +1.5")
    elif vp>=55: _c("Volume", 1.0, 2.0, f"Vol above avg pct={vp:.0f} +1.0")
    elif vp>=30: _c("Volume", 0.4, 2.0, f"Vol normal pct={vp:.0f} +0.4")
    else: _c("Volume", 0.0, 2.0, f"Vol low pct={vp:.0f} +0")
    rsi = float(last["RSI_14"]); r_lo = float(last["Dynamic_RSI_Lower"]); r_hi = float(last["Dynamic_RSI_Upper"])
    mid_lo, mid_hi = r_lo + (r_hi - r_lo) * 0.25, r_hi - (r_hi - r_lo) * 0.25
    if r_lo<=rsi<=mid_lo: _c("RSI", 1.5, 1.5, f"RSI buy zone {rsi:.1f} +1.5")
    elif mid_hi<=rsi<=r_hi: _c("RSI", 1.5, 1.5, f"RSI sell zone {rsi:.1f} +1.5")
    elif rsi<r_lo or rsi>r_hi: _c("RSI", 0.3, 1.5, f"RSI extreme {rsi:.1f} +0.3")
    else: _c("RSI", 0.7, 1.5, f"RSI neutral {rsi:.1f} +0.7")
    mh = float(last["MACD_Hist"]); sl_mh = mh - (float(df["MACD_Hist"].iloc[-2]) if len(df)>=3 else 0)
    if (mh>0 and sl_mh>0) or (mh<0 and sl_mh<0): _c("MACD", 1.0, 1.0, "MACD accelerating +1.0")
    elif mh!=0: _c("MACD", 0.4, 1.0, "MACD weak +0.4")
    else: _c("MACD", 0.0, 1.0, "MACD flat +0")
    sk, sd = float(last["Stoch_K"]), float(last["Stoch_D"])
    if sk<25 and sk>sd: _c("Stoch", 1.0, 1.0, f"Stoch bull cross {sk:.1f} +1.0")
    elif sk>75 and sk<sd: _c("Stoch", 1.0, 1.0, f"Stoch bear cross {sk:.1f} +1.0")
    elif 40<=sk<=60: _c("Stoch", 0.3, 1.0, f"Stoch mid {sk:.1f} +0.3")
    else: _c("Stoch", 0.5, 1.0, f"Stoch trending {sk:.1f} +0.5")
    adx_bull = float(last["ADX_Pos"]) > float(last["ADX_Neg"])
    st_ok = (float(last["ST_Direction"])==1 and adx_bull) or (float(last["ST_Direction"])==-1 and not adx_bull)
    _c("Supertrend", 1.0 if st_ok else 0.0, 1.0, "Supertrend aligned +1.0" if st_ok else "Supertrend opposing +0")
    lstm_confirms = False
    if predicted_price is not None:
        pct = (predicted_price - price) / price * 100
        if adx_bull and pct > 0.3:
            _c("LSTM", 1.5, 1.5, f"LSTM confirms BUY {pct:+.2f}% +1.5"); lstm_confirms = True
        elif not adx_bull and pct < -0.3:
            _c("LSTM", 1.5, 1.5, f"LSTM confirms SELL {pct:+.2f}% +1.5"); lstm_confirms = True
        else:
            _c("LSTM", 0.0, 1.5, f"LSTM no confirm {pct:+.2f}% +0")
    bull_pats = ["bullish_engulfing","hammer","morning_star"]
    bear_pats = ["bearish_engulfing","shooting_star","evening_star"]
    found_pat = next((p for p in bull_pats+bear_pats if patterns.get(p)), None)
    _c("Pattern", 1.0 if found_pat else 0.0, 1.0, f"Candle: {found_pat} +1.0" if found_pat else "Candle: none +0")
    if bull_div: _c("Diverge", 1.0, 1.0, "Divergence: bullish +1.0")
    elif bear_div: _c("Diverge", 1.0, 1.0, "Divergence: bearish +1.0")
    else: _c("Diverge", 0.0, 1.0, "Divergence: none +0")
    if (htf_bias=="BULL" and adx_bull) or (htf_bias=="BEAR" and not adx_bull): _c("4H", 1.0, 1.0, "4H bias aligned +1.0")
    elif htf_bias=="NEUTRAL": _c("4H", 0.3, 1.0, "4H bias neutral +0.3")
    else: _c("4H", 0.0, 1.0, "4H bias against +0")
    if whale_score>=7.5: _c("Whale", 1.0, 1.0, f"Whale confirmed {whale_score:.1f}/10 +1.0")
    elif whale_score>=5.0: _c("Whale", 0.6, 1.0, f"Whale partial {whale_score:.1f}/10 +0.6")
    elif whale_score>=3.0: _c("Whale", 0.3, 1.0, f"Whale neutral {whale_score:.1f}/10 +0.3")
    else: _c("Whale", 0.0, 1.0, f"Whale opposing {whale_score:.1f}/10 +0")
    if structure:
        stype = structure.get("type", "RANGING"); sconf = structure.get("confidence", 0)
        if (stype=="UPTREND" and adx_bull) or (stype=="DOWNTREND" and not adx_bull):
            pts = min(1.0, sconf / 100)
            _c("Structure", pts, 1.0, f"Structure aligned {stype} conf:{sconf}% +{pts:.2f}")
        elif stype in ("BREAKOUT","BREAKDOWN"): _c("Structure", 0.5, 1.0, f"Structure breakout {stype} +0.5")
        else: _c("Structure", 0.0, 1.0, f"Structure ranging {stype} +0")
    earned = sum(v[0] for v in comps.values())
    total = sum(v[1] for v in comps.values())
    final = round(min(100.0, (earned / max(total, 0.1)) * 100), 1)
    lbl = ("🔥 MONSTER" if final>=80 else "💪 STRONG" if final>=65 else "🟡 MODERATE" if final>=45 else "😐 WEAK")
    return final, lbl, notes, lstm_confirms

def generate_signal(df, price_chg_pct, predicted_price=None, htf_bias="NEUTRAL",
                    patterns=None, bull_div=False, bear_div=False,
                    whale_score=5.0, whale_label="", structure=None):
    if patterns is None: patterns = {}
    if price_chg_pct < -3.5: return "HOLD", [], 0.0, "Hard guard: price drop >3.5%"
    regime, _ = classify_regime(df)
    if regime == "VOLATILE": return "HOLD", [], 0.0, "Regime: VOLATILE – skip entry"
    if regime == "RANGING" and abs(price_chg_pct) < 0.8: return "HOLD", [], 0.0, "Regime: RANGING – no momentum"
    last = df.iloc[-1]
    adx, adxp, adxn = float(last["ADX"]), float(last["ADX_Pos"]), float(last["ADX_Neg"])
    rsi, r_lo, r_hi = float(last["RSI_14"]), float(last["Dynamic_RSI_Lower"]), float(last["Dynamic_RSI_Upper"])
    sk, sd = float(last["Stoch_K"]), float(last["Stoch_D"])
    close = float(last["close"])
    vp = float(last["Volume_Percentile"]) if "Volume_Percentile" in last.index else 50.0
    vwap = float(last["VWAP"]) if "VWAP" in last.index else close
    cvd20 = float(df["CVD_20"].iloc[-1]) if "CVD_20" in df.columns else 0.0
    macd_b = float(last["MACD"]) > float(last["MACD_Signal"])
    st_bull = int(last["ST_Direction"]) == 1

    def side_score(weights):
        t, a = 0.0, []
        for name, (cond, w) in weights.items():
            if cond: t += w; a.append(name)
        return t, a

    buy_w = {
        "macd_cross": (macd_b, 2.0),
        "ema_align": (close > float(last["EMA_9"]) > float(last["EMA_50"]), 2.0),
        "adx_bull": (adx > 22 and adxp > adxn, 1.5),
        "rsi_zone": (rsi < r_lo, 1.0),
        "stoch_bull": (sk < 30 and sk > sd, 1.0),
        "vol_spike": (vp >= 55, 1.0),
        "supertrend": (st_bull, 1.0),
        "vwap_above": (close > vwap, 0.5),
        "lstm_bull": (predicted_price is not None and predicted_price > close*1.003, 1.5),
        "bull_pat": (any(patterns.get(p, False) for p in ["bullish_engulfing","hammer","morning_star"]), 1.0),
        "bull_div": (bull_div, 1.0),
        "htf_bull": (htf_bias == "BULL", 1.0),
        "cvd_bull": (cvd20 > 0, 0.5),
    }
    sell_w = {
        "macd_cross": (not macd_b, 2.0),
        "ema_align": (close < float(last["EMA_9"]) < float(last["EMA_50"]), 2.0),
        "adx_bear": (adx > 22 and adxn > adxp, 1.5),
        "rsi_zone": (rsi > r_hi, 1.0),
        "stoch_bear": (sk > 70 and sk < sd, 1.0),
        "vol_spike": (vp >= 55, 1.0),
        "supertrend": (not st_bull, 1.0),
        "vwap_below": (close < vwap, 0.5),
        "lstm_bear": (predicted_price is not None and predicted_price < close*0.997, 1.5),
        "bear_pat": (any(patterns.get(p, False) for p in ["bearish_engulfing","shooting_star","evening_star"]), 1.0),
        "bear_div": (bear_div, 1.0),
        "htf_bear": (htf_bias == "BEAR", 1.0),
        "cvd_bear": (cvd20 < 0, 0.5),
    }
    buy_s, buy_a = side_score(buy_w)
    sell_s, sell_a = side_score(sell_w)

    if htf_bias == "BEAR" and buy_s > sell_s:
        buy_s *= 0.75
        logger.warning(f"⚠ 4H BEAR penalty on BUY → {buy_s:.1f}")
    elif htf_bias == "BULL" and sell_s > buy_s:
        sell_s *= 0.75
        logger.warning(f"⚠ 4H BULL penalty on SELL → {sell_s:.1f}")

    if buy_s > sell_s:
        fs = buy_s; active = buy_a
        raw = "STRONG BUY" if fs >= 7.5 else "BUY" if fs >= 5.0 else "HOLD"
    else:
        fs = sell_s; active = sell_a
        raw = "STRONG SELL" if fs >= 7.5 else "SELL" if fs >= 5.0 else "HOLD"

    if whale_score < 2.5 and raw != "HOLD":
        logger.error(f"🚫 HARD BLOCK: whale {whale_score:.1f}/10 < 2.5 → signal killed")
        return "HOLD", [], 0.0, f"BLOCKED: whale {whale_score:.1f} opposing"

    if structure and raw != "HOLD":
        allowed, sreason = structure_gate(structure, raw)
        if not allowed:
            logger.error(f"🚫 HARD BLOCK: {sreason}")
            return "HOLD", [], 0.0, f"BLOCKED: {sreason}"
        logger.success(f"✓ Structure: {sreason}")

    final_sig = raw
    whale_note = ""
    if 2.5 <= whale_score < 3.5 and raw in ("STRONG BUY", "STRONG SELL"):
        final_sig = raw.replace("STRONG ", "")
        whale_note = f"Downgraded STRONG→{final_sig} (whale weak {whale_score:.1f})"
        logger.warning(f"⚠ {whale_note}")
    if final_sig == "HOLD":
        return "HOLD", [], max(buy_s, sell_s), f"Score too low (B:{buy_s:.1f} S:{sell_s:.1f})"
    return final_sig, active, fs, f"Score {fs:.1f} | {whale_note or 'Whale OK'}"

# ── TP/SL Engine ────────────────────────────────────────────────────────
_TP_TABLE = {
    6: {"low":(3.5,5.5,8.5,1.8,3), "normal":(3.0,5.0,7.5,2.0,3), "high":(2.5,4.0,6.0,2.5,3)},
    5: {"low":(2.8,4.5,6.5,1.6,3), "normal":(2.3,3.8,5.5,1.8,3), "high":(1.9,3.0,4.5,2.2,2)},
    4: {"low":(2.0,3.2,4.8,1.3,3), "normal":(1.7,2.8,4.2,1.5,3), "high":(1.4,2.2,0.0,1.9,2)},
    3: {"low":(1.4,2.2,3.2,1.0,2), "normal":(1.2,1.9,2.8,1.2,2), "high":(1.0,1.6,0.0,1.5,2)},
    2: {"low":(0.9,1.4,0.0,0.8,1), "normal":(0.8,1.2,0.0,0.9,1), "high":(0.7,0.0,0.0,1.0,1)},
    1: {"low":(0.7,0.0,0.0,0.7,1), "normal":(0.6,0.0,0.0,0.8,1), "high":(0.5,0.0,0.0,0.9,1)},
}
_REGIME_ADJ = {
    "STRONG_BULL": {"tp":1.30,"sl":1.00}, "STRONG_BEAR": {"tp":1.30,"sl":1.00},
    "TRENDING_UP": {"tp":1.10,"sl":1.00}, "TRENDING_DOWN": {"tp":1.10,"sl":1.00},
    "NORMAL": {"tp":1.00,"sl":1.00}, "RANGING": {"tp":0.65,"sl":0.85},
    "VOLATILE": {"tp":0.80,"sl":1.40},
}

def compute_tp_sl(price, df, signal, strength_score=50, predicted_price=None,
                  lstm_confirms=False, htf_bias="NEUTRAL"):
    if "HOLD" in signal: return (price*0.98, {"TP1": price*1.02, "TP2": None, "TP3": None}, "HOLD",
                                  {"cancel_reason":"HOLD","rr_ratio":0})
    last = df.iloc[-1]; atr = float(last["ATR"]); atp = float(last["ATR_Percentile"])
    regime, _ = classify_regime(df)
    mp, mp_lbl, mp_tier = market_power(df, htf_bias, strength_score, signal)
    vz = "low" if atp<30 else "high" if atp>70 else "normal"
    vn = (f"Low Vol ({atp:.0f}th)" if vz=="low" else f"High Vol ({atp:.0f}th)" if vz=="high" else f"Normal Vol ({atp:.0f}th)")
    tp1_m, tp2_m, tp3_m, sl_m, tp_count = _TP_TABLE[mp_tier][vz]
    radj = _REGIME_ADJ.get(regime, {"tp":1.0,"sl":1.0})
    tp1_m *= radj["tp"]; tp2_m *= radj["tp"]; tp3_m *= radj["tp"]; sl_m *= radj["sl"]
    if regime == "RANGING": tp_count = 1
    d = 1 if "BUY" in signal else -1
    tp1 = price + d * atr * tp1_m
    tp2 = (price + d * atr * tp2_m) if tp_count>=2 and tp2_m>0 else None
    tp3 = (price + d * atr * tp3_m) if tp_count>=3 and tp3_m>0 else None
    sl = price - d * atr * sl_m
    sup, res = find_sr(df, signal)
    sr_note = ""
    if "BUY" in signal:
        if tp1>res: tp1=res*0.997; sr_note+="TP1@R "
        if tp2 and tp2>res: tp2=res*0.997; sr_note+="TP2@R "
        if tp3 and tp3>res: tp3=res*0.997
        if sl<sup: sl=sup*1.003; sr_note+="SL@S"
    else:
        if tp1<sup: tp1=sup*1.003; sr_note+="TP1@S "
        if tp2 and tp2<sup: tp2=sup*1.003; sr_note+="TP2@S "
        if tp3 and tp3<sup: tp3=sup*1.003
        if sl>res: sl=res*0.997; sr_note+="SL@R"
    if not sr_note: sr_note = f"Clean – S={sup:.5f} R={res:.5f}"
    if abs(tp1-price) < atr * 0.5: tp1 = price + d * atr * 0.5; sr_note += " | TP1 floored"
    lstm_tp3 = "Not triggered"
    if tp_count==3 and lstm_confirms and predicted_price is not None and tp2:
        if "BUY" in signal and predicted_price > tp2: tp3 = predicted_price; lstm_tp3 = f"LSTM → {predicted_price:.5f}"
        elif "SELL" in signal and predicted_price < tp2: tp3 = predicted_price; lstm_tp3 = f"LSTM → {predicted_price:.5f}"
    if "BUY" in signal and tp1 <= price: return sl, {"TP1":tp1,"TP2":None,"TP3":None}, "HOLD", {"cancel_reason":"TP1≤entry","rr_ratio":0}
    if "SELL" in signal and tp1 >= price: return sl, {"TP1":tp1,"TP2":None,"TP3":None}, "HOLD", {"cancel_reason":"TP1≥entry","rr_ratio":0}
    tp1_d = abs(tp1-price); sl_d = abs(sl-price)
    rr = round(tp1_d / max(sl_d, 1e-10), 2)
    min_rr = (cfg["MIN_RISK_REWARD"] if mp_tier>=4 else
              max(1.2, cfg["MIN_RISK_REWARD"]*0.80) if mp_tier==3 else
              max(1.0, cfg["MIN_RISK_REWARD"]*0.65) if mp_tier==2 else
              max(0.8, cfg["MIN_RISK_REWARD"]*0.50))
    if rr < min_rr: return sl, {"TP1":round(tp1,6),"TP2":None,"TP3":None}, "HOLD", {"cancel_reason":f"R:R {rr:.2f} < {min_rr:.1f}","rr_ratio":rr}
    def pct(t): return round(abs(t-price)/price*100, 2)
    tp_levels = {"TP1":round(tp1,6), "TP2":round(tp2,6) if tp2 else None, "TP3":round(tp3,6) if tp3 else None}
    info = {
        "market_power": mp, "power_label": mp_lbl, "power_tier": mp_tier,
        "vol_note": vn, "regime": regime, "sr_note": sr_note,
        "lstm_tp3_note": lstm_tp3, "tp_count": tp_count,
        "tp1_pct": pct(tp1), "tp2_pct": pct(tp2) if tp2 else None,
        "tp3_pct": pct(tp3) if tp3 else None,
        "sl_pct": round(sl_d/price*100, 2), "rr_ratio": rr,
        "min_rr_used": min_rr, "nearest_support": sup, "nearest_resistance": res,
        "cancel_reason": "None – valid ✓", "tp1_m": round(tp1_m,2), "sl_m": round(sl_m,2),
    }
    return round(sl,6), tp_levels, regime, info

def confidence_tier(w_score, strength, rr, htf_bias, signal, mp=50, whale=5.0, struct_conf=0):
    pts = 0
    if w_score >= 9.0: pts += 3
    elif w_score >= 7.5: pts += 2
    elif w_score >= 5.5: pts += 1
    if strength >= 75: pts += 3
    elif strength >= 60: pts += 2
    elif strength >= 45: pts += 1
    if rr >= 3.0: pts += 2
    elif rr >= 2.0: pts += 1
    if signal != "HOLD":
        d = "BULL" if "BUY" in signal else "BEAR"
        if htf_bias == d: pts += 2
        elif htf_bias=="NEUTRAL": pts += 1
    if mp >= 70: pts += 2
    elif mp >= 50: pts += 1
    if whale >= 7.5: pts += 1
    if struct_conf >= 75: pts += 1
    if pts >= 12: return "A+", "🏆 Supreme setup"
    elif pts >= 9: return "A", "🏆 Premium confidence"
    elif pts >= 7: return "B", "✅ Good – above average"
    elif pts >= 4: return "C", "🟡 Moderate – trade with caution"
    else: return "D", "🚫 Weak – consider skipping"

def position_size(entry, sl, balance=1000.0, risk_pct=0.01, tier="B", mp=50, whale=5.0):
    tier_m = {"A+":1.0,"A":1.0,"B":0.75,"C":0.5,"D":0.25}
    pow_m = round(max(0.5, min(1.0, mp/100)), 3)
    whl_m = round(max(0.85, min(1.15, 0.85 + (whale/10)*cfg["WHALE_SIZE_WEIGHT"]*2)), 3)
    adj = risk_pct * tier_m.get(tier, 0.5) * pow_m * whl_m
    sl_dist = abs(entry - sl) / max(entry, 1e-10)
    if sl_dist < 1e-6: return {"error": "SL too close to entry"}
    risk_amt = balance * adj
    pos_usdt = risk_amt / sl_dist
    pos_unit = pos_usdt / max(entry, 1e-10)
    return {
        "balance": round(balance, 2), "risk_pct": round(adj*100, 3),
        "risk_amt": round(risk_amt, 2), "pos_usdt": round(pos_usdt, 2),
        "pos_units": round(pos_unit, 6), "entry": round(entry, 6),
        "sl": round(sl, 6), "sl_dist": round(sl_dist*100, 2),
        "pow_mult": pow_m, "whl_mult": whl_m,
    }

# ── PyTorch LSTM Model (replaces Keras Sequential) ──────────────────────
class LSTMModel(nn.Module):
    def __init__(self, n_feats):
        super().__init__()
        self.conv1  = nn.Conv1d(n_feats, 64, 3, padding=1)
        self.conv2  = nn.Conv1d(64, 32, 3, padding=1)
        self.lstm1  = nn.LSTM(32, 128, batch_first=True)
        self.drop1  = nn.Dropout(0.25)
        self.lstm2  = nn.LSTM(128, 64, batch_first=True)
        self.drop2  = nn.Dropout(0.20)
        self.fc1    = nn.Linear(64, 32)
        self.fc2    = nn.Linear(32, 16)
        self.fc3    = nn.Linear(16, 1)

    def forward(self, x):
        # x: (batch, seq_len, n_feats)
        x = x.permute(0, 2, 1)          # → (batch, n_feats, seq_len) for Conv1d
        x = torch.relu(self.conv1(x))
        x = torch.relu(self.conv2(x))
        x = x.permute(0, 2, 1)          # → (batch, seq_len, 32) for LSTM
        x, _ = self.lstm1(x)
        x = self.drop1(x)
        x, _ = self.lstm2(x)
        x = self.drop2(x)
        x = x[:, -1, :]                 # last timestep
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)


def prepare_lstm(df, seq_len=60):
    feats = [c for c in ["close","RSI_14","MACD","MACD_Hist","ATR","OBV",
                          "EMA_9","BB_Width","Volume_Ratio","ADX","Stoch_K","ST_Direction"]
             if c in df.columns]
    logger.info(f"LSTM features ({len(feats)}): {', '.join(feats[:6])}{'…' if len(feats)>6 else ''}")
    scaler = MinMaxScaler((0, 1))
    scaled = scaler.fit_transform(df[feats])
    cs = MinMaxScaler((0, 1))
    cs.fit_transform(df[["close"]])
    X, y = [], []
    for i in range(seq_len, len(scaled)):
        X.append(scaled[i-seq_len:i]); y.append(scaled[i, 0])
    X, y = np.array(X), np.array(y)
    return X, y, scaler, cs, feats

def _cache_key(X):
    h = hashlib.sha256(X.astype(np.float32).tobytes()).hexdigest()[:16]
    return f"{cfg['COIN_SYMBOL'].replace('/','_')}_{h}"

def train_lstm(X, y, epochs=80):
    ck = _cache_key(X)
    cp = os.path.join(cfg["MODEL_CACHE_DIR"], f"m_{ck}.pt")
    hp = os.path.join(cfg["MODEL_CACHE_DIR"], f"h_{ck}.pkl")

    if cfg["USE_MODEL_CACHE"] and os.path.exists(cp):
        logger.info(f"Model cache hit – {ck}")
        try:
            mdl = LSTMModel(X.shape[2])
            mdl.load_state_dict(torch.load(cp, map_location="cpu", weights_only=True))
            mdl.eval()
            with open(hp, "rb") as f: h = pickle.load(f)
            class _H: pass
            hi = _H(); hi.history = h
            return mdl, hi
        except Exception as e:
            logger.warning(f"Cache load fail: {e}")

    device = torch.device("cpu")
    mdl = LSTMModel(X.shape[2]).to(device)

    # Train / val split
    split = int(len(X) * 0.85)
    X_tr, X_val = X[:split], X[split:]
    y_tr, y_val = y[:split], y[split:]

    X_tr_t  = torch.FloatTensor(X_tr).to(device)
    y_tr_t  = torch.FloatTensor(y_tr).unsqueeze(1).to(device)
    X_val_t = torch.FloatTensor(X_val).to(device)
    y_val_t = torch.FloatTensor(y_val).unsqueeze(1).to(device)

    loader    = DataLoader(TensorDataset(X_tr_t, y_tr_t), batch_size=64, shuffle=False)
    optimizer = optim.Adam(mdl.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5, min_lr=1e-6)
    criterion = nn.HuberLoss()

    history   = {"loss": [], "mae": [], "val_loss": []}
    best_val  = float("inf")
    best_state= None
    pat_count = 0
    patience  = 10

    t0 = time.time()
    for ep in range(epochs):
        mdl.train()
        ep_loss = ep_mae = 0.0
        for xb, yb in loader:
            optimizer.zero_grad()
            pred = mdl(xb)
            loss = criterion(pred, yb)
            loss.backward()
            optimizer.step()
            ep_loss += loss.item()
            ep_mae  += torch.mean(torch.abs(pred - yb)).item()
        ep_loss /= max(len(loader), 1)
        ep_mae  /= max(len(loader), 1)

        mdl.eval()
        with torch.no_grad():
            val_loss = criterion(mdl(X_val_t), y_val_t).item()

        history["loss"].append(ep_loss)
        history["mae"].append(ep_mae)
        history["val_loss"].append(val_loss)
        scheduler.step(val_loss)

        if val_loss < best_val:
            best_val   = val_loss
            best_state = {k: v.clone() for k, v in mdl.state_dict().items()}
            pat_count  = 0
        else:
            pat_count += 1
            if pat_count >= patience:
                logger.info(f"Early stop at epoch {ep+1}")
                break

    if best_state:
        mdl.load_state_dict(best_state)
    logger.success(f"Trained {len(history['loss'])} epochs in {time.time()-t0:.0f}s")

    if cfg["USE_MODEL_CACHE"]:
        try:
            os.makedirs(cfg["MODEL_CACHE_DIR"], exist_ok=True)
            torch.save(mdl.state_dict(), cp)
            with open(hp, "wb") as f: pickle.dump(history, f)
            logger.info(f"Cached → {ck}")
        except Exception as e:
            logger.warning(f"Cache save fail: {e}")

    mdl.eval()
    class _H: pass
    hi = _H(); hi.history = history
    return mdl, hi

def _predict(mdl, X, scaler, feats):
    inp = torch.FloatTensor(X[-1:])   # (1, seq_len, n_feats)
    with torch.no_grad():
        ps = mdl(inp).item()
    dum = np.zeros((1, len(feats)))
    dum[0, 0] = ps
    return float(scaler.inverse_transform(dum)[0, 0])

def pre_screen(df):
    last = df.iloc[-1]; reasons = []
    if float(last["ADX"]) < 15: reasons.append(f"ADX={last['ADX']:.1f}")
    if float(last["BB_Width"]) < float(df["BB_Width"].quantile(0.20)): reasons.append("BB tight")
    vp = float(last["Volume_Percentile"]) if "Volume_Percentile" in last.index else 50.0
    if vp < 20: reasons.append(f"VolPct={vp:.0f}")
    if 48 <= float(last["RSI_14"]) <= 52: reasons.append(f"RSI flat ({last['RSI_14']:.1f})")
    if abs(float(last["MACD_Hist"])) < float(last["ATR"]) * 0.01: reasons.append("MACD_Hist≈0")
    if len(reasons) >= 3:
        logger.warning(f"Pre-screen HOLD: {', '.join(reasons)}")
        return True, f"Pre-screened: {', '.join(reasons)}"
    return False, "Training required"

def _skip_history():
    class H: pass
    h = H(); h.history = {"loss":[0.0],"mae":[0.0],"val_loss":[0.0]}
    return h

# ── Main Run ────────────────────────────────────────────────────────────
def run_bot():
    wt = WhaleTracker(_engine.pool)
    result = {}
    try:
        df1h = get_data(cfg["COIN_SYMBOL"], cfg["TIMEFRAME_MAIN"])
        spreads = _engine.get_spread(cfg["COIN_SYMBOL"])
        if spreads:
            logger.info("💰 Market spreads:")
            for ex, d in list(spreads.items())[:3]:
                logger.info(f"  {ex.upper()}: Bid={d['bid']:.5f} Ask={d['ask']:.5f} Spr={d['spread_pct']:.4f}%")

        logger.info("📡 Fetching 4H data...")
        try:
            df4h = get_data(cfg["COIN_SYMBOL"], cfg["TIMEFRAME_HIGHER"])
            df4h = compute_indicators(df4h)
            htf_bias, htf_desc = get_htf_bias(df4h)
        except Exception as e:
            logger.warning(f"4H failed: {e}")
            df4h = None; htf_bias = "NEUTRAL"; htf_desc = "Unavailable"

        df1h = compute_indicators(df1h)
        patterns = detect_patterns(df1h)
        bull_div, bear_div, _ = detect_divergences(df1h)
        structure = analyze_structure(df1h, cfg["STRUCTURE_LOOKBACK"])

        current_price = float(df1h["close"].iloc[-1])
        ob_res = wt.analyze_ob(cfg["COIN_SYMBOL"], current_price)
        wc_res = wt.detect_whales(df1h)

        last_adx = float(df1h["ADX"].iloc[-1])
        skip, skip_reason = pre_screen(df1h)
        lstm_gated = last_adx < 20

        if lstm_gated:
            logger.info(f"LSTM GATED – ADX={last_adx:.1f} < 20")
            pred_price = current_price; chg_pct = 0.0
            feats = ["close"]; hist_obj = _skip_history(); X = np.zeros((1,60,1))
            skip = True; skip_reason = f"LSTM gated ADX={last_adx:.1f}<20"
        elif skip:
            pred_price = current_price; chg_pct = 0.0
            feats = ["close"]; hist_obj = _skip_history(); X = np.zeros((1,60,1))
        else:
            X, y, scaler, cs, feats = prepare_lstm(df1h, 60)
            mdl, hist_obj = train_lstm(X, y, epochs=80)
            pred_price = _predict(mdl, X, scaler, feats)
            chg_pct = (pred_price - current_price) / current_price * 100

        sig_pre, _, _, _ = generate_signal(df1h, chg_pct, predicted_price=pred_price if not skip else None,
                                           htf_bias=htf_bias, patterns=patterns, bull_div=bull_div,
                                           bear_div=bear_div, whale_score=5.0, structure=structure)
        whale_score, whale_label, whale_notes = wt.score(ob_res, wc_res, sig_pre)
        strength, s_lbl, s_notes, lstm_confirms = compute_strength(
            df1h, predicted_price=pred_price if not skip else None,
            patterns=patterns, bull_div=bull_div, bear_div=bear_div,
            htf_bias=htf_bias, whale_score=whale_score, structure=structure)

        signal, active, w_score, sig_reason = generate_signal(
            df1h, chg_pct, predicted_price=pred_price if not skip else None,
            htf_bias=htf_bias, patterns=patterns, bull_div=bull_div,
            bear_div=bear_div, whale_score=whale_score, whale_label=whale_label,
            structure=structure)

        stop_loss, tp_levels, regime, ai = compute_tp_sl(
            current_price, df1h, signal, strength_score=strength,
            predicted_price=pred_price if not skip else None,
            lstm_confirms=lstm_confirms, htf_bias=htf_bias)

        final_signal = signal
        cr = ai.get("cancel_reason","")
        if "valid" not in str(cr).lower(): final_signal = "HOLD"
        rr = ai.get("rr_ratio", 0)
        mp_val = ai.get("market_power", 50)
        mp_label = ai.get("power_label", "")
        tier, tier_desc = confidence_tier(w_score, strength, rr, htf_bias,
                                          final_signal, mp_val, whale_score,
                                          structure.get("confidence", 0))
        pos = position_size(current_price, stop_loss,
                            cfg["ACCOUNT_BALANCE"], cfg["RISK_PER_TRADE"],
                            tier, mp_val, whale_score)

        result = {
            "signal": final_signal, "tier": tier, "entry": current_price,
            "sl": stop_loss, "tp_levels": tp_levels, "rr": rr,
            "strength": strength, "market_power": mp_val,
            "whale_score": whale_score, "whale_label": whale_label,
            "structure": structure["type"], "structure_conf": structure["confidence"],
            "position": pos, "chg_pct": chg_pct, "pred_price": pred_price,
            "skip": skip, "df1h": df1h, "df4h": df4h, "patterns": patterns,
            "bull_div": bull_div, "bear_div": bear_div, "htf_bias": htf_bias,
            "htf_desc": htf_desc, "ai": ai, "mp_label": mp_label,
            "tier_desc": tier_desc, "sig_reason": sig_reason,
            "s_lbl": s_lbl, "whale_notes": whale_notes, "ob_res": ob_res,
            "wc_res": wc_res, "structure": structure, "hist_obj": hist_obj,
            "feats": feats, "skip_reason": skip_reason,
        }
        logger.success("✅ Analysis complete")
        return result

    except Exception as e:
        logger.error(f"CRITICAL ERROR: {e}")
        st.error(traceback.format_exc())
        return {"error": str(e)}

# ── Streamlit UI ────────────────────────────────────────────────────────
st.title("🐋 Crypto Trading Bot V8 · Structure + Whale Edition")
st.markdown("Multi-exchange data · LSTM gated · Adaptive TP/SL · Anti-overfit")

if st.sidebar.button("🚀 Run Analysis", use_container_width=True):
    with st.spinner("Running full analysis... This may take a minute."):
        res = run_bot()

    if "error" in res:
        st.error(res["error"])
    else:
        with st.expander("📋 Execution Logs", expanded=False):
            st.text(logger.get_text())

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        sig = res.get("signal", "HOLD")
        col1.metric("Signal", sig)
        col2.metric("Tier", res.get("tier", "?"), help=res.get("tier_desc",""))
        col3.metric("Strength", f"{res.get('strength',0)}/100")
        col4.metric("Market Power", f"{res.get('market_power',0)}/100")
        col5.metric("Whale Score", f"{res.get('whale_score',0)}/10")
        col6.metric("R:R", f"1:{res.get('rr',0):.2f}")

        colA, colB, colC, colD = st.columns(4)
        colA.metric("Entry", f"{res['entry']:.6f}")
        colB.metric("Stop Loss", f"{res['sl']:.6f}")
        tp = res.get("tp_levels", {})
        colC.metric("TP1", f"{tp.get('TP1', 'N/A')}")
        colD.metric("TP2", f"{tp.get('TP2', 'N/A') or 'N/A'}")

        colS, colW = st.columns(2)
        with colS:
            st.subheader("🏗 Market Structure")
            st.write(f"**{res.get('structure','?')}** (Conf: {res.get('structure_conf','?')}%)")
        with colW:
            st.subheader("🐋 Whale Tracker")
            st.write(f"**{res.get('whale_label','?')}** ({res['whale_score']}/10)")
            for note in res.get("whale_notes", []):
                st.caption(note)

        pos = res.get("position", {})
        st.subheader("💼 Position Sizing")
        colP1, colP2, colP3, colP4 = st.columns(4)
        colP1.metric("Risk %", f"{pos.get('risk_pct','?')}%")
        colP2.metric("Risk Amt", f"${pos.get('risk_amt','?')}")
        colP3.metric("Pos USDT", f"${pos.get('pos_usdt','?')}")
        colP4.metric("Pos Units", f"{pos.get('pos_units','?')}")

        df1h = res.get("df1h")
        if df1h is not None:
            st.subheader("📈 Price Chart")
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.plot(df1h["timestamp"], df1h["close"], color="#58a6ff", label="Close")
            ax.plot(df1h["timestamp"], df1h["EMA_9"], color="#f0883e", ls="--", label="EMA9")
            ax.plot(df1h["timestamp"], df1h["EMA_50"], color="#bc8cff", ls="-.", label="EMA50")
            ax.axhline(res["entry"], color="white", ls=":", label=f"Entry {res['entry']:.4f}")
            ax.axhline(res["sl"], color="red", ls="--", label=f"SL {res['sl']:.4f}")
            if tp.get("TP1"): ax.axhline(tp["TP1"], color="green", ls="--", label=f"TP1 {tp['TP1']:.4f}")
            if tp.get("TP2"): ax.axhline(tp["TP2"], color="lime", ls=":", label=f"TP2 {tp['TP2']:.4f}")
            ax.legend()
            ax.set_facecolor("#161b22"); fig.patch.set_facecolor("#0d1117")
            ax.tick_params(colors="#8b949e"); ax.spines["bottom"].set_color("#30363d"); ax.spines["left"].set_color("#30363d")
            ax.grid(True, alpha=0.2)
            st.pyplot(fig)

        st.success("Dashboard updated. Use sidebar to change configuration and run again.")
else:
    st.info("Adjust parameters in the sidebar and click **Run Analysis** to start.")
