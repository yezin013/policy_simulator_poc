import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import random

BACKEND_URL = "http://localhost:8000"

st.set_page_config(layout="wide", page_title="Policy Simulator PoC", page_icon="📈")

st.markdown("""
<style>
.metric-container { margin-bottom: 20px; }
marquee { font-size: 20px; font-weight: bold; color: #ff4b4b; background-color: #222; padding: 10px; border-radius: 5px; }
.headline { font-size: 13px; color: #dcdcdc; border-bottom: 1px solid #444; padding: 8px 0; }
.dashboard-title { font-size: 14px; color: lightgray; text-align: center; margin-top: 15px; font-weight: bold; font-family: sans-serif; }
</style>
""", unsafe_allow_html=True)

if "auto_run" not in st.session_state: st.session_state.auto_run = False
if "history" not in st.session_state: st.session_state.history = {"tick": [], "price": [], "low_balance": [], "high_balance": []}

# Advanced mock history for the dashboard
if "gdp_hist" not in st.session_state: st.session_state.gdp_hist = [5.0]
if "inf_hist" not in st.session_state: st.session_state.inf_hist = [2.5]
if "hap_hist" not in st.session_state: st.session_state.hap_hist = [60.0]
if "gini_hist" not in st.session_state: st.session_state.gini_hist = [0.45]

def fetch_state():
    try:
        r = requests.get(f"{BACKEND_URL}/simulation/state")
        return r.json()
    except Exception:
        return None

def start_sim():
    try:
        requests.post(f"{BACKEND_URL}/simulation/start")
        st.session_state.history = {"tick": [], "price": [], "low_balance": [], "high_balance": []}
        st.session_state.auto_run = False
        st.session_state.gdp_hist = [5.0]
        st.session_state.inf_hist = [2.5]
        st.session_state.hap_hist = [60.0]
        st.session_state.gini_hist = [0.45]
        if "policy_tick" in st.session_state:
            del st.session_state.policy_tick
    except Exception:
        pass
    
def apply_policy():
    try:
        requests.post(f"{BACKEND_URL}/simulation/policy")
    except Exception:
        pass

def next_tick():
    try:
        requests.post(f"{BACKEND_URL}/simulation/tick")
    except Exception:
        pass

state = fetch_state()

if state is None:
    st.error("백엔드 서버(FastAPI)에 연결할 수 없습니다. 터미널에서 `uvicorn backend:app --reload` 로 서버를 실행해주세요.")
    st.stop()

if state.get("policy_active") and "policy_tick" not in st.session_state:
    st.session_state.policy_tick = state["tick"]

# Update History Data
if state["tick"] > 0:
    if len(st.session_state.history["tick"]) == 0 or st.session_state.history["tick"][-1] != state["tick"]:
        low_bals = [a["balance"] for a in state["agents"] if a["income_level"] == "low"]
        high_bals = [a["balance"] for a in state["agents"] if a["income_level"] == "high"]
        
        st.session_state.history["tick"].append(state["tick"])
        st.session_state.history["price"].append(state["average_price"])
        st.session_state.history["low_balance"].append(sum(low_bals)/len(low_bals) if low_bals else 0)
        st.session_state.history["high_balance"].append(sum(high_bals)/len(high_bals) if high_bals else 0)
        
        # Update dummy macro metrics
        if state["policy_active"]:
            st.session_state.gdp_hist.append(st.session_state.gdp_hist[-1] + random.uniform(0.5, 2.0))
            st.session_state.inf_hist.append(st.session_state.inf_hist[-1] + random.uniform(1.0, 3.0))
            st.session_state.hap_hist.append(min(100.0, st.session_state.hap_hist[-1] + random.uniform(2.0, 5.0)))
            st.session_state.gini_hist.append(max(0.2, st.session_state.gini_hist[-1] - 0.02))
        else:
            st.session_state.gdp_hist.append(st.session_state.gdp_hist[-1] + random.uniform(-0.5, 0.5))
            st.session_state.inf_hist.append(max(0.0, st.session_state.inf_hist[-1] + random.uniform(-0.2, 0.3)))
            st.session_state.hap_hist.append(max(0.0, min(100.0, st.session_state.hap_hist[-1] + random.uniform(-2.0, 2.0))))
            st.session_state.gini_hist.append(max(0.2, min(0.8, st.session_state.gini_hist[-1] + random.uniform(-0.01, 0.01))))

