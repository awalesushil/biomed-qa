"""
    Retriever module for the Question Answering System
"""
import json

from sentence_transformers import util

from biomedqa.retrievers.elasticsearchclient import ElasticsearchClient
from biomedqa.retrievers.hnswlib import HNSWlibRetriever


class Retriever:
    """
        Retrieve passages from the index
    """
    def __init__(self, model, passage_model=None):
        with open("/code/app/config.json", encoding="utf-8") as config:
            config = json.load(config)
            self.conn = ElasticsearchClient(config)
        self.model = model
        self.passage_model = passage_model

    def encode_passages(self, passages):
        """
            Encode passages using the sentence transformer
        """
        passages = [p[1] for p in passages]
        passages = self.passage_model.encode(passages, show_progress_bar=False)
        return passages

    def tokenize(self, docs, passage_length=5):
        """
            Tokenize the passages
        """
        passages = []

        for doc in docs:
            title = doc["title"]
            full_text = doc["abstract"] + " " + doc["body"]
            sentences = full_text.split(".")
            passages.extend([(title, " ".join(sentences[i:i+passage_length])) \
                for i in range(0, len(sentences), passage_length)])

        titles = [p[0] for p in passages]
        passages = [p[1] for p in passages]

        return titles, passages

    def get_passages(self, query):
        """
            Retrieve passages from the index
        """
        # hits = self.conn.search(where=["title","body"], values=[query]*2)
        query_embedding = self.passage_model.encode([query])
        labels, _ = self.model.search(query_embedding)
        passages = [self.conn.get(label)['_source'] for label in labels[0]]
        return passages
