import streamlit as st
import feedparser
import google.generativeai as genai
from datetime import datetime, timezone
from data_manager import DataManager
import json
import re
import time

# 페이지 설정
st.set_page_config(
    page_title="IT 뉴스룸",
    page_icon="📰",
    layout="wide"
)

# DataManager 초기화
@st.cache_resource
def get_data_manager():
    return DataManager()

dm = get_data_manager()

# Gemini API 설정
try:
    gemini_api_key = st.secrets.get("GEMINI_API_KEY")
    if not gemini_api_key:
        st.error("⚠️ GEMINI_API_KEY가 설정되지 않았습니다. `.streamlit/secrets.toml` 파일을 확인하세요.")
        st.stop()
    genai.configure(api_key=gemini_api_key)
except (AttributeError, KeyError):
    st.error("⚠️ GEMINI_API_KEY가 설정되지 않았습니다. `.streamlit/secrets.toml` 파일을 확인하세요.")
    st.stop()

# 사용 가능한 모델 찾기 함수
@st.cache_data
def get_available_models():
    """사용 가능한 Gemini 모델 목록 가져오기"""
    try:
        all_models = genai.list_models()
        available_models = []
        for model in all_models:
            if 'generateContent' in model.supported_generation_methods:
                available_models.append({
                    'name': model.name,
                    'display_name': model.display_name,
                    'description': model.description
                })
        return available_models
    except Exception as e:
        st.warning(f"모델 목록을 가져올 수 없습니다: {e}")
        return []

@st.cache_data
def find_working_model():
    """작동하는 모델 찾기"""
    try:
        available_models = get_available_models()
        if available_models:
            # 첫 번째 사용 가능한 모델 반환
            return available_models[0]['name']
    except Exception:
        pass
    
    # 기본 모델 목록
    model_names = [
        'gemini-2.0-flash',
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'gemini-pro'
    ]
    return model_names[0]

# 방문자 통계 업데이트 (세션당 한 번만)
if "visit_counted" not in st.session_state:
    stats = dm.get_data("stats.json")
    stats["visits"] = stats.get("visits", 0) + 1
    dm.save_data("stats.json", stats, "방문자 통계 업데이트")
    st.session_state.visit_counted = True

# 사이드바 메뉴
st.sidebar.title("📰 IT 뉴스룸")
menu = st.sidebar.radio("메뉴 선택", ["뉴스룸 (Home)", "대시보드 (Admin)"])

if menu == "뉴스룸 (Home)":
    st.title("📰 IT 뉴스룸")
    st.markdown("---")
    
    # 뉴스 데이터 불러오기
    news_data = dm.get_data("news_data.json")
    
    if not news_data:
        st.info("📭 아직 수집된 뉴스가 없습니다. 대시보드에서 뉴스를 수집해주세요.")
    else:
        # 날짜별로 정렬 (최신순)
        dates = sorted(news_data.keys(), reverse=True)
        
        # 탭으로 날짜별 뉴스 표시
        tabs = st.tabs(dates)
        
        for idx, date in enumerate(dates):
            with tabs[idx]:
                date_data = news_data[date]
                
                # 오늘의 브리핑
                if "summary" in date_data and date_data["summary"]:
                    st.subheader("📋 오늘의 브리핑")
                    st.info(date_data["summary"])
                    st.markdown("---")
                
                # 주요 뉴스 리스트
                if "articles" in date_data and date_data["articles"]:
                    st.subheader("📰 주요 뉴스")
                    for article in date_data["articles"]:
                        with st.container():
                            st.markdown(f"### {article.get('title', '제목 없음')}")
                            if "summary" in article:
                                st.write(article["summary"])
                            if "link" in article:
                                st.markdown(f"[원문 보기]({article['link']})")
                            st.markdown("---")

