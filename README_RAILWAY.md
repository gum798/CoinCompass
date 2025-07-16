# 🚂 Railway 배포 가이드

Railway는 Flask + Socket.IO를 완벽하게 지원하는 무료 호스팅 서비스입니다.

## 🎯 왜 Railway를 선택하나요?

### ✅ 장점:
- **완전한 백엔드 지원**: Flask + Socket.IO + 백그라운드 프로세스
- **무료 크레딧**: 월 $5 크레딧 제공 (소규모 프로젝트에 충분)
- **자동 배포**: GitHub 연동으로 푸시할 때마다 자동 배포
- **실시간 로그**: 애플리케이션 상태 실시간 모니터링
- **PostgreSQL/Redis**: 무료 데이터베이스 제공
- **SSL 자동 설정**: HTTPS 자동 적용
- **커스텀 도메인**: 무료로 도메인 연결 가능

### ❌ 단점:
- 무료 크레딧 소진 시 비용 발생
- Vercel보다 콜드 스타트 시간 길음

## 🚀 배포 방법

### 1. Railway 계정 생성
1. [Railway.app](https://railway.app) 접속
2. GitHub 계정으로 로그인
3. 무료 크레딧 $5 받기

### 2. 프로젝트 연결
```bash
# Railway CLI 설치
npm install -g @railway/cli

# 로그인
railway login

# 프로젝트 연결 (프로젝트 루트에서)
cd /Users/jhseo/Desktop/0020.project/coin
railway link
```

### 3. 환경 변수 설정
Railway 대시보드에서 설정:
```bash
PYTHONPATH=/app
FLASK_ENV=production
PORT=5001
```

### 4. 배포 실행
```bash
# 즉시 배포
railway up

# 또는 GitHub 연동 후 자동 배포
railway connect
```

## 📁 배포 파일 구조

```
coin/
├── Dockerfile              # Docker 설정
├── railway.json           # Railway 설정
├── requirements.txt       # Python 의존성
├── .dockerignore         # Docker 제외 파일
├── coincompass/
│   └── web/
│       └── app.py        # Flask 애플리케이션
└── README_RAILWAY.md     # 이 파일
```

## 🔧 설정 파일 설명

### `railway.json`
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python coincompass/web/app.py",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### `Dockerfile`
- Python 3.9 베이스 이미지
- 필요한 시스템 의존성 설치
- Flask 애플리케이션 설정

## 🌐 배포 후 기능

### ✅ 완전 지원 기능:
- **실시간 WebSocket**: Socket.IO 완벽 작동
- **백그라운드 모니터링**: 실시간 가격 추적
- **모의투자 시뮬레이션**: 포트폴리오 관리
- **시간대 차트**: 1시간~전체 기간 차트
- **자동 데이터 업데이트**: 30초마다 실시간 업데이트
- **알림 시스템**: 가격 변동 알림

### 🔄 실시간 기능:
- 가격 카드 자동 업데이트
- 기술적 지표 실시간 계산
- 거시경제 데이터 모니터링
- 신호 & 알림 실시간 표시

## 📊 모니터링 및 디버깅

### 실시간 로그 확인:
```bash
railway logs
```

### 서비스 상태 확인:
```bash
railway status
```

### 환경 변수 확인:
```bash
railway variables
```

## 🗃️ 데이터베이스 연결 (선택사항)

### PostgreSQL 추가:
```bash
railway add postgresql
```

### Redis 추가:
```bash
railway add redis
```

## 🎨 커스텀 도메인 설정

1. Railway 대시보드에서 "Custom Domain" 클릭
2. 도메인 입력 (예: `coincompass.yourdomain.com`)
3. DNS 설정에서 CNAME 레코드 추가

## 🔒 보안 설정

### 환경 변수로 API 키 관리:
```bash
railway variables set FRED_API_KEY=your_key_here
railway variables set SECRET_KEY=your_secret_key
```

### HTTPS 자동 설정:
Railway에서 자동으로 SSL 인증서 발급 및 HTTPS 적용

## 💰 비용 관리

### 무료 크레딧 모니터링:
- Railway 대시보드에서 사용량 확인
- 월 $5 크레딧으로 소규모 프로젝트 충분히 운영 가능

### 비용 절약 팁:
- 사용하지 않는 서비스 정지
- 리소스 사용량 최적화
- 필요시에만 데이터베이스 추가

## 🚨 트러블슈팅

### 배포 실패 시:
1. `railway logs` 확인
2. `requirements.txt` 의존성 확인
3. 환경 변수 설정 확인

### 애플리케이션 오류:
1. Railway 대시보드에서 재시작
2. 로그에서 오류 메시지 확인
3. 로컬 환경에서 테스트

## 📈 성능 최적화

### 메모리 사용량 최적화:
```python
# coincompass/web/app.py에서
import gc
gc.collect()  # 가비지 컬렉션 강제 실행
```

### 캐싱 구현:
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_price_data(coin_id):
    return api_provider.get_price_data(coin_id)
```

## 🎯 배포 체크리스트

- [ ] Railway 계정 생성 및 로그인
- [ ] GitHub 리포지토리 연결
- [ ] 환경 변수 설정 완료
- [ ] `railway.json` 설정 확인
- [ ] `Dockerfile` 설정 확인
- [ ] 배포 실행 (`railway up`)
- [ ] 배포 URL 접속 테스트
- [ ] 실시간 기능 작동 확인
- [ ] 모의투자 기능 테스트
- [ ] 로그 모니터링 설정

---

## 🌟 추가 서비스 비교

| 서비스 | 백엔드 지원 | Socket.IO | 무료 플랜 | 추천도 |
|--------|-------------|-----------|-----------|--------|
| Railway | ✅ | ✅ | $5/월 크레딧 | ⭐⭐⭐⭐⭐ |
| Render | ✅ | ✅ | 750시간/월 | ⭐⭐⭐⭐ |
| Fly.io | ✅ | ✅ | 160시간/월 | ⭐⭐⭐⭐ |
| Vercel | ❌ | ❌ | 무제한 | ⭐⭐ |
| Heroku | ✅ | ✅ | 없음 (유료) | ⭐⭐⭐ |

**결론**: CoinCompass 프로젝트에는 **Railway**가 가장 적합합니다! 🚂