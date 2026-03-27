import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

BACKEND_URL = "http://localhost:8000"
st.set_page_config(layout="wide", page_title="POLICY SIMULATOR")

# 1. 타이틀 고정
st.title("🎮 POLICY SIMULATOR")
st.caption("Game Economy Stress Test Lab")

try:
    state = requests.get(f"{BACKEND_URL}/simulation/state").json()
except:
    st.error("백엔드 서버를 먼저 실행해주세요!")
    st.stop()

# 2. 사이드바 (컨트롤 및 틱 버튼)
with st.sidebar:
    st.header("🕹️ CONTROL PANEL")
    # [중요] 사이드바에도 틱 버튼 배치
    if st.button("▶ 다음 틱 진행 (Tick)", key="side_tick", type="primary", use_container_width=True):
        requests.post(f"{BACKEND_URL}/simulation/tick")
        st.rerun()
    
    st.divider()
    st.header("🧨 FATAL PATCHES")
    if st.button("🔥 하이퍼 인플레이션 주입"):
        requests.post(f"{BACKEND_URL}/simulation/patch", json={"type": "hyper_inf"})
        st.rerun()
    if st.button("🐛 골드 복사 버그 발생"):
        requests.post(f"{BACKEND_URL}/simulation/patch", json={"type": "gold_bug"})
        st.rerun()
    
    st.divider()
    st.header("⚙️ ENV SETTINGS")
    diff = st.slider("성장 난이도", 0.5, 10.0, float(state["difficulty_mult"]))
    if st.button("난이도 적용"):
        requests.post(f"{BACKEND_URL}/harness/update", json={"diff": diff})
        st.rerun()

    if st.button("🔄 전체 서버 리셋", use_container_width=True):
        requests.post(f"{BACKEND_URL}/simulation/patch", json={"type": "reset"})
        st.rerun()

# 3. 메인 지표
m1, m2, m3 = st.columns(3)
with m1: st.metric("골드 환율 (1000G 당)", f"{state['gold_price']:.2f}원")
with m2: 
    active = sum(1 for a in state["agents"] if a["is_active"])
    st.metric("동시 접속자", f"{active} / 20")
with m3:
    status = "🚨 ECONOMY CRASHED" if state["market_panic"] else "✅ STABLE"
    st.subheader(f"서버 상태: {status}")

st.divider()

# 4. 시각화
col_l, col_r = st.columns(2)
with col_l:
    st.subheader("📈 로렌츠 곡선 (불평등도)")
    fig_l = go.Figure()
    fig_l.add_trace(go.Scatter(x=[0, 1], y=[0, 1], name="평등", line=dict(dash='dash', color='gray')))
    fig_l.add_trace(go.Scatter(x=state["lorenz_x"], y=state["lorenz_y"], name="자산 분포", fill='toself'))
    st.plotly_chart(fig_l, use_container_width=True)

with col_r:
    st.subheader("💰 유저 자산 분포 (Gold vs Cash)")
    df = pd.DataFrame(state["agents"])
    fig_s = px.scatter(df[df['is_active']], x="gold", y="cash", color="persona", size="happiness",
                       color_discrete_map={"Whale":"gold", "Farmer":"purple", "Newbie":"green"})
    st.plotly_chart(fig_s, use_container_width=True)

# 5. 하단 제어 (메인 틱 버튼)
st.divider()
c_log, c_btn = st.columns([2, 1])
with c_log:
    st.subheader("📝 서버 메시지")
    for log in reversed(state["logs"][-5:]):
        st.write(f"> {log}")

with c_btn:
    st.write(" ") # 간격 조정
    # [가장 중요한 버튼]
    if st.button("▶ 다음 틱 진행 (Next Step)", key="main_tick", type="primary", use_container_width=True):
        requests.post(f"{BACKEND_URL}/simulation/tick")
        st.rerun()

with st.expander("👤 전체 에이전트 데이터"):
    st.dataframe(df)