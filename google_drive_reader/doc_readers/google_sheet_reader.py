from typing import Tuple

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from .document_type import DocumentType
from .google_item_reader import GoogleItemReader


class GoogleSheetReader(GoogleItemReader):
    base_url = DocumentType.SHEET

    def __init__(self, creds: Credentials):
        super().__init__(creds)

    def _get_service(self):
        return build("sheets", "v4", credentials=self.creds)

    def _get_doc_content_and_meta(self, service, doc_id: str) -> Tuple[str, str]:
        url = f"{self.base_url}{doc_id}/edit"
        doc_data = service.spreadsheets().get(spreadsheetId=doc_id).execute()
        sheets = doc_data.get("sheets")
        sheet_text = ''

        for sheet in sheets:
            properties = sheet.get("properties")
            title = properties.get("title")
            sheet_text += title + "\n"
            grid_props = properties.get("gridProperties")
            rows = grid_props.get("rowCount")
            cols = grid_props.get("columnCount")
            range_pattern = f"R1C1:R{rows}C{cols}"
            response = (
                service.spreadsheets()
                .values()
                .get(spreadsheetId=doc_id, range=range_pattern)
                .execute()
            )
            sheet_text += (
                    "\n".join(map(lambda row: "\t".join(row), response.get("values", [])))
                    + "\n"
            )
        return sheet_text, url
