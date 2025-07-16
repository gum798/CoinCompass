# CoinCompass Vercel 배포 가이드

## 🚀 Vercel 배포 방법

### 1. 사전 준비
```bash
# Vercel CLI 설치
npm install -g vercel

# 또는 yarn 사용
yarn global add vercel
```

### 2. 배포 실행
```bash
# 프로젝트 루트 디렉토리에서 실행
cd /path/to/coin/
vercel --prod
```

### 3. 배포 설정 파일

#### `vercel.json`
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ],
  "env": {
    "PYTHONPATH": "/var/task"
  },
  "functions": {
    "api/index.py": {
      "maxDuration": 30
    }
  }
}
```

#### `requirements.txt`
필요한 Python 패키지들이 모두 포함되어 있습니다.

### 4. 환경 변수 설정
Vercel 대시보드에서 다음 환경 변수를 설정하세요:
- `VERCEL_ENV=production`
- `FLASK_ENV=production`

### 5. 제한사항

#### Vercel에서 지원되지 않는 기능:
- **WebSocket (Socket.IO)**: 실시간 업데이트 기능 제한
- **백그라운드 스레드**: 실시간 모니터링 기능 제한
- **파일 시스템 쓰기**: 데이터 저장 제한

#### 대안 방안:
- **폴링 기반 업데이트**: 주기적으로 API 호출하여 데이터 새로고침
- **클라이언트 사이드 타이머**: JavaScript로 자동 새로고침 구현
- **외부 데이터베이스**: Vercel KV 또는 외부 DB 사용

### 6. 로컬 테스트

```bash
# 로컬에서 Vercel 환경 시뮬레이션
VERCEL_ENV=production python api/index.py

# 또는 Flask 앱 직접 실행
python coincompass/web/app.py
```

### 7. 배포 후 확인사항

#### ✅ 정상 작동 기능:
- 메인 대시보드 페이지 로드
- 가격 데이터 API 호출
- 모의투자 시뮬레이션
- 설정 페이지
- 시간대 차트 탭 전환

#### ⚠️ 제한된 기능:
- 실시간 WebSocket 연결
- 자동 데이터 업데이트
- 백그라운드 모니터링

### 8. 트러블슈팅

#### 배포 실패 시:
1. `requirements.txt` 확인
2. Python 버전 호환성 확인
3. 파일 경로 문제 확인
4. Vercel 로그 확인

#### 런타임 에러:
1. 환경 변수 설정 확인
2. API 키 설정 확인
3. 의존성 설치 확인

### 9. 성능 최적화

```javascript
// 클라이언트 사이드 자동 새로고침
setInterval(() => {
    if (!socket) { // Socket.IO가 없을 때만
        loadInitialData();
    }
}, 30000); // 30초마다 새로고침
```

### 10. 배포 URL
배포 완료 후 Vercel에서 제공하는 URL을 통해 접속 가능합니다.

---

## 📝 배포 체크리스트

- [ ] `vercel.json` 설정 완료
- [ ] `requirements.txt` 업데이트
- [ ] `api/index.py` 진입점 파일 생성
- [ ] Socket.IO 대체 방안 구현
- [ ] 환경 변수 설정
- [ ] 로컬 테스트 완료
- [ ] 배포 실행
- [ ] 배포 후 기능 테스트

---

## 🎯 다음 단계

1. **데이터베이스 연동**: Vercel KV 또는 외부 DB 사용
2. **실시간 기능 개선**: Server-Sent Events 또는 폴링 구현
3. **캐싱 최적화**: Redis 또는 Vercel Edge Cache 활용
4. **모니터링 설정**: 에러 추적 및 성능 모니터링