from pathlib import Path
import os
from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel

from google_drive_reader.indexer.index_runner import IndexRunner
app = FastAPI()

os.environ['OPENAI_API_KEY'] = ''

index = IndexRunner(
    index_path=str(Path(__file__).parent / 'google_drive_reader' / '.store'/'hr-store.json')
)


class QueryRequest(BaseModel):
    query: str


@app.post("/query")
def query(request: QueryRequest):
    response = index.query(request.query)
    return {"message": str(response)}


@app.get("/run")
def run():
    return {"message": "This is the run endpoint"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
