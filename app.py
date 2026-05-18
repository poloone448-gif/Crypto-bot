"""
╔══════════════════════════════════════════════════════════════════════════╗
║       CRYPTO TRADING BOT  v8-WEB  ·  Render-Ready  ·  No ML            ║
║  Structure Gate · Whale Tracker · Volume Accuracy · Adaptive TP/SL      ║
║  Flask Dashboard · Lightweight · Production-Grade UI                    ║
╚══════════════════════════════════════════════════════════════════════════╝

Install (requirements.txt):
    flask
    ccxt
    ta
    pandas
    numpy
    gunicorn

Run locally:   python app.py
Run on Render: gunicorn app:app  (Start Command)
"""

# ── Standard Library ──────────────────────────────────────────────────────────
import os, time, queue, warnings, traceback, threading
import concurrent.futures
from datetime import datetime, timezone

warnings.filterwarnings("ignore")

# ── Third-party ───────────────────────────────────────────────────────────────
import numpy as np
import pandas as pd
import ccxt
import ta
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                           CONFIGURATION                                 ║
# ╚══════════════════════════════════════════════════════════════════════════╝

DEFAULT_COIN         = "BTC/USDT"
MIN_RISK_REWARD      = 1.5
TIMEFRAME_MAIN       = "1h"
TIMEFRAME_HIGHER     = "4h"
ACCOUNT_BALANCE      = 1_000.0
RISK_PER_TRADE       = 0.01

# Whale tracker
WHALE_VOL_THRESHOLD  = 3.0
WHALE_PRICE_MOVE_MIN = 0.003
ORDER_BOOK_DEPTH     = 20
WALL_MULT            = 5.0
WHALE_SIZE_WEIGHT    = 0.15

# Structure
STRUCTURE_LOOKBACK   = 75
STRUCTURE_MIN_SWING  = 0.008

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                        MARKET DATA ENGINE                               ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class MarketDataEngine:
    EXCHANGES = ["binance", "bybit", "okx", "kucoin", "gateio"]

    def __init__(self, workers=5):
        self.pool = {}
        for name in self.EXCHANGES:
            try:
                self.pool[name] = getattr(ccxt, name)({"enableRateLimit": True})
            except Exception:
                pass
        self._scores   = {ex: 1.0 for ex in self.pool}
        self._cache    = {}
        self._cache_ts = {}
        self._ttl      = 90

    def fetch(self, symbol, timeframe="1h", timeout=15, need=2):
        key = f"{symbol}_{timeframe}"
        now = time.time()
        if key in self._cache and now - self._cache_ts.get(key, 0) < self._ttl:
            return self._cache[key]

        q    = queue.Queue()
        stop = threading.Event()
        limit = 500 if timeframe in ("4h", "1d") else 1000

        def _one(name):
            if stop.is_set():
                return
            try:
                ohlcv = self.pool[name].fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
                df    = pd.DataFrame(ohlcv, columns=["timestamp","open","high","low","close","volume"])
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
                df["_src"]      = name
                if len(df) >= 60:
                    self._scores[name] = 1.0
                    q.put(df)
            except Exception:
                self._scores[name] = self._scores.get(name, 1.0) * 0.8

        sorted_ex = sorted(self.pool, key=lambda x: self._scores.get(x, 1.0), reverse=True)
        threads   = [threading.Thread(target=_one, args=(ex,), daemon=True) for ex in sorted_ex[:4]]
        for t in threads:
            t.start()

        results, deadline = [], time.time() + timeout
        while time.time() < deadline:
            try:
                results.append(q.get(timeout=0.5))
                if len(results) >= need:
                    stop.set()
                    break
            except queue.Empty:
                if all(not t.is_alive() for t in threads):
                    break

        if not results:
            raise RuntimeError(f"All exchanges failed for {symbol} [{timeframe}]")

        merged = self._merge(results)
        self._cache[key]    = merged
        self._cache_ts[key] = now
        return merged

    def get_spread(self, symbol):
        spreads = {}
        for name in list(self.pool)[:2]:
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

    def _merge(self, frames):
        combined = pd.concat(frames, ignore_index=True).sort_values("timestamp")
        n_src    = combined["_src"].nunique() if "_src" in combined.columns else 1

        if n_src > 1:
            def _agg(g):
                vol = g["volume"].values
                w   = vol if vol.sum() > 0 else np.ones(len(g))
                return pd.Series({
                    "timestamp": g["timestamp"].iloc[0],
                    "open":      np.average(g["open"].values,  weights=w),
                    "high":      np.average(g["high"].values,  weights=w),
                    "low":       np.average(g["low"].values,   weights=w),
                    "close":     np.average(g["close"].values, weights=w),
                    "volume":    float(np.median(vol)),
                    "source":    "multi_vwap",
                    "volume_quality": "multi_median",
                    "n_sources": len(g),
                })
            agg = combined.groupby("timestamp", sort=True).apply(_agg).reset_index(drop=True)
        else:
            combined = combined.drop_duplicates(subset=["timestamp"], keep="last")
            if "_src" in combined.columns:
                combined = combined.rename(columns={"_src": "source"})
            combined["volume_quality"] = "single"
            combined["n_sources"]      = 1
            agg = combined.reset_index(drop=True)

        for col in ["open","high","low","close","volume"]:
            agg[col] = agg[col].interpolate(method="linear").ffill().bfill()

        q1, q3 = agg["volume"].quantile(0.25), agg["volume"].quantile(0.75)
        cap     = q3 + 5.0 * (q3 - q1)
        agg["volume"] = agg["volume"].clip(upper=cap)
        return agg.reset_index(drop=True)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                          WHALE TRACKER                                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class WhaleTracker:
    def __init__(self, pool):
        self.pool    = pool
        self._ob     = {}
        self._ob_ts  = {}
        self._ob_ttl = 45

    def fetch_ob(self, symbol):
        key = f"ob_{symbol}"
        now = time.time()
        if key in self._ob and now - self._ob_ts.get(key, 0) < self._ob_ttl:
            return self._ob[key]
        for name, ex in self.pool.items():
            try:
                ob = ex.fetch_order_book(symbol, limit=ORDER_BOOK_DEPTH)
                if ob and ob.get("bids") and ob.get("asks"):
                    self._ob[key] = ob
                    self._ob_ts[key] = now
                    return ob
            except Exception:
                continue
        return None

    def analyze_ob(self, symbol, price):
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

        avg_b = float(np.mean(bid_sz)) if len(bid_sz) else 1.0
        avg_a = float(np.mean(ask_sz)) if len(ask_sz) else 1.0
        b_walls = [(float(bid_px[i]), float(bid_sz[i])) for i in range(len(bid_sz)) if bid_sz[i] >= avg_b * WALL_MULT]
        a_walls = [(float(ask_px[i]), float(ask_sz[i])) for i in range(len(ask_sz)) if ask_sz[i] >= avg_a * WALL_MULT]

        if   imbal >= 0.65: sig, note = "BULL",      f"Heavy Bid ({imbal:.1%})"
        elif imbal <= 0.35: sig, note = "BEAR",      f"Heavy Ask ({1-imbal:.1%})"
        elif imbal >= 0.55: sig, note = "MILD_BULL", f"Mild Bid ({imbal:.1%})"
        elif imbal <= 0.45: sig, note = "MILD_BEAR", f"Mild Ask ({1-imbal:.1%})"
        else:               sig, note = "NEUTRAL",   f"Balanced ({imbal:.1%})"

        return {
            "imbalance": round(imbal, 4), "bid_usdt": round(bid_usdt, 2),
            "ask_usdt":  round(ask_usdt, 2),
            "bid_walls": len(b_walls), "ask_walls": len(a_walls),
            "ob_signal": sig, "ob_note": note, "available": True,
        }

    def detect_whales(self, df):
        if len(df) < 20:
            return self._empty_whale()
        ma20    = df["volume"].rolling(20).mean().bfill()
        candles = []
        for i in range(max(0, len(df) - 50), len(df)):
            vm = ma20.iloc[i]
            if vm == 0 or pd.isna(vm): continue
            vr   = df["volume"].iloc[i] / vm
            op   = max(float(df["open"].iloc[i]), 1e-10)
            pmov = abs(float(df["close"].iloc[i]) - op) / op
            if vr >= WHALE_VOL_THRESHOLD and pmov >= WHALE_PRICE_MOVE_MIN:
                bull = float(df["close"].iloc[i]) >= op
                candles.append({
                    "idx": i,
                    "price":      float(df["close"].iloc[i]),
                    "vol_ratio":  round(vr, 2),
                    "price_move": round(pmov * 100, 3),
                    "direction":  "BUY" if bull else "SELL",
                    "type":       "ACCUMULATION" if bull else "DISTRIBUTION",
                })
        rec      = df.tail(30)
        bull_vol = float(rec.loc[rec["close"] >= rec["open"], "volume"].sum())
        bear_vol = float(rec.loc[rec["close"] <  rec["open"], "volume"].sum())
        cvd_r    = bull_vol / max(bull_vol + bear_vol, 1e-10)
        cvd_t    = "BULL" if cvd_r >= 0.60 else "BEAR" if cvd_r <= 0.40 else "NEUTRAL"
        return {
            "whale_candles":  candles,
            "recent_whale":   candles[-1] if candles else None,
            "cvd_ratio":      round(cvd_r, 4),
            "cvd_trend":      cvd_t,
            "bull_vol":       round(bull_vol, 2),
            "bear_vol":       round(bear_vol, 2),
            "total_detected": len(candles),
        }

    def score(self, ob, wc, signal):
        pts, notes = 0.0, []
        is_bull = "BUY" in signal
        if ob.get("available"):
            s = ob["ob_signal"]
            if   (is_bull  and s == "BULL"):        pts += 4; notes.append(f"OB BULL aligned — {ob['ob_note']}")
            elif (not is_bull and s == "BEAR"):      pts += 4; notes.append(f"OB BEAR aligned — {ob['ob_note']}")
            elif (is_bull  and s == "MILD_BULL"):    pts += 2; notes.append(f"OB mild BULL — {ob['ob_note']}")
            elif (not is_bull and s == "MILD_BEAR"): pts += 2; notes.append(f"OB mild BEAR — {ob['ob_note']}")
            elif s == "NEUTRAL":                     pts += 1; notes.append(f"OB neutral — {ob['ob_note']}")
            else:                                              notes.append(f"OB against — {ob['ob_note']}")
            if   is_bull  and ob["bid_walls"] > 0:  pts += 1; notes.append(f"Bid whale wall ({ob['bid_walls']} lvls)")
            elif not is_bull and ob["ask_walls"] > 0:pts += 1; notes.append(f"Ask whale wall ({ob['ask_walls']} lvls)")
        else:
            notes.append("OB unavailable — skipped")

        cvd   = wc.get("cvd_trend", "NEUTRAL")
        cvd_r = wc.get("cvd_ratio", 0.5)
        if   (is_bull  and cvd == "BULL"):  pts += 3; notes.append(f"CVD bull ({cvd_r:.1%})")
        elif (not is_bull and cvd == "BEAR"):pts += 3; notes.append(f"CVD bear ({cvd_r:.1%})")
        elif cvd == "NEUTRAL":               pts += 1; notes.append(f"CVD neutral ({cvd_r:.1%})")
        else:                                          notes.append(f"CVD opposing ({cvd_r:.1%})")

        rw = wc.get("recent_whale")
        if rw:
            match = (is_bull and rw["direction"]=="BUY") or (not is_bull and rw["direction"]=="SELL")
            if match:
                pts += 2; notes.append(f"Whale {rw['type']} {rw['vol_ratio']:.1f}× vol  {rw['price_move']:.2f}% move")
            else:
                notes.append(f"Whale opposing {rw['type']} {rw['vol_ratio']:.1f}×")
        else:
            notes.append("No whale candle in last 50 bars")

        final = round(min(10.0, pts), 1)
        label = ("🐋 CONFIRMED" if final >= 7.5 else
                 "🐟 PARTIAL"   if final >= 5.0 else
                 "🔍 NEUTRAL"   if final >= 3.0 else
                 "🚨 OPPOSING")
        return final, label, notes

    @staticmethod
    def _empty_ob():
        return {"imbalance":0.5,"bid_usdt":0,"ask_usdt":0,
                "bid_walls":0,"ask_walls":0,"ob_signal":"NEUTRAL",
                "ob_note":"OB unavailable","available":False}

    @staticmethod
    def _empty_whale():
        return {"whale_candles":[],"recent_whale":None,"cvd_ratio":0.5,
                "cvd_trend":"NEUTRAL","bull_vol":0.0,"bear_vol":0.0,"total_detected":0}


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                     MARKET STRUCTURE ANALYZER                           ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def analyze_structure(df, lookback=STRUCTURE_LOOKBACK):
    if len(df) < lookback + 7:
        return _empty_structure("UNKNOWN", 0, "Insufficient data")
    rec    = df.tail(lookback).reset_index(drop=True)
    hi, lo = rec["high"].values, rec["low"].values
    cl     = rec["close"].values
    s_highs, s_lows = [], []
    for i in range(3, len(rec) - 3):
        lh, rh = hi[i-3:i], hi[i+1:i+4]
        ll, rl = lo[i-3:i], lo[i+1:i+4]
        if len(lh) < 3 or len(rh) < 3: continue
        if hi[i] >= max(lh) and hi[i] >= max(rh):
            local_lo = lo[max(0, i-5):i]
            if len(local_lo) > 0:
                base = max(float(min(local_lo)), 1e-10)
                if (hi[i] - base) / base >= STRUCTURE_MIN_SWING:
                    s_highs.append((i, float(hi[i])))
        if lo[i] <= min(ll) and lo[i] <= min(rl):
            local_hi = hi[max(0, i-5):i]
            if len(local_hi) > 0:
                base = max(float(lo[i]), 1e-10)
                if (max(local_hi) - lo[i]) / base >= STRUCTURE_MIN_SWING:
                    s_lows.append((i, float(lo[i])))

    if len(s_highs) < 2 or len(s_lows) < 2:
        return _empty_structure("RANGING", 35, "Insufficient swings", s_highs, s_lows)

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

    if hh and hl:       stype, conf = "UPTREND",   90 if breakout else 78
    elif lh and ll:     stype, conf = "DOWNTREND", 90 if breakdown else 78
    elif breakout:      stype, conf = "BREAKOUT",  72
    elif breakdown:     stype, conf = "BREAKDOWN", 72
    else:               stype, conf = "RANGING",   45

    return {
        "type": stype, "confidence": conf,
        "swing_highs": len(s_highs), "swing_lows": len(s_lows),
        "last_high": s_highs[-1][1] if s_highs else None,
        "last_low":  s_lows[-1][1]  if s_lows  else None,
        "prev_high": prev_high, "prev_low": prev_low,
        "breakout": breakout, "breakdown": breakdown,
        "hh": hh, "hl": hl, "lh": lh, "ll": ll,
    }


