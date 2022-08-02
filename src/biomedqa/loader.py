"""
    Script to load data into Elasticsearch
"""
import json
from elasticsearchclient import ElasticsearchClient

connection_config = json.load(open("retriever/config.json", encoding="utf-8"))

conn = ElasticsearchClient(connection_config)

# Create Elasticsearch Index named pubmed
conn.create("pubmed2", "retriever/schema.json")

conn.load("retriever/data.json")
