from typing import List, Tuple
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from llama_index import Document
from document_type import DocumentType


class GoogleItemReader:
    base_url: str = DocumentType.DOCUMENT

    def __init__(self, creds: Credentials):
        self.creds = creds

    def _get_service(self):
        return build('docs', 'v1', credentials=self.creds)

    def load(self, items_ids: List[str]):
        service = self._get_service()
        documents = []
        for item_id in items_ids:
            doc_content, url = self._get_doc_content_and_meta(service, item_id)
            documents.append(Document(doc_content, extra_info={
                "id": item_id,
                "source_url": url
            }))

        return documents

    def _get_doc_content_and_meta(self, service, item_id: str) -> Tuple[str, str]:
        pass