def _empty_structure(stype, conf, note, sh=None, sl=None):
    return {
        "type": stype, "confidence": conf,
        "swing_highs": len(sh or []), "swing_lows": len(sl or []),
        "last_high": None, "last_low": None,
        "prev_high": None, "prev_low": None,
        "breakout": False, "breakdown": False,
        "hh": False, "hl": False, "lh": False, "ll": False,
    }


def structure_gate(structure, signal):
    stype   = structure.get("type", "RANGING")
    conf    = structure.get("confidence", 0)
    is_bull = "BUY" in signal
    if signal == "HOLD":
        return True, "HOLD — no gate"
    rules = {
        "UPTREND":   (is_bull,      "UPTREND"),
        "DOWNTREND": (not is_bull,  "DOWNTREND"),
        "BREAKOUT":  (is_bull,      "BREAKOUT"),
        "BREAKDOWN": (not is_bull,  "BREAKDOWN"),
    }
    if stype in rules:
        allowed, label = rules[stype]
        if allowed:
            return True, f"✓ {label} supports signal (conf:{conf}%)"
        else:
            return False, f"✗ BLOCKED — {label} forbids signal (conf:{conf}%)"
    return True, f"⚠ RANGING — allowed with caution (conf:{conf}%)"


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                      TECHNICAL INDICATORS                               ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def _supertrend(df, period=10, mult=3.0):
    atr   = ta.volatility.AverageTrueRange(df["high"],df["low"],df["close"],window=period,fillna=True).average_true_range()
    hl2   = (df["high"] + df["low"]) / 2
    upper = (hl2 + mult * atr).values
    lower = (hl2 - mult * atr).values
    close = df["close"].values
    n     = len(close)
    fu, fl, st, di = upper.copy(), lower.copy(), np.zeros(n), np.ones(n)
    for i in range(1, n):
        fu[i] = upper[i] if upper[i] < fu[i-1] or close[i-1] > fu[i-1] else fu[i-1]
        fl[i] = lower[i] if lower[i] > fl[i-1] or close[i-1] < fl[i-1] else fl[i-1]
        st[i] = (fu[i] if (st[i-1]==fu[i-1] and close[i]<=fu[i]) else
                 fl[i] if (st[i-1]==fu[i-1] and close[i]>fu[i]) else
                 fl[i] if close[i]>=fl[i] else fu[i])
        di[i] = -1 if st[i] == fu[i] else 1
    df["Supertrend"]   = st
    df["ST_Direction"] = di
    return df