elif menu == "대시보드 (Admin)":
    st.title("📊 대시보드")
    st.markdown("---")
    
    # 접속자 통계
    st.subheader("👥 접속자 통계")
    stats = dm.get_data("stats.json")
    total_visits = stats.get("visits", 0)
    st.metric("총 방문자 수", f"{total_visits:,}")
    st.markdown("---")
    
    # RSS 관리
    st.subheader("🔗 RSS 관리")
    feeds = dm.get_data("feeds.json")
    
    if feeds:
        st.write("**현재 등록된 RSS 피드:**")
        for i, feed_url in enumerate(feeds):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.text(feed_url)
            with col2:
                if st.button("삭제", key=f"delete_{i}"):
                    feeds.remove(feed_url)
                    dm.save_data("feeds.json", feeds, f"RSS 피드 삭제: {feed_url}")
                    st.rerun()
    
    # RSS 추가
    st.write("**새 RSS 피드 추가:**")
    new_feed = st.text_input("RSS URL을 입력하세요", key="new_feed")
    if st.button("추가"):
        if new_feed and new_feed.strip():
            if new_feed.strip() in feeds:
                st.warning("이미 등록된 RSS 피드입니다.")
            else:
                feeds.append(new_feed.strip())
                dm.save_data("feeds.json", feeds, f"RSS 피드 추가: {new_feed.strip()}")
                st.success("RSS 피드가 추가되었습니다!")
                st.rerun()
        else:
            st.warning("유효한 URL을 입력해주세요.")
    
    st.markdown("---")
    
    # 모델 디버깅 정보 (확장 가능)
    with st.expander("🔧 모델 디버깅 정보"):
        st.write("**사용 가능한 Gemini 모델 목록:**")
        available_models = get_available_models()
        if available_models:
            for model in available_models:
                st.write(f"- **{model['name']}**")
                if model.get('display_name'):
                    st.caption(f"  표시명: {model['display_name']}")
        else:
            st.warning("사용 가능한 모델을 찾을 수 없습니다. API 키를 확인하세요.")
            st.info("**시도할 기본 모델:**")
            st.write("- gemini-2.0-flash")
            st.write("- gemini-1.5-flash")
            st.write("- gemini-1.5-pro")
            st.write("- gemini-pro")
    
    st.markdown("---")
    
    # 데이터 수집 및 분석
    st.subheader("🤖 데이터 수집 및 AI 분석")
    
    if st.button("🔄 뉴스 수집 & AI 분석 시작", type="primary"):
        feeds = dm.get_data("feeds.json")
        
        if not feeds:
            st.warning("등록된 RSS 피드가 없습니다. 먼저 RSS 피드를 추가해주세요.")
        else:
            with st.spinner("뉴스를 수집하고 분석 중입니다..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # 오늘 날짜 (YYYY-MM-DD)
                today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                
                # RSS 피드 수집
                all_articles = []
                status_text.text(f"RSS 피드 수집 중... (0/{len(feeds)})")
                
                for idx, feed_url in enumerate(feeds):
                    try:
                        feed = feedparser.parse(feed_url)
                        progress_bar.progress((idx + 1) / (len(feeds) + 2))
                        status_text.text(f"RSS 피드 수집 중... ({idx + 1}/{len(feeds)})")
                        
                        for entry in feed.entries:
                            # 날짜 파싱
                            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                                article_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).strftime("%Y-%m-%d")
                            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                                article_date = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc).strftime("%Y-%m-%d")
                            else:
                                continue
                            
                            # 오늘 날짜 기사만 필터링
                            if article_date == today:
                                # 본문 앞부분 200자만 추출
                                summary = ""
                                if hasattr(entry, 'summary'):
                                    summary = entry.summary[:200]
                                elif hasattr(entry, 'description'):
                                    summary = entry.description[:200]
                                
                                all_articles.append({
                                    "title": entry.get("title", "제목 없음"),
                                    "content": summary,
                                    "link": entry.get("link", "")
                                })
                    except Exception as e:
                        st.warning(f"RSS 피드 파싱 실패 ({feed_url}): {e}")
                        continue
                
                if not all_articles:
                    st.info(f"오늘({today}) 날짜의 뉴스가 없습니다.")
                else:
                    # 최대 20개로 제한 (토큰 제한 방지)
                    if len(all_articles) > 20:
                        st.warning(f"뉴스가 너무 많아서 최대 20개만 처리합니다. (전체: {len(all_articles)}개)")
                        all_articles = all_articles[:20]
                    
                    status_text.text(f"AI 분석 중... ({len(all_articles)}개 기사)")
                    progress_bar.progress(0.8)
                    
                        # Gemini에게 프롬프트 전송
                    try:
                        # 프롬프트 구성
                        articles_text = "\n\n".join([
                            f"제목: {art['title']}\n내용: {art['content']}"
                            for art in all_articles
                        ])
                        
                        prompt = f"""다음은 오늘의 IT 뉴스 기사들입니다. 

{articles_text}

이 뉴스들을 IT 트렌드 관점에서 종합 브리핑해주고, 각 개별 기사는 3줄 요약해주세요.

응답은 다음 JSON 형식으로 반환해주세요:
{{
    "summary": "종합 브리핑 내용 (200자 이내)",
    "articles": [
        {{
            "title": "기사 제목",
            "summary": "3줄 요약",
            "link": "기사 링크"
        }}
    ]
}}

JSON 형식만 반환하고 다른 설명은 포함하지 마세요."""

                        # 사용 가능한 모델 목록 가져오기
                        available_models = get_available_models()
                        
                        if available_models:
                            # 실제 사용 가능한 모델 사용
                            model_names = [m['name'] for m in available_models]
                            status_text.text(f"사용 가능한 모델 발견: {len(model_names)}개")
                        else:
                            # 폴백: 기본 모델 목록
                            model_names = [
                                'gemini-2.0-flash',
                                'gemini-1.5-flash',
                                'gemini-1.5-pro',
                                'gemini-pro',
                                'models/gemini-2.0-flash',
                                'models/gemini-1.5-flash',
                                'models/gemini-1.5-pro',
                                'models/gemini-pro'
                            ]
                            st.warning("⚠️ 사용 가능한 모델 목록을 가져올 수 없어 기본 모델을 시도합니다.")
                        
                        response = None
                        last_error = None
                        
                        # 여러 모델 시도
                        for model_name in model_names:
                            try:
                                model = genai.GenerativeModel(model_name)
                                # 모델이 작동하는지 테스트
                                response = model.generate_content(prompt)
                                break  # 성공하면 루프 종료
                            except Exception as e:
                                error_str = str(e)
                                last_error = e
                                
                                # 404 에러면 다음 모델 시도
                                if "404" in error_str or "not found" in error_str.lower():
                                    continue  # 다음 모델 시도
                                
                                # 할당량 초과 에러면 재시도
                                if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                                    # 재시도 로직
                                    max_retries = 3
                                    retry_delay = 15
                                    
                                    for attempt in range(max_retries):
                                        try:
                                            wait_time = retry_delay * (attempt + 1)
                                            status_text.text(f"할당량 초과로 인해 {wait_time}초 대기 중... (시도 {attempt + 1}/{max_retries})")
                                            time.sleep(wait_time)
                                            response = model.generate_content(prompt)
                                            break  # 성공
                                        except Exception as retry_e:
                                            if attempt == max_retries - 1:
                                                raise retry_e
                                            continue
                                    
                                    if response:
                                        break  # 성공했으면 외부 루프 종료
                                else:
                                    # 다른 종류의 에러는 즉시 발생
                                    raise e
                        
                        if response is None:
                            raise Exception(f"사용 가능한 모델을 찾을 수 없습니다. 마지막 오류: {last_error}")
                        
                        # JSON 파싱 (더 견고한 파싱)
                        response_text = response.text.strip()
                        
                        # JSON 코드 블록 제거 (```json ... ``` 또는 ``` ... ```)
                        if "```" in response_text:
                            # ```json ... ``` 또는 ``` ... ``` 패턴 찾기
                            json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', response_text, re.DOTALL)
                            if json_match:
                                response_text = json_match.group(1)
                            else:
                                # 첫 번째 ``` 와 마지막 ``` 사이의 내용 추출
                                parts = response_text.split("```")
                                if len(parts) >= 3:
                                    response_text = parts[1]
                                    if response_text.startswith("json"):
                                        response_text = response_text[4:]
                                    response_text = response_text.strip()
                        
                        # JSON 객체만 추출 (중괄호로 시작하고 끝나는 부분)
                        if "{" in response_text and "}" in response_text:
                            start_idx = response_text.find("{")
                            end_idx = response_text.rfind("}") + 1
                            response_text = response_text[start_idx:end_idx]
                        
                        result = json.loads(response_text)
                        
                        # 기존 뉴스 데이터 불러오기
                        news_data = dm.get_data("news_data.json")
                        
                        # 오늘 날짜 데이터 병합
                        if today in news_data:
                            # 기존 기사와 새 기사 합치기 (중복 제거)
                            existing_links = {art.get("link") for art in news_data[today].get("articles", [])}
                            new_articles = [art for art in result["articles"] if art.get("link") not in existing_links]
                            news_data[today]["articles"].extend(new_articles)
                            # 요약 업데이트
                            if result.get("summary"):
                                news_data[today]["summary"] = result["summary"]
                        else:
                            news_data[today] = result
                        
                        # 저장
                        progress_bar.progress(1.0)
                        status_text.text("저장 중...")
                        dm.save_data("news_data.json", news_data, f"뉴스 수집 및 분석: {today}")
                        
                        st.success(f"✅ 완료! {len(all_articles)}개의 뉴스를 수집하고 분석했습니다.")
                        st.balloons()
                        
                    except json.JSONDecodeError as e:
                        st.error(f"AI 응답 파싱 오류: {e}")
                        st.code(response_text)
                    except Exception as e:
                        st.error(f"AI 분석 오류: {e}")
                        import traceback
                        st.code(traceback.format_exc())

