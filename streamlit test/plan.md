Streamlit Cloud는 **"Read-Only(읽기 전용)"** 환경이기 때문에, 앱에서 생성된 데이터(JSON)를 영구적으로 저장하려면 **GitHub 리포지토리에 커밋(Commit)** 하는 방식을 써야 합니다. 즉, 앱이 DB 역할을 하는 JSON 파일을 GitHub에서 읽어오고, 수정되면 다시 GitHub로 푸시(Push)하는 구조입니다.

Cursor AI에게 이 구조를 명확히 이해시키고 코드를 작성하게 하는 것이 핵심입니다.

다음 단계에 따라 프로젝트를 진행해 보세요.

---

### 1. 사전 준비 (API 키 발급)

프로젝트 시작 전, 꼭 필요한 키 2가지입니다.

1.  **Google Gemini API Key**: [Google AI Studio](https://aistudio.google.com/app/apikey)에서 발급.
2.  **GitHub Personal Access Token (Classic)**:
    *   GitHub Settings -> Developer settings -> Personal access tokens -> Tokens (classic)
    *   `repo` (Full control of private repositories) 권한 체크 후 생성.
    *   **토큰 값은 한 번만 보여주니 꼭 복사해두세요.**

---

### 2. 프로젝트 폴더 구조

Cursor의 탐색기에서 아래와 같이 파일과 폴더를 만들어주세요.

```text
my-newsroom/
├── .streamlit/
│   └── secrets.toml      (로컬 테스트용 키 저장소)
├── .gitignore            (GitHub 업로드 제외 파일 목록)
├── data/                 (데이터 저장소 - 초기 파일 필요)
│   ├── feeds.json        (RSS 목록)
│   ├── news_data.json    (분석된 뉴스)
│   └── stats.json        (방문자 통계)
├── app.py                (메인 실행 파일)
├── data_manager.py       (GitHub 연동 및 JSON 처리 담당)
└── requirements.txt      (라이브러리 목록)
```

**초기 JSON 파일 내용 (빈 파일로 두면 에러가 날 수 있으니 아래 내용으로 각각 생성하세요):**

*   `data/feeds.json`: `["https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=ko&gl=KR&ceid=KR:ko"]`
*   `data/news_data.json`: `{}`
*   `data/stats.json`: `{"visits": 0}`

---

### 3. Cursor AI에게 요청할 프롬프트 및 코드

이제 Cursor의 `Composer (Ctrl+I)` 기능을 켜고 각 파일에 들어갈 코드를 작성해 달라고 요청합니다.

#### 단계 1: 라이브러리 설치 (`requirements.txt`)

**Cursor 프롬프트:**
> "Streamlit, PyGithub, feedparser, google-generativeai, pandas를 사용하는 requirements.txt 파일을 만들어줘."

**결과 내용:**
```text
streamlit
PyGithub
feedparser
google-generativeai
pandas
plotly
```

#### 단계 2: GitHub 데이터 연동 모듈 (`data_manager.py`)

이 파일이 **핵심**입니다. Streamlit Cloud에서 파일 시스템 대신 GitHub API를 통해 데이터를 읽고 씁니다.

**Cursor 프롬프트:**
> "data_manager.py를 만들 거야. PyGithub 라이브러리를 사용해서 GitHub 리포지토리의 data 폴더 내 json 파일들을 읽고 쓰는 클래스를 작성해줘.
> 로컬 환경에서는 그냥 파일을 읽고 쓰고, Streamlit Cloud 환경(secrets에 GITHUB_TOKEN이 있을 때)에서는 GitHub API를 통해 내용을 가져오고 커밋하는 로직을 분기 처리해줘.
> 캐싱(st.cache_data)을 사용해서 API 호출을 최적화해줘."

**`data_manager.py` (참고용 코드):**
```python
import json
import os
import streamlit as st
from github import Github
from github.GithubException import GithubException

BRANCH = "main"

class DataManager:
    def __init__(self):
        # Streamlit secrets는 함수 내에서 접근해야 함 (보안)
        try:
            self.github_token = st.secrets.get("GITHUB_TOKEN")
            self.repo_name = st.secrets.get("REPO_NAME")  # 예: "username/my-newsroom"
        except (AttributeError, KeyError):
            self.github_token = None
            self.repo_name = None
        
        self.use_github = self.github_token is not None and self.repo_name is not None
        
        if self.use_github:
            try:
                self.g = Github(self.github_token)
                self.repo = self.g.get_repo(self.repo_name)
            except Exception as e:
                st.warning(f"GitHub 연결 실패: {e}. 로컬 모드로 전환합니다.")
                self.use_github = False
    
    def _read_local(self, filename):
        """로컬 파일 읽기"""
        try:
            with open(f"data/{filename}", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            # 기본값 반환
            if filename == "feeds.json":
                return []
            elif filename == "stats.json":
                return {"visits": 0}
            else:
                return {}
        except json.JSONDecodeError:
            st.error(f"JSON 파싱 오류: {filename}")
            return {} if filename != "feeds.json" else []

    def _save_local(self, filename, data):
        """로컬 파일 저장"""
        os.makedirs("data", exist_ok=True)
        with open(f"data/{filename}", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @st.cache_data(ttl=60)  # 60초 캐싱으로 API 호출 최적화
    def _get_github_data(self, filename):
        """GitHub에서 데이터 읽기 (캐싱 적용)"""
        try:
            path = f"data/{filename}"
            contents = self.repo.get_contents(path, ref=BRANCH)
            return json.loads(contents.decoded_content.decode("utf-8"))
        except GithubException as e:
            if e.status == 404:
                # 파일이 없으면 기본값 반환
                return {} if filename != "feeds.json" else []
            raise e

    def get_data(self, filename):
        """데이터 읽기 (GitHub 우선, 없으면 로컬)"""
        if self.use_github:
            try:
                return self._get_github_data(filename)
            except Exception as e:
                st.warning(f"GitHub 로드 실패 ({filename}): {e}. 로컬 파일을 사용합니다.")
                return self._read_local(filename)
        else:
            return self._read_local(filename)

    def save_data(self, filename, data, message="Update data"):
        """데이터 저장 (GitHub 커밋 또는 로컬 저장)"""
        if self.use_github:
            try:
                path = f"data/{filename}"
                json_str = json.dumps(data, ensure_ascii=False, indent=2)
                
                try:
                    # 파일이 존재하면 업데이트
                    contents = self.repo.get_contents(path, ref=BRANCH)
                    self.repo.update_file(path, message, json_str, contents.sha, branch=BRANCH)
                except GithubException as e:
                    if e.status == 404:
                        # 파일이 없으면 생성
                        self.repo.create_file(path, message, json_str, branch=BRANCH)
                    else:
                        raise e
                
                st.cache_data.clear()  # 캐시 무효화
                st.toast(f"✅ GitHub에 {filename} 저장 완료!", icon="✅")
                return True
            except Exception as e:
                st.error(f"GitHub 저장 실패: {e}")
                # 실패 시 로컬에 백업 저장
                self._save_local(filename, data)
                st.warning("로컬에 백업 저장했습니다.")
                return False
        else:
            self._save_local(filename, data)
            st.toast(f"💾 로컬에 {filename} 저장 완료!", icon="💾")
            return True
```

#### 단계 3: 메인 앱 로직 (`app.py`)

**Cursor 프롬프트:**
> "app.py를 작성해줘.
> 1. data_manager.py를 import해서 사용해.
> 2. `st.secrets`에서 'GEMINI_API_KEY'를 가져와서 설정해. 키가 없으면 에러 메시지를 보여줘.
> 3. 앱이 시작될 때 'stats.json'의 'visits' 카운트를 1 증가시키고 저장해. (단, 세션당 한 번만 실행되도록 st.session_state 사용)
> 4. 사이드바 메뉴로 '뉴스룸(Home)'과 '대시보드(Admin)'를 만들어.
>
> **뉴스룸(Home):**
> - 'news_data.json'을 불러와서 날짜별로 탭(Tab)이나 아코디언으로 정리해서 보여줘.
> - 날짜는 최신순으로 정렬해줘 (YYYY-MM-DD 형식).
> - 각 날짜별로 Gemini가 요약한 '오늘의 브리핑'과 주요 뉴스 리스트를 카드 형태로 보여줘.
> - 뉴스가 없으면 '아직 수집된 뉴스가 없습니다' 메시지를 보여줘.
>
> **대시보드(Admin):**
> - **접속자 통계:** 현재 총 방문자 수를 큰 숫자로 보여줘.
> - **RSS 관리:** 'feeds.json'을 불러와서 현재 등록된 RSS URL 리스트를 보여주고, 추가/삭제할 수 있는 기능을 넣어줘. (변경 시 save_data 호출)
>   - URL 유효성 검사 추가 (빈 문자열, 중복 체크)
> - **데이터 수집 및 분석:** '뉴스 수집 & AI 분석 시작' 버튼을 만들어.
>   - 버튼을 누르면 `st.spinner`로 로딩 표시를 해줘.
>   - 등록된 모든 RSS를 feedparser로 긁어와. (에러 발생 시 해당 RSS는 스킵하고 계속 진행)
>   - 오늘 날짜(YYYY-MM-DD) 기사만 필터링해. (시간대 고려)
>   - **중요:** 뉴스가 너무 많으면 Gemini 토큰 제한에 걸릴 수 있으니, 각 기사의 제목과 본문 앞부분 200자만 잘라서 프롬프트에 넣어줘.
>   - Gemini 1.5 Flash 모델에게 '이 뉴스들을 IT 트렌드 관점에서 종합 브리핑해주고, 개별 기사는 3줄 요약해줘'라고 프롬프트를 보내.
>   - 결과를 날짜를 Key로 하는 JSON 구조로 만들어서 'news_data.json'에 저장(병합)해.
>   - JSON 구조: `{"2024-01-15": {"summary": "...", "articles": [{"title": "...", "summary": "...", "link": "..."}, ...]}}`
>   - 수집된 뉴스 개수와 분석 완료 메시지를 보여줘."

---

### 4. 로컬 테스트 및 배포 설정

코드가 완성되었다면 배포를 위한 설정을 합니다.

**1. `.gitignore` 파일 생성**
프로젝트 루트에 `.gitignore` 파일을 만들고 다음 내용을 추가하세요:

```text
# Streamlit secrets (절대 GitHub에 올리면 안 됨!)
.streamlit/secrets.toml

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

**2. 로컬 비밀키 설정 (`.streamlit/secrets.toml`)**
이 파일은 `.gitignore`에 추가되어 있어 GitHub에 업로드되지 않습니다.

```toml
GEMINI_API_KEY = "내_GEMINI_키"
# 로컬 테스트할 때는 아래 두 줄 주석 처리해도 됨 (로컬 파일 쓰기 모드 작동)
# GITHUB_TOKEN = "내_GITHUB_토큰"
# REPO_NAME = "내아이디/리포지토리이름"
```

**3. GitHub 업로드**
`my-newsroom` 폴더의 내용을 GitHub에 푸시합니다. `.gitignore`에 의해 secrets.toml과 venv는 자동으로 제외됩니다.

**4. Streamlit Cloud 배포**
1.  [Streamlit Cloud](https://share.streamlit.io/)에 접속하여 로그인.
2.  "New app" -> GitHub 리포지토리 선택.
3.  **Advanced settings (중요)** 버튼 클릭.
4.  **Secrets** 입력창에 다음 내용을 복사해 넣습니다.

```toml
GEMINI_API_KEY = "발급받은_GEMINI_API_KEY"
GITHUB_TOKEN = "발급받은_GITHUB_TOKEN"
REPO_NAME = "github아이디/리포지토리이름"
```

5.  **Deploy!**

---

### 5. 핵심 팁 (Cursor 사용 시)

*   **Gemini 프롬프트 최적화:** 
    - 뉴스 데이터가 많으면 Gemini 토큰 제한에 걸릴 수 있으니, 기사 제목과 본문 앞부분 200자만 잘라서 프롬프트에 넣도록 코드를 짜줘.
    - 한 번에 처리할 뉴스 개수를 제한(예: 최대 20개)하고, 나머지는 다음에 처리하도록 배치 처리 로직을 추가하면 더 안정적입니다.
*   **날짜 키 관리:** 
    - JSON 구조를 `{"2024-01-15": { "summary": "...", "articles": [...] }}` 형태로 잡아야 나중에 날짜별로 불러오기 편합니다.
    - 날짜는 ISO 형식(YYYY-MM-DD)을 사용하고, `datetime` 모듈로 일관성 있게 처리하세요.
*   **에러 처리:** 
    - RSS 피드 파싱 실패, GitHub API 오류, Gemini API 오류 등 각 단계에서 try-except로 에러를 처리하고 사용자에게 명확한 메시지를 보여주세요.
*   **성능 최적화:** 
    - `data_manager.py`의 `get_data` 메서드에 `@st.cache_data` 데코레이터를 사용해 API 호출을 최소화하세요.
    - 데이터 저장 후에는 `st.cache_data.clear()`로 캐시를 무효화해야 최신 데이터를 보여줍니다.
*   **사용자 경험:** 
    - 뉴스 수집 버튼을 누르면 시간이 오래 걸리니 `st.spinner`나 프로그레스 바를 꼭 넣어주세요.
    - 각 단계별 진행 상황을 `st.progress`로 표시하면 더 좋습니다.
*   **보안 주의사항:** 
    - `.streamlit/secrets.toml` 파일은 절대 GitHub에 커밋하지 마세요. `.gitignore`에 추가되어 있는지 확인하세요.
    - Streamlit Cloud의 Secrets는 암호화되어 저장되므로 안전합니다.

### 6. 트러블슈팅

**자주 발생하는 문제들:**

1. **GitHub API Rate Limit 오류**
   - GitHub API는 시간당 요청 횟수 제한이 있습니다. 캐싱을 활용하고 불필요한 호출을 줄이세요.
   - 오류 발생 시 로컬 모드로 자동 전환되도록 코드에 폴백 로직을 추가했습니다.

2. **Gemini API 토큰 제한**
   - 한 번에 너무 많은 뉴스를 처리하려고 하면 오류가 발생할 수 있습니다.
   - 뉴스 개수를 제한하거나 배치로 나눠서 처리하세요.

3. **RSS 피드 파싱 실패**
   - 일부 RSS 피드가 잘못된 형식이거나 접근 불가능할 수 있습니다.
   - 각 피드마다 try-except로 처리하고 실패한 피드는 스킵하도록 하세요.

4. **Streamlit Cloud에서 파일 저장 안 됨**
   - `GITHUB_TOKEN`과 `REPO_NAME`이 Secrets에 제대로 설정되었는지 확인하세요.
   - 리포지토리 이름은 `"username/repo-name"` 형식이어야 합니다.

---

이제 Cursor를 열고 위 **단계 2**부터 차근차근 복사해서 붙여넣으시면 됩니다. 에러가 나면 에러 메시지를 그대로 Cursor 채팅창에 넣고 "이거 해결해줘"라고 하면 바로 고쳐줄 거예요.