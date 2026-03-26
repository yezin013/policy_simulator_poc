from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
import random
from typing import List

app = FastAPI()

class TradeDecision(BaseModel):
    action: str
    price: int
    reason: str

class AgentState(BaseModel):
    id: int
    income_level: str
    balance: int
    x: int
    y: int
    activity: int = 0

class GlobalState(BaseModel):
    tick: int = 0
    policy_active: bool = False
    average_price: float = 1000.0
    agents: List[AgentState] = []
    dummy_report: str = ""

state = GlobalState()

def init_state():
    state.tick = 0
    state.policy_active = False
    state.average_price = 1000.0
    state.agents = []
    state.dummy_report = ""
    for i in range(20):
        income_level = "low" if i < 10 else "high"
        balance = 50000 if income_level == "low" else 300000
        state.agents.append(AgentState(
            id=i, income_level=income_level, balance=balance,
            x=random.randint(0, 9), y=random.randint(0, 9)
        ))

init_state()

class MockAgent:
    def __init__(self, agent_state: AgentState):
        self.state = agent_state

    async def decide(self, global_state: GlobalState) -> TradeDecision:
        # Mock network delay for async representation effect
        await asyncio.sleep(0.01) 
        
        base_price = global_state.average_price
        action = "hold"
        price = int(base_price)
        reason = "관망"
        
        if global_state.policy_active and self.state.income_level == "low":
            # Scenario: Basic income boosts purchasing power for low income
            if random.random() < 0.8:  
                action = "buy"
                price = int(base_price * random.uniform(1.0, 1.2))
                reason = "기본소득 덕분에 구매 여력 상승"
        else:
            if self.state.income_level == "low":
                if random.random() < 0.2:
                    action = "buy"
                    price = int(base_price * 0.9)
                    reason = "필수품 구매"
                elif random.random() < 0.2:
                    action = "sell"
                    price = int(base_price * 0.9)
                    reason = "급전 필요"
            else:
                if random.random() < 0.4:
                    action = "buy"
                    price = int(base_price * 1.05)
                    reason = "자산 투자"
                elif random.random() < 0.3:
                    action = "sell"
                    price = int(base_price * 1.1)
                    reason = "차익 실현"
                    
        return TradeDecision(action=action, price=price, reason=reason)

global_lock = asyncio.Lock()

@app.post("/simulation/start")
def start_sim():
    init_state()
    return {"status": "started", "state": state}

@app.post("/simulation/policy")
def apply_policy():
    if not state.policy_active:
        state.policy_active = True
        for a in state.agents:
            if a.income_level == "low":
                a.balance += 100000
    return {"status": "policy_applied"}

@app.post("/simulation/tick")
async def run_tick():
    async with global_lock:
        if state.tick >= 24:
            return {"status": "finished", "state": state}
            
        state.tick += 1
        
        # Reset activity tracker for the heatmap
        for a in state.agents:
            a.activity = 0
            
        mock_agents = [MockAgent(a) for a in state.agents]
        # Barrier Synchronization: Wait for all 20 agents to submit decisions in this tick
        decisions = await asyncio.gather(*(agent.decide(state) for agent in mock_agents))
        
        buy_prices = []
        sell_prices = []
        
        # Apply decisions to global state
        for i, decision in enumerate(decisions):
            agent = state.agents[i]
            if decision.action == "buy":
                spend_amount = min(decision.price, agent.balance) # 잔고 0 미만 방지
                buy_prices.append(spend_amount)
                agent.activity += 1
                agent.balance -= spend_amount
            elif decision.action == "sell":
                sell_prices.append(decision.price)
                agent.activity += 1
                agent.balance += decision.price
                
            # Random walk on 10x10 grid
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
            agent.x = max(0, min(9, agent.x + dx))
            agent.y = max(0, min(9, agent.y + dy))

        # Adjust market price based on supply/demand mock logic
        if buy_prices or sell_prices:
            all_p = buy_prices + sell_prices
            state.average_price = (state.average_price * 0.5) + (sum(all_p) / len(all_p) * 0.5)
            
        if state.policy_active:
            # Structural mock inflation triggered by sudden money supply increase
            state.average_price *= 1.03 
            
        if state.tick == 24:
            state.dummy_report = "6개월(24 Ticks) 시뮬레이션 종료.\n\n📌 결과 브리핑\n- 기본소득(10만 원) 도입 이후 시장 활성화 효과가 포착되었습니다.\n- 저소득층의 강한 구매(Buy) 수요가 확인되었으나, 시장 전반의 화폐 유동성 증가에 따라 물가가 단계적으로 우상향(인플레이션)하는 추세도 뚜렷하게 관찰되었습니다."
            
        return {"status": "tick_done", "state": state}

@app.get("/simulation/state")
def get_state():
    return state
