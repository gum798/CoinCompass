# 🧭 CoinCompass

**스마트 암호화폐 투자 나침반 - 시장의 방향을 제시하는 AI 기반 분석 플랫폼**

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![API](https://img.shields.io/badge/API-Multi--Provider-orange.svg)](docs/api.md)

## 📖 소개

CoinCompass는 암호화폐 투자자들을 위한 종합적인 시장 분석 및 모니터링 플랫폼입니다. 
다양한 무료 API를 활용하여 실시간 가격 추적, 기술적 분석, 센티먼트 분석을 제공하며, 
투자 결정에 필요한 모든 정보를 한 곳에서 확인할 수 있습니다.

## ✨ 주요 기능

### 📊 실시간 모니터링
- **다중 API 로테이션**: CoinPaprika, CoinGecko 등 여러 API 자동 전환
- **TOP 10 코인 추적**: 시가총액 상위 코인 30분 간격 모니터링
- **실시간 알림**: 가격 변동, RSI 과매수/과매도 신호

### 📈 기술적 분석
- **핵심 지표**: RSI, MACD, 볼린저 밴드, 이동평균선
- **매매 신호**: 골든크로스, 데드크로스 자동 감지
- **종합 판단**: 여러 지표 조합으로 매수/매도/관망 권장

### 📊 시각화 & 보고서
- **차트 생성**: 6개 패널 종합 시장 분석 차트
- **자동 보고서**: 시장 현황, TOP 퍼포머, 투자 권장사항
- **이미지 출력**: 고화질 PNG 차트 자동 저장

### 🔍 다차원 분석
- **온체인 지표**: 네트워크 활동, 고래 움직임
- **거시경제**: 금리, 인플레이션, 달러 지수
- **센티먼트**: 공포탐욕지수, 소셜미디어 분석

## 🚀 빠른 시작

### 필요 조건
- Python 3.12+
- pip (패키지 관리자)

### 설치 및 실행

```bash
# 저장소 클론
git clone https://github.com/gum798/CoinCompass.git
cd CoinCompass

# 가상환경 생성 및 활성화
python -m venv coin_env
source coin_env/bin/activate  # Windows: coin_env\\Scripts\\activate

# 의존성 설치
pip install -r requirements.txt

# 기본 분석 실행
python main.py

# 실시간 모니터링
python real_time_monitor.py

# TOP 10 분석 및 차트 생성
python top10_monitor.py
```

## 📁 프로젝트 구조

```
CoinCompass/
├── 📊 crypto_data.py              # 기본 데이터 수집
├── 🔄 multi_api_manager.py        # 다중 API 관리
├── 📈 enhanced_crypto_data.py     # 향상된 데이터 수집
├── 🔧 technical_indicators.py     # 기술적 지표 계산
├── 👁️ real_time_monitor.py        # 실시간 모니터링
├── 🏆 top10_monitor.py            # TOP 10 코인 분석
├── 🎨 demo_charts.py              # 차트 생성 데모
├── 🧠 price_influence_factors.py  # 가격 영향 요소 분석
├── 📊 charts/                     # 생성된 차트 이미지
├── 📋 reports/                    # 분석 보고서
└── ⚙️ monitor_config.json         # 모니터링 설정
```

## 📊 사용 예시

### 기본 분석
```python
from enhanced_crypto_data import EnhancedCryptoAPI

api = EnhancedCryptoAPI()

# 비트코인 현재 가격
btc_price = api.get_price("bitcoin")
print(f"BTC: ${btc_price['bitcoin']['usd']:,.2f}")

# 상위 10개 코인
top_coins = api.get_top_coins(10)
print(top_coins[['name', 'current_price', 'price_change_percentage_24h']])
```

### 차트 생성
```python
from demo_charts import create_demo_market_overview

# 시장 개요 차트 생성
chart_path = create_demo_market_overview(sample_data)
print(f"차트 저장: {chart_path}")
```

## 🔧 설정

### 모니터링 설정 (`monitor_config.json`)
```json
{
  "coins": ["bitcoin", "ethereum", "ripple"],
  "interval": 1800,
  "rsi_oversold": 30,
  "rsi_overbought": 70,
  "price_change_threshold": 5.0,
  "enable_alerts": true
}
```

### API 설정
- **CoinPaprika**: API 키 불필요 (월 20,000 호출)
- **CoinGecko**: 무료 등록 (월 10,000 호출)
- **Alternative.me**: 공포탐욕지수 무료

## 📈 분석 지표

### 기술적 지표
- **RSI**: 과매수/과매도 신호
- **MACD**: 모멘텀 변화 추적
- **볼린저 밴드**: 변동성 및 지지/저항
- **이동평균**: 5일/20일 트렌드

### 시장 지표
- **시가총액 분포**: 상위 코인 점유율
- **거래량 분석**: 24시간 거래 활동
- **가격 변동**: 일간 수익률 분포
- **안정성 스코어**: RSI + 가격 안정성

## 🔮 로드맵

### v1.0 (현재)
- ✅ 다중 API 시스템
- ✅ 실시간 모니터링
- ✅ 차트 생성
- ✅ 기술적 분석

### v1.1 (계획)
- 🔄 웹 대시보드
- 🔄 백테스팅
- 🔄 포트폴리오 추적
- 🔄 알림 확장

### v2.0 (향후)
- 🤖 AI 예측 모델
- 📱 모바일 앱
- 🌐 다국어 지원
- ☁️ 클라우드 배포

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 연락처

- **GitHub**: [@gum798](https://github.com/gum798)
- **프로젝트 링크**: [https://github.com/gum798/CoinCompass](https://github.com/gum798/CoinCompass)

## 🙏 감사의 말

- [CoinPaprika](https://coinpaprika.com/) - 무료 암호화폐 API
- [CoinGecko](https://coingecko.com/) - 시장 데이터 제공
- [Alternative.me](https://alternative.me/) - 공포탐욕지수

---

**⚠️ 면책 조항**: CoinCompass는 교육 및 정보 제공 목적으로만 사용됩니다. 투자 결정은 개인의 책임이며, 금전적 손실에 대한 책임을 지지 않습니다.