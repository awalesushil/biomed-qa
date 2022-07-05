from ElasticseachClient import ElasticsearchClient
import json

connection_config = json.load(open("retriever/config.json"))
        
conn = ElasticsearchClient(connection_config)

# Create Elasticsearch Index named pubmed
conn.create("pubmed", "retriever/schema.json")

# Load data from JSON file
with open("retriever/data.json", encoding="utf-8") as f:
    data = f.read()
    data = "[" + data.replace("}{", "},{") + "]"

data = json.loads(data)
conn.load(data)
