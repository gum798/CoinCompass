/**
 * CoinCompass 피드백 시스템
 * RandomPassword 프로젝트 기반으로 구현
 */

class FeedbackSystem {
    constructor(config = {}) {
        this.isModalOpen = false;
        this.isSubmitting = false;
        this.language = this.detectLanguage();
        this.serviceId = config.service_id || '';    // EmailJS 서비스 ID
        this.templateId = config.template_id || 'template_feedback';  // EmailJS 템플릿 ID
        this.publicKey = config.public_key || '';    // EmailJS 공개키
        
        this.init();
    }

    init() {
        this.createHTML();
        this.createCSS();
        this.bindEvents();
        this.loadEmailJS();
    }

    detectLanguage() {
        const lang = navigator.language || navigator.userLanguage;
        return lang.startsWith('ko') ? 'ko' : 'en';
    }

    getTexts() {
        const texts = {
            ko: {
                buttonText: '💡 의견 제안',
                modalTitle: '의견을 들려주세요',
                modalSubtitle: 'CoinCompass 개선을 위한 소중한 의견을 남겨주세요',
                nameLabel: '이름',
                namePlaceholder: '이름을 입력해주세요 (선택사항)',
                emailLabel: '이메일',
                emailPlaceholder: '연락받을 이메일 (선택사항)',
                typeLabel: '의견 유형',
                types: {
                    feature: '새 기능 제안',
                    improvement: '기존 기능 개선',
                    bug: '버그 신고',
                    other: '기타 의견'
                },
                messageLabel: '의견 내용',
                messagePlaceholder: '암호화폐 분석 기능, UI/UX 개선사항, 버그 등 무엇이든 자유롭게 의견을 남겨주세요...',
                optional: '(선택사항)',
                required: '(필수)',
                submitButton: '의견 전송',
                submittingButton: '전송 중...',
                cancelButton: '취소',
                shortcut: 'Tab + Space/Enter로 빠른 전송',
                successMessage: '소중한 의견 감사합니다! 검토 후 반영하겠습니다.',
                errorMessage: '전송에 실패했습니다. 로컬 저장되었으니 나중에 다시 시도해주세요.',
                validationError: '의견 내용을 입력해주세요.',
                closeButton: '×'
            },
            en: {
                buttonText: '💡 Feedback',
                modalTitle: 'Share Your Thoughts',
                modalSubtitle: 'Help us improve CoinCompass with your valuable feedback',
                nameLabel: 'Name',
                namePlaceholder: 'Enter your name (optional)',
                emailLabel: 'Email',
                emailPlaceholder: 'Email for contact (optional)',
                typeLabel: 'Feedback Type',
                types: {
                    feature: 'New Feature Request',
                    improvement: 'Existing Feature Improvement',
                    bug: 'Bug Report',
                    other: 'Other Feedback'
                },
                messageLabel: 'Feedback Content',
                messagePlaceholder: 'Share your thoughts on crypto analysis features, UI/UX improvements, bugs, or anything else...',
                optional: '(optional)',
                required: '(required)',
                submitButton: 'Send Feedback',
                submittingButton: 'Sending...',
                cancelButton: 'Cancel',
                shortcut: 'Tab + Space/Enter for quick send',
                successMessage: 'Thank you for your valuable feedback! We\'ll review and implement it.',
                errorMessage: 'Failed to send. Saved locally, please try again later.',
                validationError: 'Please enter your feedback content.',
                closeButton: '×'
            }
        };
        return texts[this.language];
    }

