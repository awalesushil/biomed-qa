"""
    Retriever module for the Question Answering System
"""
import json

from sentence_transformers import util

from biomedqa.retrievers.elasticsearchclient import ElasticsearchClient


class Retriever:
    """
        Retrieve passages from the index
    """
    def __init__(self, model=None, passage_model=None):
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

    def get_passages(self, query, top_k=10):
        """
            Retrieve passages from the index
        """
        passages = self.conn.search(where=["body"], values=[query])
        return passages[:top_k]
