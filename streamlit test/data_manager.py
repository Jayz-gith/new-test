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

