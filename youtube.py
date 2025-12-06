import sys
import requests
import yt_dlp
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# --- 다운로드 작업을 담당하는 백그라운드 스레드 ---
class DownloadThread(QThread):
    # PyQt5에서는 pyqtSignal을 사용합니다.
    progress_signal = pyqtSignal(str) # 상태 메시지 전달용
    finished_signal = pyqtSignal()    # 완료 신호

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        # yt-dlp 설정
        ydl_opts = {
            'format': 'best',  # 최적의 화질/음질 (단일 파일)
            'outtmpl': '%(title)s.%(ext)s', # 파일명: 제목.확장자
            'quiet': True,
        }
        try:
            self.progress_signal.emit("다운로드 시작... 잠시만 기다려주세요.")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            self.progress_signal.emit("다운로드 완료!")
        except Exception as e:
            self.progress_signal.emit(f"오류 발생: {str(e)}")
        
        self.finished_signal.emit()

# --- 메인 윈도우 클래스 ---
class YouTubeDownloader(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("유튜브 다운로더 (PyQt5)")
        self.setGeometry(100, 100, 500, 600)

        self.current_video_info = None
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # 1. 상단: 링크 입력 및 조회 버튼
        input_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("유튜브 링크를 붙여넣으세요 (Ctrl+V)")
        self.btn_search = QPushButton("조회")
        self.btn_search.clicked.connect(self.fetch_info)
        
        input_layout.addWidget(self.url_input)
        input_layout.addWidget(self.btn_search)
        layout.addLayout(input_layout)

        # 2. 중단: 정보 표시 (썸네일, 제목, 통계)
        # 썸네일
        self.lbl_thumbnail = QLabel()
        self.lbl_thumbnail.setAlignment(Qt.AlignCenter)
        self.lbl_thumbnail.setMinimumHeight(200)
        self.lbl_thumbnail.setStyleSheet("border: 1px solid #ccc; background-color: #eee;")
        self.lbl_thumbnail.setText("영상을 조회하면 썸네일이 표시됩니다")
        layout.addWidget(self.lbl_thumbnail)

        # 제목
        self.lbl_title = QLabel("-")
        self.lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
        self.lbl_title.setWordWrap(True)
        layout.addWidget(self.lbl_title)

        # 통계 (조회수, 좋아요)
        stats_layout = QHBoxLayout()
        self.lbl_views = QLabel("조회수: -")
        self.lbl_likes = QLabel("좋아요: -")
        stats_layout.addWidget(self.lbl_views)
        stats_layout.addWidget(self.lbl_likes)
        layout.addLayout(stats_layout)

        # 3. 하단: 다운로드 버튼 및 상태바
        layout.addSpacing(20)
        self.btn_download = QPushButton("영상 다운로드")
        self.btn_download.setStyleSheet("background-color: #d32f2f; color: white; font-weight: bold; padding: 12px;")
        self.btn_download.setEnabled(False) # 조회 전 비활성화
        self.btn_download.clicked.connect(self.start_download)
        layout.addWidget(self.btn_download)

        self.lbl_status = QLabel("대기 중")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_status)

        layout.addStretch()
        central_widget.setLayout(layout)

    def fetch_info(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "알림", "유튜브 링크를 입력해주세요.")
            return

        self.lbl_status.setText("영상 정보를 분석 중입니다...")
        self.btn_search.setEnabled(False)
        QApplication.processEvents() # UI 갱신

        # yt-dlp 메타데이터 추출 (다운로드 X)
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                self.current_video_info = info
                self.update_ui_with_info(info)
                
                self.lbl_status.setText("정보 조회 완료")
                self.btn_download.setEnabled(True)

        except Exception as e:
            self.lbl_status.setText("정보 조회 실패")
            QMessageBox.critical(self, "에러", f"정보를 가져올 수 없습니다.\n{str(e)}")
        
        self.btn_search.setEnabled(True)

    def update_ui_with_info(self, info):
        # 제목 설정
        self.lbl_title.setText(info.get('title', '제목 없음'))
        
        # 조회수, 좋아요 설정
        views = info.get('view_count', 0)
        likes = info.get('like_count', 0)
        self.lbl_views.setText(f"조회수: {views:,}회")
        self.lbl_likes.setText(f"좋아요: {likes:,}개" if likes else "좋아요: 집계불가")

        # 썸네일 이미지 다운로드 및 표시
        thumbnail_url = info.get('thumbnail')
        if thumbnail_url:
            try:
                response = requests.get(thumbnail_url)
                if response.status_code == 200:
                    image_data = response.content
                    image = QImage()
                    image.loadFromData(image_data)
                    pixmap = QPixmap.fromImage(image)
                    # 너비 400px로 비율 유지하며 리사이징
                    self.lbl_thumbnail.setPixmap(pixmap.scaledToWidth(400, Qt.SmoothTransformation))
            except:
                self.lbl_thumbnail.setText("썸네일 로드 실패")

    def start_download(self):
        if not self.current_video_info:
            return

        url = self.current_video_info.get('webpage_url')
        
        self.btn_download.setEnabled(False)
        self.btn_search.setEnabled(False)
        
        # 스레드 실행
        self.download_thread = DownloadThread(url)
        self.download_thread.progress_signal.connect(self.update_status)
        self.download_thread.finished_signal.connect(self.download_finished)
        self.download_thread.start()

    def update_status(self, msg):
        self.lbl_status.setText(msg)

    def download_finished(self):
        self.btn_download.setEnabled(True)
        self.btn_search.setEnabled(True)
        QMessageBox.information(self, "완료", "다운로드가 끝났습니다.\n파일이 저장된 폴더를 확인하세요.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YouTubeDownloader()
    window.show()
    # PyQt5에서는 app.exec_()를 사용합니다.
    sys.exit(app.exec_())