# UI Helper functions
def make_gauge(val, min_v, max_v, suffix="", color="red"):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = val,
        number = {'suffix': suffix, 'font': {'size': 24, 'color': 'white'}},
        gauge = {'axis': {'range': [min_v, max_v], 'visible': False}, 'bar': {'color': color, 'thickness': 1.0}}
    ))
    fig.update_layout(height=120, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", font={'color': 'white'})
    return fig

def make_mini_sparkline(data, color="yellow"):
    fig = px.line(x=list(range(len(data))), y=data)
    fig.update_layout(
        height=100, margin=dict(l=0, r=0, t=20, b=0),
        xaxis_visible=False, yaxis_visible=False,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False
    )
    fig.update_traces(line_color=color, line_width=3)
    return fig

# ----------------- MAIN LAYOUT -----------------
st.markdown("<h2 style='text-align: center; color: lightgray;'>≡ THE SENTIMENT PRESS: SOCIAL-ECONOMIC POLICY SIMULATOR (v0.8)</h2>", unsafe_allow_html=True)
st.markdown("---")

if state["tick"] == 24 and state.get("dummy_report"):
    st.info(f"📊 **FINAL REPORT (Tick 24 Reached!)**\n\n{state['dummy_report']}")


col1, col2, col3 = st.columns([1, 2, 1], gap="large")

with col1:
    st.markdown("#### SOCIO-ECONOMIC DASHBOARD")
    
    metrics = [
        ("GDP GROWTH RATE", st.session_state.gdp_hist, -2, 12, "%", "gold"),
        ("INFLATION INDEX", st.session_state.inf_hist, 0, 20, "%", "red"),
        ("SOCIAL HAPPINESS", st.session_state.hap_hist, 0, 100, "", "dodgerblue"),
        ("GINI COEFFICIENT", st.session_state.gini_hist, 0.0, 1.0, "", "orange"),
    ]
    
    for title, hist, min_v, max_v, suffix, color in metrics:
        st.markdown(f"<div class='dashboard-title'>{title}</div>", unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1])
        with c1: st.plotly_chart(make_mini_sparkline(hist, color), use_container_width=True)
        with c2: st.plotly_chart(make_gauge(hist[-1], min_v, max_v, suffix, color), use_container_width=True)

with col2:
    st.markdown("#### LIVE WORLD SIMULATION")
    
    grid = [[0 for _ in range(10)] for _ in range(10)]
    agents_map = {}
    for a in state["agents"]:
        if a["balance"] > 150000: v = 2 # Wealthy (Green)
        elif a["balance"] > 60000: v = 1 # Middle (Yellow)
        else: v = 0 # Poor/Crisis (Red/Black)
        grid[a["y"]][a["x"]] = v
        agents_map[(a["y"], a["x"])] = a
        
    df_grid = pd.DataFrame(grid)
    
    fig_heatmap = px.imshow(
        df_grid, 
        color_continuous_scale=[(0.0, "#a00000"), (0.5, "#d4af37"), (1.0, "#228b22")], 
        zmin=0, zmax=2,
        origin='lower'
    )
    fig_heatmap.update_layout(
        coloraxis_showscale=False, 
        margin=dict(l=0, r=0, t=10, b=10), 
        height=650,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
    )
    
    text_grid = [[f"{chr(65+j)}{10-i}" for j in range(10)] for i in range(10)]
    fig_heatmap.update_traces(text=text_grid, texttemplate="<b>%{text}</b>", textfont=dict(color="rgba(255,255,255,0.7)", size=12))
    
    if state["policy_active"] and state["tick"] > 6:
        fig_heatmap.add_annotation(x=4, y=4, text="PROTEST IN SECTOR E5", showarrow=True, arrowhead=1, bgcolor="maroon", font=dict(color='white'))
        fig_heatmap.add_annotation(x=7, y=2, text="RESIDENTIAL BOOM", showarrow=True, arrowhead=1, bgcolor="forestgreen", font=dict(color='white'))

    st.plotly_chart(fig_heatmap, use_container_width=True)
    st.markdown("<div style='text-align:center; font-size:14px;'>Agent Wealth: <span style='color:#228b22;'>■ Wealthy</span> &nbsp; <span style='color:#d4af37;'>■ Middle Class</span> &nbsp; <span style='color:#a00000;'>■ Poor/Crisis Sector</span></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center; font-size:14px; margin-top:10px; color:lightgray;'>Current Tick: {state['tick']} / 24</div>", unsafe_allow_html=True)

