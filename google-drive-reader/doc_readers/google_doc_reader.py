from typing import Tuple, Any, List
from google.oauth2.credentials import Credentials

from google_item_reader import GoogleItemReader
from document_type import DocumentType, ContentType


class GoogleDocReader(GoogleItemReader):
    def __init__(self, creds: Credentials):
        super().__init__(creds)

    def _get_doc_content_and_meta(self, service, doc_id: str) -> Tuple[str, str]:
        url = f"{self.base_url}{doc_id}/edit"
        doc = service.documents().get(documentId=doc_id).execute()
        doc_content = doc.get("body").get("content")
        text = self._read_content(doc_content)
        return text, url

    def _read_content(self, content_elements: List[Any]) -> str:
        text = ''
        for element in content_elements:
            if ContentType.PARAGRAPH in element:
                text += self._read_table_content(element)
            elif ContentType.TABLE in element:
                text += self._read_table_content(element)
            elif ContentType.TABLE_OF_CONTENTS in element:
                text += self._read_table_of_contents_content(element)

        return text

    def _read_paragraphs_content(self, doc_element: Any) -> str:
        text = ''
        paragraphs = doc_element.get("paragraph").get("elements")
        for paragraph in paragraphs:
            text_run = paragraph.get("textRun")
            text += '' if not text_run else text_run.get('content')
        return text

    def _read_table_content(self, doc_element: Any):
        text = ''
        table = doc_element.get("table")
        rows = table.get("tableRows")
        if rows is not None:
            for row in rows:
                cells = row.get("tableCells")
                if cells is not None:
                    for cell in cells:
                        text += self._read_content(cell.get("content"))
        return text

    def _read_table_of_contents_content(self, doc_element: Any):
        toc = doc_element.get("tableOfContents")
        return self._read_content(toc.get("content"))