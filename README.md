# 🧭 CoinCompass - 스마트 암호화폐 투자 나침반

CoinCompass는 암호화폐 투자를 위한 종합적인 분석 도구입니다. 실시간 가격 모니터링, 기술적 지표 분석, 거시경제 데이터 연동, 가격 변동 요인 분석 등을 통해 데이터 기반의 투자 인사이트를 제공합니다.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![FRED](https://img.shields.io/badge/FRED-API-orange.svg)](https://fred.stlouisfed.org/)

## ✨ 주요 기능

### 📊 종합 시장 분석
- **실시간 가격 데이터**: CoinGecko, CoinPaprika API 연동
- **기술적 지표**: RSI, MACD, 볼린저 밴드, 이동평균 등
- **거시경제 지표**: FRED API 연동으로 연방기금금리, 실업률, GDP 등
- **온체인 데이터**: 네트워크 활동, 거래량, 주소 활동 분석
- **센티먼트 분석**: 공포탐욕지수, Reddit 감정 분석

### 📈 가격 변동 분석
- **요인 분석**: 가격 변동의 4가지 주요 요인 분석 (기술적, 센티먼트, 거시경제, 구조적)
- **일반인 친화적 설명**: 복잡한 분석을 쉬운 언어로 설명
- **투자 추천**: 신뢰도 기반 매수/매도/관망 추천
- **시각화**: 상세한 분석 차트 생성

### 🔄 백테스팅 및 검증
- **과거 데이터 검증**: Yahoo Finance 연동으로 예측 정확도 검증
- **성능 평가**: 변동 유형별, 요인별 효과성 측정
- **검증 보고서**: 시각적 성능 리포트 자동 생성

### 🔐 API 키 관리
- **암호화 저장**: FRED API 키 안전한 암호화 저장
- **자동 연동**: 저장된 키로 경제 지표 자동 수집
- **키 관리**: 저장, 조회, 삭제, 테스트 기능

## 🚀 빠른 시작

### 1. 설치

```bash
# 저장소 클론
git clone https://github.com/gum798/CoinCompass.git
cd CoinCompass

# 필요 라이브러리 설치
pip3 install -r requirements.txt
```

### 2. FRED API 키 설정 (선택사항)

경제 지표 분석을 위해 [FRED API 키](https://fred.stlouisfed.org/docs/api/api_key.html)를 발급받으세요.

### 3. 실행

```bash
python3 run_coincompass.py
```

### 4. 메뉴 사용법

```
🧭 CoinCompass 메뉴
==============================
1. 빠른 가격 체크           # 주요 코인 현재 가격 조회
2. 기술적 분석 데모          # RSI, MACD 등 기술적 지표
3. 종합 시장 분석           # 모든 분석 통합 (추천)
4. 가격 변동 요인 분석       # 가격 변동 원인 분석
5. 검증 보고서 생성         # 백테스팅 성능 검증
6. 실시간 모니터링          # 지속적 모니터링
7. API 키 관리 🔐         # FRED API 키 설정
8. 예제 실행              # 사용법 예제
0. 종료
==============================
```

## 📁 프로젝트 구조

### 🎯 핵심 실행 파일
```
run_coincompass.py          # 메인 실행 스크립트 - 여기서 시작하세요!
```

### 📦 coincompass/ (메인 패키지)

#### 🔍 analysis/ - 분석 모듈
```
backtesting.py              # 백테스팅 및 검증 시스템
                            # 과거 데이터로 예측 정확도 검증

macro.py                    # 거시경제 지표 분석 (FRED API)
                            # 연방기금금리, 실업률, GDP 등 경제 데이터

market_analyzer.py          # 종합 시장 분석기
                            # 모든 분석 모듈을 통합한 메인 분석기

onchain.py                  # 온체인 데이터 분석
                            # 비트코인/이더리움 네트워크 활동 분석

price_driver.py             # 가격 변동 요인 분석
                            # 가격이 오르고 내리는 이유를 분석

technical.py                # 기술적 지표 계산
                            # RSI, MACD, 볼린저 밴드 등
```

#### 🌐 api/ - API 연동
```
multi_provider.py           # 다중 API 제공자 관리
                            # 여러 암호화폐 API를 자동으로 전환

providers/
  ├── base.py              # API 제공자 기본 클래스
  ├── coingecko.py         # CoinGecko API 연동
  └── coinpaprika.py       # CoinPaprika API 연동
```

#### ⚙️ config/ - 설정 관리
```
api_keys.py                 # API 키 암호화 저장/관리
                            # FRED API 키를 안전하게 저장

settings.py                 # 시스템 설정 관리
                            # 모니터링 간격, 알림 설정 등
```

#### 📊 core/ - 핵심 데이터 관리
```
data_manager.py             # 데이터 수집 및 관리
                            # 모든 데이터 소스를 통합 관리

models.py                   # 데이터 모델 정의
                            # 가격, 지표, 분석 결과 데이터 구조
```

#### 📈 visualization/ - 시각화
```
enhanced_charts.py          # 고급 차트 생성
                            # 가격 분석, 요인 분석 시각화
```

#### 📋 reporting/ - 보고서 생성
```
validation_report.py        # 검증 보고서 자동 생성
                            # 백테스팅 결과를 시각적으로 표현
```

#### ⏰ monitoring/ - 모니터링
```
alerts.py                   # 알림 시스템
real_time.py                # 실시간 모니터링
```

#### 🛠️ utils/ - 유틸리티
```
formatters.py               # 데이터 포맷팅 (가격, 퍼센트 등)
logger.py                   # 로깅 시스템
validators.py               # 데이터 검증
```

### 📁 기타 디렉토리
```
charts/                     # 생성된 차트 이미지 저장
reports/                    # 분석 보고서 저장
examples/                   # 사용 예제 코드
config/                     # 시스템 설정 파일
archive/                    # 이전 버전 및 테스트 파일 보관
```

## 🔧 설정 파일 설명

### requirements.txt - 필수 라이브러리
```
pandas>=2.0.0              # 데이터 분석 및 처리
numpy>=1.20.0              # 수치 계산
matplotlib>=3.5.0          # 기본 차트 생성
seaborn>=0.11.0            # 고급 시각화
plotly>=5.0.0              # 인터랙티브 차트
requests>=2.25.0           # HTTP API 요청
yfinance>=0.2.0            # Yahoo Finance 데이터
cryptography>=40.0.0       # API 키 암호화
```

### config/settings.json - 시스템 설정
```json
{
  "api": {
    "timeout": 10,           # API 요청 타임아웃 (초)
    "retry_count": 3         # 실패 시 재시도 횟수
  },
  "monitoring": {
    "interval_seconds": 300, # 모니터링 간격 (5분)
    "coins": ["bitcoin", "ethereum", "ripple"]
  },
  "alerts": {
    "price_change_threshold": 5.0,    # 가격 변동 알림 기준 (%)
    "volume_change_threshold": 50.0   # 거래량 변동 알림 기준 (%)
  }
}
```

### monitor_config.json - 모니터링 상세 설정
```json
{
  "coins_to_monitor": ["bitcoin", "ethereum"],
  "check_interval_minutes": 5,
  "price_alerts": {
    "bitcoin": {"min": 40000, "max": 80000}
  }
}
```

## 💾 데이터 저장 위치

### API 키 저장 (자동 생성)
```
~/.coincompass/             # 사용자 홈 디렉토리에 자동 생성
├── api_keys.enc           # 암호화된 API 키 (cryptography 사용 시)
├── api_keys.json          # 평문 API 키 (fallback)
└── master.key             # 암호화 마스터 키
```

### 로그 및 캐시
```
coincompass/data/
├── cache/                 # API 응답 캐시 (성능 향상)
├── logs/                  # 시스템 운영 로그
└── reports/               # 자동 생성된 분석 보고서
```

## 🔗 지원하는 API 서비스

### 암호화폐 데이터
- **CoinGecko API**: 17,000+ 코인, 무료 티어 월 10,000 호출
- **CoinPaprika API**: 2,500+ 자산, 무료 티어 월 25,000 호출

### 경제 데이터
- **FRED API**: 미국 연방준비제도 경제 데이터 (무료)
- **Yahoo Finance**: 주식 시장 지수, 국채 수익률 (무료)

### 온체인 데이터
- **Blockstream API**: 비트코인 네트워크 통계 (무료)
- **Etherscan API**: 이더리움 네트워크 활동 (무료 티어)

## 📊 제공하는 분석 지표

### 기술적 지표
- **RSI (Relative Strength Index)**: 과매수/과매도 구간 감지 (>70: 과매수, <30: 과매도)
- **MACD**: 모멘텀 변화 추적 (골든크로스/데드크로스)
- **볼린저 밴드**: 변동성 및 지지/저항선 분석
- **이동평균**: 단기/장기 추세 분석 (5일, 20일, 50일)

### 거시경제 지표 (FRED API 필요)
- **연방기금금리 (FEDFUNDS)**: 미국 기준금리
- **실업률 (UNRATE)**: 경제 상황 지표
- **소비자물가지수 (CPIAUCSL)**: 인플레이션 측정
- **10년 국채 수익률 (GS10)**: 장기 금리 환경
- **VIX 지수**: 시장 변동성/불안감 측정

### 가격 변동 요인 (4가지 카테고리)
1. **기술적 요인**: 차트 패턴, 지지/저항선, 거래량 분석
2. **센티먼트 요인**: 투자자 심리, 소셜미디어 감정 분석
3. **거시경제 요인**: 금리, 인플레이션, 주요 경제 지표
4. **구조적 요인**: 규제 변화, 기술 발전, 제도적 변화

## 🎯 사용 예제

### 기본 사용법 (메뉴 3번 추천)
```python
# run_coincompass.py 실행 후 메뉴 3번 선택
# 또는 직접 코드 사용:

from coincompass.analysis.market_analyzer import MarketAnalyzer
from coincompass.api.multi_provider import MultiAPIProvider

# 시장 분석기 초기화
analyzer = MarketAnalyzer()
api = MultiAPIProvider()

# 비트코인 종합 분석
btc_data = api.get_price_data("bitcoin")
analysis = analyzer.get_comprehensive_analysis("bitcoin")

print(f"현재가: ${btc_data.price:,.2f}")
print(f"추천: {analysis['summary']['recommendation']}")
print(f"신뢰도: {analysis['summary']['confidence']:.1%}")
```

### FRED API 활용 (자동으로 저장된 키 사용)
```python
from coincompass.analysis.macro import MacroeconomicAnalyzer

# 거시경제 분석 (저장된 FRED API 키 자동 사용)
macro_analyzer = MacroeconomicAnalyzer()
indicators = macro_analyzer.get_economic_indicators()

if 'fed_rate' in indicators:
    print(f"연방기금금리: {indicators['fed_rate']['value']}%")
if 'unemployment' in indicators:
    print(f"실업률: {indicators['unemployment']['value']}%")
```

### 가격 변동 요인 분석
```python
from coincompass.analysis.price_driver import PriceDriverAnalyzer

analyzer = PriceDriverAnalyzer()
analysis = analyzer.analyze_price_movement(
    coin_id="bitcoin",
    current_price=45000,
    price_24h_ago=43000
)

print(f"변동 유형: {analysis.movement_type}")
print(f"주요 원인: {analysis.summary}")
print(f"투자 추천: {analysis.recommendation}")
```

## 📈 개발 로드맵

### ✅ v1.0 (현재 완료)
- 다중 API 시스템
- 실시간 모니터링
- 종합 시장 분석
- 기술적 지표 분석
- 거시경제 지표 연동 (FRED)
- 가격 변동 요인 분석
- 백테스팅 및 검증
- API 키 관리 시스템

### 🔄 v1.1 (계획 중)
- 웹 대시보드 개발
- 포트폴리오 추적 기능
- 알림 시스템 확장 (이메일, 텔레그램)
- 추가 기술적 지표

### 🚀 v2.0 (향후 계획)
- AI 기반 가격 예측 모델
- 모바일 앱 개발
- 다국어 지원
- 클라우드 배포

## 🛠️ 개발 및 확장 가이드

### 새로운 API 제공자 추가
1. `coincompass/api/providers/` 에 새 파일 생성
2. `BaseProvider` 클래스 상속
3. 필수 메서드 구현: `get_price()`, `get_historical_data()`
4. `multi_provider.py`에 등록

### 새로운 분석 모듈 추가
1. `coincompass/analysis/` 에 새 분석 모듈 생성
2. `MarketAnalyzer`에 통합
3. 시각화 및 보고서 기능 추가
4. 메뉴 시스템에 연동

## 🔐 보안 및 개인정보 보호

- **API 키 암호화**: cryptography 라이브러리로 안전한 저장
- **파일 권한**: 설정 파일은 사용자만 접근 가능 (chmod 600)
- **로그 보안**: API 키나 민감한 정보는 로그에 기록하지 않음
- **SSL 검증**: HTTPS 연결 시 인증서 검증 (환경에 따라 조정)

## 📈 성능 최적화

- **API 캐싱**: 중복 요청 방지를 위한 응답 캐싱
- **요청 제한**: API 레이트 리미트 준수
- **병렬 처리**: 다중 API 동시 호출로 속도 향상
- **에러 처리**: 견고한 예외 처리 및 자동 재시도

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙏 감사의 말

- **CoinGecko & CoinPaprika**: 무료 암호화폐 데이터 제공
- **FRED (Federal Reserve Economic Data)**: 경제 지표 데이터 무료 제공
- **Yahoo Finance**: 금융 시장 데이터 제공
- **오픈소스 커뮤니티**: 지속적인 피드백과 개선 제안

## 📞 지원 및 문의

- **GitHub Issues**: [프로젝트 이슈 보고](https://github.com/gum798/CoinCompass/issues)
- **프로젝트 링크**: [https://github.com/gum798/CoinCompass](https://github.com/gum798/CoinCompass)
- **문서**: 이 README와 `coincompass/docs/` 디렉토리 참조

## 💡 사용 팁

1. **처음 사용**: `python3 run_coincompass.py` → 메뉴 1번으로 시작
2. **경제 분석**: FRED API 키 설정 후 메뉴 3번 사용 (추천)
3. **변동 분석**: 메뉴 4번으로 가격 변동 원인 파악
4. **성능 검증**: 메뉴 5번으로 분석 시스템 정확도 확인
5. **지속 모니터링**: 메뉴 6번으로 실시간 추적

---

**⚠️ 투자 책임 고지**: CoinCompass는 정보 제공 목적의 도구입니다. 모든 투자 결정은 사용자의 책임이며, 투자 전 충분한 연구와 전문가 상담을 권장합니다.

**🚀 CoinCompass와 함께 스마트한 암호화폐 투자를 시작하세요!**