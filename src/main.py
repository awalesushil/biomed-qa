"""
    FAST Api app
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sentence_transformers import SentenceTransformer

from src.biomedqa.queryformulator import QueryFormulator
from src.biomedqa.retriever import Retriever
from src.biomedqa.qamodel import QAModel

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="/code/app/static"), name="static")

passage_model = SentenceTransformer("msmarco-bert-base-dot-v5")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
        Home page
    """
    queryForumulator = QueryFormulator()
    retriever = Retriever(passage_model)
    qamodel = QAModel()

    params = request.query_params
    if params:
        query = params.get("query").lower()
        # keywords = queryFormulator.get_keywords(query)
        # passages = retriever.get_passages(keywords)
        # answers = qamodel.get_answers(passages)
        results = retriever.get_passages(query)

        data = {
            "query": query,
            "results": results
        }

        return templates.TemplateResponse("index.html", {"request": request, "data": data})
    else:
        return templates.TemplateResponse("index.html", {"request": request, "data": {"query": ""}})