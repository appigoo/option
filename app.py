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
# CSS  ── 米白底 · 灰綠 accent · IBM Plex Mono · Noto Sans TC · 無硬陰影
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Noto+Sans+TC:wght@300;400;500;700&display=swap');

:root {
    --bg:       #f5f2ed;
    --bg2:      #edeae4;
    --card:     #faf8f5;
    --border:   #dedad3;
    --border2:  #ccc8bf;
    --acc:      #5c7f6e;
    --acc2:     #4a6b5b;
    --acc-lt:   #e8f0ec;
    --red:      #c0392b;
    --red-lt:   #fbeae8;
    --grn:      #2e7d5e;
    --grn-lt:   #e6f2ec;
    --gold:     #9b7e3d;
    --text:     #2c2a27;
    --muted:    #7a756c;
    --muted2:   #a09a91;
    --mono:     'IBM Plex Mono', monospace;
    --sans:     'Noto Sans TC', sans-serif;
}

html, body, [class*="css"] {
    font-family: var(--sans);
    background-color: var(--bg);
    color: var(--text);
}
.stApp { background-color: var(--bg); }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem; max-width: 1360px; }

/* ── PAGE HEADER ── */
.pg-header {
    padding-bottom: 1.1rem;
    margin-bottom: 1.4rem;
    border-bottom: 1px solid var(--border);
}
.pg-title { font-size: 1.15rem; font-weight: 700; color: var(--text); margin:0 0 .15rem; }
.pg-sub   { font-size: 0.78rem; color: var(--muted); font-weight: 300; }

/* ── METRIC ROW ── */
.m-row {
    display: grid;
    grid-template-columns: repeat(4,1fr);
    gap: .75rem;
    margin-bottom: .9rem;
}
.m-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.1rem;
}
.m-label { font-size:.72rem; color:var(--muted); margin-bottom:.45rem; }
.m-val   { font-family:var(--mono); font-size:1.38rem; font-weight:600; letter-spacing:-.02em; }
.m-sub   { font-family:var(--mono); font-size:.7rem; color:var(--muted2); margin-top:.2rem; }
.cu { color:var(--grn); } .cd { color:var(--red); }
.ca { color:var(--acc); } .cg { color:var(--gold); }

/* ── SIGNAL PANEL ── */
.sig-panel {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    margin-bottom: .9rem;
}
.sig-head {
    display: flex;
    align-items: center;
    gap: .7rem;
    margin-bottom: .85rem;
}
.sig-panel-title { font-size:.78rem; color:var(--muted); font-weight:400; }
.badge {
    display:inline-block; padding:.22rem .75rem;
    border-radius:20px; font-size:.74rem; font-weight:500;
}
.b-bull { background:var(--grn-lt); color:var(--grn); }
.b-bear { background:var(--red-lt); color:var(--red); }
.b-neut { background:var(--acc-lt); color:var(--acc2); }
.conf-txt { font-family:var(--mono); font-size:.72rem; color:var(--muted2); }

.sig-row {
    display:flex; align-items:center; gap:.55rem;
    padding:.5rem 0; border-bottom:1px solid var(--bg2);
    font-size:.81rem;
}
.sig-row:last-child { border-bottom:none; }
.dot { width:7px;height:7px; border-radius:50%; flex-shrink:0; }
.dg { background:var(--grn); } .dr { background:var(--red); } .dm { background:var(--muted2); }
.sig-lbl { color:var(--muted); width:70px; flex-shrink:0; font-size:.78rem; }
.sig-val { font-family:var(--mono); font-size:.79rem; color:var(--text); font-weight:500; }

/* ── STRATEGY CARDS ── */
.sc {
    background:var(--card);
    border:1px solid var(--border);
    border-radius:14px;
    padding:1.3rem 1.5rem;
    margin-bottom:.85rem;
}
.sc.top { border-color:var(--acc); }
.top-tag {
    display:inline-block;
    background:var(--acc-lt); color:var(--acc2);
    font-size:.66rem; font-weight:600;
    padding:.16rem .55rem; border-radius:10px;
    letter-spacing:.04em; margin-bottom:.45rem;
}
.sc-title { font-size:.94rem; font-weight:700; color:var(--text); margin-bottom:.2rem; }
.sc-desc  { font-size:.77rem; color:var(--muted); line-height:1.6; margin-bottom:.95rem; }

