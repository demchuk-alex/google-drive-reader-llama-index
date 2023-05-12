import json
from pathlib import Path

from google_drive_reader.doc_readers.googledrivereader import GoogleDriveReader
import logging


def main():
    logger = logging.getLogger(main.__name__)
    logger.setLevel(logging.INFO)

    google_creds_path = Path(__file__).resolve().parent / 'google_drive_reader' / '.creds' / 'credentials.json'
    google_creds_json = google_creds_path.read_text().replace('\n', '')
    google_creds_dict = json.loads(google_creds_json)

    doc_reader = GoogleDriveReader(
        google_creds_dict=google_creds_dict,
        folder_id=''
    )
    docs = doc_reader.load()

    logger.info(f'Documents created {len(docs)}')
    logger.info(f'docs {[doc.extra_info for doc in docs]}')


if __name__ == "__main__":
    main()