def compute_indicators(df):
    df = df.copy()
    df["EMA_9"]   = df["close"].ewm(span=9,   adjust=False).mean()
    df["SMA_20"]  = df["close"].rolling(20).mean()
    df["EMA_50"]  = df["close"].ewm(span=50,  adjust=False).mean()
    df["EMA_200"] = df["close"].ewm(span=200, adjust=False).mean()

    typical    = (df["high"] + df["low"] + df["close"]) / 3
    df["VWAP"] = (typical * df["volume"]).cumsum() / df["volume"].cumsum().replace(0, np.nan)
    df["RSI_14"] = ta.momentum.RSIIndicator(df["close"], window=14, fillna=True).rsi()

    macd              = ta.trend.MACD(df["close"], window_slow=26, window_fast=12, fillna=True)
    df["MACD"]        = macd.macd()
    df["MACD_Signal"] = macd.macd_signal()
    df["MACD_Hist"]   = df["MACD"] - df["MACD_Signal"]

    df["ATR"] = ta.volatility.AverageTrueRange(df["high"],df["low"],df["close"],window=14,fillna=True).average_true_range()
    atr_arr = df["ATR"].values
    wp = min(100, len(atr_arr))
    ap = np.full(len(atr_arr), 50.0)
    for i in range(wp, len(atr_arr)):
        ap[i] = np.sum(atr_arr[i-wp:i] < atr_arr[i]) / wp * 100
    df["ATR_Percentile"] = ap

    df["OBV"] = ta.volume.OnBalanceVolumeIndicator(df["close"],df["volume"],fillna=True).on_balance_volume()

    bb = ta.volatility.BollingerBands(df["close"], window=20, window_dev=2, fillna=True)
    df["BB_Upper"] = bb.bollinger_hband()
    df["BB_Lower"] = bb.bollinger_lband()
    df["BB_Mid"]   = bb.bollinger_mavg()
    df["BB_Width"] = ((df["BB_Upper"] - df["BB_Lower"]) / df["BB_Mid"]).fillna(0)

    adx_i         = ta.trend.ADXIndicator(df["high"],df["low"],df["close"],window=14,fillna=True)
    df["ADX"]     = adx_i.adx()
    df["ADX_Pos"] = adx_i.adx_pos()
    df["ADX_Neg"] = adx_i.adx_neg()

    stoch         = ta.momentum.StochasticOscillator(df["high"],df["low"],df["close"],window=14,smooth_window=3,fillna=True)
    df["Stoch_K"] = stoch.stoch()
    df["Stoch_D"] = stoch.stoch_signal()

    atr_vol = (df["ATR"] / df["close"].rolling(20).mean()).fillna(0).clip(0, 1)
    df["Dynamic_RSI_Lower"] = 30 + atr_vol * 10
    df["Dynamic_RSI_Upper"] = 70 - atr_vol * 10

    df["Williams_R"] = ta.momentum.WilliamsRIndicator(df["high"],df["low"],df["close"],lbp=14,fillna=True).williams_r()
    df["CCI"]        = ta.trend.CCIIndicator(df["high"],df["low"],df["close"],window=20,fillna=True).cci()

    df["Volume_MA20"] = df["volume"].rolling(20).mean().bfill()
    vol_arr  = df["volume"].values
    roll100  = min(100, len(vol_arr))
    vp_arr   = np.full(len(vol_arr), 50.0)
    for i in range(roll100, len(vol_arr)):
        vp_arr[i] = np.sum(vol_arr[i-roll100:i] < vol_arr[i]) / roll100 * 100
    df["Volume_Percentile"] = vp_arr
    df["Volume_Ratio"]      = (df["volume"] / df["Volume_MA20"].replace(0, np.nan)).fillna(1.0).clip(0, 10)
    df["Volume_Delta"]      = np.where(df["close"] >= df["open"], df["volume"], -df["volume"])
    df["CVD_20"]            = df["Volume_Delta"].rolling(20).sum()

    df = _supertrend(df)
    df = df.dropna(subset=["EMA_200","ADX","ATR"]).reset_index(drop=True)
    return df


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                      CANDLESTICK PATTERNS                               ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def detect_patterns(df):
    if len(df) < 5:
        return {}
    o, h, l, c = df["open"].values, df["high"].values, df["low"].values, df["close"].values
    def body(i):    return abs(c[i] - o[i])
    def rng(i):     return max(h[i] - l[i], 1e-10)
    def uw(i):      return h[i] - max(c[i], o[i])
    def lw(i):      return min(c[i], o[i]) - l[i]
    avg = np.mean([body(x) for x in range(-min(10,len(df)),0)]) or 1e-10
    i, j, k = -1, -2, -3
    return {
        "bullish_engulfing": bool(c[j]<o[j] and c[i]>o[i] and c[i]>o[j] and o[i]<c[j] and body(i)>body(j)*1.1),
        "bearish_engulfing": bool(c[j]>o[j] and c[i]<o[i] and c[i]<o[j] and o[i]>c[j] and body(i)>body(j)*1.1),
        "hammer":            bool(lw(i)>=body(i)*2 and uw(i)<=body(i)*0.3 and body(i)>0 and rng(i)>avg*0.5),
        "shooting_star":     bool(uw(i)>=body(i)*2 and lw(i)<=body(i)*0.3 and body(i)>0 and rng(i)>avg*0.5),
        "doji":              bool(body(i)<=rng(i)*0.1 and rng(i)>avg*0.3),
        "morning_star":      bool(c[k]<o[k] and body(k)>avg*0.8 and body(j)<avg*0.3 and c[i]>o[i] and c[i]>(o[k]+c[k])/2),
        "evening_star":      bool(c[k]>o[k] and body(k)>avg*0.8 and body(j)<avg*0.3 and c[i]<o[i] and c[i]<(o[k]+c[k])/2),
    }


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                        DIVERGENCE DETECTOR                              ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def detect_divergences(df, lookback=30):
    if len(df) < lookback:
        return False, False
    rec   = df.tail(lookback).reset_index(drop=True)
    price = rec["close"].values
    rsi   = rec["RSI_14"].values
    obv   = rec["OBV"].values
    sw    = max(3, lookback // 5)

    def swings(arr, w):
        hi, lo = [], []
        for i in range(w, len(arr) - w):
            s = arr[i-w:i+w+1]
            if arr[i] >= np.max(s) - 1e-10: hi.append(i)
            if arr[i] <= np.min(s) + 1e-10: lo.append(i)
        return hi, lo

    ph, pl      = swings(price, sw)
    bull_div    = bear_div = False
    if len(pl) >= 2:
        p1, p2 = pl[-2], pl[-1]
        if price[p2] < price[p1] * 0.999 and rsi[p2] > rsi[p1] + 1.5:
            bull_div = True
    if len(ph) >= 2:
        p1, p2 = ph[-2], ph[-1]
        if price[p2] > price[p1] * 1.001 and rsi[p2] < rsi[p1] - 1.5:
            bear_div = True
    half = lookback // 2
    pt = price[-1] - price[-half] if half < len(price) else 0
    ot = obv[-1]   - obv[-half]   if half < len(obv)   else 0
    if pt < -price[-1]*0.005 and ot > 0: bull_div = True
    elif pt > price[-1]*0.005 and ot < 0: bear_div = True
    return bull_div, bear_div


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                          REGIME + HTF                                   ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def classify_regime(df):
    last  = df.iloc[-1]
    adx   = float(last["ADX"])
    bbw   = float(last["BB_Width"])
    atp   = float(last["ATR_Percentile"])
    price = float(last["close"])
    e9    = float(last["EMA_9"])
    e50   = float(last["EMA_50"])
    e200  = float(last["EMA_200"])
    adxp  = float(last["ADX_Pos"])
    adxn  = float(last["ADX_Neg"])
    pb = price > e9 > e50 > e200
    nb = price < e9 < e50 < e200
    ub = price > e9 > e50
    db = price < e9 < e50
    q80 = float(df["BB_Width"].quantile(0.80))
    q40 = float(df["BB_Width"].quantile(0.40))
    if atp > 85 and bbw > q80:           return "VOLATILE",      "Very high volatility"
    if adx >= 35 and adxp > adxn and pb: return "STRONG_BULL",   "Very strong uptrend"
    if adx >= 35 and adxn > adxp and nb: return "STRONG_BEAR",   "Very strong downtrend"
    if adx > 22 and adxp > adxn and ub:  return "TRENDING_UP",   "Uptrend"
    if adx > 22 and adxn > adxp and db:  return "TRENDING_DOWN", "Downtrend"
    if adx < 20 and bbw < q40:           return "RANGING",       "Sideways"
    return "NORMAL", "Normal"


def get_htf_bias(df4):
    if df4 is None or df4.empty or len(df4) < 10:
        return "NEUTRAL", "4H unavailable"
    last  = df4.iloc[-1]
    price = float(last["close"])
    checks = [
        price > float(last["EMA_9"]), price > float(last["EMA_50"]),
        price > float(last["EMA_200"]),
        float(last["MACD"]) > float(last["MACD_Signal"]),
        float(last["RSI_14"]) > 55, int(last["ST_Direction"]) == 1,
        float(last["ADX_Pos"]) > float(last["ADX_Neg"]),
    ]
    bull = sum(checks)
    bear = len(checks) - bull
    tot  = len(checks)
    if   bull >= int(tot * 0.7): return "BULL",    f"4H Bullish ({bull}/{tot})"
    elif bear >= int(tot * 0.7): return "BEAR",    f"4H Bearish ({bear}/{tot})"
    else:                        return "NEUTRAL",  f"4H Neutral B={bull} Br={bear}"


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                      SUPPORT / RESISTANCE                               ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def find_sr(df, lookback=100, gap_pct=0.005):
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


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                      MARKET POWER ENGINE                                ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def market_power(df, htf_bias="NEUTRAL", strength_score=50, signal="HOLD"):
    last    = df.iloc[-1]
    score   = 0.0; max_s = 0.0; log = []
    is_bull = "BUY" in signal

    def _add(pts, mx, label):
        nonlocal score, max_s
        score += pts; max_s += mx
        log.append((pts, mx, label))

    adx = float(last["ADX"])
    pts = 25 if adx>=50 else 22 if adx>=40 else 18 if adx>=30 else 12 if adx>=22 else 5 if adx>=15 else 0
    _add(pts, 25, f"ADX {adx:.1f}")

    p, e9, e50, e200 = float(last["close"]), float(last["EMA_9"]), float(last["EMA_50"]), float(last["EMA_200"])
    if is_bull:
        pts = 20 if p>e9>e50>e200 else 14 if p>e9>e50 else 7 if p>e9 else 0
    else:
        pts = 20 if p<e9<e50<e200 else 14 if p<e9<e50 else 7 if p<e9 else 0
    _add(pts, 20, "EMA alignment")

    if (htf_bias=="BULL" and is_bull) or (htf_bias=="BEAR" and not is_bull): pts=15
    elif htf_bias=="NEUTRAL": pts=6
    else: pts=0
    _add(pts, 15, f"4H bias {htf_bias}")

    st_ok = (float(last["ST_Direction"])==1 and is_bull) or (float(last["ST_Direction"])==-1 and not is_bull)
    _add(10 if st_ok else 0, 10, "Supertrend")

    mh = float(last["MACD_Hist"])
    mb = float(last["MACD"]) > float(last["MACD_Signal"])
    if   (is_bull and mb) or (not is_bull and not mb): pts = 10
    else: pts = 0
    _add(pts, 10, "MACD")

    vp  = float(last["Volume_Percentile"]) if "Volume_Percentile" in last.index else 50.0
    pts = 10 if vp>=90 else 8 if vp>=75 else 5 if vp>=55 else 2 if vp>=30 else 0
    _add(pts, 10, f"Vol pct {vp:.0f}th")

    _add(min(5, round(strength_score/20)), 5, "Strength carry")

    final = round(min(100.0, (score / max(max_s, 0.01)) * 100), 1)
    if   final>=86: label,tier = "SUPREME",  6
    elif final>=71: label,tier = "V.STRONG", 5
    elif final>=56: label,tier = "STRONG",   4
    elif final>=41: label,tier = "MODERATE", 3
    elif final>=26: label,tier = "WEAK",     2
    else:           label,tier = "RISKY",    1
    return final, label, tier, log


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                        STRENGTH SCORE                                   ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def compute_strength(df, patterns=None, bull_div=False, bear_div=False,
                     htf_bias="NEUTRAL", whale_score=5.0, structure=None):
    if patterns is None: patterns = {}
    last  = df.iloc[-1]
    price = float(last["close"])
    comps = {}

    def _c(name, pts, mx):
        comps[name] = (pts, mx)

    e9, e50, e200 = float(last["EMA_9"]), float(last["EMA_50"]), float(last["EMA_200"])
    if   price>e9>e50>e200: _c("EMA", 2.5, 2.5)
    elif price>e9>e50:       _c("EMA", 1.8, 2.5)
    elif price>e9:            _c("EMA", 0.8, 2.5)
    elif price<e9<e50<e200:  _c("EMA", 2.5, 2.5)
    elif price<e9<e50:        _c("EMA", 1.8, 2.5)
    else:                     _c("EMA", 0.8, 2.5)

    adx = float(last["ADX"])
    if   adx>=40: _c("ADX", 2.0, 2.0)
    elif adx>=30: _c("ADX", 1.5, 2.0)
    elif adx>=25: _c("ADX", 1.0, 2.0)
    elif adx>=18: _c("ADX", 0.4, 2.0)
    else:         _c("ADX", 0.0, 2.0)

    vp = float(last["Volume_Percentile"]) if "Volume_Percentile" in last.index else 50.0
    if   vp>=90: _c("Volume", 2.0, 2.0)
    elif vp>=75: _c("Volume", 1.5, 2.0)
    elif vp>=55: _c("Volume", 1.0, 2.0)
    elif vp>=30: _c("Volume", 0.4, 2.0)
    else:        _c("Volume", 0.0, 2.0)

    rsi    = float(last["RSI_14"])
    r_lo   = float(last["Dynamic_RSI_Lower"])
    r_hi   = float(last["Dynamic_RSI_Upper"])
    mid_lo = r_lo + (r_hi - r_lo) * 0.25
    mid_hi = r_hi - (r_hi - r_lo) * 0.25
    if   r_lo<=rsi<=mid_lo or mid_hi<=rsi<=r_hi: _c("RSI", 1.5, 1.5)
    elif rsi<r_lo or rsi>r_hi:                    _c("RSI", 0.3, 1.5)
    else:                                          _c("RSI", 0.7, 1.5)

    mh = float(last["MACD_Hist"])
    if mh != 0: _c("MACD", 1.0, 1.0)
    else:        _c("MACD", 0.0, 1.0)

    sk, sd = float(last["Stoch_K"]), float(last["Stoch_D"])
    if   (sk<25 and sk>sd) or (sk>75 and sk<sd): _c("Stoch", 1.0, 1.0)
    elif 40<=sk<=60:                               _c("Stoch", 0.3, 1.0)
    else:                                          _c("Stoch", 0.5, 1.0)

    adx_bull = float(last["ADX_Pos"]) > float(last["ADX_Neg"])
    st_ok    = (float(last["ST_Direction"])==1 and adx_bull) or (float(last["ST_Direction"])==-1 and not adx_bull)
    _c("Supertrend", 1.0 if st_ok else 0.0, 1.0)

    bull_pats = ["bullish_engulfing","hammer","morning_star"]
    bear_pats = ["bearish_engulfing","shooting_star","evening_star"]
    found_pat = any(patterns.get(p, False) for p in bull_pats + bear_pats)
    _c("Pattern", 1.0 if found_pat else 0.0, 1.0)

    _c("Diverge", 1.0 if (bull_div or bear_div) else 0.0, 1.0)

    if (htf_bias=="BULL" and adx_bull) or (htf_bias=="BEAR" and not adx_bull): _c("4H", 1.0, 1.0)
    elif htf_bias=="NEUTRAL":                                                    _c("4H", 0.3, 1.0)
    else:                                                                        _c("4H", 0.0, 1.0)

    if   whale_score>=7.5: _c("Whale", 1.0, 1.0)
    elif whale_score>=5.0: _c("Whale", 0.6, 1.0)
    elif whale_score>=3.0: _c("Whale", 0.3, 1.0)
    else:                  _c("Whale", 0.0, 1.0)

    if structure:
        stype = structure.get("type","RANGING")
        sconf = structure.get("confidence", 0)
        if (stype=="UPTREND" and adx_bull) or (stype=="DOWNTREND" and not adx_bull):
            _c("Structure", min(1.0, sconf/100), 1.0)
        elif stype in ("BREAKOUT","BREAKDOWN"):
            _c("Structure", 0.5, 1.0)
        else:
            _c("Structure", 0.0, 1.0)

    earned = sum(v[0] for v in comps.values())
    total  = sum(v[1] for v in comps.values())
    final  = round(min(100.0, (earned / max(total, 0.1)) * 100), 1)
    lbl = ("MONSTER" if final>=80 else "STRONG" if final>=65 else "MODERATE" if final>=45 else "WEAK")
    return final, lbl, comps


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                       SIGNAL GENERATION                                 ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def generate_signal(df, price_chg_pct=0.0, htf_bias="NEUTRAL",
                    patterns=None, bull_div=False, bear_div=False,
                    whale_score=5.0, whale_label="", structure=None):
    if patterns is None: patterns = {}
    if price_chg_pct < -3.5:
        return "HOLD", [], 0.0, "Hard guard: price drop >3.5%"
    regime, _ = classify_regime(df)
    if regime == "VOLATILE":
        return "HOLD", [], 0.0, "Regime: VOLATILE"
    if regime == "RANGING" and abs(price_chg_pct) < 0.8:
        return "HOLD", [], 0.0, "Regime: RANGING — no momentum"

    last   = df.iloc[-1]
    adx    = float(last["ADX"]); adxp = float(last["ADX_Pos"]); adxn = float(last["ADX_Neg"])
    rsi    = float(last["RSI_14"]); r_lo = float(last["Dynamic_RSI_Lower"]); r_hi = float(last["Dynamic_RSI_Upper"])
    sk, sd = float(last["Stoch_K"]), float(last["Stoch_D"])
    close  = float(last["close"])
    vp     = float(last["Volume_Percentile"]) if "Volume_Percentile" in last.index else 50.0
    vwap   = float(last["VWAP"]) if "VWAP" in last.index else close
    cvd20  = float(df["CVD_20"].iloc[-1]) if "CVD_20" in df.columns else 0.0
    macd_b = float(last["MACD"]) > float(last["MACD_Signal"])
    st_bull= int(last["ST_Direction"]) == 1

    def side_score(weights):
        t, a = 0.0, []
        for name, (cond, w) in weights.items():
            if cond: t += w; a.append(name)
        return t, a

    buy_w = {
        "macd_cross":  (macd_b,                                          2.0),
        "ema_align":   (close > float(last["EMA_9"]) > float(last["EMA_50"]), 2.0),
        "adx_bull":    (adx > 22 and adxp > adxn,                       1.5),
        "rsi_zone":    (rsi < r_lo,                                      1.0),
        "stoch_bull":  (sk < 30 and sk > sd,                             1.0),
        "vol_spike":   (vp >= 55,                                        1.0),
        "supertrend":  (st_bull,                                         1.0),
        "vwap_above":  (close > vwap,                                    0.5),
        "bull_pat":    (any(patterns.get(p,False) for p in ["bullish_engulfing","hammer","morning_star"]), 1.0),
        "bull_div":    (bull_div,                                        1.0),
        "htf_bull":    (htf_bias == "BULL",                              1.0),
        "cvd_bull":    (cvd20 > 0,                                       0.5),
    }
    sell_w = {
        "macd_cross":  (not macd_b,                                      2.0),
        "ema_align":   (close < float(last["EMA_9"]) < float(last["EMA_50"]), 2.0),
        "adx_bear":    (adx > 22 and adxn > adxp,                       1.5),
        "rsi_zone":    (rsi > r_hi,                                      1.0),
        "stoch_bear":  (sk > 70 and sk < sd,                             1.0),
        "vol_spike":   (vp >= 55,                                        1.0),
        "supertrend":  (not st_bull,                                     1.0),
        "vwap_below":  (close < vwap,                                    0.5),
        "bear_pat":    (any(patterns.get(p,False) for p in ["bearish_engulfing","shooting_star","evening_star"]), 1.0),
        "bear_div":    (bear_div,                                        1.0),
        "htf_bear":    (htf_bias == "BEAR",                              1.0),
        "cvd_bear":    (cvd20 < 0,                                       0.5),
    }

    buy_s, buy_a   = side_score(buy_w)
    sell_s, sell_a = side_score(sell_w)

    if htf_bias == "BEAR" and buy_s > sell_s:   buy_s  *= 0.75
    elif htf_bias == "BULL" and sell_s > buy_s: sell_s *= 0.75

    if buy_s > sell_s:
        fs = buy_s; active = buy_a
        raw = "STRONG BUY" if fs >= 7.5 else "BUY" if fs >= 5.0 else "HOLD"
    else:
        fs = sell_s; active = sell_a
        raw = "STRONG SELL" if fs >= 7.5 else "SELL" if fs >= 5.0 else "HOLD"

    if whale_score < 2.5 and raw != "HOLD":
        return "HOLD", [], 0.0, f"BLOCKED: whale {whale_score:.1f} opposing"

    if structure and raw != "HOLD":
        allowed, sreason = structure_gate(structure, raw)
        if not allowed:
            return "HOLD", [], 0.0, f"BLOCKED: {sreason}"

    final_sig  = raw
    whale_note = ""
    if 2.5 <= whale_score < 3.5 and raw in ("STRONG BUY","STRONG SELL"):
        final_sig  = raw.replace("STRONG ", "")
        whale_note = f"Downgraded STRONG→{final_sig} (whale weak {whale_score:.1f})"

    if final_sig == "HOLD":
        return "HOLD", [], max(buy_s, sell_s), f"Score too low (B:{buy_s:.1f} S:{sell_s:.1f})"

    return final_sig, active, fs, f"Score {fs:.1f} | {whale_note or 'Whale OK'}"


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                      ADAPTIVE TP/SL ENGINE                              ║
# ╚══════════════════════════════════════════════════════════════════════════╝

_TP_TABLE = {
    6: {"low":(3.5,5.5,8.5,1.8,3), "normal":(3.0,5.0,7.5,2.0,3), "high":(2.5,4.0,6.0,2.5,3)},
    5: {"low":(2.8,4.5,6.5,1.6,3), "normal":(2.3,3.8,5.5,1.8,3), "high":(1.9,3.0,4.5,2.2,2)},
    4: {"low":(2.0,3.2,4.8,1.3,3), "normal":(1.7,2.8,4.2,1.5,3), "high":(1.4,2.2,0.0,1.9,2)},
    3: {"low":(1.4,2.2,3.2,1.0,2), "normal":(1.2,1.9,2.8,1.2,2), "high":(1.0,1.6,0.0,1.5,2)},
    2: {"low":(0.9,1.4,0.0,0.8,1), "normal":(0.8,1.2,0.0,0.9,1), "high":(0.7,0.0,0.0,1.0,1)},
    1: {"low":(0.7,0.0,0.0,0.7,1), "normal":(0.6,0.0,0.0,0.8,1), "high":(0.5,0.0,0.0,0.9,1)},
}
_REGIME_ADJ = {
    "STRONG_BULL":   {"tp":1.30,"sl":1.00}, "STRONG_BEAR":   {"tp":1.30,"sl":1.00},
    "TRENDING_UP":   {"tp":1.10,"sl":1.00}, "TRENDING_DOWN": {"tp":1.10,"sl":1.00},
    "NORMAL":        {"tp":1.00,"sl":1.00}, "RANGING":       {"tp":0.65,"sl":0.85},
    "VOLATILE":      {"tp":0.80,"sl":1.40},
}


def compute_tp_sl(price, df, signal, strength_score=50, htf_bias="NEUTRAL"):
    if "HOLD" in signal:
        return price*0.98, {"TP1":price*1.02,"TP2":None,"TP3":None}, "HOLD", {"cancel_reason":"HOLD","rr_ratio":0}

    last   = df.iloc[-1]
    atr    = float(last["ATR"])
    atp    = float(last["ATR_Percentile"])
    regime, _ = classify_regime(df)
    mp, mp_lbl, mp_tier, _ = market_power(df, htf_bias, strength_score, signal)

    vz = "low" if atp<30 else "high" if atp>70 else "normal"
    tp1_m, tp2_m, tp3_m, sl_m, tp_count = _TP_TABLE[mp_tier][vz]
    radj   = _REGIME_ADJ.get(regime, {"tp":1.0,"sl":1.0})
    tp1_m *= radj["tp"]; tp2_m *= radj["tp"]; tp3_m *= radj["tp"]; sl_m *= radj["sl"]
    if regime == "RANGING": tp_count = 1

    d   = 1 if "BUY" in signal else -1
    tp1 = price + d * atr * tp1_m
    tp2 = (price + d * atr * tp2_m) if tp_count>=2 and tp2_m>0 else None
    tp3 = (price + d * atr * tp3_m) if tp_count>=3 and tp3_m>0 else None
    sl  = price - d * atr * sl_m

    sup, res = find_sr(df)
    if "BUY" in signal:
        if tp1>res: tp1=res*0.997
        if tp2 and tp2>res: tp2=res*0.997
        if sl<sup:  sl=sup*1.003
    else:
        if tp1<sup: tp1=sup*1.003
        if tp2 and tp2<sup: tp2=sup*1.003
        if sl>res:  sl=res*0.997

    if abs(tp1-price) < atr * 0.5:
        tp1 = price + d * atr * 0.5

    if "BUY"  in signal and tp1 <= price:
        return sl, {"TP1":tp1,"TP2":None,"TP3":None}, "HOLD", {"cancel_reason":"TP1≤entry","rr_ratio":0}
    if "SELL" in signal and tp1 >= price:
        return sl, {"TP1":tp1,"TP2":None,"TP3":None}, "HOLD", {"cancel_reason":"TP1≥entry","rr_ratio":0}

    tp1_d = abs(tp1-price); sl_d = abs(sl-price)
    rr    = round(tp1_d / max(sl_d, 1e-10), 2)
    min_rr = (MIN_RISK_REWARD if mp_tier>=4 else max(1.2,MIN_RISK_REWARD*0.80) if mp_tier==3 else
              max(1.0,MIN_RISK_REWARD*0.65) if mp_tier==2 else max(0.8,MIN_RISK_REWARD*0.50))

    if rr < min_rr:
        return sl, {"TP1":round(tp1,6),"TP2":None,"TP3":None}, "HOLD", \
               {"cancel_reason":f"R:R {rr:.2f} < {min_rr:.1f}","rr_ratio":rr}

    def pct(t): return round(abs(t-price)/price*100, 2)
    tp_levels = {"TP1":round(tp1,6), "TP2":round(tp2,6) if tp2 else None, "TP3":round(tp3,6) if tp3 else None}
    info = {
        "market_power": mp, "power_label": mp_lbl, "power_tier": mp_tier,
        "regime": regime, "rr_ratio": rr, "min_rr_used": min_rr,
        "tp1_pct": pct(tp1), "tp2_pct": pct(tp2) if tp2 else None,
        "tp3_pct": pct(tp3) if tp3 else None,
        "sl_pct": round(sl_d/price*100, 2), "nearest_support": sup,
        "nearest_resistance": res, "cancel_reason": "None — valid ✓",
        "tp1_m": round(tp1_m,2), "sl_m": round(sl_m,2), "atr": round(atr,6),
    }
    return round(sl,6), tp_levels, regime, info


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                       CONFIDENCE + POSITION                             ║
# ╚══════════════════════════════════════════════════════════════════════════╝

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
        elif htf_bias == "NEUTRAL": pts += 1
    if mp >= 70: pts += 2
    elif mp >= 50: pts += 1
    if whale >= 7.5: pts += 1
    if struct_conf >= 75: pts += 1
    if   pts >= 12: return "A+", "Supreme setup"
    elif pts >= 9:  return "A",  "Premium confidence"
    elif pts >= 7:  return "B",  "Good — above average"
    elif pts >= 4:  return "C",  "Moderate — trade with caution"
    else:           return "D",  "Weak — consider skipping"


def position_size(entry, sl, balance=ACCOUNT_BALANCE, risk_pct=RISK_PER_TRADE,
                  tier="B", mp=50, whale=5.0):
    tier_m  = {"A+":1.0,"A":1.0,"B":0.75,"C":0.5,"D":0.25}
    pow_m   = round(max(0.5, min(1.0, mp/100)), 3)
    whl_m   = round(max(0.85, min(1.15, 0.85 + (whale/10)*WHALE_SIZE_WEIGHT*2)), 3)
    adj     = risk_pct * tier_m.get(tier, 0.5) * pow_m * whl_m
    sl_dist = abs(entry - sl) / max(entry, 1e-10)
    if sl_dist < 1e-6:
        return {"error": "SL too close to entry"}
    risk_amt = balance * adj
    pos_usdt = risk_amt / sl_dist
    pos_unit = pos_usdt / max(entry, 1e-10)
    return {
        "balance": round(balance,2), "risk_pct": round(adj*100,3),
        "risk_amt": round(risk_amt,2), "pos_usdt": round(pos_usdt,2),
        "pos_units": round(pos_unit,6), "entry": round(entry,6),
        "sl": round(sl,6), "sl_dist": round(sl_dist*100,2),
        "pow_mult": pow_m, "whl_mult": whl_m,
    }


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                            BOT CORE                                     ║
# ╚══════════════════════════════════════════════════════════════════════════╝

_engine = MarketDataEngine(workers=5)


def run_analysis(symbol=DEFAULT_COIN):
    wt     = WhaleTracker(_engine.pool)
    logs   = []

    def log(msg):
        logs.append(msg)
        print(msg)

    # 1. Fetch 1H
    log(f"[1] Fetching {symbol} 1H data...")
    df1h = _engine.fetch(symbol, "1h", timeout=15, need=2)
    if df1h.empty or len(df1h) < 60:
        raise ValueError("Insufficient 1H candles")

    # 2. Fetch 4H
    df4h = None
    htf_bias = "NEUTRAL"; htf_desc = "Unavailable"
    try:
        log("[2] Fetching 4H HTF data...")
        df4h = _engine.fetch(symbol, "4h", timeout=12, need=1)
        df4h = compute_indicators(df4h)
        htf_bias, htf_desc = get_htf_bias(df4h)
    except Exception as e:
        log(f"[2] 4H failed: {e}")

    # 3. Indicators
    log("[3] Computing indicators...")
    df1h = compute_indicators(df1h)

    # 4. Patterns + divergences
    log("[4] Detecting patterns and divergences...")
    patterns              = detect_patterns(df1h)
    bull_div, bear_div    = detect_divergences(df1h)

    # 5. Structure
    log("[5] Analyzing market structure...")
    structure = analyze_structure(df1h)

    # 6. Whale
    current_price = float(df1h["close"].iloc[-1])
    log("[6] Running whale tracker...")
    ob_res = wt.analyze_ob(symbol, current_price)
    wc_res = wt.detect_whales(df1h)

    # 7. Provisional signal for whale direction
    sig_pre, _, _, _ = generate_signal(
        df1h, 0.0, htf_bias=htf_bias, patterns=patterns,
        bull_div=bull_div, bear_div=bear_div, whale_score=5.0, structure=structure)

    # 8. Whale score
    whale_score, whale_label, whale_notes = wt.score(ob_res, wc_res, sig_pre)

    # 9. Strength
    log("[7] Computing strength score...")
    strength, s_lbl, strength_comps = compute_strength(
        df1h, patterns=patterns, bull_div=bull_div, bear_div=bear_div,
        htf_bias=htf_bias, whale_score=whale_score, structure=structure)

    # 10. Final signal
    log("[8] Generating final signal...")
    signal, active, w_score, sig_reason = generate_signal(
        df1h, 0.0, htf_bias=htf_bias, patterns=patterns,
        bull_div=bull_div, bear_div=bear_div,
        whale_score=whale_score, whale_label=whale_label, structure=structure)

    # 11. TP/SL
    stop_loss, tp_levels, regime, ai = compute_tp_sl(
        current_price, df1h, signal, strength_score=strength, htf_bias=htf_bias)

    final_signal = signal
    cr = ai.get("cancel_reason","")
    if isinstance(cr, str) and "valid" not in cr and cr != "HOLD":
        final_signal = "HOLD"

    rr       = ai.get("rr_ratio", 0)
    mp_val   = ai.get("market_power", 50)
    mp_label = ai.get("power_label", "")
    mp_tier  = ai.get("power_tier", 3)

    # 12. Confidence + position
    tier, tier_desc = confidence_tier(
        w_score, strength, rr, htf_bias, final_signal,
        mp_val, whale_score, structure.get("confidence",0))
    pos = position_size(current_price, stop_loss, ACCOUNT_BALANCE, RISK_PER_TRADE,
                        tier, mp_val, whale_score)

    # 13. Price history for chart (last 100 candles)
    chart_data = df1h.tail(100)
    price_history = [
        {"t": str(row["timestamp"]), "o": round(float(row["open"]),6),
         "h": round(float(row["high"]),6), "l": round(float(row["low"]),6),
         "c": round(float(row["close"]),6), "v": round(float(row["volume"]),2),
         "ema9": round(float(row["EMA_9"]),6), "ema50": round(float(row["EMA_50"]),6)}
        for _, row in chart_data.iterrows()
    ]

    last = df1h.iloc[-1]
    return {
        "symbol":        symbol,
        "timestamp":     datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "price":         round(current_price, 6),
        "signal":        final_signal,
        "tier":          tier,
        "tier_desc":     tier_desc,
        "sig_reason":    sig_reason,
        "active_factors": active,
        "w_score":       round(w_score, 2),
        # Market Power
        "market_power":  mp_val,
        "power_label":   mp_label,
        "power_tier":    mp_tier,
        "regime":        regime,
        # Structure
        "structure":     structure,
        # 4H
        "htf_bias":      htf_bias,
        "htf_desc":      htf_desc,
        # Indicators
        "rsi":           round(float(last["RSI_14"]), 2),
        "rsi_lo":        round(float(last["Dynamic_RSI_Lower"]), 1),
        "rsi_hi":        round(float(last["Dynamic_RSI_Upper"]), 1),
        "adx":           round(float(last["ADX"]), 1),
        "adx_pos":       round(float(last["ADX_Pos"]), 1),
        "adx_neg":       round(float(last["ADX_Neg"]), 1),
        "macd":          round(float(last["MACD"]), 6),
        "macd_signal":   round(float(last["MACD_Signal"]), 6),
        "macd_hist":     round(float(last["MACD_Hist"]), 6),
        "stoch_k":       round(float(last["Stoch_K"]), 1),
        "stoch_d":       round(float(last["Stoch_D"]), 1),
        "cci":           round(float(last["CCI"]), 1),
        "williams_r":    round(float(last["Williams_R"]), 1),
        "ema9":          round(float(last["EMA_9"]), 6),
        "ema50":         round(float(last["EMA_50"]), 6),
        "ema200":        round(float(last["EMA_200"]), 6),
        "atr":           round(float(last["ATR"]), 6),
        "atr_pct":       round(float(last["ATR_Percentile"]), 1),
        "bb_width":      round(float(last["BB_Width"]), 4),
        "vol_pct":       round(float(last["Volume_Percentile"]) if "Volume_Percentile" in last.index else 50, 1),
        "vol_ratio":     round(float(last["Volume_Ratio"]), 2),
        "st_direction":  int(last["ST_Direction"]),
        "cvd_20":        round(float(df1h["CVD_20"].iloc[-1]) if "CVD_20" in df1h.columns else 0, 2),
        # Patterns
        "patterns":      {k: v for k, v in patterns.items() if v},
        "bull_div":      bull_div,
        "bear_div":      bear_div,
        # Whale
        "whale_score":   whale_score,
        "whale_label":   whale_label,
        "whale_notes":   whale_notes,
        "ob":            ob_res,
        "wc":            wc_res,
        # Strength
        "strength":      strength,
        "strength_label":s_lbl,
        # TP/SL
        "stop_loss":     stop_loss,
        "tp_levels":     tp_levels,
        "rr":            rr,
        "ai":            ai,
        # Position
        "position":      pos,
        # Chart
        "price_history": price_history,
        "logs":          logs,
        "error":         None,
    }


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                         HTML DASHBOARD                                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CRYPTO BOT v8 · Pro Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Syne:wght@400;600;800&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
:root{
  --bg:#060810;--surface:#0b0f1a;--surface2:#111827;--surface3:#1a2235;
  --border:#1f2d47;--border2:#2a3f5f;
  --green:#00e5a0;--green2:#00ff88;--red:#ff3b6b;--red2:#ff6b9d;
  --blue:#4fa3ff;--blue2:#7bbfff;--yellow:#ffd166;--purple:#c77dff;
  --text:#e8f0fe;--text2:#8fa6c8;--text3:#4a6080;
  --font-mono:'Space Mono',monospace;--font-sans:'Syne',sans-serif;
}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--text);font-family:var(--font-mono);min-height:100vh;overflow-x:hidden}

