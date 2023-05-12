import json
from pathlib import Path
from typing import Any

from llama_index.indices.vector_store import GPTSimpleVectorIndex


class IndexRunner:
    def __init__(self, doc_reader: Any = None,
                 index_path: str = None,
                 index_fname: str = 'store.json'):
        self.doc_reader = doc_reader

        if not Path('.\\google_drive_reader\\.store').exists():
            Path('.\\google_drive_reader\\.store').mkdir(parents=True, exist_ok=True)

        self.index_path = str(Path(__file__).parents[1] / '.store' / index_fname) \
            if index_path is None else index_path

        self.index = None
        if index_path is not None:
            self.index = GPTSimpleVectorIndex.load_from_disk(index_path)

    def run(self):
        docs = self.doc_reader.load()
        if self.index is None:
            self.index = GPTSimpleVectorIndex.from_documents(docs)
            self.index.save_to_disk(self.index_path)

    def query(self, prompt: str):
        return self.index.query(prompt)
