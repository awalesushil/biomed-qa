from ElasticsearchClient import ElasticsearchClient
import json
import pprint

connection_config = json.load(open("config.json"))
        
conn = ElasticsearchClient(connection_config)

# Create Elasticsearch Index named pubmed
conn.create("pubmed", "schema.json")

# Load data from JSON file
conn.load("data.json")

# Search in the index
results = conn.search(where=["title"], values=["some value"])

pprint.pprint(results, indent=4)