/* Scan line overlay */
body::before{content:'';position:fixed;inset:0;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,229,160,.015) 2px,rgba(0,229,160,.015) 4px);pointer-events:none;z-index:9999}

/* ── Top Bar ── */
.topbar{display:flex;align-items:center;justify-content:space-between;padding:16px 28px;border-bottom:1px solid var(--border);background:rgba(6,8,16,.9);position:sticky;top:0;z-index:100;backdrop-filter:blur(10px)}
.logo{font-family:var(--font-sans);font-weight:800;font-size:1.1rem;letter-spacing:.15em;text-transform:uppercase}
.logo span{color:var(--green)}
.topbar-right{display:flex;align-items:center;gap:16px}
.live-dot{width:8px;height:8px;border-radius:50%;background:var(--green);box-shadow:0 0 8px var(--green);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.5;transform:scale(.8)}}
.timestamp{font-size:.7rem;color:var(--text3);letter-spacing:.05em}

/* ── Search ── */
.search-bar{padding:20px 28px;display:flex;gap:12px;align-items:center;border-bottom:1px solid var(--border)}
.search-bar input{background:var(--surface2);border:1px solid var(--border);color:var(--text);font-family:var(--font-mono);font-size:.85rem;padding:10px 16px;border-radius:6px;flex:1;outline:none;transition:border .2s;text-transform:uppercase;letter-spacing:.1em}
.search-bar input:focus{border-color:var(--green);box-shadow:0 0 0 2px rgba(0,229,160,.1)}
.btn{background:var(--green);color:#000;font-family:var(--font-sans);font-weight:700;font-size:.8rem;padding:10px 24px;border:none;border-radius:6px;cursor:pointer;letter-spacing:.1em;text-transform:uppercase;transition:all .2s;white-space:nowrap}
.btn:hover{background:var(--green2);transform:translateY(-1px);box-shadow:0 4px 20px rgba(0,229,160,.3)}
.btn:active{transform:translateY(0)}
.btn:disabled{opacity:.5;cursor:not-allowed;transform:none}
.btn-pair{display:flex;gap:8px;flex-shrink:0}
.btn-sm{font-size:.72rem;padding:10px 16px}

/* ── Main Grid ── */
.grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;padding:20px 28px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:20px;position:relative;overflow:hidden;transition:border .2s}
.card:hover{border-color:var(--border2)}
.card::before{content:'';position:absolute;inset:0;background:linear-gradient(135deg,rgba(255,255,255,.02),transparent);pointer-events:none}
.card-label{font-size:.65rem;letter-spacing:.2em;text-transform:uppercase;color:var(--text3);margin-bottom:8px;font-family:var(--font-sans);font-weight:600}
.card-value{font-size:1.8rem;font-weight:700;font-family:var(--font-sans);line-height:1}
.card-sub{font-size:.72rem;color:var(--text2);margin-top:6px}
.col-span2{grid-column:span 2}
.col-span3{grid-column:span 3}

