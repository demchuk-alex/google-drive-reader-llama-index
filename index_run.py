import json
from pathlib import Path
import os

from google_drive_reader.doc_readers.googledrivereader import GoogleDriveReader
from google_drive_reader.indexer.index_runner import IndexRunner


if __name__ == "__main__":
    os.environ['OPENAI_API_KEY'] = ''

    google_creds_path = Path(__file__).resolve().parent / 'google_drive_reader' / '.creds' / 'credentials.json'
    google_creds_json = google_creds_path.read_text().replace('\n', '')
    google_creds_dict = json.loads(google_creds_json)

    index_runner = IndexRunner(doc_reader=GoogleDriveReader(
        google_creds_dict=google_creds_dict,
        folder_id='',
    ), index_fname='store.json')

    index_runner.run()


