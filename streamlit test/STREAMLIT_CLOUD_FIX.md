# 🔧 Streamlit Cloud 배포 오류 해결 가이드

## 발생한 오류

```
error: Failed to parse: test/requirements.txt
ERROR: Invalid requirement: 'test/requirements.txt'
```

## 원인 분석

Streamlit Cloud가 `test/requirements.txt`를 **패키지 이름**으로 해석하고 있습니다.
- 실제로는 파일 경로인데, pip/uv가 패키지로 인식
- 그런 패키지는 존재하지 않아 설치 실패

## 해결 방법

### ✅ 방법 1: requirements.txt 확인 및 수정 (권장)

1. **현재 requirements.txt 확인**
   ```bash
   cat requirements.txt
   ```

2. **문제가 되는 줄 제거**
   - `test/requirements.txt` 같은 줄이 있다면 삭제
   - 실제 라이브러리 이름만 남기기

3. **올바른 requirements.txt 예시**
   ```text
   streamlit>=1.28.0
   PyGithub>=1.59.0
   feedparser>=6.0.10
   google-generativeai>=0.3.0
   pandas>=2.0.0
   plotly>=5.17.0
   ```

4. **커밋 및 푸시**
   ```bash
   git add requirements.txt
   git commit -m "Fix requirements.txt for Streamlit Cloud"
   git push origin main
   ```

5. **Streamlit Cloud에서 재배포**
   - Streamlit Cloud 콘솔에서 "Restart" 또는 "Rerun" 클릭

### ✅ 방법 2: Streamlit Cloud 설정 확인

1. **Main file path 확인**
   - Streamlit Cloud 설정에서 "Main file path" 확인
   - 루트에 `app.py`가 있다면: `app.py`
   - ❌ `test/requirements.txt` 같은 경로가 아닌지 확인

2. **올바른 설정**
   ```
   Repository: Jayz-gith/new-test
   Branch: main
   Main file path: app.py
   ```

### ✅ 방법 3: 프로젝트 구조 확인

현재 프로젝트 구조:
```
new-test/
├── app.py              ← 메인 파일 (Streamlit Cloud에서 이 파일 실행)
├── requirements.txt    ← 의존성 파일 (여기에 라이브러리만!)
├── data_manager.py
├── data/
│   ├── feeds.json
│   ├── news_data.json
│   └── stats.json
└── .streamlit/
    └── config.toml
```

**중요**: 
- `requirements.txt`에는 **라이브러리 이름만** 있어야 함
- 파일 경로나 다른 requirements 파일 참조는 `-r` 옵션 사용 시에만

## requirements.txt 작성 규칙

### ✅ 올바른 예시
```text
streamlit
PyGithub
feedparser
google-generativeai
pandas
plotly
```

### ❌ 잘못된 예시
```text
test/requirements.txt          # 파일 경로를 패키지로 인식
-r test/requirements.txt        # 파일이 없으면 에러
requirements-dev.txt            # 파일 경로를 패키지로 인식
```

### ✅ 다른 requirements 파일 포함하기 (고급)

만약 정말로 다른 requirements 파일을 포함해야 한다면:

1. **파일 구조**
   ```
   new-test/
   ├── requirements.txt
   └── test/
       └── requirements.txt
   ```

2. **루트 requirements.txt**
   ```text
   streamlit
   PyGithub
   -r test/requirements.txt    # -r 옵션으로 포함
   ```

3. **test/requirements.txt**
   ```text
   pytest
   pytest-cov
   ```

## Streamlit Cloud 로그 확인 방법

1. Streamlit Cloud 콘솔 접속
2. 앱 선택 → "Manage app" → "Logs" 탭
3. 에러 메시지 확인:
   - `Invalid requirement` → requirements.txt에 문제
   - `ModuleNotFoundError` → 라이브러리 누락
   - `FileNotFoundError` → 파일 경로 문제

## 체크리스트

배포 전 확인:
- [ ] `requirements.txt`에 라이브러리 이름만 있는지 확인
- [ ] 파일 경로나 잘못된 형식이 없는지 확인
- [ ] Main file path가 올바른지 확인 (`app.py`)
- [ ] 모든 변경사항이 GitHub에 푸시되었는지 확인

## 추가 참고사항

### 로컬 vs Cloud 환경 분리 (선택사항)

개발용과 프로덕션용 requirements를 분리하고 싶다면:

1. **파일 구조**
   ```
   requirements.txt          # 프로덕션용 (Streamlit Cloud에서 사용)
   requirements-dev.txt      # 개발용 (로컬에서만 사용)
   ```

2. **로컬 설치**
   ```bash
   pip install -r requirements-dev.txt
   ```

3. **Streamlit Cloud**
   - 자동으로 `requirements.txt` 사용
   - `requirements-dev.txt`는 무시됨

## 문제 해결 후

1. ✅ requirements.txt 수정 완료
2. ✅ GitHub에 푸시 완료
3. ✅ Streamlit Cloud에서 재배포
4. ✅ 로그에서 에러가 사라졌는지 확인
5. ✅ 앱이 정상적으로 로드되는지 확인

## 도움이 필요하면

- [Streamlit Cloud 문서](https://docs.streamlit.io/streamlit-community-cloud)
- [pip requirements 파일 형식](https://pip.pypa.io/en/stable/reference/requirements-file-format/)

