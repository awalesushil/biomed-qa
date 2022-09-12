"""
    FAST Api app
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from biomedqa.queryformulators.queryformulator import QueryFormulator
from biomedqa.retrievers.retriever import Retriever
from biomedqa.qamodels.qamodel import QAModel

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="/code/app/static"), name="static")

queryForumulator = QueryFormulator()
retriever = Retriever()
qamodel = QAModel()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
        Home page
    """

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
