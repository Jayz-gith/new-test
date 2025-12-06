# 🚀 Streamlit Cloud 배포 체크리스트

## 배포 전 확인 사항

### ✅ 필수 파일 확인
- [x] `app.py` - 메인 앱 파일 (루트 디렉토리)
- [x] `requirements.txt` - Python 의존성 목록
- [x] `.streamlit/config.toml` - Streamlit 설정
- [x] `.gitignore` - secrets.toml 제외 확인
- [x] `data/` 폴더 및 초기 JSON 파일들

### ✅ API 키 준비
- [ ] Google Gemini API Key 발급 완료
- [ ] GitHub Personal Access Token 발급 완료 (repo 권한 필요)

### ✅ GitHub 저장소 확인
- [x] 저장소 URL: `https://github.com/Jayz-gith/new-test.git`
- [x] 모든 파일이 커밋 및 푸시 완료
- [x] `.streamlit/secrets.toml`이 GitHub에 업로드되지 않았는지 확인

## 배포 단계

### 1. Streamlit Cloud 접속
1. [Streamlit Cloud](https://share.streamlit.io/) 접속
2. GitHub 계정으로 로그인

### 2. 새 앱 생성
1. "New app" 버튼 클릭
2. GitHub 리포지토리 선택: `Jayz-gith/new-test`
3. 브랜치: `main`
4. **메인 파일 경로**: `app.py` ⚠️ **중요: 루트에 있는 `app.py`를 지정**
   - 만약 폴더 구조가 다르다면 실제 경로를 정확히 입력
   - 예: `app.py` (루트에 있을 경우)
   - ❌ 절대 `test/requirements.txt` 같은 경로를 입력하지 마세요

### 3. Advanced Settings 설정
1. **Advanced settings** 버튼 클릭
2. **Secrets** 섹션에 다음 내용 입력:

```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
GITHUB_TOKEN = "your_github_token_here"
REPO_NAME = "Jayz-gith/new-test"
```

**중요**: 
- `REPO_NAME`은 정확히 `"Jayz-gith/new-test"` 형식으로 입력
- 따옴표 포함하여 입력

### 4. 배포 실행
1. **Deploy!** 버튼 클릭
2. 배포 진행 상황 확인
3. 배포 완료 후 제공되는 URL로 접속

## 배포 후 확인

### ✅ 기능 테스트
- [ ] 앱이 정상적으로 로드되는지 확인
- [ ] 뉴스룸 페이지가 표시되는지 확인
- [ ] 대시보드 페이지가 표시되는지 확인
- [ ] RSS 피드 추가/삭제 기능 테스트
- [ ] 뉴스 수집 및 AI 분석 기능 테스트
- [ ] GitHub에 데이터가 저장되는지 확인

### ✅ 에러 확인
- [ ] Streamlit Cloud 로그에서 에러 확인
- [ ] 브라우저 콘솔에서 에러 확인
- [ ] API 키가 올바르게 설정되었는지 확인

## 트러블슈팅

### 앱이 로드되지 않는 경우
1. Streamlit Cloud 로그 확인
2. `requirements.txt`의 의존성 확인
3. `app.py` 파일 경로 확인

### GitHub 연동이 안 되는 경우
1. `GITHUB_TOKEN`이 올바른지 확인
2. `REPO_NAME`이 정확한 형식인지 확인 (`"username/repo-name"`)
3. GitHub Token에 `repo` 권한이 있는지 확인

### API 에러가 발생하는 경우
1. `GEMINI_API_KEY`가 올바른지 확인
2. API 키의 할당량 확인
3. 모델 디버깅 정보에서 사용 가능한 모델 확인

## 유용한 링크
- [Streamlit Cloud 문서](https://docs.streamlit.io/streamlit-community-cloud)
- [GitHub Personal Access Token 생성](https://github.com/settings/tokens)
- [Google AI Studio](https://aistudio.google.com/app/apikey)

