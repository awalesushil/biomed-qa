import json
from .ElasticseachClient import ElasticsearchClient

class Retriever:

    def __init__(self):
        self.conn = ElasticsearchClient(json.load(open("/code/app/retriever/config.json")))
    
    def get_passages(self, keywords):
        docs = self.conn.search(where=["abstract","title","body"], values=[keywords]*3)
        return docs