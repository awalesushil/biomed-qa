"""
    Script to load data into Elasticsearch
"""
import json
from tqdm import tqdm
import pandas as pd

from biomedqa.retrievers.elasticsearchclient import ElasticsearchClient
from biomedqa.retrievers.hnswlib import HNSWlibRetriever
from biomedqa.extractors.extractor import Extractor

from sentence_transformers import SentenceTransformer
passage_model = SentenceTransformer("msmarco-bert-base-dot-v5")

with open("app/config.json", encoding="utf-8") as config:
    connection_config = json.load(config)
    connection_config["host"] = "localhost"

conn = ElasticsearchClient(connection_config)
index = HNSWlibRetriever(50130, 768, "app/hnswlib_index.bin")
index.create()

def read_definitions(only_doc=False):
    """
        Generator to read the definitions from the file
    """
    with open("definitions/definitions", encoding="utf-8") as datafile:
        for i, line in tqdm(enumerate(datafile.readlines()[:5000])):
            segments = line.split(":")
            doc = {
                "id": i,
                "title": segments[0],
                "body": line
            }
            yield doc if only_doc else {
                "_id": i,
                "_index": connection_config["index"],
                "_source": doc
            }


# Load defintions
conn.load(generator=read_definitions())
df = pd.DataFrame(read_definitions(only_doc=True))
data = passage_model.encode(df['body'], show_progress_bar=True)
index.add(data, df["id"])


# Load articles
extractor = Extractor(path="xml_data_dump")
conn.load(generator=extractor.extract_to(connection_config["index"]))
df = pd.DataFrame(extractor.extract_to())
data = passage_model.encode(df['body'], show_progress_bar=True)
index.add(data, df["id"])

index.save()