/* Signal Card */
.signal-card{background:linear-gradient(135deg,var(--surface),var(--surface2));border-width:2px}
.signal-card.buy{border-color:var(--green);box-shadow:0 0 30px rgba(0,229,160,.1)}
.signal-card.sell{border-color:var(--red);box-shadow:0 0 30px rgba(255,59,107,.1)}
.signal-card.hold{border-color:var(--yellow);box-shadow:0 0 30px rgba(255,209,102,.1)}
.signal-text{font-size:2.4rem;font-weight:800;font-family:var(--font-sans);letter-spacing:.05em}
.signal-text.buy{color:var(--green)}
.signal-text.sell{color:var(--red)}
.signal-text.hold{color:var(--yellow)}
.tier-badge{display:inline-block;padding:4px 12px;border-radius:20px;font-size:.7rem;font-weight:700;font-family:var(--font-sans);letter-spacing:.1em;margin-top:8px}
.tier-badge.Aplus,.tier-badge.A{background:rgba(0,229,160,.15);color:var(--green);border:1px solid var(--green)}
.tier-badge.B{background:rgba(79,163,255,.15);color:var(--blue);border:1px solid var(--blue)}
.tier-badge.C{background:rgba(255,209,102,.15);color:var(--yellow);border:1px solid var(--yellow)}
.tier-badge.D{background:rgba(255,59,107,.15);color:var(--red);border:1px solid var(--red)}