    createHTML() {
        const texts = this.getTexts();
        
        // 플로팅 버튼
        const floatingButton = document.createElement('div');
        floatingButton.id = 'feedback-floating-btn';
        floatingButton.innerHTML = texts.buttonText;
        floatingButton.className = 'feedback-floating-btn';
        document.body.appendChild(floatingButton);

        // 모달 오버레이
        const modalOverlay = document.createElement('div');
        modalOverlay.id = 'feedback-modal-overlay';
        modalOverlay.className = 'feedback-modal-overlay';
        modalOverlay.innerHTML = `
            <div class="feedback-modal">
                <div class="feedback-modal-header">
                    <div>
                        <h3 class="feedback-modal-title">${texts.modalTitle}</h3>
                        <p class="feedback-modal-subtitle">${texts.modalSubtitle}</p>
                    </div>
                    <button class="feedback-close-btn" aria-label="Close">${texts.closeButton}</button>
                </div>
                <div class="feedback-modal-body">
                    <form id="feedback-form">
                        <div class="feedback-form-row">
                            <div class="feedback-form-group">
                                <label class="feedback-label">
                                    ${texts.nameLabel} <span class="feedback-optional">${texts.optional}</span>
                                </label>
                                <input type="text" 
                                       id="feedback-name" 
                                       class="feedback-input" 
                                       placeholder="${texts.namePlaceholder}">
                            </div>
                            <div class="feedback-form-group">
                                <label class="feedback-label">
                                    ${texts.emailLabel} <span class="feedback-optional">${texts.optional}</span>
                                </label>
                                <input type="email" 
                                       id="feedback-email" 
                                       class="feedback-input" 
                                       placeholder="${texts.emailPlaceholder}">
                            </div>
                        </div>
                        
                        <div class="feedback-form-group">
                            <label class="feedback-label">
                                ${texts.typeLabel} <span class="feedback-required">${texts.required}</span>
                            </label>
                            <select id="feedback-type" class="feedback-select">
                                <option value="feature">${texts.types.feature}</option>
                                <option value="improvement">${texts.types.improvement}</option>
                                <option value="bug">${texts.types.bug}</option>
                                <option value="other">${texts.types.other}</option>
                            </select>
                        </div>
                        
                        <div class="feedback-form-group">
                            <label class="feedback-label">
                                ${texts.messageLabel} <span class="feedback-required">${texts.required}</span>
                            </label>
                            <textarea id="feedback-message" 
                                      class="feedback-textarea" 
                                      placeholder="${texts.messagePlaceholder}" 
                                      rows="4" 
                                      required></textarea>
                        </div>
                        
                        <div class="feedback-form-actions">
                            <div class="feedback-shortcut-hint">${texts.shortcut}</div>
                            <div class="feedback-buttons">
                                <button type="button" class="feedback-btn feedback-btn-cancel">${texts.cancelButton}</button>
                                <button type="submit" class="feedback-btn feedback-btn-submit" id="feedback-submit">
                                    ${texts.submitButton}
                                </button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        `;
        document.body.appendChild(modalOverlay);

        // 토스트 컨테이너
        const toastContainer = document.createElement('div');
        toastContainer.id = 'feedback-toast-container';
        toastContainer.className = 'feedback-toast-container';
        document.body.appendChild(toastContainer);
    }

