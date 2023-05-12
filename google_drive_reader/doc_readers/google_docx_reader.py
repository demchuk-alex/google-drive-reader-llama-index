import io
from typing import Tuple

import docx
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from .google_item_reader import GoogleItemReader


class GoogleDocXReader(GoogleItemReader):
    def __init__(self, creds: Credentials):
        super().__init__(creds)

    def _get_service(self):
        return build('drive', 'v3', credentials=self.creds)

    def _get_doc_content_and_meta(self, service, doc_id: str) -> Tuple[str, str]:
        url = f"{self.base_url}{doc_id}/edit"
        request = service.files().get_media(fileId=doc_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            _, done = downloader.next_chunk()
        file.seek(0)

        doc = docx.Document(file)
        full_text = []
        for paragraph in doc.paragraphs:
            full_text.append(paragraph.text)
        text = '\n'.join(full_text)
        return text, url
