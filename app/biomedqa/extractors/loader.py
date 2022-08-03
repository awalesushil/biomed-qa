"""
    Script to load data into Elasticsearch
"""
import json
from app.biomedqa.retrievers.elasticsearchclient import ElasticsearchClient

connection_config = json.load(open("config.json", encoding="utf-8"))

conn = ElasticsearchClient(connection_config)

# Create Elasticsearch Index named pubmed
conn.create("pubmed2", "schema.json")

conn.load("retriever/data.json")