/* Gauge */
.gauge-wrap{position:relative;width:120px;height:65px;margin:8px auto 0}
.gauge-svg{width:120px;height:65px}

/* TP/SL Block */
.tp-row{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid var(--border)}
.tp-row:last-child{border:none}
.tp-label{font-size:.68rem;color:var(--text3);font-family:var(--font-sans);font-weight:600;letter-spacing:.1em}
.tp-val{font-size:.82rem;font-weight:700}
.tp-val.green{color:var(--green)}
.tp-val.red{color:var(--red)}
.tp-val.dim{color:var(--text3)}

/* Indicator Grid */
.ind-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.ind-item{background:var(--surface2);border-radius:8px;padding:12px}
.ind-name{font-size:.6rem;letter-spacing:.15em;text-transform:uppercase;color:var(--text3);font-family:var(--font-sans);font-weight:600;margin-bottom:4px}
.ind-val{font-size:1rem;font-weight:700}

/* Bar indicators */
.bar-wrap{margin-top:4px;height:4px;background:var(--surface3);border-radius:2px;overflow:hidden}
.bar-fill{height:100%;border-radius:2px;transition:width .6s ease}

/* Whale */
.whale-score-ring{width:90px;height:90px;margin:0 auto}
.ob-bar{display:flex;height:20px;border-radius:4px;overflow:hidden;margin:8px 0;gap:2px}
.ob-bid{background:rgba(0,229,160,.4)}
.ob-ask{background:rgba(255,59,107,.4)}

