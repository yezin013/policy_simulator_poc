# Policy Simulator PoC (The 24-Tick Challenge)

LLM 기반 에이전트들을 가상 시장에 풀어놓고, 특정 정책(예: 기본소득, 금리 인상 등) 변화에 따른 시장의 반응을 실시간 대시보드로 리포팅하는 고성능 정책 시뮬레이터 포트폴리오입니다.

## 📍 주요 기능
- **FastAPI 백엔드**: 수천 명의 에이전트 행동을 한 틱(Tick) 안에 동기화하는 오케스트레이션 엔진.
- **Streamlit 프론트엔드**: 거시 경제 지표(GDP, 인플레이션 등)와 월드 맵 히트맵을 결합한 사이버펑크 스타일 대시보드.
- **정책 시뮬레이션**: 기본소득 지급 시나리오에 따른 저소득층 잔고 변화 및 물가 변동 실시간 시각화.

## 🛠️ 실행 방법

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 백엔드(FastAPI) 서버 실행
```bash
uvicorn backend:app --reload
```

### 3. 프론트엔드(Streamlit) 실행
```bash
streamlit run frontend.py
```

## 📈 시연 시나리오
1. **Tick 1~5**: 평범한 소비 패턴 유지.
2. **Tick 6**: 'RUN STRESS TEST' 버튼을 통한 기본소득(10만 원) 투입 정책 트리거.
3. **Tick 7~23**: 저소득층의 구매력 상승 및 시장 유동성 증가폭 관찰.
4. **Tick 24**: 최종 리포트 브리핑 및 시뮬레이션 종료.


<img width="1872" height="944" alt="캡처" src="https://github.com/user-attachments/assets/18d01608-6bc8-4aab-81a5-a744541d7b74" />
