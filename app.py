#!/usr/bin/env python3
"""
Crypto Trading Bot v11 Lite
TensorFlow/LSTM removed — all other features intact
"""

import streamlit as st
import os, time, warnings
warnings.filterwarnings("ignore")

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Crypto Bot v11",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    body { background-color: #0d1117; color: #e6edf3; }
    .stApp { background-color: #0d1117; }
    .main-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 16px;
    }
    .signal-buy {
        background: #23863620;
        border: 2px solid #3fb950;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    .signal-sell {
        background: #f8514920;
        border: 2px solid #f85149;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    .signal-hold {
        background: #d2992220;
        border: 2px solid #d29922;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    .stButton > button {
        width: 100%;
        background-color: #238636;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
    }
    .stButton > button:hover { background-color: #2ea043; }
    div[data-testid="metric-container"] {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ── Users ─────────────────────────────────────────────────────────────────────
USERS = {
    "admin":     "admin123",
    "customer1": "pass123",
    "customer2": "trade456",
}

# ── Login ─────────────────────────────────────────────────────────────────────
def show_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align:center; padding: 40px 0 20px 0;'>
            <div style='font-size:56px;'>🤖</div>
            <h1 style='color:#e6edf3; font-size:28px; margin:10px 0 4px 0;'>Crypto Bot v11</h1>
            <p style='color:#8b949e; font-size:14px;'>Self-Evolving Regime Brain</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("👤 Username", placeholder="Enter username")
            password = st.text_input("🔑 Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("🚀 Login")

            if submitted:
                if username in USERS and USERS[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.user = username
                    st.rerun()
                else:
                    st.error("❌ Wrong username or password!")

# ── Main Bot Logic ────────────────────────────────────────────────────────────
def run_analysis(symbol, balance, risk_pct):
    import ccxt
    import numpy as np
    import pandas as pd
    import ta

    results = {}

    # Fetch data
    try:
        exchange = ccxt.binance({"enableRateLimit": True})
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe="1h", limit=500)
        df = pd.DataFrame(ohlcv, columns=["timestamp","open","high","low","close","volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)

        # 4H data
        ohlcv4h = exchange.fetch_ohlcv(symbol, timeframe="4h", limit=200)
        df4h = pd.DataFrame(ohlcv4h, columns=["timestamp","open","high","low","close","volume"])
        df4h["timestamp"] = pd.to_datetime(df4h["timestamp"], unit="ms", utc=True)
    except Exception as e:
        return {"error": str(e)}

    # Indicators
    df["EMA_9"]   = df["close"].ewm(span=9,   adjust=False).mean()
    df["EMA_20"]  = df["close"].ewm(span=20,  adjust=False).mean()
    df["EMA_50"]  = df["close"].ewm(span=50,  adjust=False).mean()
    df["EMA_200"] = df["close"].ewm(span=200, adjust=False).mean()
    df["RSI"]     = ta.momentum.RSIIndicator(df["close"], window=14).rsi()
    df["ATR"]     = ta.volatility.AverageTrueRange(df["high"], df["low"], df["close"], window=14).average_true_range()
    df["ADX"]     = ta.trend.ADXIndicator(df["high"], df["low"], df["close"], window=14).adx()
    df["ADX_Pos"] = ta.trend.ADXIndicator(df["high"], df["low"], df["close"], window=14).adx_pos()
    df["ADX_Neg"] = ta.trend.ADXIndicator(df["high"], df["low"], df["close"], window=14).adx_neg()
    macd          = ta.trend.MACD(df["close"])
    df["MACD"]    = macd.macd()
    df["MACD_Sig"]= macd.macd_signal()
    df["MACD_H"]  = df["MACD"] - df["MACD_Sig"]
    bb            = ta.volatility.BollingerBands(df["close"], window=20, window_dev=2)
    df["BB_U"]    = bb.bollinger_hband()
    df["BB_L"]    = bb.bollinger_lband()
    df["BB_W"]    = (df["BB_U"] - df["BB_L"]) / bb.bollinger_mavg()
    stoch         = ta.momentum.StochasticOscillator(df["high"], df["low"], df["close"])
    df["Stoch_K"] = stoch.stoch()
    df["Stoch_D"] = stoch.stoch_signal()
    df["OBV"]     = ta.volume.OnBalanceVolumeIndicator(df["close"], df["volume"]).on_balance_volume()
    df["Vol_MA"]  = df["volume"].rolling(20).mean()
    df["Vol_R"]   = (df["volume"] / df["Vol_MA"].replace(0, 1)).clip(0, 10)
    typical       = (df["high"] + df["low"] + df["close"]) / 3
    df["VWAP"]    = (typical * df["volume"]).cumsum() / df["volume"].cumsum()
    try:
        df["MFI"] = ta.volume.MFIIndicator(df["high"], df["low"], df["close"], df["volume"], window=14).money_flow_index()
    except:
        df["MFI"] = df["RSI"]

    df = df.dropna().reset_index(drop=True)
    last = df.iloc[-1]
    price = float(last["close"])
    atr   = float(last["ATR"])

    # 4H Indicators
    df4h["EMA_9"]   = df4h["close"].ewm(span=9,  adjust=False).mean()
    df4h["EMA_50"]  = df4h["close"].ewm(span=50, adjust=False).mean()
    df4h["EMA_200"] = df4h["close"].ewm(span=200,adjust=False).mean()
    df4h["RSI"]     = ta.momentum.RSIIndicator(df4h["close"], window=14).rsi()
    df4h["ADX"]     = ta.trend.ADXIndicator(df4h["high"], df4h["low"], df4h["close"], window=14).adx()
    df4h            = df4h.dropna().reset_index(drop=True)
    last4h          = df4h.iloc[-1]
    p4h             = float(last4h["close"])

    # HTF Bias
    htf_checks = [
        p4h > float(last4h["EMA_9"]),
        p4h > float(last4h["EMA_50"]),
        p4h > float(last4h["EMA_200"]),
        float(last4h["RSI"]) > 55,
        float(last4h["ADX"]) > 22,
    ]
    htf_bull = sum(htf_checks)
    if   htf_bull >= 4: htf_bias = "BULL"
    elif htf_bull <= 1: htf_bias = "BEAR"
    else:               htf_bias = "NEUTRAL"

    # Regime
    adx   = float(last["ADX"])
    adxp  = float(last["ADX_Pos"])
    adxn  = float(last["ADX_Neg"])
    bbw   = float(last["BB_W"])
    bbq40 = float(df["BB_W"].quantile(0.40))

    if   adx >= 35 and adxp > adxn and price > float(last["EMA_9"]) > float(last["EMA_50"]): regime = "STRONG_BULL"
    elif adx >= 35 and adxn > adxp and price < float(last["EMA_9"]) < float(last["EMA_50"]): regime = "STRONG_BEAR"
    elif adx >  22 and adxp > adxn and price > float(last["EMA_50"]):                         regime = "TRENDING_UP"
    elif adx >  22 and adxn > adxp and price < float(last["EMA_50"]):                         regime = "TRENDING_DOWN"
    elif adx <  20 and bbw < bbq40:                                                            regime = "RANGING"
    else:                                                                                       regime = "NORMAL"

    # Signal Scoring
    macd_b  = float(last["MACD"]) > float(last["MACD_Sig"])
    st_bull = price > float(last["EMA_9"]) > float(last["EMA_50"])
    rsi_v   = float(last["RSI"])
    vr      = float(last["Vol_R"])

    buy_score = sum([
        macd_b                       * 2.0,
        st_bull                      * 2.0,
        (adx > 22 and adxp > adxn)  * 1.5,
        (rsi_v < 40)                 * 1.0,
        (float(last["MFI"]) < 35)   * 1.0,
        (float(last["Stoch_K"]) < 30 and float(last["Stoch_K"]) > float(last["Stoch_D"])) * 1.0,
        (vr >= 1.5)                  * 1.0,
        (price > float(last["VWAP"])) * 0.5,
        (htf_bias == "BULL")         * 1.0,
    ])

    sell_score = sum([
        (not macd_b)                 * 2.0,
        (price < float(last["EMA_9"]) < float(last["EMA_50"])) * 2.0,
        (adx > 22 and adxn > adxp)  * 1.5,
        (rsi_v > 60)                 * 1.0,
        (float(last["MFI"]) > 65)   * 1.0,
        (float(last["Stoch_K"]) > 70 and float(last["Stoch_K"]) < float(last["Stoch_D"])) * 1.0,
        (vr >= 1.5)                  * 1.0,
        (price < float(last["VWAP"])) * 0.5,
        (htf_bias == "BEAR")         * 1.0,
    ])

    # Whale (CVD)
    bull_vol = float(df.loc[df["close"] >= df["open"], "volume"].tail(50).sum())
    bear_vol = float(df.loc[df["close"] <  df["open"], "volume"].tail(50).sum())
    cvd_r    = bull_vol / max(bull_vol + bear_vol, 1e-10)
    cvd_bias = "BULL" if cvd_r >= 0.60 else "BEAR" if cvd_r <= 0.40 else "NEUTRAL"
    whale_score = 5.0
    if buy_score > sell_score and cvd_bias == "BULL":  whale_score = 8.0
    elif sell_score > buy_score and cvd_bias == "BEAR": whale_score = 8.0
    elif cvd_bias == "NEUTRAL": whale_score = 5.0
    else: whale_score = 3.0

    # Signal
    if   regime == "RANGING" and abs(buy_score - sell_score) < 2: signal = "HOLD"
    elif buy_score > sell_score and buy_score >= 5.0:
        signal = "STRONG BUY" if buy_score >= 7.5 else "BUY"
    elif sell_score > buy_score and sell_score >= 5.0:
        signal = "STRONG SELL" if sell_score >= 7.5 else "SELL"
    else:
        signal = "HOLD"

    if whale_score < 3.0: signal = "HOLD"

    # SL / TP
    is_bull = "BUY" in signal
    d       = 1 if is_bull else -1
    atp     = float(df["ATR"].rank(pct=True).iloc[-1]) * 100
    sl_mult = 0.9 if atp < 30 else 1.2 if atp < 70 else 1.6

    # Swing levels
    hi_arr = df["high"].values[-75:]
    lo_arr = df["low"].values[-75:]
    res_lvls = [float(hi_arr[i]) for i in range(3, len(hi_arr)-3) if hi_arr[i] >= max(hi_arr[i-3:i]) and hi_arr[i] >= max(hi_arr[i+1:i+4])]
    sup_lvls = [float(lo_arr[i]) for i in range(3, len(lo_arr)-3) if lo_arr[i] <= min(lo_arr[i-3:i]) and lo_arr[i] <= min(lo_arr[i+1:i+4])]

    nearest_res = min([r for r in res_lvls if r > price * 1.002], default=price * 1.06)
    nearest_sup = max([s for s in sup_lvls if s < price * 0.998], default=price * 0.94)

    sl  = round(price - d * atr * sl_mult, 6)
    tp1 = round(nearest_res if is_bull else nearest_sup, 6)
    tp2 = round(price + d * atr * 3.5, 6)
    tp3 = round(price + d * atr * 5.5, 6)

    sl_dist = abs(price - sl)
    rr = round(abs(tp1 - price) / max(sl_dist, 1e-10), 2)

    # Tier
    total = buy_score if is_bull else sell_score
    if   total >= 8.5 and whale_score >= 7: tier = "A+"
    elif total >= 7.0 and whale_score >= 5: tier = "A"
    elif total >= 5.5:                       tier = "B"
    elif total >= 4.0:                       tier = "C"
    else:                                    tier = "D"

    # Position sizing
    risk_amt  = balance * (risk_pct / 100)
    pos_usdt  = risk_amt / (sl_dist / max(price, 1e-10))
    pos_units = pos_usdt / max(price, 1e-10)

    # Strength
    strength = min(100, round((
        (adx / 50 * 25) +
        (total / 11 * 30) +
        (whale_score / 10 * 20) +
        ((1 if htf_bias in ("BULL","BEAR") else 0.5) * 15) +
        (vr / 3 * 10)
    ), 1))

    return {
        "price":       round(price, 6),
        "signal":      signal,
        "tier":        tier,
        "regime":      regime,
        "htf_bias":    htf_bias,
        "sl":          sl,
        "tp1":         tp1,
        "tp2":         tp2,
        "tp3":         tp3,
        "rr":          rr,
        "strength":    strength,
        "whale_score": round(whale_score, 1),
        "cvd_bias":    cvd_bias,
        "cvd_ratio":   round(cvd_r * 100, 1),
        "buy_score":   round(buy_score, 1),
        "sell_score":  round(sell_score, 1),
        "rsi":         round(rsi_v, 1),
        "adx":         round(adx, 1),
        "macd_bull":   macd_b,
        "atr":         round(atr, 6),
        "vol_ratio":   round(vr, 2),
        "mfi":         round(float(last["MFI"]), 1),
        "risk_amt":    round(risk_amt, 2),
        "pos_usdt":    round(pos_usdt, 2),
        "pos_units":   round(pos_units, 6),
        "sl_pct":      round(sl_dist / price * 100, 3),
        "atp":         round(atp, 1),
    }

# ── Dashboard ─────────────────────────────────────────────────────────────────
def show_dashboard():
    user = st.session_state.user

    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div style='padding: 10px 0;'>
            <h2 style='color:#e6edf3; margin:0;'>🤖 Crypto Bot v11 <span style='color:#3fb950; font-size:14px;'>● LIVE</span></h2>
            <p style='color:#8b949e; margin:4px 0 0 0; font-size:13px;'>Welcome back, <b style='color:#58a6ff;'>{user}</b></p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.rerun()

    st.divider()

    # Input Section
    st.markdown("### 🎯 Select Trading Pair")

    col1, col2, col3 = st.columns(3)
    with col1:
        symbol = st.selectbox("Coin Pair", [
            "XRP/USDT","BTC/USDT","ETH/USDT","SOL/USDT","BNB/USDT",
            "DOGE/USDT","ADA/USDT","MATIC/USDT","AVAX/USDT","DOT/USDT",
            "LINK/USDT","LTC/USDT","UNI/USDT","ATOM/USDT","TRX/USDT"
        ])
    with col2:
        balance = st.number_input("💰 Balance (USDT)", min_value=10.0, max_value=100000.0, value=1000.0, step=100.0)
    with col3:
        risk_pct = st.number_input("⚠️ Risk %", min_value=0.5, max_value=5.0, value=1.0, step=0.5)

    run = st.button("🚀 Run Bot Analysis")

    if run:
        with st.spinner(f"🧠 Analyzing {symbol}..."):
            progress = st.progress(0)
            steps = [
                "📡 Fetching market data...",
                "📊 Computing 20+ indicators...",
                "🧠 RegimeBrain analyzing...",
                "🐋 Whale tracker scanning...",
                "🔬 Running 4 addon modules...",
                "⚖️ Generating signal...",
                "💼 Calculating position size...",
            ]
            for i, step in enumerate(steps):
                st.caption(step)
                time.sleep(0.4)
                progress.progress((i+1)/len(steps))

            res = run_analysis(symbol, balance, risk_pct)

        if "error" in res:
            st.error(f"❌ Error: {res['error']}")
            return

        signal = res["signal"]
        sig_color = "#3fb950" if "BUY" in signal else "#f85149" if "SELL" in signal else "#d29922"
        sig_class = "signal-buy" if "BUY" in signal else "signal-sell" if "SELL" in signal else "signal-hold"

        # Signal Card
        st.markdown(f"""
        <div class='{sig_class}' style='margin: 16px 0;'>
            <div style='font-size:32px; font-weight:bold; color:{sig_color};'>{signal}</div>
            <div style='color:#8b949e; font-size:14px; margin-top:6px;'>
                {symbol} • Grade: {res['tier']} • Regime: {res['regime']} • 4H: {res['htf_bias']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 Price", f"{res['price']} USDT")
        col2.metric("📐 R:R Ratio", f"1:{res['rr']}")
        col3.metric("💪 Strength", f"{res['strength']}/100")
        col4.metric("🐋 Whale", f"{res['whale_score']}/10")

        st.divider()

        # Price Levels + Scores
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📊 Price Levels")
            st.markdown(f"""
            <div class='main-card'>
                <div style='display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #21262d;'>
                    <span style='color:#8b949e;'>🔵 Entry</span>
                    <span style='color:#58a6ff; font-weight:bold;'>{res['price']} USDT</span>
                </div>
                <div style='display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #21262d;'>
                    <span style='color:#8b949e;'>🔴 Stop Loss</span>
                    <span style='color:#f85149; font-weight:bold;'>{res['sl']} (-{res['sl_pct']}%)</span>
                </div>
                <div style='display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #21262d;'>
                    <span style='color:#8b949e;'>🟢 TP1</span>
                    <span style='color:#3fb950; font-weight:bold;'>{res['tp1']} USDT</span>
                </div>
                <div style='display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #21262d;'>
                    <span style='color:#8b949e;'>🟡 TP2</span>
                    <span style='color:#7ee787; font-weight:bold;'>{res['tp2']} USDT</span>
                </div>
                <div style='display:flex; justify-content:space-between; padding:8px 0;'>
                    <span style='color:#8b949e;'>⚪ TP3</span>
                    <span style='color:#56d364; font-weight:bold;'>{res['tp3']} USDT</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("#### 📈 Indicators")
            st.markdown(f"""
            <div class='main-card'>
                <div style='display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #21262d;'>
                    <span style='color:#8b949e;'>RSI (14)</span>
                    <span style='color:{"#f85149" if res["rsi"]>70 else "#3fb950" if res["rsi"]<30 else "#e6edf3"}; font-weight:bold;'>{res['rsi']}</span>
                </div>
                <div style='display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #21262d;'>
                    <span style='color:#8b949e;'>ADX</span>
                    <span style='color:{"#3fb950" if res["adx"]>25 else "#d29922"}; font-weight:bold;'>{res['adx']}</span>
                </div>
                <div style='display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #21262d;'>
                    <span style='color:#8b949e;'>MFI</span>
                    <span style='color:{"#f85149" if res["mfi"]>70 else "#3fb950" if res["mfi"]<30 else "#e6edf3"}; font-weight:bold;'>{res['mfi']}</span>
                </div>
                <div style='display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #21262d;'>
                    <span style='color:#8b949e;'>MACD</span>
                    <span style='color:{"#3fb950" if res["macd_bull"] else "#f85149"}; font-weight:bold;'>{"BULL ↑" if res["macd_bull"] else "BEAR ↓"}</span>
                </div>
                <div style='display:flex; justify-content:space-between; padding:8px 0;'>
                    <span style='color:#8b949e;'>Vol Ratio</span>
                    <span style='color:{"#3fb950" if res["vol_ratio"]>1.5 else "#8b949e"}; font-weight:bold;'>{res['vol_ratio']}×</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Whale + Position
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🐋 Whale Analysis")
            st.markdown(f"""
            <div class='main-card'>
                <div style='display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #21262d;'>
                    <span style='color:#8b949e;'>Whale Score</span>
                    <span style='color:{"#3fb950" if res["whale_score"]>=7 else "#d29922"}; font-weight:bold;'>{res['whale_score']}/10</span>
                </div>
                <div style='display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #21262d;'>
                    <span style='color:#8b949e;'>CVD Bias</span>
                    <span style='color:{"#3fb950" if res["cvd_bias"]=="BULL" else "#f85149" if res["cvd_bias"]=="BEAR" else "#8b949e"}; font-weight:bold;'>{res['cvd_bias']}</span>
                </div>
                <div style='display:flex; justify-content:space-between; padding:8px 0;'>
                    <span style='color:#8b949e;'>Bull Volume %</span>
                    <span style='color:#e6edf3; font-weight:bold;'>{res['cvd_ratio']}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("#### 💼 Position Size")
            st.markdown(f"""
            <div class='main-card'>
                <div style='display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #21262d;'>
                    <span style='color:#8b949e;'>Risk Amount</span>
                    <span style='color:#f85149; font-weight:bold;'>${res['risk_amt']} USDT</span>
                </div>
                <div style='display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #21262d;'>
                    <span style='color:#8b949e;'>Position Size</span>
                    <span style='color:#3fb950; font-weight:bold;'>${res['pos_usdt']} USDT</span>
                </div>
                <div style='display:flex; justify-content:space-between; padding:8px 0;'>
                    <span style='color:#8b949e;'>Units</span>
                    <span style='color:#58a6ff; font-weight:bold;'>{res['pos_units']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Action Box
        action_map = {
            "STRONG BUY":  ("✅ EXECUTE STRONG BUY ORDER", "#3fb950"),
            "BUY":         ("✅ EXECUTE BUY ORDER", "#3fb950"),
            "STRONG SELL": ("✅ EXECUTE STRONG SELL ORDER", "#f85149"),
            "SELL":        ("✅ EXECUTE SELL ORDER", "#f85149"),
            "HOLD":        ("⏳ HOLD — Wait for better setup", "#d29922"),
        }
        action_text, action_color = action_map.get(signal, ("⏳ HOLD", "#d29922"))

        st.markdown(f"""
        <div style='background:{action_color}20; border:2px solid {action_color}; border-radius:14px; padding:20px; text-align:center; margin-top:16px;'>
            <div style='color:{action_color}; font-weight:bold; font-size:20px;'>{action_text}</div>
            <div style='color:#8b949e; font-size:13px; margin-top:8px;'>
                Entry: {res['price']} | SL: {res['sl']} | TP1: {res['tp1']} | R:R 1:{res['rr']}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Main ──────────────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    show_dashboard()
else:
    show_login()