/* Structure */
.struct-badges{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
.struct-badge{padding:3px 10px;border-radius:4px;font-size:.65rem;font-family:var(--font-sans);font-weight:700;letter-spacing:.08em}
.struct-active{background:rgba(0,229,160,.2);color:var(--green);border:1px solid rgba(0,229,160,.4)}
.struct-inactive{background:var(--surface3);color:var(--text3);border:1px solid var(--border)}

/* Chart */
.chart-container{width:100%;height:280px;position:relative}
canvas{border-radius:6px}

/* Whale candle list */
.whale-list{max-height:120px;overflow-y:auto;margin-top:8px}
.whale-list::-webkit-scrollbar{width:4px}
.whale-list::-webkit-scrollbar-track{background:var(--surface3)}
.whale-list::-webkit-scrollbar-thumb{background:var(--border2);border-radius:2px}
.wc-item{display:flex;justify-content:space-between;font-size:.68rem;padding:4px 0;border-bottom:1px solid var(--border);color:var(--text2)}
.wc-item .buy{color:var(--green)}
.wc-item .sell{color:var(--red)}

/* Notes */
.note-list{margin-top:8px}
.note-item{font-size:.68rem;color:var(--text2);padding:3px 0;border-bottom:1px solid var(--border);display:flex;align-items:flex-start;gap:6px}
.note-item::before{content:'›';color:var(--green);flex-shrink:0}

/* Factors */
.factors-wrap{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.factor-chip{background:var(--surface3);border:1px solid var(--border);padding:3px 10px;border-radius:20px;font-size:.62rem;color:var(--text2);font-family:var(--font-sans);font-weight:600;letter-spacing:.05em}
.factor-chip.active{background:rgba(0,229,160,.1);border-color:rgba(0,229,160,.3);color:var(--green)}

/* Log */
.log-box{background:var(--bg);border:1px solid var(--border);border-radius:6px;padding:12px;font-size:.68rem;color:var(--text3);max-height:100px;overflow-y:auto;font-family:var(--font-mono);line-height:1.8}
.log-box::-webkit-scrollbar{width:4px}
.log-box::-webkit-scrollbar-thumb{background:var(--border2);border-radius:2px}

/* Error banner */
.error-banner{background:rgba(255,59,107,.1);border:1px solid var(--red);border-radius:8px;padding:16px 20px;margin:20px 28px;color:var(--red);font-size:.82rem}

/* Loading overlay */
.loading{position:fixed;inset:0;background:rgba(6,8,16,.95);z-index:9998;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:20px}
.loading.hide{display:none}
.spinner{width:48px;height:48px;border:3px solid var(--border);border-top-color:var(--green);border-radius:50%;animation:spin 1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.loading-text{font-family:var(--font-sans);font-size:.85rem;color:var(--text2);letter-spacing:.15em}
.loading-log{font-size:.7rem;color:var(--text3);max-width:400px;text-align:center;line-height:1.8}

/* Position size grid */
.pos-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:4px}
.pos-item{background:var(--surface2);border-radius:6px;padding:10px 12px}
.pos-label{font-size:.58rem;letter-spacing:.15em;text-transform:uppercase;color:var(--text3);font-family:var(--font-sans);font-weight:600}
.pos-val{font-size:.85rem;font-weight:700;margin-top:2px}

/* Responsive */
@media(max-width:1100px){.grid{grid-template-columns:1fr 1fr}}
@media(max-width:680px){.grid{grid-template-columns:1fr}.col-span2,.col-span3{grid-column:span 1}.search-bar{flex-wrap:wrap}.search-bar input{min-width:0}}

/* Animate-in */
.card{animation:fadeUp .4s ease both}
@keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
.card:nth-child(1){animation-delay:.05s}.card:nth-child(2){animation-delay:.1s}.card:nth-child(3){animation-delay:.15s}
.card:nth-child(4){animation-delay:.2s}.card:nth-child(5){animation-delay:.25s}.card:nth-child(6){animation-delay:.3s}
.card:nth-child(7){animation-delay:.35s}.card:nth-child(8){animation-delay:.4s}.card:nth-child(9){animation-delay:.45s}
</style>
</head>
<body>

<!-- Loading overlay -->
<div class="loading" id="loader">
  <div class="spinner"></div>
  <div class="loading-text">ANALYZING MARKET</div>
  <div class="loading-log" id="loaderLog">Connecting to exchanges...</div>
</div>

<!-- Top bar -->
<div class="topbar">
  <div class="logo">CRYPTO <span>BOT</span> v8 · PRO</div>
  <div class="topbar-right">
    <div class="live-dot" id="liveDot"></div>
    <div class="timestamp" id="ts">—</div>
  </div>
</div>

<!-- Search bar -->
<div class="search-bar">
  <input type="text" id="symbolInput" value="BTC/USDT" placeholder="BTC/USDT" />
  <div class="btn-pair">
    <button class="btn" id="analyzeBtn" onclick="analyze()">▶ ANALYZE</button>
    <button class="btn btn-sm" style="background:transparent;color:var(--text2);border:1px solid var(--border)" onclick="autoRefresh()" id="autoBtn">AUTO</button>
  </div>
</div>

<!-- Error banner -->
<div class="error-banner" id="errBanner" style="display:none"></div>

<!-- Dashboard Grid -->
<div class="grid" id="dashboard" style="display:none">

  <!-- 1. Signal -->
  <div class="card signal-card" id="signalCard">
    <div class="card-label">Signal</div>
    <div class="signal-text" id="signalText">—</div>
    <div style="margin-top:10px">
      <span class="tier-badge" id="tierBadge">—</span>
    </div>
    <div class="card-sub" id="sigReason" style="margin-top:10px;font-size:.67rem;color:var(--text3);line-height:1.6"></div>
  </div>

  <!-- 2. Price -->
  <div class="card">
    <div class="card-label">Current Price</div>
    <div class="card-value" id="priceVal" style="font-size:1.6rem">—</div>
    <div class="card-sub" id="priceSub">—</div>
    <div style="margin-top:16px">
      <div style="display:flex;gap:20px;font-size:.72rem">
        <div><div style="color:var(--text3);font-size:.6rem;letter-spacing:.1em;font-family:var(--font-sans);font-weight:600">4H BIAS</div><div id="htfBias" style="font-weight:700">—</div></div>
        <div><div style="color:var(--text3);font-size:.6rem;letter-spacing:.1em;font-family:var(--font-sans);font-weight:600">REGIME</div><div id="regime" style="font-weight:700">—</div></div>
      </div>
    </div>
  </div>

  <!-- 3. R:R & Strength -->
  <div class="card">
    <div class="card-label">Risk : Reward</div>
    <div class="card-value" id="rrVal">—</div>
    <div class="card-sub" id="strengthVal">Strength —/100</div>
    <div style="margin-top:12px">
      <div style="font-size:.6rem;color:var(--text3);font-family:var(--font-sans);font-weight:600;letter-spacing:.1em;margin-bottom:4px">STRENGTH</div>
      <div class="bar-wrap"><div class="bar-fill" id="strengthBar" style="background:var(--green);width:0%"></div></div>
    </div>
    <div style="margin-top:8px">
      <div style="font-size:.6rem;color:var(--text3);font-family:var(--font-sans);font-weight:600;letter-spacing:.1em;margin-bottom:4px">MARKET POWER</div>
      <div class="bar-wrap"><div class="bar-fill" id="powerBar" style="background:var(--blue);width:0%"></div></div>
    </div>
  </div>

  <!-- 4. Price Chart -->
  <div class="card col-span3">
    <div class="card-label">Price Action · 1H · Last 100 Candles</div>
    <div class="chart-container">
      <canvas id="priceChart"></canvas>
    </div>
  </div>

  <!-- 5. TP/SL -->
  <div class="card">
    <div class="card-label">Adaptive TP / SL Levels</div>
    <div id="tpslBlock"></div>
    <div style="margin-top:12px;font-size:.65rem;color:var(--text3)" id="srNote"></div>
  </div>

  <!-- 6. Market Power -->
  <div class="card">
    <div class="card-label">Market Power Engine</div>
    <div style="font-size:2rem;font-weight:800;font-family:var(--font-sans)" id="mpVal">—</div>
    <div style="font-size:.75rem;color:var(--text2);margin-top:4px" id="mpLabel">—</div>
    <div style="margin-top:12px" id="mpLog"></div>
  </div>

  <!-- 7. Whale Tracker -->
  <div class="card">
    <div class="card-label">🐋 Whale Tracker</div>
    <div style="display:flex;align-items:center;gap:16px;margin-bottom:12px">
      <div>
        <div style="font-size:2rem;font-weight:800;font-family:var(--font-sans)" id="whaleScore">—</div>
        <div style="font-size:.72rem;color:var(--text2);margin-top:2px" id="whaleLabel">—</div>
      </div>
    </div>
    <div id="obBlock"></div>
    <div style="font-size:.67rem;color:var(--text3);margin-top:8px" id="cvdBlock">—</div>
    <div class="whale-list" id="whaleList"></div>
  </div>

  <!-- 8. Market Structure -->
  <div class="card col-span2">
    <div class="card-label">🏗 Market Structure</div>
    <div style="display:flex;gap:20px;align-items:flex-start;flex-wrap:wrap">
      <div>
        <div style="font-size:1.8rem;font-weight:800;font-family:var(--font-sans)" id="structType">—</div>
        <div style="font-size:.72rem;color:var(--text2)" id="structConf">—</div>
        <div class="struct-badges" id="structBadges"></div>
      </div>
      <div style="flex:1;min-width:180px">
        <div class="ind-grid" id="structGrid"></div>
      </div>
    </div>
  </div>

  <!-- 9. Indicators Part 1 -->
  <div class="card col-span2">
    <div class="card-label">Technical Indicators</div>
    <div class="ind-grid" id="indGrid"></div>
  </div>

  <!-- 10. Position Sizing -->
  <div class="card">
    <div class="card-label">💼 Position Sizing</div>
    <div class="pos-grid" id="posGrid"></div>
  </div>

  <!-- 11. Active Factors -->
  <div class="card col-span2">
    <div class="card-label">Active Signal Factors</div>
    <div class="factors-wrap" id="factorsWrap"></div>
    <div style="margin-top:16px">
      <div class="card-label">Patterns</div>
      <div class="factors-wrap" id="patternsWrap"></div>
    </div>
  </div>

  <!-- 12. Whale Notes -->
  <div class="card">
    <div class="card-label">Whale Analysis Notes</div>
    <div class="note-list" id="whaleNotes"></div>
  </div>

  <!-- 13. System Log -->
  <div class="card col-span3">
    <div class="card-label">System Log</div>
    <div class="log-box" id="sysLog">Waiting for analysis...</div>
  </div>

</div><!-- /grid -->

<script>
let priceChart = null;
let autoTimer  = null;
let autoActive = false;
const FACTORS_ALL = ['macd_cross','ema_align','adx_bull','adx_bear','rsi_zone','stoch_bull','stoch_bear','vol_spike','supertrend','vwap_above','vwap_below','bull_pat','bear_pat','bull_div','bear_div','htf_bull','htf_bear','cvd_bull','cvd_bear','lstm_bull','lstm_bear'];

function colorCls(signal){
  if(!signal) return 'hold';
  if(signal.includes('BUY')) return 'buy';
  if(signal.includes('SELL')) return 'sell';
  return 'hold';
}

function colorHex(signal){
  const c = colorCls(signal);
  return c==='buy'?'#00e5a0':c==='sell'?'#ff3b6b':'#ffd166';
}

function fmt(n,d=6){ return n==null?'—':parseFloat(n).toFixed(d); }

function buildGauge(pct, color){
  const r=50, cx=60, cy=60;
  const a = Math.PI * pct;
  const ex = cx - r * Math.cos(a), ey = cy - r * Math.sin(a);
  const laf = a > Math.PI ? 1 : 0;
  return `<svg width="120" height="70" viewBox="0 0 120 70">
    <path d="M10,60 A50,50 0 0,1 110,60" fill="none" stroke="#1f2d47" stroke-width="8" stroke-linecap="round"/>
    <path d="M10,60 A50,50 0 0,1 ${ex},${ey}" fill="none" stroke="${color}" stroke-width="8" stroke-linecap="round"/>
    <text x="60" y="52" text-anchor="middle" fill="${color}" font-size="18" font-weight="700" font-family="Syne">${Math.round(pct*100)}</text>
  </svg>`;
}

function renderDashboard(d){
  document.getElementById('dashboard').style.display='grid';
  document.getElementById('ts').textContent = d.timestamp || '—';
  document.getElementById('errBanner').style.display='none';

  // Signal card
  const sc = document.getElementById('signalCard');
  sc.className = 'card signal-card ' + colorCls(d.signal);
  const st = document.getElementById('signalText');
  st.textContent = d.signal || 'HOLD';
  st.className = 'signal-text ' + colorCls(d.signal);
  const tb = document.getElementById('tierBadge');
  const tierKey = (d.tier||'D').replace('+','plus');
  tb.className = 'tier-badge ' + tierKey;
  tb.textContent = 'Grade ' + (d.tier||'D') + ' · ' + (d.tier_desc||'');
  document.getElementById('sigReason').textContent = d.sig_reason || '';

  // Price
  const sigColor = colorHex(d.signal);
  document.getElementById('priceVal').textContent = fmt(d.price,4) + ' USDT';
  document.getElementById('priceVal').style.color = sigColor;
  document.getElementById('priceSub').textContent = (d.symbol||'') + ' · ' + (d.ai?.regime||d.regime||'');
  const htfEl = document.getElementById('htfBias');
  htfEl.textContent = d.htf_bias||'—';
  htfEl.style.color = d.htf_bias==='BULL'?'#00e5a0':d.htf_bias==='BEAR'?'#ff3b6b':'#ffd166';
  document.getElementById('regime').textContent = d.regime||'—';

  // R:R & Strength
  document.getElementById('rrVal').innerHTML = '<span style="color:' + (d.rr>=2?'#00e5a0':d.rr>=1.5?'#ffd166':'#ff3b6b') + '">1 : ' + fmt(d.rr,2) + '</span>';
  document.getElementById('strengthVal').textContent = 'Strength ' + fmt(d.strength,0) + '/100 · ' + (d.strength_label||'');
  document.getElementById('strengthBar').style.width = (d.strength||0) + '%';
  const mp = d.market_power || 0;
  document.getElementById('powerBar').style.width = mp + '%';
  document.getElementById('powerBar').style.background = mp>=70?'#00e5a0':mp>=40?'#4fa3ff':'#ff3b6b';

  // TP/SL
  const tp = d.tp_levels||{}; const ai = d.ai||{};
  const sl = d.stop_loss;
  let tpHtml = '';
  const isBuy = d.signal?.includes('BUY');
  tpHtml += `<div class="tp-row"><span class="tp-label">ENTRY</span><span class="tp-val" style="color:#e8f0fe">${fmt(d.price,5)} USDT</span></div>`;
  tpHtml += `<div class="tp-row"><span class="tp-label">STOP LOSS</span><span class="tp-val red">${fmt(sl,5)} <span style="font-size:.62rem;color:#ff6b9d">(-${ai.sl_pct||'?'}%)</span></span></div>`;
  if(tp.TP1) tpHtml += `<div class="tp-row"><span class="tp-label">TP1</span><span class="tp-val green">${fmt(tp.TP1,5)} <span style="font-size:.62rem;color:#00ff88">(+${ai.tp1_pct||'?'}%)</span></span></div>`;
  if(tp.TP2) tpHtml += `<div class="tp-row"><span class="tp-label">TP2</span><span class="tp-val green">${fmt(tp.TP2,5)} <span style="font-size:.62rem;color:#7ee787">(+${ai.tp2_pct||'?'}%)</span></span></div>`;
  if(tp.TP3) tpHtml += `<div class="tp-row"><span class="tp-label">TP3</span><span class="tp-val" style="color:#56d364">${fmt(tp.TP3,5)} <span style="font-size:.62rem;color:#56d364">(+${ai.tp3_pct||'?'}%)</span></span></div>`;
  if(!tp.TP1 && d.signal==='HOLD') tpHtml += `<div class="tp-row" style="justify-content:center;color:#ffd166;font-size:.78rem;font-family:Syne;font-weight:700">⏸ HOLD — NO ENTRY</div>`;
  document.getElementById('tpslBlock').innerHTML = tpHtml;
  document.getElementById('srNote').textContent = ai.cancel_reason && !ai.cancel_reason.includes('valid') ? '⚠ '+ai.cancel_reason : '✓ '+((d.ai?.nearest_support?'S:'+fmt(d.ai.nearest_support,4):'')||'');

  // Market Power
  document.getElementById('mpVal').textContent = fmt(mp,0) + '/100';
  document.getElementById('mpVal').style.color = mp>=70?'#00e5a0':mp>=40?'#4fa3ff':'#ff3b6b';
  document.getElementById('mpLabel').textContent = (d.power_label||'') + ' · Tier ' + (d.power_tier||'?') + ' of 6';
  document.getElementById('mpLog').innerHTML = buildGauge(mp/100, mp>=70?'#00e5a0':mp>=40?'#4fa3ff':'#ff3b6b');

  // Whale
  const ws = d.whale_score||0;
  const whaleColor = ws>=7.5?'#00e5a0':ws>=5?'#ffd166':ws>=3?'#f0883e':'#ff3b6b';
  document.getElementById('whaleScore').textContent = fmt(ws,1) + '/10';
  document.getElementById('whaleScore').style.color = whaleColor;
  document.getElementById('whaleLabel').textContent = d.whale_label||'—';
  const ob = d.ob||{};
  const total = Math.max(ob.bid_usdt||0, 1) + Math.max(ob.ask_usdt||0, 1);
  const bidW = Math.round((ob.bid_usdt||0)/total*100);
  const askW = 100 - bidW;
  document.getElementById('obBlock').innerHTML = `
    <div style="font-size:.62rem;color:var(--text3);font-family:Syne;font-weight:600;letter-spacing:.1em;margin-bottom:4px">ORDER BOOK</div>
    <div class="ob-bar"><div class="ob-bid" style="width:${bidW}%"></div><div class="ob-ask" style="width:${askW}%"></div></div>
    <div style="display:flex;justify-content:space-between;font-size:.65rem;color:var(--text2)">
      <span style="color:#00e5a0">BID $${(ob.bid_usdt||0).toLocaleString()}</span>
      <span style="color:#ff3b6b">ASK $${(ob.ask_usdt||0).toLocaleString()}</span>
    </div>`;
  const wc = d.wc||{};
  document.getElementById('cvdBlock').textContent = `CVD: ${wc.cvd_trend||'N/A'} (${((wc.cvd_ratio||0.5)*100).toFixed(0)}% bull vol)  ·  Whales detected: ${wc.total_detected||0}`;
  const wList = (wc.whale_candles||[]).slice(-5).reverse();
  document.getElementById('whaleList').innerHTML = wList.length
    ? wList.map(w=>`<div class="wc-item"><span class="${w.direction.toLowerCase()}">${w.direction}</span><span>${w.type}</span><span>${w.vol_ratio}× vol</span><span>${w.price_move}%</span></div>`).join('')
    : '<div style="font-size:.68rem;color:var(--text3);padding:6px 0">No whale candles in last 50 bars</div>';

  // Structure
  const st2 = d.structure||{};
  const sColor = ['UPTREND','BREAKOUT'].includes(st2.type)?'#00e5a0':['DOWNTREND','BREAKDOWN'].includes(st2.type)?'#ff3b6b':'#ffd166';
  document.getElementById('structType').textContent = st2.type||'—';
  document.getElementById('structType').style.color = sColor;
  document.getElementById('structConf').textContent = `Confidence: ${st2.confidence||0}%  ·  ${st2.swing_highs||0} swing highs  ·  ${st2.swing_lows||0} swing lows`;
  const sbadges = ['UPTREND','DOWNTREND','BREAKOUT','BREAKDOWN','RANGING'];
  document.getElementById('structBadges').innerHTML = sbadges.map(b=>`<span class="struct-badge ${b===st2.type?'struct-active':'struct-inactive'}">${b}</span>`).join('');
  document.getElementById('structGrid').innerHTML = [
    ['HH',st2.hh],['HL',st2.hl],['LH',st2.lh],['LL',st2.ll],
    ['Breakout',st2.breakout],['Breakdown',st2.breakdown]
  ].map(([k,v])=>`<div class="ind-item"><div class="ind-name">${k}</div><div class="ind-val" style="color:${v?'#00e5a0':'#4a6080'}">${v?'YES':'NO'}</div></div>`).join('');

  // Indicators
  const indData = [
    {n:'RSI 14',   v:fmt(d.rsi,1),      bar:d.rsi,       max:100, color:d.rsi<40?'#00e5a0':d.rsi>60?'#ff3b6b':'#4fa3ff'},
    {n:'ADX',      v:fmt(d.adx,1),      bar:d.adx,       max:80,  color:d.adx>30?'#00e5a0':d.adx>20?'#ffd166':'#ff3b6b'},
    {n:'Stoch %K', v:fmt(d.stoch_k,1),  bar:d.stoch_k,   max:100, color:d.stoch_k<25?'#00e5a0':d.stoch_k>75?'#ff3b6b':'#4fa3ff'},
    {n:'Stoch %D', v:fmt(d.stoch_d,1),  bar:d.stoch_d,   max:100, color:'#8fa6c8'},
    {n:'CCI',      v:fmt(d.cci,1),      bar:Math.min(Math.max(d.cci||0,-200),200)+200, max:400, color:d.cci>100?'#00e5a0':d.cci<-100?'#ff3b6b':'#4fa3ff'},
    {n:'Williams%R',v:fmt(d.williams_r,1),bar:(d.williams_r||0)+100,max:100,color:d.williams_r<-80?'#00e5a0':d.williams_r>-20?'#ff3b6b':'#4fa3ff'},
    {n:'Vol Pct',  v:fmt(d.vol_pct,0)+'th',bar:d.vol_pct,max:100, color:d.vol_pct>=75?'#c77dff':d.vol_pct>=50?'#4fa3ff':'#4a6080'},
    {n:'ATR Pct',  v:fmt(d.atr_pct,0)+'th',bar:d.atr_pct,max:100, color:d.atr_pct>70?'#ff3b6b':d.atr_pct<30?'#00e5a0':'#ffd166'},
  ];
  document.getElementById('indGrid').innerHTML = indData.map(i=>`
    <div class="ind-item">
      <div class="ind-name">${i.n}</div>
      <div class="ind-val" style="color:${i.color}">${i.v}</div>
      <div class="bar-wrap"><div class="bar-fill" style="width:${Math.min(100,(i.bar||0)/i.max*100)}%;background:${i.color}"></div></div>
    </div>`).join('');

  // Position sizing
  const pos = d.position||{};
  document.getElementById('posGrid').innerHTML = [
    {l:'Balance',v:'$'+(pos.balance||0).toLocaleString()+' USDT'},
    {l:'Risk %',v:(pos.risk_pct||0)+'%'},
    {l:'Risk Amount',v:'$'+(pos.risk_amt||0).toLocaleString()},
    {l:'Position',v:'$'+(pos.pos_usdt||0).toLocaleString()},
    {l:'SL Distance',v:(pos.sl_dist||0)+'%'},
    {l:'Multipliers',v:'Pwr:'+pos.pow_mult+'× Whl:'+pos.whl_mult+'×'},
  ].map(({l,v})=>`<div class="pos-item"><div class="pos-label">${l}</div><div class="pos-val">${v}</div></div>`).join('');

  // Factors
  const active = d.active_factors||[];
  document.getElementById('factorsWrap').innerHTML = FACTORS_ALL.map(f=>`<span class="factor-chip ${active.includes(f)?'active':''}">${f.replace(/_/g,' ')}</span>`).join('');

  // Patterns
  const pats = Object.keys(d.patterns||{});
  document.getElementById('patternsWrap').innerHTML = pats.length
    ? pats.map(p=>`<span class="factor-chip active">${p.replace(/_/g,' ')}</span>`).join('')
    : '<span style="font-size:.68rem;color:var(--text3)">No patterns detected</span>';
  if(d.bull_div) document.getElementById('patternsWrap').innerHTML += '<span class="factor-chip active">bull divergence</span>';
  if(d.bear_div) document.getElementById('patternsWrap').innerHTML += '<span class="factor-chip active">bear divergence</span>';

  // Whale notes
  document.getElementById('whaleNotes').innerHTML = (d.whale_notes||[]).map(n=>`<div class="note-item">${n}</div>`).join('') || '<div class="note-item">No notes</div>';

  // System log
  document.getElementById('sysLog').textContent = (d.logs||[]).join('\n') || 'Analysis complete.';

  // Price Chart
  renderChart(d);
}

function renderChart(d){
  const hist = d.price_history||[];
  if(!hist.length) return;
  const labels = hist.map(h=>h.t.replace('T',' ').substring(5,16));
  const closes = hist.map(h=>h.c);
  const ema9   = hist.map(h=>h.ema9);
  const ema50  = hist.map(h=>h.ema50);
  const sigColor = colorHex(d.signal);

  if(priceChart){ priceChart.destroy(); priceChart=null; }
  const ctx = document.getElementById('priceChart').getContext('2d');
  priceChart = new Chart(ctx, {
    type:'line',
    data:{
      labels,
      datasets:[
        {label:'Price', data:closes, borderColor:sigColor, borderWidth:2, pointRadius:0, tension:0.3,
         fill:'origin', backgroundColor:(ctx2=>{
           const g=ctx2.chart.ctx.createLinearGradient(0,0,0,280);
           g.addColorStop(0,sigColor+'33'); g.addColorStop(1,sigColor+'00'); return g;
         })},
        {label:'EMA9', data:ema9, borderColor:'#f0883e', borderWidth:1.5, pointRadius:0, tension:0.3, borderDash:[4,2]},
        {label:'EMA50',data:ema50,borderColor:'#bc8cff', borderWidth:1.5, pointRadius:0, tension:0.3, borderDash:[6,3]},
      ]
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      animation:{duration:600,easing:'easeInOutQuart'},
      plugins:{legend:{labels:{color:'#8fa6c8',font:{family:'Space Mono',size:10},boxWidth:20}},tooltip:{mode:'index',intersect:false,backgroundColor:'#0b0f1a',borderColor:'#1f2d47',borderWidth:1,titleColor:'#e8f0fe',bodyColor:'#8fa6c8',titleFont:{family:'Space Mono'}}},
      scales:{
        x:{ticks:{color:'#4a6080',font:{family:'Space Mono',size:9},maxRotation:0,maxTicksLimit:12},grid:{color:'#0f1825'}},
        y:{ticks:{color:'#4a6080',font:{family:'Space Mono',size:9}},grid:{color:'#0f1825'}}
      },
      interaction:{mode:'nearest',axis:'x',intersect:false}
    }
  });

  // Add horizontal TP/SL lines as annotations via afterDraw
  const slVal = d.stop_loss;
  const tp1   = d.tp_levels?.TP1;
  const tp2   = d.tp_levels?.TP2;
  priceChart.data.annotations = [];
  const origDraw = priceChart.draw?.bind(priceChart);
  const origAfterDraw = ()=>{
    const chart = priceChart;
    const {ctx:c, scales:{y, x}} = chart;
    const drawLine = (val, color, label)=>{
      if(!val) return;
      const yPx = y.getPixelForValue(val);
      if(yPx<chart.chartArea.top || yPx>chart.chartArea.bottom) return;
      c.save(); c.strokeStyle=color; c.lineWidth=1.2; c.setLineDash([6,4]);
      c.beginPath(); c.moveTo(chart.chartArea.left, yPx); c.lineTo(chart.chartArea.right, yPx); c.stroke();
      c.fillStyle=color; c.font='700 9px Space Mono'; c.textAlign='right';
      c.fillText(label+' '+val.toFixed(4), chart.chartArea.right-4, yPx-4); c.restore(); c.setLineDash([]);
    };
    drawLine(slVal, '#ff3b6b','SL');
    drawLine(tp1,   '#00e5a0','TP1');
    drawLine(tp2,   '#7ee787','TP2');
  };
  Chart.register({id:'tpsl',afterDraw: origAfterDraw});
}

async function analyze(){
  const symbol = document.getElementById('symbolInput').value.trim().toUpperCase()||'BTC/USDT';
  const btn = document.getElementById('analyzeBtn');
  btn.disabled=true; btn.textContent='⟳ ANALYZING';
  document.getElementById('loader').classList.remove('hide');
  document.getElementById('loaderLog').textContent = 'Connecting to exchanges for ' + symbol + '...';
  document.getElementById('errBanner').style.display='none';

  try {
    const resp = await fetch('/api/analyze?symbol=' + encodeURIComponent(symbol));
    const d    = await resp.json();
    document.getElementById('loader').classList.add('hide');
    if(d.error){
      document.getElementById('errBanner').style.display='block';
      document.getElementById('errBanner').textContent = '⚠ Error: ' + d.error;
      document.getElementById('dashboard').style.display='none';
    } else {
      renderDashboard(d);
    }
  } catch(e){
    document.getElementById('loader').classList.add('hide');
    document.getElementById('errBanner').style.display='block';
    document.getElementById('errBanner').textContent = '⚠ Network error: ' + e.message;
  }
  btn.disabled=false; btn.textContent='▶ ANALYZE';
}

function autoRefresh(){
  const btn = document.getElementById('autoBtn');
  if(autoActive){
    clearInterval(autoTimer); autoActive=false;
    btn.style.color='var(--text2)'; btn.textContent='AUTO';
  } else {
    autoActive=true;
    btn.style.color='#00e5a0'; btn.textContent='AUTO ✓';
    analyze();
    autoTimer = setInterval(analyze, 5 * 60 * 1000); // every 5 min
  }
}

// Symbol input → Enter key
document.getElementById('symbolInput').addEventListener('keydown', e=>{
  if(e.key==='Enter') analyze();
});

// Load on start
window.addEventListener('load', ()=>{
  // Preload common coins as chips
  const coins = ['BTC/USDT','ETH/USDT','BNB/USDT','SOL/USDT','OP/USDT','ARB/USDT','AVAX/USDT'];
  const inp = document.getElementById('symbolInput');
  // Quick-select row
  const bar = document.getElementById('symbolInput').parentNode;
  const quickRow = document.createElement('div');
  quickRow.style.cssText='width:100%;display:flex;flex-wrap:wrap;gap:6px;padding:10px 0 0';
  quickRow.innerHTML = coins.map(c=>`<button onclick="document.getElementById('symbolInput').value='${c}';analyze()" style="background:var(--surface3);border:1px solid var(--border);color:var(--text2);font-family:Space Mono;font-size:.62rem;padding:5px 12px;border-radius:20px;cursor:pointer;letter-spacing:.05em;transition:all .2s" onmouseover="this.style.borderColor='#00e5a0';this.style.color='#00e5a0'" onmouseout="this.style.borderColor='var(--border)';this.style.color='var(--text2)'">${c}</button>`).join('');
  bar.appendChild(quickRow);
  // Auto-analyze BTC
  analyze();
});
</script>
</body>
</html>"""


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                            FLASK ROUTES                                 ║
# ╚══════════════════════════════════════════════════════════════════════════╝

@app.route("/")
def index():
    return render_template_string(DASHBOARD_HTML)


@app.route("/api/analyze")
def api_analyze():
    symbol = request.args.get("symbol", DEFAULT_COIN).strip().upper()
    if not symbol:
        symbol = DEFAULT_COIN
    try:
        result = run_analysis(symbol)
        return jsonify(result)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e), "symbol": symbol}), 500


@app.route("/health")
def health():
    return jsonify({"status": "ok", "bot": "v8-web", "timestamp": datetime.now(timezone.utc).isoformat()})


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                              ENTRY POINT                                ║
# ╚══════════════════════════════════════════════════════════════════════════╝

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n  🚀 Crypto Bot v8-Web starting on http://0.0.0.0:{port}")
    print(f"  📊 Dashboard: http://localhost:{port}")
    print(f"  🔌 API:       http://localhost:{port}/api/analyze?symbol=BTC/USDT\n")
    app.run(host="0.0.0.0", port=port, debug=False)
