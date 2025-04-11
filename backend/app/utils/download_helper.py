
from app.core.config import settings


class DownloadHelper:
    def __init__(self, download_dir: str):
        self.download_dir = download_dir
        self.file_type = None
    
    def download_file(self, url: str):
        return f"{self.download_dir}"
    
    def gen_download_url(self,file_path: str ,file_name: str) -> str:
        return f"{settings.APP_URL}/download/{file_name}"