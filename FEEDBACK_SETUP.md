# CoinCompass 피드백 시스템 설정 가이드

CoinCompass에 RandomPassword와 동일한 피드백 시스템이 구현되었습니다. 이메일 전송 기능을 활성화하려면 EmailJS 설정이 필요합니다.

## 📧 EmailJS 설정 방법

### 1. EmailJS 계정 생성
1. [EmailJS 웹사이트](https://www.emailjs.com/)에 방문
2. "Sign Up" 클릭하여 무료 계정 생성
3. 이메일 인증 완료

### 2. 이메일 서비스 연결
1. Dashboard → "Email Services" 클릭
2. "Add New Service" 버튼 클릭
3. Gmail, Outlook, Yahoo 등 원하는 서비스 선택
4. 이메일 계정 정보 입력 및 연결 테스트

### 3. 이메일 템플릿 생성
1. Dashboard → "Email Templates" 클릭
2. "Create New Template" 버튼 클릭
3. 템플릿 ID: `template_feedback`
4. 다음 템플릿 사용:

```html
Subject: [CoinCompass] 새로운 사용자 피드백

안녕하세요,

CoinCompass에서 새로운 사용자 피드백이 접수되었습니다.

📝 피드백 정보:
- 이름: {{name}}
- 이메일: {{email}}
- 유형: {{type}}
- 작성시간: {{timestamp}}
- 페이지: {{page}}
- 언어: {{language}}

💬 내용:
{{message}}

🔧 시스템 정보:
{{userAgent}}

---
CoinCompass 피드백 시스템
```

### 4. 공개키 및 서비스 ID 확인
1. Dashboard → "Integration" 클릭
2. "Public Key" 복사
3. "Email Services"에서 Service ID 복사

### 5. CoinCompass에 설정 적용

#### 방법 1: JavaScript 파일 직접 수정
`/coincompass/web/static/js/feedback.js` 파일의 다음 부분 수정:

```javascript
// 생성자 내부에서
this.serviceId = 'your_service_id_here';     // EmailJS 서비스 ID 입력
this.templateId = 'template_feedback';       // 위에서 만든 템플릿 ID
this.publicKey = 'your_public_key_here';     // EmailJS 공개키 입력
```

#### 방법 2: 환경변수 사용 (권장)
`.env` 파일에 다음 추가:
```
EMAILJS_SERVICE_ID=your_service_id_here
EMAILJS_TEMPLATE_ID=template_feedback
EMAILJS_PUBLIC_KEY=your_public_key_here
```

Flask 애플리케이션에서 템플릿에 전달:
```python
# app.py에 추가
import os
from dotenv import load_dotenv

load_dotenv()

@app.route('/')
def index():
    emailjs_config = {
        'service_id': os.getenv('EMAILJS_SERVICE_ID', ''),
        'template_id': os.getenv('EMAILJS_TEMPLATE_ID', 'template_feedback'),
        'public_key': os.getenv('EMAILJS_PUBLIC_KEY', '')
    }
    return render_template('dashboard.html', 
                         coins=monitor_settings['coins'],
                         settings=monitor_settings,
                         emailjs=emailjs_config)
```

## 🎯 기능 특징

### ✅ 구현된 기능
- **글래스모피즘 디자인**: RandomPassword와 동일한 현대적 UI
- **다국어 지원**: 한국어/영어 자동 감지
- **이중 저장**: localStorage 백업 + 이메일 전송
- **단축키 지원**: Ctrl/Alt + Space/Enter로 빠른 전송
- **반응형 디자인**: 모바일/데스크톱 최적화
- **실시간 토스트**: 성공/실패 알림

### 📝 수집되는 데이터
- 사용자 이름 (선택사항)
- 이메일 주소 (선택사항)
- 피드백 유형 (새기능/개선/버그/기타)
- 피드백 내용 (필수)
- 현재 페이지 URL
- 브라우저 정보
- 작성 시간
- 언어 설정

### 🔧 사용 방법
1. **피드백 버튼**: 우하단 "💡 의견 제안" 버튼 클릭
2. **단축키**: `Ctrl + Space` 또는 `Alt + Enter`로 빠른 접근
3. **폼 작성**: 필수 항목(의견 내용) 입력
4. **전송**: "의견 전송" 버튼 클릭 또는 `Ctrl + Enter`

## 🚀 테스트 방법

### 로컬 테스트
1. CoinCompass 웹 애플리케이션 실행
2. 우하단 피드백 버튼 확인
3. 모달 열기/닫기 테스트
4. 폼 검증 테스트 (빈 내용 전송 시도)
5. 성공적인 전송 테스트

### EmailJS 연결 테스트
1. EmailJS 설정 완료 후
2. 실제 피드백 전송
3. 설정한 이메일 주소로 수신 확인
4. 브라우저 개발자 도구에서 오류 확인

## 📊 월 사용량 제한
- **EmailJS 무료 플랜**: 월 200건
- **로컬 저장**: 제한 없음 (최근 10개 보관)

## 🔒 보안 및 개인정보
- 클라이언트 사이드 처리 (서버리스)
- 이메일 주소는 선택사항
- 로컬 저장은 사용자 브라우저에만 저장
- HTTPS 사용 권장

## 🐛 문제 해결

### 피드백 버튼이 보이지 않을 때
- 브라우저 개발자 도구에서 JavaScript 오류 확인
- `feedback.js` 파일 로드 확인
- CSS z-index 충돌 확인

### 이메일이 전송되지 않을 때
- EmailJS 설정 정보 재확인
- 네트워크 연결 상태 확인
- 브라우저 콘솔에서 오류 메시지 확인
- EmailJS 대시보드에서 사용량 한도 확인

### 모달이 제대로 동작하지 않을 때
- Bootstrap 버전 호환성 확인
- CSS 충돌 확인
- JavaScript 이벤트 바인딩 확인

---

이 피드백 시스템은 RandomPassword 프로젝트와 동일한 수준의 기능과 디자인을 제공합니다. 사용자 경험과 피드백 수집 효율성을 극대화하도록 설계되었습니다.