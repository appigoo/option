import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="期權策略評估系統",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Noto+Sans+TC:wght@300;400;700&display=swap');

:root {
    --bg: #0a0e1a;
    --bg2: #0f1628;
    --card: #131d35;
    --card2: #1a2540;
    --border: #1e2d50;
    --accent: #00d4ff;
    --accent2: #0099cc;
    --green: #00e676;
    --red: #ff4444;
    --gold: #ffd700;
    --purple: #b388ff;
    --text: #e0e8ff;
    --muted: #7a90b8;
}

html, body, [class*="css"] {
    font-family: 'Noto Sans TC', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

.stApp { background-color: var(--bg); }

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem; max-width: 1400px; }

/* ── HEADER ── */
.app-header {
    background: linear-gradient(135deg, #0f1628 0%, #1a2540 50%, #0f1628 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.app-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(ellipse at 30% 50%, rgba(0,212,255,0.06) 0%, transparent 60%);
    pointer-events: none;
}
.app-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: 2px;
    margin: 0;
}
.app-subtitle {
    color: var(--muted);
    font-size: 0.9rem;
    margin-top: 0.3rem;
    letter-spacing: 1px;
}

/* ── INPUT SECTION ── */
.input-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

/* ── METRIC CARDS ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.metric-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.metric-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
}
.metric-label { font-size: 0.72rem; color: var(--muted); letter-spacing: 1px; text-transform: uppercase; margin-bottom: 0.5rem; }
.metric-value { font-family: 'JetBrains Mono', monospace; font-size: 1.4rem; font-weight: 700; }
.metric-sub { font-size: 0.75rem; color: var(--muted); margin-top: 0.3rem; }
.up { color: var(--green); }
.down { color: var(--red); }
.neutral { color: var(--accent); }
.gold { color: var(--gold); }

/* ── SIGNAL BAR ── */
.signal-bar {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 2rem;
    flex-wrap: wrap;
}
.signal-badge {
    display: inline-block;
    padding: 0.4rem 1.2rem;
    border-radius: 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 1px;
}
.badge-bull { background: rgba(0,230,118,0.15); color: var(--green); border: 1px solid var(--green); }
.badge-bear { background: rgba(255,68,68,0.15); color: var(--red); border: 1px solid var(--red); }
.badge-neutral { background: rgba(0,212,255,0.15); color: var(--accent); border: 1px solid var(--accent); }

.indicator-row { display: flex; gap: 1.5rem; flex-wrap: wrap; }
.indicator-item { font-size: 0.8rem; color: var(--muted); }
.indicator-item span { color: var(--text); font-family: 'JetBrains Mono', monospace; }

/* ── STRATEGY CARD ── */
.strategy-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.strategy-card:hover { border-color: var(--accent2); }
.strategy-card.recommended {
    border-color: var(--gold);
    background: linear-gradient(135deg, #1a2540 0%, #1f2d4a 100%);
}
.strategy-card.recommended::before {
    content: '⭐ 最佳推薦';
    position: absolute;
    top: 0.8rem; right: 1rem;
    font-size: 0.72rem;
    color: var(--gold);
    font-weight: 700;
    letter-spacing: 1px;
}
.strategy-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--accent);
    margin-bottom: 0.3rem;
}
.strategy-desc { font-size: 0.82rem; color: var(--muted); margin-bottom: 1.2rem; }

.detail-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.8rem;
}
.detail-item {
    background: var(--card2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.8rem;
}
.detail-label { font-size: 0.68rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.4rem; }
.detail-value { font-family: 'JetBrains Mono', monospace; font-size: 0.92rem; font-weight: 700; color: var(--text); }

.greek-row {
    display: flex;
    gap: 1.2rem;
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
    flex-wrap: wrap;
}
.greek-item { font-size: 0.78rem; }
.greek-label { color: var(--muted); }
.greek-value { color: var(--purple); font-family: 'JetBrains Mono', monospace; }

.warning-box {
    background: rgba(255,68,68,0.08);
    border: 1px solid rgba(255,68,68,0.3);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin-top: 1rem;
    font-size: 0.8rem;
    color: #ff8888;
}

.cost-impact {
    background: rgba(0,212,255,0.05);
    border: 1px solid rgba(0,212,255,0.2);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin-top: 0.8rem;
    font-size: 0.8rem;
    color: var(--accent);
}

/* ── SECTION HEADER ── */
.section-header {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: var(--muted);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
}

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #0099cc, #00d4ff);
    color: #000;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    letter-spacing: 1px;
    border: none;
    border-radius: 8px;
    padding: 0.6rem 2rem;
    width: 100%;
    font-size: 1rem;
    cursor: pointer;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.85; }