    createCSS() {
        const style = document.createElement('style');
        style.textContent = `
            /* 플로팅 버튼 */
            .feedback-floating-btn {
                position: fixed;
                bottom: 30px;
                right: 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 20px;
                border-radius: 50px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 600;
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
                z-index: 9998;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                animation: feedbackPulse 2s infinite;
                user-select: none;
            }

            .feedback-floating-btn:hover {
                transform: translateY(-2px) scale(1.05);
                box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4);
                animation: none;
            }

            @keyframes feedbackPulse {
                0%, 100% { transform: scale(1); opacity: 0.9; }
                50% { transform: scale(1.05); opacity: 1; }
            }

            /* 모달 오버레이 */
            .feedback-modal-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.6);
                backdrop-filter: blur(5px);
                display: none;
                align-items: center;
                justify-content: center;
                z-index: 9999;
                animation: feedbackFadeIn 0.3s ease;
            }

            .feedback-modal-overlay.active {
                display: flex;
            }

            @keyframes feedbackFadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            /* 모달 */
            .feedback-modal {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 20px;
                width: 90%;
                max-width: 600px;
                max-height: 80vh;
                overflow: hidden;
                box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.3);
                animation: feedbackSlideUp 0.3s ease;
                color: #333;
            }

            @keyframes feedbackSlideUp {
                from { transform: translateY(50px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }

            /* 모달 헤더 */
            .feedback-modal-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 25px 30px;
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
            }

            .feedback-modal-title {
                margin: 0 0 5px 0;
                font-size: 24px;
                font-weight: 700;
            }

            .feedback-modal-subtitle {
                margin: 0;
                font-size: 14px;
                opacity: 0.9;
                line-height: 1.4;
            }

            .feedback-close-btn {
                background: none;
                border: none;
                color: white;
                font-size: 24px;
                cursor: pointer;
                width: 30px;
                height: 30px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                transition: background 0.2s ease;
            }

            .feedback-close-btn:hover {
                background: rgba(255, 255, 255, 0.2);
            }

            /* 모달 바디 */
            .feedback-modal-body {
                padding: 30px;
                max-height: 60vh;
                overflow-y: auto;
            }

            /* 폼 스타일 */
            .feedback-form-row {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 20px;
            }

            .feedback-form-group {
                margin-bottom: 20px;
            }

            .feedback-label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #333;
                font-size: 14px;
            }

            .feedback-optional {
                color: #666;
                font-weight: 400;
                font-size: 12px;
            }

            .feedback-required {
                color: #e74c3c;
                font-weight: 400;
                font-size: 12px;
            }

            .feedback-input,
            .feedback-select,
            .feedback-textarea {
                width: 100%;
                padding: 12px 16px;
                border: 2px solid rgba(102, 126, 234, 0.2);
                border-radius: 12px;
                font-size: 14px;
                background: rgba(255, 255, 255, 0.8);
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
                box-sizing: border-box;
                color: #333;
            }

            .feedback-input:focus,
            .feedback-select:focus,
            .feedback-textarea:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
                background: rgba(255, 255, 255, 0.95);
            }

            .feedback-textarea {
                resize: vertical;
                min-height: 100px;
                font-family: inherit;
                line-height: 1.5;
            }

            /* 폼 액션 */
            .feedback-form-actions {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid rgba(102, 126, 234, 0.1);
            }

            .feedback-shortcut-hint {
                font-size: 12px;
                color: #666;
                font-style: italic;
            }

            .feedback-buttons {
                display: flex;
                gap: 12px;
            }

            .feedback-btn {
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s ease;
            }

            .feedback-btn-cancel {
                background: rgba(108, 117, 125, 0.1);
                color: #666;
                border: 1px solid rgba(108, 117, 125, 0.3);
            }

            .feedback-btn-cancel:hover {
                background: rgba(108, 117, 125, 0.2);
            }

            .feedback-btn-submit {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            }

            .feedback-btn-submit:hover:not(:disabled) {
                transform: translateY(-1px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
            }

            .feedback-btn-submit:disabled {
                opacity: 0.7;
                cursor: not-allowed;
                transform: none;
            }

            /* 토스트 */
            .feedback-toast-container {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                display: flex;
                flex-direction: column;
                gap: 10px;
            }

            .feedback-toast {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                padding: 16px 20px;
                border-radius: 12px;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.3);
                animation: feedbackToastSlide 0.3s ease;
                max-width: 350px;
                font-size: 14px;
                line-height: 1.4;
            }

            .feedback-toast.success {
                border-left: 4px solid #27ae60;
                color: #27ae60;
            }

            .feedback-toast.error {
                border-left: 4px solid #e74c3c;
                color: #e74c3c;
            }

            @keyframes feedbackToastSlide {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }

            /* 반응형 */
            @media (max-width: 768px) {
                .feedback-floating-btn {
                    bottom: 20px;
                    right: 20px;
                    padding: 10px 16px;
                    font-size: 13px;
                }

                .feedback-modal {
                    width: 95%;
                    margin: 20px;
                    max-height: 90vh;
                }

                .feedback-modal-header {
                    padding: 20px 25px;
                }

                .feedback-modal-title {
                    font-size: 20px;
                }

                .feedback-modal-body {
                    padding: 25px;
                }

                .feedback-form-row {
                    grid-template-columns: 1fr;
                    gap: 0;
                }

                .feedback-form-actions {
                    flex-direction: column;
                    gap: 15px;
                    align-items: stretch;
                }

                .feedback-shortcut-hint {
                    text-align: center;
                }

                .feedback-buttons {
                    justify-content: center;
                }

                .feedback-toast {
                    margin: 0 10px;
                    max-width: calc(100vw - 40px);
                }
            }
        `;
        document.head.appendChild(style);
    }

