import logging
from pathlib import Path
from typing import Optional, List, Any, Dict, Type

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from llama_index import Document
from pydantic import BaseModel

from google_drive_reader.doc_readers import (
    GoogleDocXReader,
    GoogleSheetReader,
    GoogleDocReader,
    DocumentMimeType,
    GooglePdfReader
)
from google_drive_reader.doc_readers.google_item_reader import GoogleItemReader

SCOPES = ['https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/documents.readonly',
          "https://www.googleapis.com/auth/spreadsheets.readonly"]


class GoogleDriveReader(BaseModel):
    google_creds_dict: Optional[Dict[str, str]] = None
    service_account_key: Path = Path.home() / ".google_creds" / "keys.json"
    credentials_path: Path = Path.home() / ".google_creds" / "credentials.json"
    token_path: Path = Path.home() / ".google_creds" / "token.json"
    folder_id: Optional[str] = None
    logger: Any = None

    credentials: Optional[Credentials] = None
    doc_readers: Optional[Dict[str, Type[GoogleItemReader]]] = None

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.logger = logging.getLogger('Test')
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

        self.doc_readers = self.doc_readers if self.doc_readers is not None else {
            DocumentMimeType.DOC: GoogleDocReader,
            DocumentMimeType.DOCX: GoogleDocXReader,
            DocumentMimeType.SHEET: GoogleSheetReader,
            DocumentMimeType.PDF: GooglePdfReader,
        }

    def load(self, query: str = None):
        files = self._load_files_from_folder(query_str=query)
        self.logger.info(f"There are {len(files)} files")
        grouped_files = self._group_by_doc_mimetype(files)

        documents: List[Document] = []
        for doc_type in grouped_files:
            google_docs = grouped_files[doc_type]
            doc_reader = self.doc_readers[doc_type](self._get_credentials())
            files_ids = [doc['id'] for doc in google_docs]
            docs = doc_reader.load(files_ids)
            documents.extend(docs)

        return documents

    def _load_files_from_folder(self, query_str=None) -> List[Any]:
        file_type_query = ' or '.join([f"mimeType='{file_type}'" for file_type, _ in self.doc_readers.items()])
        filter_str = f" and ({file_type_query})"
        query = f"'{self.folder_id}' in parents {filter_str}" if query_str is None else query_str
        self.logger.info(query)
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
        ALLOWED_TYPES = self.doc_readers.keys()
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

        self.logger.info(self.service_account_key)
        if self.service_account_key.exists():
            self.credentials = service_account.Credentials.from_service_account_file(
                str(self.service_account_key), scopes=SCOPES
            )
            return self.credentials
        elif self.google_creds_dict is not None:
            self.credentials = service_account.Credentials.from_service_account_info(
                self.google_creds_dict
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
