"""
    Script to load data into Elasticsearch
"""
import json
from tqdm import tqdm

from biomedqa.retrievers.elasticsearchclient import ElasticsearchClient
from biomedqa.extractors.extractor import Extractor

with open("app/config.json", encoding="utf-8") as config:
    connection_config = json.load(config)
    connection_config["host"] = "localhost"

conn = ElasticsearchClient(connection_config)

def read_definitions(only_doc=False):
    """
        Generator to read the definitions from the file
    """
    with open("definitions/definitions", encoding="utf-8") as datafile:
        for i, line in tqdm(enumerate(datafile.readlines())):
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

# Load articles
extractor = Extractor(path="xml_data_dump")
conn.load(generator=extractor.extract_to(connection_config["index"]))
