# CoinCompass API 사용량 최적화 가이드

CoinCompass는 외부 API 사용량을 최소화하면서도 효율적인 모니터링을 제공하도록 설계되었습니다.

## 🎯 핵심 아이디어

**"초기에 한 번, 그 후로는 10~30분 간격으로 호출"**

- **실시간 느낌**: 30초마다 UI 업데이트 (기존 데이터 재사용)
- **API 절약**: 30분마다만 실제 API 호출
- **무료 한도 보호**: 하루 최대 48회 호출 (30분 간격 기준)

## ⚙️ 환경설정 파라미터

### 기본 설정값
```bash
# 모니터링 체크 간격 (WebSocket 업데이트)
MONITORING_INTERVAL=30          # 30초마다 상태 체크

# API 실제 호출 간격 (외부 API 호출)
API_CALL_INTERVAL=1800          # 30분(1800초)마다 API 호출

# 초기 지연 시간
MONITORING_INITIAL_DELAY=60     # 시작 후 1분 뒤 첫 API 호출

# API 호출 활성화
API_CALLS_ENABLED=true          # false로 설정하면 완전 중단
```

### 사용량별 권장 설정

#### 🟢 매우 절약 모드 (하루 24회 호출)
```bash
API_CALL_INTERVAL=3600    # 1시간마다
MONITORING_INTERVAL=60    # 1분마다 상태 체크
```

#### 🟡 균형 모드 (하루 48회 호출) - **권장**
```bash
API_CALL_INTERVAL=1800    # 30분마다
MONITORING_INTERVAL=30    # 30초마다 상태 체크
```

#### 🟠 적극적 모드 (하루 144회 호출)
```bash
API_CALL_INTERVAL=600     # 10분마다
MONITORING_INTERVAL=15    # 15초마다 상태 체크
```

#### 🔴 실시간 모드 (하루 288회 호출)
```bash
API_CALL_INTERVAL=300     # 5분마다
MONITORING_INTERVAL=10    # 10초마다 상태 체크
```

## 🔄 동작 방식

### 1. 초기 실행
1. 앱 시작 → `MONITORING_INITIAL_DELAY` 시간 대기
2. 첫 번째 API 호출 실행 (모든 데이터 수집)
3. 수집된 데이터를 메모리에 저장

### 2. 정규 모니터링
1. `MONITORING_INTERVAL`마다 모니터링 루프 실행
2. 마지막 API 호출 시간 확인
3. `API_CALL_INTERVAL` 경과 시에만 새로운 API 호출
4. 그 외에는 기존 데이터 재사용하여 WebSocket 전송

### 3. 사용자 경험
- **실시간 느낌**: WebSocket으로 30초마다 데이터 전송
- **상태 표시**: API 호출 여부를 대시보드에 표시
- **부드러운 UX**: 기존 데이터로도 차트와 카드 업데이트

## 📊 API 사용량 계산

### CoinGecko API (무료 플랜)
- **한도**: 월 10,000-30,000회 (API에 따라 다름)
- **30분 간격**: 하루 48회 × 30일 = 1,440회/월
- **1시간 간격**: 하루 24회 × 30일 = 720회/월

### FRED API (연준 경제 데이터)
- **한도**: 하루 120,000회 (충분함)
- **거시경제 데이터는 자주 변경되지 않음**

### yfinance (Yahoo Finance)
- **한도**: 명시적 제한 없음 (과도한 호출 시 차단 가능)
- **권장**: 1분 이상 간격

## 🎮 실제 사용 시나리오

### 시나리오 1: 데이터 절약형 사용자
```bash
# .env 설정
API_CALL_INTERVAL=3600        # 1시간마다 호출
MONITORING_INTERVAL=120       # 2분마다 상태 체크
API_CALLS_ENABLED=true

# 결과: 하루 24회 호출, 매우 안전
```

### 시나리오 2: 일반 사용자 (권장)
```bash
# .env 설정
API_CALL_INTERVAL=1800        # 30분마다 호출
MONITORING_INTERVAL=30        # 30초마다 상태 체크
API_CALLS_ENABLED=true

# 결과: 하루 48회 호출, 실시간 느낌 유지
```

### 시나리오 3: 개발/테스트 환경
```bash
# .env 설정
API_CALL_INTERVAL=300         # 5분마다 호출
MONITORING_INTERVAL=10        # 10초마다 상태 체크
API_CALLS_ENABLED=true

# 결과: 빠른 업데이트, 개발 시 편리
```

### 시나리오 4: API 호출 완전 중단
```bash
# .env 설정
API_CALLS_ENABLED=false       # API 호출 중단

# 결과: 기존 더미 데이터만 사용, 0회 호출
```

## 🛠️ 모니터링 및 디버깅

### 로그 확인
```bash
# API 호출 상태 확인
tail -f logs/coincompass.log | grep "API 호출"

# 모니터링 루프 상태 확인
tail -f logs/coincompass.log | grep "모니터링"
```

### 대시보드 상태 표시
- **녹색 점**: API 호출 완료 (최신 데이터)
- **파란색 점**: API 대기 중 (기존 데이터 사용)
- **빨간색 점**: API 호출 실패

### WebSocket 메시지 구조
```javascript
{
  "prices": {...},
  "market_analysis": {...},
  "macro_data": {...},
  "timestamp": "2025-07-23T...",
  "api_call_made": true/false    // 이번에 API 호출했는지 표시
}
```

## 🚨 주의사항

1. **첫 실행 시**: 모든 API를 호출하므로 사용량이 일시적으로 증가
2. **네트워크 오류**: API 호출 실패 시 기존 데이터 유지
3. **시간 동기화**: 서버 시간과 API 호출 간격이 정확해야 함
4. **메모리 사용량**: 데이터를 메모리에 캐시하므로 적절한 서버 메모리 필요

## 📈 성능 최적화 팁

1. **개발 환경**: 짧은 간격으로 설정하여 빠른 테스트
2. **운영 환경**: 긴 간격으로 설정하여 안정적 운영
3. **모바일 환경**: WebSocket 재연결 고려하여 적절한 간격 설정
4. **서버 리소스**: CPU/메모리 사용량 모니터링

---

이 설정을 통해 CoinCompass는 무료 API 한도 내에서도 실시간에 가까운 사용자 경험을 제공할 수 있습니다.