    bindEvents() {
        const floatingBtn = document.getElementById('feedback-floating-btn');
        const modalOverlay = document.getElementById('feedback-modal-overlay');
        const closeBtn = document.querySelector('.feedback-close-btn');
        const cancelBtn = document.querySelector('.feedback-btn-cancel');
        const form = document.getElementById('feedback-form');

        // 모달 열기
        floatingBtn.addEventListener('click', () => this.openModal());

        // 모달 닫기
        closeBtn.addEventListener('click', () => this.closeModal());
        cancelBtn.addEventListener('click', () => this.closeModal());
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) this.closeModal();
        });

        // ESC 키로 모달 닫기
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isModalOpen) {
                this.closeModal();
            }
        });

        // 폼 제출
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitFeedback();
        });

        // 단축키 (Tab + Space/Enter)
        document.addEventListener('keydown', (e) => {
            if (e.key === ' ' || e.key === 'Enter') {
                if (e.altKey || e.ctrlKey) {
                    e.preventDefault();
                    if (this.isModalOpen && !this.isSubmitting) {
                        this.submitFeedback();
                    } else if (!this.isModalOpen) {
                        this.openModal();
                    }
                }
            }
        });
    }

    loadEmailJS() {
        if (typeof emailjs === 'undefined') {
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/@emailjs/browser@4/dist/email.min.js';
            script.onload = () => {
                if (this.publicKey) {
                    emailjs.init(this.publicKey);
                }
            };
            document.head.appendChild(script);
        }
    }

    openModal() {
        const modalOverlay = document.getElementById('feedback-modal-overlay');
        modalOverlay.classList.add('active');
        this.isModalOpen = true;
        
        // 첫 번째 입력 필드에 포커스
        setTimeout(() => {
            const messageField = document.getElementById('feedback-message');
            if (messageField) messageField.focus();
        }, 300);
    }

    closeModal() {
        const modalOverlay = document.getElementById('feedback-modal-overlay');
        modalOverlay.classList.remove('active');
        this.isModalOpen = false;
        this.resetForm();
    }

    resetForm() {
        const form = document.getElementById('feedback-form');
        if (form) form.reset();
        this.isSubmitting = false;
        this.updateSubmitButton();
    }

    async submitFeedback() {
        if (this.isSubmitting) return;

        const message = document.getElementById('feedback-message').value.trim();
        if (!message) {
            this.showToast(this.getTexts().validationError, 'error');
            return;
        }

        this.isSubmitting = true;
        this.updateSubmitButton();

        const feedbackData = {
            name: document.getElementById('feedback-name').value || 'Anonymous',
            email: document.getElementById('feedback-email').value || 'No email provided',
            type: document.getElementById('feedback-type').value,
            message: message,
            page: window.location.href,
            userAgent: navigator.userAgent,
            timestamp: new Date().toISOString(),
            language: this.language
        };

        try {
            // 로컬 저장 (백업)
            this.saveToLocalStorage(feedbackData);

            // EmailJS로 이메일 전송 (설정되어 있을 경우)
            if (this.publicKey && typeof emailjs !== 'undefined') {
                await emailjs.send(this.serviceId, this.templateId, feedbackData);
            }

            this.showToast(this.getTexts().successMessage, 'success');
            this.closeModal();
        } catch (error) {
            console.error('Feedback submission error:', error);
            this.showToast(this.getTexts().errorMessage, 'error');
        } finally {
            this.isSubmitting = false;
            this.updateSubmitButton();
        }
    }

    updateSubmitButton() {
        const submitBtn = document.getElementById('feedback-submit');
        const texts = this.getTexts();
        
        if (this.isSubmitting) {
            submitBtn.disabled = true;
            submitBtn.textContent = texts.submittingButton;
        } else {
            submitBtn.disabled = false;
            submitBtn.textContent = texts.submitButton;
        }
    }

    saveToLocalStorage(data) {
        try {
            const saved = JSON.parse(localStorage.getItem('coincompass_feedback') || '[]');
            saved.push(data);
            // 최근 10개만 보관
            if (saved.length > 10) saved.splice(0, saved.length - 10);
            localStorage.setItem('coincompass_feedback', JSON.stringify(saved));
        } catch (error) {
            console.error('Local storage save error:', error);
        }
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('feedback-toast-container');
        const toast = document.createElement('div');
        toast.className = `feedback-toast ${type}`;
        toast.textContent = message;
        
        container.appendChild(toast);
        
        // 5초 후 자동 제거
        setTimeout(() => {
            if (toast.parentNode) {
                toast.style.animation = 'feedbackToastSlide 0.3s ease reverse';
                setTimeout(() => toast.remove(), 300);
            }
        }, 5000);
    }

    // 외부에서 토스트 메시지 표시용
    static showToast(message, type = 'info') {
        if (window.feedbackSystem) {
            window.feedbackSystem.showToast(message, type);
        }
    }
}

// 전역 초기화 (템플릿에서 설정 값 전달)
document.addEventListener('DOMContentLoaded', function() {
    const emailjsConfig = window.emailjsConfig || {};
    window.feedbackSystem = new FeedbackSystem(emailjsConfig);
});