/* ── INPUT FIELDS ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: var(--card2);
    border: 1px solid var(--border);
    color: var(--text);
    border-radius: 8px;
    font-family: 'JetBrains Mono', monospace;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 1px var(--accent);
}

label { color: var(--muted) !important; font-size: 0.8rem !important; letter-spacing: 1px !important; }

.divider { border: none; border-top: 1px solid var(--border); margin: 1.5rem 0; }

.rollover-box {
    background: rgba(179,136,255,0.08);
    border: 1px solid rgba(179,136,255,0.25);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin-top: 0.8rem;
    font-size: 0.8rem;
    color: var(--purple);
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# TECHNICAL ANALYSIS HELPERS
# ─────────────────────────────────────────
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    return 100 - 100 / (1 + rs)

def compute_macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    hist = macd - signal_line
    return macd, signal_line, hist

def compute_bbands(series, period=20, std=2):
    sma = series.rolling(period).mean()
    std_dev = series.rolling(period).std()
    upper = sma + std * std_dev
    lower = sma - std * std_dev
    return upper, sma, lower

def compute_atr(high, low, close, period=14):
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def is_leveraged_etf(ticker):
    leveraged = ['TSLL','TSLQ','NVDL','NVDD','SOXL','SOXS','TQQQ','SQQQ',
                 'SPXL','SPXS','UPRO','SPXU','LABU','LABD','FNGU','FNGD',
                 'UVXY','SVXY','BOIL','KOLD','UCO','SCO']
    return ticker.upper() in leveraged

def get_leverage_multiplier(ticker):
    two_x = ['TSLL','TSLQ','NVDL','NVDD','QLD','SSO','USD','MVV']
    three_x = ['SOXL','SOXS','TQQQ','SQQQ','SPXL','SPXS','UPRO','SPXU','LABU','LABD','FNGU','FNGD']
    if ticker.upper() in three_x:
        return 3
    if ticker.upper() in two_x:
        return 2
    return 1


# ─────────────────────────────────────────
# MARKET DATA & ANALYSIS
# ─────────────────────────────────────────
def fetch_and_analyze(ticker, cost_basis):
    tk = yf.Ticker(ticker)
    hist = tk.history(period="3mo", interval="1d")
    if hist.empty:
        return None

    close = hist['Close']
    high  = hist['High']
    low   = hist['Low']
    vol   = hist['Volume']

    current_price = float(close.iloc[-1])

    # Indicators
    rsi = compute_rsi(close)
    macd_line, signal_line, macd_hist = compute_macd(close)
    ema20 = close.ewm(span=20).mean()
    ema50 = close.ewm(span=50).mean()
    bb_upper, bb_mid, bb_lower = compute_bbands(close)
    atr = compute_atr(high, low, close)

    latest_rsi   = float(rsi.iloc[-1])
    latest_macd  = float(macd_line.iloc[-1])
    latest_sig   = float(signal_line.iloc[-1])
    latest_hist  = float(macd_hist.iloc[-1])
    latest_ema20 = float(ema20.iloc[-1])
    latest_ema50 = float(ema50.iloc[-1])
    latest_atr   = float(atr.iloc[-1])
    latest_bbu   = float(bb_upper.iloc[-1])
    latest_bbl   = float(bb_lower.iloc[-1])

    # Volume trend
    avg_vol = float(vol.rolling(20).mean().iloc[-1])
    last_vol = float(vol.iloc[-1])
    vol_ratio = last_vol / avg_vol if avg_vol > 0 else 1.0

    # Support / Resistance
    support    = float(low.rolling(20).min().iloc[-1])
    resistance = float(high.rolling(20).max().iloc[-1])

    # Trend scoring
    score = 0
    signals = []

    if latest_rsi < 35:
        score += 2; signals.append(f"RSI超賣({latest_rsi:.1f})")
    elif latest_rsi > 65:
        score -= 2; signals.append(f"RSI超買({latest_rsi:.1f})")
    else:
        signals.append(f"RSI中性({latest_rsi:.1f})")

    if latest_macd > latest_sig:
        score += 1; signals.append("MACD金叉✅")
    else:
        score -= 1; signals.append("MACD死叉❌")

    if latest_ema20 > latest_ema50:
        score += 1; signals.append("EMA20>EMA50✅")
    else:
        score -= 1; signals.append("EMA20<EMA50❌")

    if current_price < latest_bbl:
        score += 1; signals.append("跌破布林下軌")
    elif current_price > latest_bbu:
        score -= 1; signals.append("突破布林上軌")

    if score >= 2:
        trend = "BULLISH"
        confidence = min(90, 55 + score * 8)
        trend_zh = "📈 看漲"
    elif score <= -2:
        trend = "BEARISH"
        confidence = min(90, 55 + abs(score) * 8)
        trend_zh = "📉 看跌"
    else:
        trend = "NEUTRAL"
        confidence = 55
        trend_zh = "↔️ 橫盤整固"

    pnl_pct  = (current_price - cost_basis) / cost_basis * 100
    is_lev   = is_leveraged_etf(ticker)
    lev_mult = get_leverage_multiplier(ticker)

    return {
        "ticker": ticker.upper(),
        "current_price": current_price,
        "cost_basis": cost_basis,
        "pnl_pct": pnl_pct,
        "pnl_dollar": current_price - cost_basis,
        "rsi": latest_rsi,
        "macd": latest_macd,
        "macd_signal": latest_sig,
        "macd_hist": latest_hist,
        "ema20": latest_ema20,
        "ema50": latest_ema50,
        "atr": latest_atr,
        "bb_upper": latest_bbu,
        "bb_lower": latest_bbl,
        "support": support,
        "resistance": resistance,
        "vol_ratio": vol_ratio,
        "trend": trend,
        "trend_zh": trend_zh,
        "confidence": confidence,
        "signals": signals,
        "is_leveraged": is_lev,
        "leverage_mult": lev_mult,
    }


# ─────────────────────────────────────────
# STRATEGY ENGINE
# ─────────────────────────────────────────
def generate_strategies(data):
    px   = data["current_price"]
    cost = data["cost_basis"]
    atr  = data["atr"]
    trend = data["trend"]
    is_lev = data["is_leveraged"]
    pnl_pct = data["pnl_pct"]

    iv_mult = 1.8 if is_lev else 1.0
    # Rough IV estimate: annualised ATR / price
    iv_est = min(0.95, (atr / px) * np.sqrt(252) * iv_mult)

    strategies = []

    # ── Helper to estimate option premium (simplified Black-Scholes approximation)
    def est_premium(strike, dte, is_call, iv=None):
        if iv is None:
            iv = iv_est
        t = dte / 365
        moneyness = abs(px - strike) / px
        atm_premium = px * iv * np.sqrt(t) * 0.4
        otm_discount = max(0.2, 1 - moneyness * 3)
        prem = atm_premium * otm_discount
        return round(max(0.01, prem), 2)

    # ─────────────────────────────────────
    # 1. COVERED CALL
    # ─────────────────────────────────────
    cc_dte = 21 if is_lev else 30
    cc_strike_pct = 0.10 if is_lev else 0.08
    cc_strike = round(px * (1 + cc_strike_pct) / 0.5) * 0.5
    cc_premium = est_premium(cc_strike, cc_dte, is_call=True)
    cc_be = cost - cc_premium
    cc_new_cost = cost - cc_premium
    cc_cost_reduction = cc_premium / cost * 100

    strategies.append({
        "name": "Covered Call（備兌認購）",
        "name_en": "Covered Call",
        "desc": "持有正股同時賣出虛值Call，收取權利金攤薄持倉成本。橫盤或緩漲市況最佳。",
        "type": "income",
        "recommended": (trend in ["NEUTRAL", "BULLISH"] or pnl_pct < 0),
        "actions": [
            f"賣出 1張 {data['ticker']} ${cc_strike:.2f} Call",
            f"到期日：約 {cc_dte} 天後（{(datetime.now()+timedelta(days=cc_dte)).strftime('%Y-%m-%d')}）",
        ],
        "details": {
            "建議行使價": f"${cc_strike:.2f}（虛值 {cc_strike_pct*100:.0f}%）",
            "到期天數 (DTE)": f"{cc_dte} 天",
            "預計收取權利金": f"${cc_premium:.2f}/股 (${cc_premium*100:.0f}/張)",
            "損益平衡點": f"${cc_be:.2f}",
            "最大盈利": f"${cc_premium:.2f}/股（Call 作廢時）",
            "最大虧損": f"正股繼續下跌（已收 ${cc_premium:.2f} 緩衝）",
            "成本攤薄": f"${cost:.2f} → ${cc_new_cost:.2f}（節省 {cc_cost_reduction:.1f}%）",
            "滾倉建議": f"距到期 5-7 天或盈利達 50% 時平倉換月",
        },
        "greeks": {"Delta": f"-0.{int(30+cc_strike_pct*100)}", "Theta": f"+${cc_premium/cc_dte:.3f}/天", "IV%": f"{iv_est*100:.0f}%"},
        "cost_impact": f"📉 每月執行一次Covered Call，年化成本攤薄可達 {cc_cost_reduction*12:.0f}%（理論值）",
        "warning": f"⚠️ {'槓桿ETF的IV極高，權利金豐厚但風險較大；' if is_lev else ''}若股價急升突破${cc_strike:.2f}，持倉將被Call走，錯失上漲利潤。",
        "rollover": f"🔄 若股價接近行使價，考慮以更高Strike滾倉（Roll Up & Out）延長到期日。",
    })

    # ─────────────────────────────────────
    # 2. PROTECTIVE PUT
    # ─────────────────────────────────────
    pp_dte = 30 if is_lev else 45
    pp_strike = round(px * 0.90 / 0.5) * 0.5
    pp_premium = est_premium(pp_strike, pp_dte, is_call=False)
    pp_be = px + pp_premium
    pp_max_loss = (px - pp_strike) + pp_premium
    pp_protection_pct = (pp_strike / px - 1) * 100

    strategies.append({
        "name": "Protective Put（保護性認沽）",
        "name_en": "Protective Put",
        "desc": "買入虛值Put作為保險，保護持倉免受大幅下跌損失。適合不確定性高的市況。",
        "type": "protection",
        "recommended": (trend == "BEARISH" and pnl_pct > -10),
        "actions": [
            f"買入 1張 {data['ticker']} ${pp_strike:.2f} Put",
            f"到期日：約 {pp_dte} 天後（{(datetime.now()+timedelta(days=pp_dte)).strftime('%Y-%m-%d')}）",
        ],
        "details": {
            "建議行使價": f"${pp_strike:.2f}（虛值 10%）",
            "到期天數 (DTE)": f"{pp_dte} 天",
            "預計支付權利金": f"${pp_premium:.2f}/股 (${pp_premium*100:.0f}/張)",
            "損益平衡點": f"${pp_be:.2f}（需漲回此價才保本）",
            "最大盈利": f"正股反彈，無上限",
            "最大虧損": f"${pp_max_loss:.2f}/股（已限定下行風險）",
            "保護啟動價": f"低於 ${pp_strike:.2f}（現價跌 {abs(pp_protection_pct):.1f}% 後啟動）",
            "相對成本": f"成本保護至 ${pp_strike:.2f}，較成本價 ${cost:.2f} {'仍有損失' if pp_strike < cost else '完全保護'}",
        },
        "greeks": {"Delta": f"+0.{int(25+abs(pp_protection_pct))}", "Theta": f"-${pp_premium/pp_dte:.3f}/天", "IV%": f"{iv_est*100:.0f}%"},
        "cost_impact": f"💡 買入保護成本為 ${pp_premium:.2f}/股，相當於持倉成本增加 {pp_premium/cost*100:.1f}%",
        "warning": f"⚠️ {'槓桿ETF Theta衰減極快，建議選擇較短DTE或改用價差策略降低成本；' if is_lev else ''}若股價橫盤，保護金將完全損耗。",
        "rollover": f"🔄 距到期 10 天且虧損未實現，考慮賣出此Put換入更低Strike延長保護。",
    })

    # ─────────────────────────────────────
    # 3. BEAR PUT SPREAD
    # ─────────────────────────────────────
    bps_dte = 21
    bps_buy_strike  = round(px * 0.97 / 0.5) * 0.5
    bps_sell_strike = round(px * 0.82 / 0.5) * 0.5
    bps_buy_prem    = est_premium(bps_buy_strike, bps_dte, is_call=False)
    bps_sell_prem   = est_premium(bps_sell_strike, bps_dte, is_call=False)
    bps_net_debit   = round(bps_buy_prem - bps_sell_prem, 2)
    bps_spread_width = bps_buy_strike - bps_sell_strike
    bps_max_profit  = bps_spread_width - bps_net_debit
    bps_be          = bps_buy_strike - bps_net_debit
    bps_reward_risk = bps_max_profit / bps_net_debit if bps_net_debit > 0 else 0

    strategies.append({
        "name": "Bear Put Spread（熊市看跌價差）",
        "name_en": "Bear Put Spread",
        "desc": "買入較高行使價Put，同時賣出較低行使價Put，以降低對沖成本。預期下跌但幅度有限時使用。",
        "type": "bearish",
        "recommended": (trend == "BEARISH"),
        "actions": [
            f"買入 1張 {data['ticker']} ${bps_buy_strike:.2f} Put",
            f"賣出 1張 {data['ticker']} ${bps_sell_strike:.2f} Put",
            f"到期日：{bps_dte} 天後",
        ],
        "details": {
            "買入行使價": f"${bps_buy_strike:.2f} Put",
            "賣出行使價": f"${bps_sell_strike:.2f} Put",
            "淨支出（Net Debit）": f"${bps_net_debit:.2f}/股 (${bps_net_debit*100:.0f}/張)",
            "損益平衡點": f"${bps_be:.2f}",
            "最大盈利": f"${bps_max_profit:.2f}/股（股價跌至 ${bps_sell_strike:.2f} 以下）",
            "最大虧損": f"${bps_net_debit:.2f}/股（僅限支付的權利金）",
            "回報風險比": f"{bps_reward_risk:.1f}x",
            "目標下跌區間": f"${bps_sell_strike:.2f} – ${bps_buy_strike:.2f}",
        },
        "greeks": {"Delta": f"-0.{int(35+5)}", "Theta": f"~${bps_net_debit/bps_dte:.3f}/天", "IV%": f"{iv_est*100:.0f}%"},
        "cost_impact": f"💡 最大風險僅 ${bps_net_debit:.2f}/股，比單買Put節省 {(bps_buy_prem-bps_net_debit)/bps_buy_prem*100:.0f}% 成本",
        "warning": f"⚠️ {'槓桿ETF波動大，股價可能直接跌穿賣出Strike，建議選擇更寬價差；' if is_lev else ''}若股價反彈，最大損失為支付的 ${bps_net_debit:.2f}。",
        "rollover": None,
    })

    # ─────────────────────────────────────
    # 4. BULL CALL SPREAD (only if bullish)
    # ─────────────────────────────────────
    if trend in ["BULLISH", "NEUTRAL"]:
        bcs_dte = 30
        bcs_buy_strike  = round(px * 1.01 / 0.5) * 0.5
        bcs_sell_strike = round(px * 1.15 / 0.5) * 0.5
        bcs_buy_prem    = est_premium(bcs_buy_strike, bcs_dte, is_call=True)
        bcs_sell_prem   = est_premium(bcs_sell_strike, bcs_dte, is_call=True)
        bcs_net_debit   = round(bcs_buy_prem - bcs_sell_prem, 2)
        bcs_width       = bcs_sell_strike - bcs_buy_strike
        bcs_max_profit  = bcs_width - bcs_net_debit
        bcs_be          = bcs_buy_strike + bcs_net_debit
        bcs_rr          = bcs_max_profit / bcs_net_debit if bcs_net_debit > 0 else 0

        strategies.append({
            "name": "Bull Call Spread（牛市看漲價差）",
            "name_en": "Bull Call Spread",
            "desc": "買入較低行使價Call，賣出較高行使價Call，低成本參與上漲行情。",
            "type": "bullish",
            "recommended": (trend == "BULLISH"),
            "actions": [
                f"買入 1張 {data['ticker']} ${bcs_buy_strike:.2f} Call",
                f"賣出 1張 {data['ticker']} ${bcs_sell_strike:.2f} Call",
                f"到期日：{bcs_dte} 天後",
            ],
            "details": {
                "買入行使價": f"${bcs_buy_strike:.2f} Call（接近平值）",
                "賣出行使價": f"${bcs_sell_strike:.2f} Call（虛值15%）",
                "淨支出（Net Debit）": f"${bcs_net_debit:.2f}/股 (${bcs_net_debit*100:.0f}/張)",
                "損益平衡點": f"${bcs_be:.2f}",
                "最大盈利": f"${bcs_max_profit:.2f}/股（股價升至 ${bcs_sell_strike:.2f} 以上）",
                "最大虧損": f"${bcs_net_debit:.2f}/股（僅限權利金）",
                "回報風險比": f"{bcs_rr:.1f}x",
                "目標上升區間": f"${bcs_buy_strike:.2f} – ${bcs_sell_strike:.2f}",
            },
            "greeks": {"Delta": f"+0.45", "Theta": f"-${bcs_net_debit/bcs_dte:.3f}/天", "IV%": f"{iv_est*100:.0f}%"},
            "cost_impact": f"💡 最大損失 ${bcs_net_debit:.2f}/股，若升回成本價 ${cost:.2f} 可考慮此策略配合正股",
            "warning": f"⚠️ {'槓桿ETF上漲時Call溢價急升，需快速止盈；' if is_lev else ''}需股價在到期前升破 ${bcs_be:.2f} 才獲利。",
            "rollover": f"🔄 盈利達 60-70% 時建議止盈，勿貪到最後。",
        })

    # ─────────────────────────────────────
    # 5. IRON CONDOR (only if neutral)
    # ─────────────────────────────────────
    if trend == "NEUTRAL":
        ic_dte = 30
        ic_put_sell   = round(px * 0.92 / 0.5) * 0.5
        ic_put_buy    = round(px * 0.85 / 0.5) * 0.5
        ic_call_sell  = round(px * 1.08 / 0.5) * 0.5
        ic_call_buy   = round(px * 1.15 / 0.5) * 0.5
        ic_put_credit  = est_premium(ic_put_sell, ic_dte, False) - est_premium(ic_put_buy, ic_dte, False)
        ic_call_credit = est_premium(ic_call_sell, ic_dte, True) - est_premium(ic_call_buy, ic_dte, True)
        ic_total_credit = round(ic_put_credit + ic_call_credit, 2)
        ic_max_loss = round((ic_put_sell - ic_put_buy) - ic_total_credit, 2)
        ic_upper_be = ic_call_sell + ic_total_credit
        ic_lower_be = ic_put_sell - ic_total_credit

        strategies.append({
            "name": "Iron Condor（鐵兀鷹）",
            "name_en": "Iron Condor",
            "desc": "賣出Put價差 + 賣出Call價差，收取雙邊權利金。適合股價橫盤震盪市況。",
            "type": "neutral",
            "recommended": (trend == "NEUTRAL"),
            "actions": [
                f"賣出 ${ic_put_sell:.2f} Put + 買入 ${ic_put_buy:.2f} Put（Put側）",
                f"賣出 ${ic_call_sell:.2f} Call + 買入 ${ic_call_buy:.2f} Call（Call側）",
                f"到期日：{ic_dte} 天後",
            ],
            "details": {
                "收取總權利金": f"${ic_total_credit:.2f}/股 (${ic_total_credit*100:.0f}/張)",
                "上方損益平衡": f"${ic_upper_be:.2f}",
                "下方損益平衡": f"${ic_lower_be:.2f}",
                "最大盈利區間": f"${ic_put_sell:.2f} – ${ic_call_sell:.2f}（股價在此區間到期）",
                "最大盈利": f"${ic_total_credit:.2f}/股（全部權利金）",
                "最大虧損": f"${ic_max_loss:.2f}/股",
                "盈利機率": f"約 {int(65-abs(data['pnl_pct'])*0.5)}%（假設橫盤震盪）",
                "成本對沖": f"收取 ${ic_total_credit:.2f} 補貼持倉成本",
            },
            "greeks": {"Delta": "~0（中性）", "Theta": f"+${ic_total_credit/ic_dte:.3f}/天", "IV%": f"{iv_est*100:.0f}%"},
            "cost_impact": f"💡 每月執行一次Iron Condor，可收取 ${ic_total_credit:.2f}/股 補貼成本",
            "warning": f"⚠️ {'槓桿ETF單日可能大幅波動，Iron Condor風險較高，不建議槓桿ETF使用；' if is_lev else ''}需密切監控股價是否突破邊界。",
            "rollover": f"🔄 若股價接近任一側邊界，考慮將該側向外滾倉降低風險。",
        })

    return strategies


# ─────────────────────────────────────────
# RENDER FUNCTIONS
# ─────────────────────────────────────────
def render_header():
    st.markdown("""
    <div class="app-header">
        <div class="app-title">⚡ OPTIONS STRATEGY ENGINE</div>
        <div class="app-subtitle">期權策略智能評估系統 · 基於技術分析自動推薦策略</div>
    </div>
    """, unsafe_allow_html=True)

def render_metrics(data):
    px    = data["current_price"]
    cost  = data["cost_basis"]
    pnl   = data["pnl_dollar"]
    pnlp  = data["pnl_pct"]
    pnl_color = "up" if pnl >= 0 else "down"
    pnl_icon  = "▲" if pnl >= 0 else "▼"

    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-label">現價</div>
            <div class="metric-value neutral">${px:.2f}</div>
            <div class="metric-sub">{data['ticker']}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">持倉盈虧</div>
            <div class="metric-value {pnl_color}">{pnl_icon} ${abs(pnl):.2f}</div>
            <div class="metric-sub">{pnlp:+.1f}%</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">ATR(14) 日均波幅</div>
            <div class="metric-value gold">${data['atr']:.2f}</div>
            <div class="metric-sub">{data['atr']/px*100:.1f}% 波動</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">技術走勢</div>
            <div class="metric-value" style="font-size:1.1rem;">{data['trend_zh']}</div>
            <div class="metric-sub">信心 {data['confidence']}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_signal_bar(data):
    badge_class = {"BULLISH": "badge-bull", "BEARISH": "badge-bear", "NEUTRAL": "badge-neutral"}[data["trend"]]
    badge_text  = {"BULLISH": "📈 看漲", "BEARISH": "📉 看跌", "NEUTRAL": "↔️ 橫盤"}[data["trend"]]

    rsi_color = "up" if data["rsi"] < 40 else ("down" if data["rsi"] > 60 else "neutral")
    macd_color = "up" if data["macd"] > data["macd_signal"] else "down"
    ema_color  = "up" if data["ema20"] > data["ema50"] else "down"

    st.markdown(f"""
    <div class="signal-bar">
        <span class="signal-badge {badge_class}">{badge_text}</span>
        <div class="indicator-row">
            <div class="indicator-item">RSI(14) <span class="{rsi_color}">{data['rsi']:.1f}</span></div>
            <div class="indicator-item">MACD <span class="{macd_color}">{'金叉✅' if data['macd'] > data['macd_signal'] else '死叉❌'}</span></div>
            <div class="indicator-item">EMA <span class="{ema_color}">{'20>50✅' if data['ema20'] > data['ema50'] else '20<50❌'}</span></div>
            <div class="indicator-item">支撐 <span>${data['support']:.2f}</span></div>
            <div class="indicator-item">阻力 <span>${data['resistance']:.2f}</span></div>
            <div class="indicator-item">成交量比 <span class="{'up' if data['vol_ratio']>1.2 else 'neutral'}">{data['vol_ratio']:.1f}x</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if data["is_leveraged"]:
        st.markdown(f"""
        <div class="warning-box">
            🚨 <b>槓桿ETF偵測</b>：{data['ticker']} 為 {data['leverage_mult']}x 槓桿產品，隱含波動率(IV)極高，
            Theta衰減{data['leverage_mult']}倍加速。建議優先使用 <b>Covered Call</b> 收取高額權利金，
            避免直接買入期權（Theta損耗風險大）。
        </div>
        """, unsafe_allow_html=True)

def render_strategy(s, idx):
    rec_class = "recommended" if s["recommended"] else ""
    st.markdown(f"""
    <div class="strategy-card {rec_class}">
        <div class="strategy-title">{idx}. {s['name']}</div>
        <div class="strategy-desc">{s['desc']}</div>
    """, unsafe_allow_html=True)

    # Actions
    actions_html = "".join([f"<div style='font-size:0.8rem; color:#7a90b8; margin-bottom:0.3rem;'>→ {a}</div>" for a in s["actions"]])
    st.markdown(f"<div style='margin-bottom:1rem;'>{actions_html}</div>", unsafe_allow_html=True)

    # Details grid
    items_html = ""
    for k, v in s["details"].items():
        items_html += f"""
        <div class="detail-item">
            <div class="detail-label">{k}</div>
            <div class="detail-value">{v}</div>
        </div>"""
    st.markdown(f'<div class="detail-grid">{items_html}</div>', unsafe_allow_html=True)

    # Greeks
    g = s["greeks"]
    greek_html = "".join([f'<div class="greek-item"><span class="greek-label">{k}：</span><span class="greek-value">{v}</span></div>' for k, v in g.items()])
    st.markdown(f'<div class="greek-row">{greek_html}</div>', unsafe_allow_html=True)

    # Cost impact
    if s.get("cost_impact"):
        st.markdown(f'<div class="cost-impact">{s["cost_impact"]}</div>', unsafe_allow_html=True)

    # Warning
    if s.get("warning"):
        st.markdown(f'<div class="warning-box">{s["warning"]}</div>', unsafe_allow_html=True)

    # Rollover
    if s.get("rollover"):
        st.markdown(f'<div class="rollover-box">{s["rollover"]}</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────
render_header()

# Input
st.markdown('<div class="input-card">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    ticker_input = st.text_input("股票代碼 TICKER", value="TSLA", placeholder="例：TSLA / TSLL / NVDA").upper().strip()
with col2:
    cost_input = st.number_input("持倉成本價 COST BASIS ($)", min_value=0.01, value=370.0, step=0.5, format="%.2f")
with col3:
    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("🔍 分析並生成策略")
st.markdown('</div>', unsafe_allow_html=True)

if run or st.session_state.get("last_ticker"):
    if run:
        st.session_state["last_ticker"] = ticker_input
        st.session_state["last_cost"]   = cost_input

    with st.spinner(f"正在抓取 {ticker_input} 市場數據並分析..."):
        data = fetch_and_analyze(
            st.session_state["last_ticker"],
            st.session_state["last_cost"]
        )

    if data is None:
        st.error(f"❌ 無法獲取 {ticker_input} 數據，請確認股票代碼正確。")
    else:
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">📊 市場數據分析</div>', unsafe_allow_html=True)
        render_metrics(data)
        render_signal_bar(data)

        strategies = generate_strategies(data)

        st.markdown('<div class="section-header">💡 期權策略推薦（詳細執行方案）</div>', unsafe_allow_html=True)

        # Sort: recommended first
        strategies.sort(key=lambda x: (not x["recommended"]))

        for i, s in enumerate(strategies, 1):
            render_strategy(s, i)

        st.markdown(f"""
        <div style='background:var(--card2); border:1px solid var(--border); border-radius:10px; padding:1rem 1.5rem; margin-top:1.5rem; font-size:0.78rem; color:var(--muted);'>
            ⚠️ <b>免責聲明</b>：本系統提供的期權策略僅供參考，不構成投資建議。期權交易涉及重大風險，
            包括損失全部已支付權利金。請在執行任何交易前諮詢持牌財務顧問。市場數據由 Yahoo Finance 提供，可能存在延遲。
            <br><br>📅 分析時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
        </div>
        """, unsafe_allow_html=True)
