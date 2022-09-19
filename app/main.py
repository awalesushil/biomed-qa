"""
    FAST Api app
"""
import os
import json
from datetime import datetime

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from biomedqa.queryformulators.queryformulator import QueryFormulator
from biomedqa.retrievers.retriever import Retriever
from biomedqa.qamodels.qamodel import QAModel

# Load Retrieval Model
from sentence_transformers import SentenceTransformer
passage_model = SentenceTransformer("msmarco-MiniLM-L6-cos-v5")
retriever = Retriever(passage_model=passage_model)

# Load QA model
from transformers import AutoTokenizer,AutoModelForQuestionAnswering
tokenizer = AutoTokenizer.from_pretrained("franklu/pubmed_bert_squadv2")
qa_bert_model = AutoModelForQuestionAnswering.from_pretrained("franklu/pubmed_bert_squadv2")
qa_model = QAModel(tokenizer=tokenizer, model=qa_bert_model)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="/code/app/static"), name="static")

queryForumulator = QueryFormulator()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
        Home page
    """
    params = request.query_params

    if params:
        query = params.get("query").lower()
        evaluate = params.get("evaluate", None)
        # keywords = queryFormulator.get_keywords(query
        passages = retriever.get_passages(query)
        answers = qa_model.get_answers(query, passages)

        data = {
            "query": query,
            "passages": passages,
            "answers": answers,
            "evaluate": evaluate
        }

        return templates.TemplateResponse("index.html", {"request": request, "data": data})
    else:
        return templates.TemplateResponse("index.html", {"request": request, "data": {"query": ""}})


@app.get("/confirm", response_class=HTMLResponse)
async def confirm(request: Request):
    """
        Confirm page
    """
    params = request.query_params
    _confirm = params.get("confirm")
    question = params.get("question")

    data = {
        "confirm": _confirm
    }
    scores = {
        "question": question,
        "data": {}
    }
    for each in params:
        if each not in ["confirm","question"]:
            scores["data"][each] = params.get(each)

    dir_path = "/code/app/responses"
    os.makedirs(dir_path, exist_ok=True)
    datetime_string = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{question} {datetime_string}.json"

    scores['datetime'] = datetime_string
    with open(os.path.join(dir_path,filename), "w", encoding="utf-8") as f:
        json.dump(scores, f)

    return templates.TemplateResponse("confirm.html", {"request": request, "data": data})
