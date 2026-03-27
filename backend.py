from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
import random
from typing import List

app = FastAPI()

# --- 모델 정의 ---
class AgentState(BaseModel):
    id: int
    persona: str
    gold: int
    cash: int
    happiness: float = 100.0
    is_active: bool = True

class GlobalState(BaseModel):
    tick: int = 0
    gold_price: float = 10.0
    difficulty_mult: float = 1.0
    drop_rate: float = 1.0
    agents: List[AgentState] = []
    logs: List[str] = []
    market_panic: bool = False
    lorenz_x: List[float] = []
    lorenz_y: List[float] = []

state = GlobalState()
state_lock = asyncio.Lock()

def update_lorenz():
    active_golds = sorted([a.gold for a in state.agents if a.is_active])
    if not active_golds: return
    n = len(active_golds)
    total_gold = sum(active_golds) if sum(active_golds) > 0 else 1
    state.lorenz_x = [i/n for i in range(n + 1)]
    state.lorenz_y = [0.0]
    cum_sum = 0
    for g in active_golds:
        cum_sum += g
        state.lorenz_y.append(cum_sum / total_gold)

def init_state():
    state.tick = 0
    state.difficulty_mult = 1.0
    state.drop_rate = 1.0
    state.market_panic = False
    state.agents = []
    for i in range(20):
        if i < 3: p, g, c = "Whale", 30000, 1000000
        elif i < 10: p, g, c = "Farmer", 60000, 5000
        else: p, g, c = "Newbie", 8000, 1000
        state.agents.append(AgentState(id=i, persona=p, gold=g, cash=c))
    
    total_gold = sum(a.gold for a in state.agents)
    state.gold_price = 1000000 / (total_gold + 50000)
    update_lorenz()
    state.logs = ["📢 🎮 POLICY SIMULATOR 서버 가동!", f"📍 초기 환율 {state.gold_price:.2f}원 동기화 완료."]

init_state()

@app.get("/simulation/state")
def get_state(): return state

@app.post("/harness/update")
async def update_harness(data: dict):
    async with state_lock:
        if "diff" in data: state.difficulty_mult = data["diff"]
        return {"status": "ok"}

@app.post("/simulation/tick")
async def run_tick():
    async with state_lock:
        state.tick += 1
        old_price = state.gold_price
        active_agents = [a for a in state.agents if a.is_active]
        
        for a in active_agents:
            a.gold += int(3000 * state.drop_rate) # 생산
            cost = int(2500 * state.difficulty_mult) # 소모
            
            # RMT 로직
            if a.persona == "Whale" and a.gold < cost:
                buy_amt = 100000
                cash_cost = int(buy_amt * (state.gold_price / 1000))
                if a.cash >= cash_cost: a.cash -= cash_cost; a.gold += buy_amt
            elif a.persona == "Farmer" and a.gold > 150000:
                sell_amt = 100000
                cash_gain = int(sell_amt * (state.gold_price / 1000))
                a.gold -= sell_amt; a.cash += cash_gain