# Gemini API 모델 404 에러 보고서

## 에러 내용
```
404 models/gemini-pro is not found for API version v1beta, or is not supported for generateContent. 
Call ListModels to see the list of available models and their supported methods.
```

## 발생 시점
- Streamlit 앱에서 뉴스 수집 및 AI 분석 기능 실행 시
- `genai.GenerativeModel()` 호출 시

## 시도한 모델 목록
1. `gemini-1.5-flash`
2. `gemini-1.5-pro`
3. `gemini-pro`
4. `models/gemini-1.5-flash`
5. `models/gemini-1.5-pro`
6. `models/gemini-pro`

**결과**: 모든 모델에서 404 에러 발생

## 원인 분석

### 가능한 원인
1. **API 버전 불일치**: 
   - 에러 메시지에 "API version v1beta" 언급
   - 현재 사용 중인 `google-generativeai` 라이브러리 버전이 v1beta API를 사용하고 있을 수 있음
   - 일부 모델이 v1beta에서 지원되지 않을 수 있음

2. **API 키 권한 문제**:
   - API 키가 특정 모델에 대한 접근 권한이 없을 수 있음
   - 무료 티어 제한으로 인해 일부 모델 사용 불가

3. **모델 이름 형식 문제**:
   - API 버전에 따라 모델 이름 형식이 다를 수 있음
   - `models/` 접두사 필요 여부가 API 버전에 따라 다를 수 있음

4. **지역/엔드포인트 문제**:
   - API 엔드포인트 설정이 잘못되었을 수 있음
   - 특정 지역에서만 사용 가능한 모델일 수 있음

## 해결 방안

### 1. 사용 가능한 모델 목록 확인
```python
import google.generativeai as genai

genai.configure(api_key="YOUR_API_KEY")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"사용 가능한 모델: {model.name}")
```

### 2. API 버전 확인
- 현재 사용 중인 `google-generativeai` 라이브러리 버전 확인
- 최신 버전으로 업데이트 필요 여부 확인

### 3. API 키 재발급
- Google AI Studio에서 새로운 API 키 발급
- API 키 권한 및 할당량 확인

### 4. 대안 모델 사용
- 다른 Gemini 모델 시도
- 또는 다른 AI 서비스 (OpenAI, Claude 등) 고려

## 현재 상태
- **라이브러리 버전**: `google-generativeai-0.8.5` (requirements.txt 기준)
- **에러 발생 모델**: 모든 시도한 모델에서 404 에러
- **API 키 상태**: 설정됨 (`.streamlit/secrets.toml`)

## 다음 단계
1. ✅ 실제 사용 가능한 모델 목록을 확인하는 디버깅 코드 추가 완료
2. API 키 권한 및 할당량 확인
3. 라이브러리 버전 업데이트 검토
4. Google AI Studio에서 사용 가능한 모델 목록 확인

## 구현된 해결책

### 1. 동적 모델 목록 확인
- `get_available_models()` 함수 추가: `genai.list_models()`를 사용하여 실제 사용 가능한 모델 목록 가져오기
- `generateContent` 메서드를 지원하는 모델만 필터링

### 2. 대시보드 디버깅 섹션
- 대시보드에 "모델 디버깅 정보" 확장 섹션 추가
- 사용 가능한 모델 목록을 실시간으로 표시
- 모델을 찾을 수 없을 경우 기본 모델 목록 표시

### 3. 자동 모델 선택
- 실제 사용 가능한 모델 목록을 우선적으로 사용
- 목록을 가져올 수 없을 경우 기본 모델 목록으로 폴백
- 여러 모델을 순차적으로 시도하여 작동하는 모델 자동 선택

## 참고 링크
- [Gemini API 문서](https://ai.google.dev/gemini-api/docs)
- [Gemini API 할당량 및 제한](https://ai.google.dev/gemini-api/docs/rate-limits)
- [사용 가능한 모델 목록](https://ai.google.dev/gemini-api/docs/models/gemini)

