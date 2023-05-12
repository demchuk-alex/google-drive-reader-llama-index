import io
from typing import Tuple, List

from llama_index import Document

from .document_type import DocumentType
from google_drive_reader.doc_readers.google_item_reader import GoogleItemReader

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


class GooglePdfReader(GoogleItemReader):
    base_url = DocumentType.PDF

    def __init__(self, creds: Credentials):
        super().__init__(creds)

    def _get_service(self):
        return build('drive', 'v3', credentials=self.creds)

    def load(self, items_ids: List[str]) -> List[Document]:
        service = self._get_service()
        documents = []
        for item_id in items_ids:
            doc_content, url = self._get_doc_content_and_meta(service, item_id)
            for page_text in doc_content:
                documents.append(Document(page_text, extra_info={
                    "document_id": item_id,
                    "document_url": url
                }))

        return documents

    def _get_doc_content_and_meta(self, service, doc_id: str) -> Tuple[List[str], str]:
        url = f"{self.base_url}{doc_id}/view?usp=drivesdk"
        request = service.files().get_media(fileId=doc_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            _, done = downloader.next_chunk()
        content = file.getvalue()

        from PyPDF2 import PdfReader

        pdf_reader = PdfReader(io.BytesIO(content))
        pages_text = [page.extract_text() for page in pdf_reader.pages]

        return pages_text, url
