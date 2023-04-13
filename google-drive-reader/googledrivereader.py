from pathlib import Path
from typing import Optional, List, Any
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from llama_index import Document

from doc_readers import (
    GoogleDocXReader,
    GoogleSheetReader,
    GoogleDocReader,
    DocumentMimeType
)

from pydantic import BaseModel

SCOPES = ['https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/documents.readonly',
          "https://www.googleapis.com/auth/spreadsheets.readonly"]


class GoogleDriveReader(BaseModel):
    service_account_key: Path = Path.home() / ".google_creds" / "keys.json"
    credentials_path: Path = Path.home() / ".google_creds" / "credentials.json"
    token_path: Path = Path.home() / ".google_creds" / "token.json"
    folder_id: Optional[str] = None

    credentials: Optional[Credentials] = None

    def load(self):
        files = self._load_files_from_folder()
        grouped_files = self._group_by_doc_mimetype(files)

        readers = {
            DocumentMimeType.DOC: GoogleDocReader(self._get_credentials()),
            DocumentMimeType.DOCX: GoogleDocXReader(self._get_credentials()),
            DocumentMimeType.SHEET: GoogleSheetReader(self._get_credentials())
        }

        documents: List[Document] = []
        for doc_type in grouped_files:
            google_docs = grouped_files[doc_type]
            doc_reader = readers[doc_type]
            files_ids = [doc['id'] for doc in google_docs]
            docs = doc_reader.load(files_ids)
            documents.extend(docs)

        return documents

    def _load_files_from_folder(self, query_str=None) -> List[Any]:
        query = f"'{self.folder_id}' in parents" if query_str is None else query_str
        creds = self._get_credentials()
        g_service = build('drive', 'v3', credentials=creds)
        request = g_service.files().list(
            q=query,
            pageSize=500,
            fields="nextPageToken, files(id, name, mimeType, properties)"
        )
        files = []
        while request is not None:
            response = request.execute()
            for file in response.get('files', []):
                if file['mimeType'] == 'application/vnd.google-apps.folder':
                    query = f"'{file['id']}' in parents"
                    files_int = self._load_files_from_folder(query)
                    files.extend(files_int)
                else:
                    files.append(file)

            request = g_service.files().list_next(previous_request=request, previous_response=response)
        return files

    def _group_by_doc_mimetype(self, files):
        grouped_data = {}
        ALLOWED_TYPES = DocumentMimeType().__dict__.values()
        for file in [item for item in files if item['mimeType'] in ALLOWED_TYPES]:
            key_value = file['mimeType']
            if key_value not in grouped_data:
                grouped_data[key_value] = []
            grouped_data[key_value].append(file)
        return grouped_data

    def _get_credentials(self):
        try:
            from google.auth.transport.requests import Request
            from google.oauth2 import service_account
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
        except ImportError:
            raise ImportError(
                "You must run"
                "`pip install --upgrade "
                "google-api-python-client google-auth-httplib2 "
                "google-auth-oauthlib`"
                "to use the Google Drive loader."
            )

        if self.credentials:
            return self.credentials

        if self.service_account_key.exists():
            self.credentials = service_account.Credentials.from_service_account_file(
                str(self.service_account_key), scopes=SCOPES
            )
            return self.credentials

        if self.token_path.exists():
            self.credentials = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)

        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open(self.token_path, "w") as token:
                token.write(self.credentials.to_json())

        return self.credentials