.act { font-family:var(--mono); font-size:.74rem; color:var(--acc2);
       border-left:2px solid var(--acc); padding:.28rem .65rem;
       background:var(--acc-lt); border-radius:0 6px 6px 0; margin-bottom:.28rem; }

.dg-grid {
    display:grid; grid-template-columns:repeat(3,1fr);
    gap:.55rem; margin:.85rem 0 .75rem;
}
.dg-cell { background:var(--bg2); border-radius:8px; padding:.6rem .75rem; }
.dg-lbl  { font-size:.63rem; color:var(--muted2); margin-bottom:.28rem; letter-spacing:.03em; }
.dg-val  { font-family:var(--mono); font-size:.81rem; font-weight:500; color:var(--text); }

.gk-row { display:flex; gap:1.3rem; padding-top:.7rem; border-top:1px solid var(--border); margin-top:.3rem; flex-wrap:wrap; }
.gk     { font-size:.73rem; }
.gk-k   { color:var(--muted2); }
.gk-v   { font-family:var(--mono); color:var(--acc2); font-weight:500; }

.ib { border-radius:8px; padding:.6rem .85rem; margin-top:.55rem; font-size:.76rem; line-height:1.55; }
.ib-cost { background:var(--acc-lt); color:var(--acc2); }
.ib-warn { background:var(--red-lt); color:#a93226; }
.ib-roll { background:#f3f0e8; color:var(--gold); }
.ib-lev  { background:var(--red-lt); color:#a93226; border:1px solid #e8b4b0; }

/* ── MISC ── */
.divider { border:none; border-top:1px solid var(--border); margin:1.1rem 0; }
.sec-lbl { font-size:.78rem; color:var(--muted); margin-bottom:.75rem; font-weight:400; }
.disc    { font-size:.7rem; color:var(--muted2); border-top:1px solid var(--border); padding-top:.75rem; margin-top:1rem; line-height:1.75; }

/* ── STREAMLIT OVERRIDES ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background:var(--card); border:1px solid var(--border);
    border-radius:8px; color:var(--text);
    font-family:var(--mono); font-size:.88rem;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color:var(--acc);
    box-shadow:0 0 0 2px rgba(92,127,110,.15);
}
label, .stTextInput label, .stNumberInput label {
    color:var(--muted) !important; font-size:.74rem !important;
    font-weight:400 !important; font-family:var(--sans) !important;
}
.stButton > button {
    background:var(--acc); color:#fff; font-family:var(--sans);
    font-weight:500; font-size:.86rem; border:none; border-radius:8px;
    padding:.52rem 1.6rem; width:100%; letter-spacing:.02em;
}
.stButton > button:hover { background:var(--acc2); }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# TECHNICAL ANALYSIS HELPERS
# ─────────────────────────────────────────
def rsi(s, n=14):
    d = s.diff()
    g = d.clip(lower=0).rolling(n).mean()
    l = (-d.clip(upper=0)).rolling(n).mean()
    return 100 - 100/(1+g/l)

def macd(s, f=12, sl=26, sig=9):
    ef = s.ewm(span=f, adjust=False).mean()
    es = s.ewm(span=sl, adjust=False).mean()
    m  = ef - es
    sg = m.ewm(span=sig, adjust=False).mean()
    return m, sg, m-sg

def bbands(s, n=20, k=2):
    mu = s.rolling(n).mean()
    sd = s.rolling(n).std()
    return mu+k*sd, mu, mu-k*sd

def atr(h, l, c, n=14):
    tr = pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    return tr.rolling(n).mean()

LEV2 = {'TSLL','TSLQ','NVDL','NVDD','QLD','SSO'}
LEV3 = {'SOXL','SOXS','TQQQ','SQQQ','SPXL','SPXS','UPRO','SPXU','LABU','LABD','FNGU','FNGD'}
LEV_ALL = LEV2 | LEV3 | {'UVXY','SVXY','BOIL','KOLD','UCO','SCO'}

def is_lev(t): return t.upper() in LEV_ALL
def lev_x(t):  return 3 if t.upper() in LEV3 else (2 if t.upper() in LEV_ALL else 1)


# ─────────────────────────────────────────
# DATA FETCH & ANALYSIS
# ─────────────────────────────────────────
def fetch(ticker, cost):
    tk   = yf.Ticker(ticker)
    hist = tk.history(period="3mo", interval="1d")
    if hist.empty: return None

    c,h,l,v = hist['Close'], hist['High'], hist['Low'], hist['Volume']
    px = float(c.iloc[-1])

    _rsi        = rsi(c)
    _macd,_sig,_hist = macd(c)
    e20,e50     = c.ewm(span=20).mean(), c.ewm(span=50).mean()
    bu,bm,bl    = bbands(c)
    _atr        = atr(h,l,c)

    r   = float(_rsi.iloc[-1])
    m   = float(_macd.iloc[-1])
    ms  = float(_sig.iloc[-1])
    mh  = float(_hist.iloc[-1])
    e20v= float(e20.iloc[-1]); e50v=float(e50.iloc[-1])
    atrv= float(_atr.iloc[-1])
    bbu = float(bu.iloc[-1]); bbl=float(bl.iloc[-1])
    sup = float(l.rolling(20).min().iloc[-1])
    res = float(h.rolling(20).max().iloc[-1])
    avgv= float(v.rolling(20).mean().iloc[-1])
    vr  = float(v.iloc[-1])/avgv if avgv>0 else 1.0

    sc = 0
    if r<35:  sc+=2
    elif r>65:sc-=2
    if m>ms:  sc+=1
    else:     sc-=1
    if e20v>e50v: sc+=1
    else:         sc-=1
    if px<bbl: sc+=1
    elif px>bbu: sc-=1

    if sc>=2:   trend,conf,tzh = "BULLISH",min(90,55+sc*8),"上升趨勢"
    elif sc<=-2:trend,conf,tzh = "BEARISH",min(90,55+abs(sc)*8),"下跌趨勢"
    else:       trend,conf,tzh = "NEUTRAL",55,"橫盤整固"

    iv_mult = 1.8 if is_lev(ticker) else 1.0
    iv = min(0.95,(atrv/px)*np.sqrt(252)*iv_mult)

    return dict(
        ticker=ticker.upper(), px=px, cost=cost,
        pnl=px-cost, pnl_pct=(px-cost)/cost*100,
        rsi=r, macd=m, macd_sig=ms, macd_hist=mh,
        e20=e20v, e50=e50v, atr=atrv,
        bbu=bbu, bbl=bbl, sup=sup, res=res,
        vr=vr, iv=iv,
        trend=trend, tzh=tzh, conf=conf,
        lev=is_lev(ticker), lx=lev_x(ticker),
    )


# ─────────────────────────────────────────
# OPTION PREMIUM ESTIMATE
# ─────────────────────────────────────────
def prem(px, strike, dte, iv):
    t = dte/365
    mn= abs(px-strike)/px
    atm = px*iv*np.sqrt(t)*0.4
    otm = max(0.15, 1-mn*3)
    return round(max(0.01, atm*otm), 2)


# ─────────────────────────────────────────
# STRATEGY ENGINE
# ─────────────────────────────────────────
def strategies(d):
    px,cost,iv  = d['px'], d['cost'], d['iv']
    trend,lf    = d['trend'], d['lev']
    pp          = d['pnl_pct']
    out         = []

    # 1 ── Covered Call
    dte = 21 if lf else 30
    otm = 0.10 if lf else 0.08
    sk  = round(px*(1+otm)/0.5)*0.5
    pr  = prem(px,sk,dte,iv)
    out.append(dict(
        name="Covered Call｜備兌認購",
        rec=(trend in ["NEUTRAL","BULLISH"] or pp<0),
        desc="持有正股，賣出虛值 Call 收取權利金，逐步攤薄持倉成本。橫盤或緩漲市況下效果最佳，每月滾倉可持續降低成本。",
        acts=[f"賣出 1張 {d['ticker']} ${sk:.2f} Call",
              f"到期日  {(datetime.now()+timedelta(days=dte)).strftime('%Y-%m-%d')}（{dte} DTE）"],
        det={"建議行使價":f"${sk:.2f}（虛值 {int(otm*100)}%）",
             "到期天數":f"{dte} DTE",
             "預計收取權利金":f"${pr:.2f}/股　(${pr*100:.0f}/張)",
             "損益平衡點":f"${cost-pr:.2f}",
             "最大盈利":f"${pr:.2f}/股（Call 作廢時）",
             "最大虧損":f"正股繼續下跌（緩衝 ${pr:.2f}）",
             "成本攤薄效果":f"${cost:.2f} → ${cost-pr:.2f}（節省 {pr/cost*100:.1f}%）",
             "滾倉時機":f"到期前 5–7 天，或盈利達 50%"},
        gk={"Delta":f"−0.{int(30+otm*100)}","Theta":f"+${pr/dte:.3f}/天","IV":f"{iv*100:.0f}%"},
        cost_n=f"每月執行一次，年化成本攤薄約 {pr/cost*100*12:.0f}%（理論值）",
        warn=f"{'槓桿ETF IV 極高，若急升將錯失漲幅；' if lf else ''}股價若突破 ${sk:.2f}，持倉將被 Call 走。",
        roll=f"股價接近行使價時，考慮 Roll Up & Out 延長到期日。",
    ))

    # 2 ── Protective Put
    dte = 30 if lf else 45
    sk  = round(px*0.90/0.5)*0.5
    pr  = prem(px,sk,dte,iv)
    out.append(dict(
        name="Protective Put｜保護性認沽",
        rec=(trend=="BEARISH" and pp>-10),
        desc="買入虛值 Put 作為保險，限定下行虧損上限。適合市況不明朗或持倉成本較高時使用。",
        acts=[f"買入 1張 {d['ticker']} ${sk:.2f} Put",
              f"到期日  {(datetime.now()+timedelta(days=dte)).strftime('%Y-%m-%d')}（{dte} DTE）"],
        det={"建議行使價":f"${sk:.2f}（虛值 10%）",
             "到期天數":f"{dte} DTE",
             "預計支付權利金":f"${pr:.2f}/股　(${pr*100:.0f}/張)",
             "損益平衡點":f"${px+pr:.2f}（需漲回此價才保本）",
             "最大盈利":f"正股反彈，無上限",
             "最大虧損":f"${(px-sk)+pr:.2f}/股（已鎖定下行）",
             "保護啟動價":f"低於 ${sk:.2f}（現價跌 {abs((sk/px-1)*100):.1f}% 後啟動）",
             "與成本比較":f"Put 保護至 ${sk:.2f}，成本 ${cost:.2f}（{'仍有損失' if sk<cost else '完全保護'}）"},
        gk={"Delta":"+0.28","Theta":f"−${pr/dte:.3f}/天","IV":f"{iv*100:.0f}%"},
        cost_n=f"保護成本 ${pr:.2f}/股，相當於持倉成本增加 {pr/cost*100:.1f}%",
        warn=f"{'槓桿ETF Theta 衰減極快，建議縮短 DTE 或改用 Bear Put Spread；' if lf else ''}若股價橫盤，保護金將完全損耗。",
        roll=f"距到期 10 天且虧損未實現，考慮換入更低 Strike 延長保護。",
    ))

    # 3 ── Bear Put Spread
    dte=21
    bs=round(px*0.97/0.5)*0.5; ss=round(px*0.82/0.5)*0.5
    bp=prem(px,bs,dte,iv); sp=prem(px,ss,dte,iv)
    net=round(bp-sp,2); mp=round((bs-ss)-net,2)
    rr=round(mp/net,1) if net>0 else 0
    out.append(dict(
        name="Bear Put Spread｜熊市看跌價差",
        rec=(trend=="BEARISH"),
        desc="買入高 Strike Put，同時賣出低 Strike Put，以降低對沖成本。預期下跌但幅度有限時的低成本方案。",
        acts=[f"買入 1張 {d['ticker']} ${bs:.2f} Put",
              f"賣出 1張 {d['ticker']} ${ss:.2f} Put",
              f"到期日  {(datetime.now()+timedelta(days=dte)).strftime('%Y-%m-%d')}（{dte} DTE）"],
        det={"買入行使價":f"${bs:.2f} Put",
             "賣出行使價":f"${ss:.2f} Put",
             "淨支出 Net Debit":f"${net:.2f}/股　(${net*100:.0f}/張)",
             "損益平衡點":f"${bs-net:.2f}",
             "最大盈利":f"${mp:.2f}/股（股價跌至 ${ss:.2f} 以下）",
             "最大虧損":f"${net:.2f}/股（僅限已付權利金）",
             "回報風險比":f"{rr}x",
             "目標下跌區間":f"${ss:.2f} – ${bs:.2f}"},
        gk={"Delta":"−0.38","Theta":f"~${net/dte:.3f}/天","IV":f"{iv*100:.0f}%"},
        cost_n=f"最大風險僅 ${net:.2f}/股，比單買 Put 節省 {int((bp-net)/bp*100)}% 成本",
        warn=f"{'槓桿ETF 波幅大，建議選擇更寬價差；' if lf else ''}若股價反彈，最大損失為 ${net:.2f}。",
        roll=None,
    ))

    # 4 ── Bull Call Spread
    if trend in ["BULLISH","NEUTRAL"]:
        dte=30
        bs=round(px*1.01/0.5)*0.5; ss=round(px*1.15/0.5)*0.5
        bp=prem(px,bs,dte,iv); sp=prem(px,ss,dte,iv)
        net=round(bp-sp,2); mp=round((ss-bs)-net,2)
        rr=round(mp/net,1) if net>0 else 0
        out.append(dict(
            name="Bull Call Spread｜牛市看漲價差",
            rec=(trend=="BULLISH"),
            desc="買入接近平值 Call，賣出虛值 Call，低成本參與上漲行情，限定最大損失。",
            acts=[f"買入 1張 {d['ticker']} ${bs:.2f} Call（接近平值）",
                  f"賣出 1張 {d['ticker']} ${ss:.2f} Call（虛值 15%）",
                  f"到期日  {(datetime.now()+timedelta(days=dte)).strftime('%Y-%m-%d')}（{dte} DTE）"],
            det={"買入行使價":f"${bs:.2f} Call",
                 "賣出行使價":f"${ss:.2f} Call",
                 "淨支出 Net Debit":f"${net:.2f}/股　(${net*100:.0f}/張)",
                 "損益平衡點":f"${bs+net:.2f}",
                 "最大盈利":f"${mp:.2f}/股（股價升至 ${ss:.2f} 以上）",
                 "最大虧損":f"${net:.2f}/股（僅限已付權利金）",
                 "回報風險比":f"{rr}x",
                 "目標上升區間":f"${bs:.2f} – ${ss:.2f}"},
            gk={"Delta":"+0.45","Theta":f"−${net/dte:.3f}/天","IV":f"{iv*100:.0f}%"},
            cost_n=f"最大損失 ${net:.2f}/股，股價須升破 ${bs+net:.2f} 方可獲利",
            warn=f"{'槓桿ETF Call 溢價急升，需快速止盈；' if lf else ''}需在到期前升破損益平衡點才獲利。",
            roll=f"盈利達 60–70% 時建議止盈，無需持有至到期。",
        ))

    # 5 ── Iron Condor
    if trend=="NEUTRAL":
        dte=30
        ps=round(px*0.92/0.5)*0.5; pb=round(px*0.85/0.5)*0.5
        cs=round(px*1.08/0.5)*0.5; cb=round(px*1.15/0.5)*0.5
        pc=prem(px,ps,dte,iv)-prem(px,pb,dte,iv)
        cc=prem(px,cs,dte,iv)-prem(px,cb,dte,iv)
        tot=round(pc+cc,2); ml=round((ps-pb)-tot,2)
        out.append(dict(
            name="Iron Condor｜鐵兀鷹",
            rec=(trend=="NEUTRAL"),
            desc="賣出 Put 價差 + 賣出 Call 價差，收取雙邊權利金。橫盤震盪市況下，Theta 每天自動累積收入。",
            acts=[f"賣出 ${ps:.2f} Put ＋ 買入 ${pb:.2f} Put（Put 側）",
                  f"賣出 ${cs:.2f} Call ＋ 買入 ${cb:.2f} Call（Call 側）",
                  f"到期日  {(datetime.now()+timedelta(days=dte)).strftime('%Y-%m-%d')}（{dte} DTE）"],
            det={"收取總權利金":f"${tot:.2f}/股　(${tot*100:.0f}/張)",
                 "上方損益平衡":f"${cs+tot:.2f}",
                 "下方損益平衡":f"${ps-tot:.2f}",
                 "最大盈利區間":f"${ps:.2f} – ${cs:.2f}",
                 "最大盈利":f"${tot:.2f}/股（全收權利金）",
                 "最大虧損":f"${ml:.2f}/股",
                 "每日 Theta":f"+${tot/dte:.3f}/天",
                 "成本補貼":f"每月收 ${tot:.2f}/股 補貼持倉"},
            gk={"Delta":"~0 中性","Theta":f"+${tot/dte:.3f}/天","IV":f"{iv*100:.0f}%"},
            cost_n=f"每月執行，年化理論補貼約 ${tot*12:.2f}/股",
            warn=f"{'槓桿ETF 單日波幅大，Iron Condor 較高風險；' if lf else ''}股價突破任一側須即時調整或平倉。",
            roll=f"股價接近任一側邊界時，考慮將該側向外滾倉（Roll Out）。",
        ))

    out.sort(key=lambda x: not x["rec"])
    return out


# ─────────────────────────────────────────
# RENDER HELPERS
# ─────────────────────────────────────────
def H(tag): return {"BULLISH":"b-bull","BEARISH":"b-bear","NEUTRAL":"b-neut"}[tag]

def sig_row(dot_cls, label, val):
    return f'<div class="sig-row"><span class="dot {dot_cls}"></span><span class="sig-lbl">{label}</span><span class="sig-val">{val}</span></div>'

def render_metrics(d):
    pc = "cu" if d['pnl']>=0 else "cd"
    pf = "+" if d['pnl']>=0 else ""
    vc = "cu" if d['vr']>1.2 else "ca"
    st.markdown(f"""
    <div class="m-row">
      <div class="m-card">
        <div class="m-label">當前股價</div>
        <div class="m-val ca">${d['px']:.2f}</div>
        <div class="m-sub">{d['ticker']}</div>
      </div>
      <div class="m-card">
        <div class="m-label">持倉盈虧</div>
        <div class="m-val {pc}">{pf}${d['pnl']:.2f}</div>
        <div class="m-sub">{pf}{d['pnl_pct']:.1f}%　成本 ${d['cost']:.2f}</div>
      </div>
      <div class="m-card">
        <div class="m-label">ATR(14) 日均波幅</div>
        <div class="m-val cg">${d['atr']:.2f}</div>
        <div class="m-sub">{d['atr']/d['px']*100:.1f}% 日波動</div>
      </div>
      <div class="m-card">
        <div class="m-label">成交量比 (20MA)</div>
        <div class="m-val {vc}">{d['vr']:.2f}x</div>
        <div class="m-sub">{'放量' if d['vr']>1.2 else '縮量' if d['vr']<0.8 else '正常'}</div>
      </div>
    </div>""", unsafe_allow_html=True)

def render_signals(d):
    macd_d = "dg" if d['macd']>d['macd_sig'] else "dr"
    ema_d  = "dg" if d['e20']>d['e50'] else "dr"
    rsi_d  = "dg" if d['rsi']<40 else ("dr" if d['rsi']>60 else "dm")
    tr_d   = "dg" if d['trend']=="BULLISH" else ("dr" if d['trend']=="BEARISH" else "dm")

    rows = (
        sig_row(tr_d,  "趨勢方向", d['tzh']) +
        sig_row(macd_d,"MACD 位置", f"DIF {d['macd']:.3f} / DEA {d['macd_sig']:.3f}") +
        sig_row("dg" if d['macd_hist']>0 else "dr", "柱量動能",
                f"{'正向' if d['macd_hist']>0 else '負向'}  {d['macd_hist']:.3f}") +
        sig_row(rsi_d, "RSI(14)", f"{d['rsi']:.1f}　{'超賣' if d['rsi']<35 else '超買' if d['rsi']>65 else '中性'}") +
        sig_row("dm",  "阻力突破", f"{'已突破' if d['px']>d['res'] else '未突破'}  {d['res']:.2f}") +
        sig_row("dm",  "支撐跌破", f"{'已跌破' if d['px']<d['sup'] else '守住'}  {d['sup']:.2f}") +
        sig_row(ema_d, "EMA 排列", f"EMA20  {d['e20']:.2f} / EMA50  {d['e50']:.2f}")
    )

    st.markdown(f"""
    <div class="sig-panel">
      <div class="sig-head">
        <span class="sig-panel-title">當前訊號分析</span>
        <span class="badge {H(d['trend'])}">{d['tzh']}</span>
        <span class="conf-txt">信心 {d['conf']}%</span>
      </div>
      {rows}
    </div>""", unsafe_allow_html=True)

    if d['lev']:
        st.markdown(f"""
        <div class="ib ib-lev">
          🚨 <b>槓桿ETF 偵測</b>：{d['ticker']} 為 {d['lx']}x 槓桿產品。
          IV 極高，Theta 衰減速度為一般股票 {d['lx']} 倍。
          優先推薦 <b>Covered Call</b> 收取豐厚權利金，避免直接買入期權。
        </div>""", unsafe_allow_html=True)

def render_strat(s, idx):
    cls  = "sc top" if s['rec'] else "sc"
    tag  = '<span class="top-tag">⭐ 最佳推薦</span><br>' if s['rec'] else ""
    acts = "".join([f'<div class="act">→ {a}</div>' for a in s['acts']])
    det  = "".join([f'<div class="dg-cell"><div class="dg-lbl">{k}</div><div class="dg-val">{v}</div></div>'
                    for k,v in s['det'].items()])
    gk   = "".join([f'<div class="gk"><span class="gk-k">{k}　</span><span class="gk-v">{v}</span></div>'
                    for k,v in s['gk'].items()])
    cn   = f'<div class="ib ib-cost">💡 {s["cost_n"]}</div>' if s.get("cost_n") else ""
    wn   = f'<div class="ib ib-warn">⚠️ {s["warn"]}</div>'  if s.get("warn")   else ""
    rl   = f'<div class="ib ib-roll">🔄 {s["roll"]}</div>'  if s.get("roll")   else ""

    st.markdown(f"""
    <div class="{cls}">
      {tag}
      <div class="sc-title">{idx}. {s['name']}</div>
      <div class="sc-desc">{s['desc']}</div>
      <div>{acts}</div>
      <div class="dg-grid">{det}</div>
      <div class="gk-row">{gk}</div>
      {cn}{wn}{rl}
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
st.markdown("""
<div class="pg-header">
  <div class="pg-title">期權策略評估系統</div>
  <div class="pg-sub">輸入持倉資料，自動分析技術面並推薦最佳期權策略</div>
</div>""", unsafe_allow_html=True)

c1, c2, c3 = st.columns([2, 2, 1])
with c1:
    ticker_in = st.text_input("股票代碼", value="TSLA", placeholder="TSLA / TSLL / NVDA").upper().strip()
with c2:
    cost_in = st.number_input("持倉成本價 ($)", min_value=0.01, value=370.0, step=0.5, format="%.2f")
with c3:
    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("分析並生成策略")

st.markdown('<hr class="divider">', unsafe_allow_html=True)

if run or st.session_state.get("_t"):
    if run:
        st.session_state["_t"] = ticker_in
        st.session_state["_c"] = cost_in

    with st.spinner(f"正在抓取 {st.session_state['_t']} 數據並分析…"):
        data = fetch(st.session_state["_t"], st.session_state["_c"])

    if data is None:
        st.error(f"無法獲取 {st.session_state['_t']} 數據，請確認股票代碼正確。")
    else:
        left, right = st.columns([1, 1.65])

        with left:
            render_metrics(data)
            render_signals(data)

        with right:
            st.markdown('<div class="sec-lbl">期權策略推薦（詳細執行方案）</div>', unsafe_allow_html=True)
            for i, s in enumerate(strategies(data), 1):
                render_strat(s, i)

        st.markdown(f"""
        <div class="disc">
          ⚠️ 免責聲明：本系統提供的期權策略僅供參考，不構成任何投資建議。
          期權交易涉及重大風險，包括損失全部已支付權利金。請在執行任何交易前諮詢持牌財務顧問。
          市場數據由 Yahoo Finance 提供，可能存在延遲。
          　📅 分析時間：{datetime.now().strftime('%Y-%m-%d %H:%M')} UTC
        </div>""", unsafe_allow_html=True)