with col3:
    st.markdown("#### MEDIA AGENT SENTIMENT")
    
    sent_val = st.session_state.hap_hist[-1]
    fig_sent = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = sent_val,
        title = {'text': "SENTIMENT SPECTRUM", 'font': {'size': 12, 'color': 'lightgray'}},
        gauge = {
            'axis': {'range': [0, 100], 'tickvals': [16, 50, 84], 'ticktext': ['PESSIMISTIC', 'NEUTRAL', 'OPTIMISTIC']},
            'bar': {'color': "rgba(255,255,255,0.5)", 'thickness': 0.15},
            'steps': [
                {'range': [0, 33], 'color': "#a00000"},
                {'range': [33, 66], 'color': "#d4af37"},
                {'range': [66, 100], 'color': "#228b22"}
            ]
        }
    ))
    fig_sent.update_layout(height=230, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="rgba(0,0,0,0)", font={'color': 'white'})
    st.plotly_chart(fig_sent, use_container_width=True)

    st.markdown("#### LATEST HEADLINES")
    headlines = [
        "CENTRAL BANK WARNS OF IMMINENT MARKET COLLAPSE - THE DAILY SKEPTIC",
        "CITIZENS PROTEST RISING FOOD PRICES - URBAN NEWS",
        "BASIC INCOME PILOT SHOWS PROMISE IN SECTOR C4",
        "MARKET RALLIES AS INFLATION COOLS DOWN",
        "UNEMPLOYMENT SPIKES IN DOWNTOWN DISTRICT"
    ]
    random.seed(state["tick"]) # pseudo-random deterministic headlines per tick
    for hd in random.sample(headlines, 3):
        st.markdown(f'<div class="headline">{hd}</div>', unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### POLICY HARNESS CONTROL")
    st.slider("BASIC INCOME (100k KRW):", 0, 100, 50 if state["policy_active"] else 0, disabled=state["policy_active"])
    st.slider("CARBON TAX (per ton):", 0, 100, 20)
    st.slider("INTEREST RATE (%):", 0, 10, 3)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("RUN STRESS TEST", type="primary", use_container_width=True):
            if not state["policy_active"]: apply_policy()
            st.session_state.auto_run = True
            st.rerun()
    with col_btn2:
        if st.button("STOP SIMULATION", use_container_width=True):
            st.session_state.auto_run = False
            st.rerun()
            
    if st.button("🔄 RESET SIMULATION", use_container_width=True):
        start_sim()
        st.rerun()

st.markdown("---")
# Marquee at bottom
alert_msg = "🚨 [ALERT] SOCIO-ECONOMIC CRISIS WARNING: MARKET CRASH RISK RISING 🚨 &nbsp;&nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp;&nbsp; UNEMPLOYMENT SPIKES &nbsp;&nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp;&nbsp; MEDIA PESSIMISM DOMINATES ECONOMIC SENTIMENT &nbsp;&nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp;&nbsp; GDP FORECAST: NEGATIVE"
if state["policy_active"]:
    alert_msg = "✅ [UPDATE] BASIC INCOME POLICY DEPLOYED. MARKET LIQUIDITY INCREASING. &nbsp;&nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp;&nbsp; CITIZEN SENTIMENT IMPROVING &nbsp;&nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp;&nbsp; INFLATION MONITORING ACTIVE"

st.markdown(f'<marquee>{alert_msg}</marquee>', unsafe_allow_html=True)

# Auto-run scenario logic at the very end
if st.session_state.auto_run:
    if state["tick"] < 24:
        time.sleep(0.5)
        next_tick()
        st.rerun()
    else:
        st.session_state.auto_run = False
