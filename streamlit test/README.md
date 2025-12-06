# 📰 IT 뉴스룸 - Streamlit 앱

Gemini AI를 활용한 IT 뉴스 수집 및 분석 플랫폼입니다.

## 🚀 주요 기능

- **뉴스 수집**: RSS 피드를 통해 IT 뉴스 자동 수집
- **AI 분석**: Google Gemini AI를 활용한 뉴스 요약 및 트렌드 분석
- **날짜별 정리**: 수집된 뉴스를 날짜별로 정리하여 표시
- **방문자 통계**: 앱 방문자 수 추적
- **GitHub 연동**: Streamlit Cloud에서도 데이터 영구 저장 (GitHub API 사용)

## 📋 사전 요구사항

1. **Google Gemini API Key**: [Google AI Studio](https://aistudio.google.com/app/apikey)에서 발급
2. **GitHub Personal Access Token** (선택사항): Streamlit Cloud 배포 시 필요
   - GitHub Settings -> Developer settings -> Personal access tokens -> Tokens (classic)
   - `repo` 권한 필요

## 🛠️ 로컬 설치 및 실행

1. 저장소 클론:
```bash
git clone https://github.com/Jayz-gith/new-test.git
cd new-test
```

2. 의존성 설치:
```bash
pip install -r requirements.txt
```

3. API 키 설정:
`.streamlit/secrets.toml` 파일 생성:
```toml
GEMINI_API_KEY = "your_gemini_api_key"
# 로컬 테스트 시 아래는 주석 처리 가능
# GITHUB_TOKEN = "your_github_token"
# REPO_NAME = "username/repository-name"
```

4. 앱 실행:
```bash
streamlit run app.py
```

## ☁️ Streamlit Cloud 배포

1. [Streamlit Cloud](https://share.streamlit.io/)에 접속하여 로그인
2. "New app" 클릭
3. GitHub 리포지토리 선택: `Jayz-gith/new-test`
4. **Advanced settings** 클릭
5. **Secrets** 섹션에 다음 내용 입력:
```toml
GEMINI_API_KEY = "your_gemini_api_key"
GITHUB_TOKEN = "your_github_token"
REPO_NAME = "Jayz-gith/new-test"
```
6. **Deploy!** 클릭

## 📁 프로젝트 구조

```
new-test/
├── .streamlit/
│   ├── config.toml          # Streamlit 설정
│   └── secrets.toml         # API 키 (로컬용, Git 제외)
├── data/
│   ├── feeds.json           # RSS 피드 목록
│   ├── news_data.json       # 분석된 뉴스 데이터
│   └── stats.json           # 방문자 통계
├── app.py                   # 메인 앱 파일
├── data_manager.py          # GitHub 연동 및 데이터 관리
├── requirements.txt         # Python 의존성
├── plan.md                  # 프로젝트 계획서
└── README.md                # 프로젝트 설명서
```

## 🔧 주요 모듈

### `app.py`
- Streamlit 메인 앱
- 뉴스룸 및 대시보드 UI
- Gemini AI를 활용한 뉴스 분석

### `data_manager.py`
- GitHub API를 통한 데이터 저장/로드
- 로컬 및 클라우드 환경 자동 감지
- JSON 데이터 관리

## 📝 사용 방법

1. **뉴스룸 (Home)**: 날짜별로 수집된 뉴스와 AI 요약 확인
2. **대시보드 (Admin)**:
   - 방문자 통계 확인
   - RSS 피드 추가/삭제
   - 뉴스 수집 및 AI 분석 실행

## 🔒 보안 주의사항

- `.streamlit/secrets.toml` 파일은 절대 GitHub에 커밋하지 마세요
- `.gitignore`에 포함되어 있어 자동으로 제외됩니다
- Streamlit Cloud의 Secrets는 암호화되어 저장됩니다

## 🐛 트러블슈팅

### 모델 404 에러
- 사용 가능한 모델을 자동으로 감지하도록 구현되어 있습니다
- 대시보드의 "모델 디버깅 정보"에서 사용 가능한 모델 목록 확인 가능

### 할당량 초과
- 자동 재시도 로직이 포함되어 있습니다
- 최대 3회 재시도하며, 대기 시간이 점진적으로 증가합니다

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 👤 작성자

Jayz-gith

## 🔗 링크

- [GitHub 저장소](https://github.com/Jayz-gith/new-test)
- [Streamlit Cloud 배포 가이드](https://docs.streamlit.io/streamlit-community-cloud)

