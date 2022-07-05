from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from queryformulator.QueryFormulator import QueryFormulator
from retriever.Retriever import Retriever
from qamodel.QAModel import QAModel

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="/code/app/static"), name="static")
        

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    queryForumulator = QueryFormulator()
    retriever = Retriever()
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