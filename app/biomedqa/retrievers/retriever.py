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

    def get_passages(self, query, top_k=10):
        """
            Retrieve passages from the index
        """

        if self.model:
            encoded_query = self.encode_passages([query])
            labels, _ = self.model.search(encoded_query, top_k=top_k)
            passages = [self.conn.get(label)['_source'] for label in labels[0]]
        else:
            top_j = 100 # Get top j passages from the index using BM25
            hits = self.conn.search(where=["title","body"], values=[query, query], size=top_j)

            # Encode the passages
            encoded_passages = self.encode_passages([hit["body"] for hit in hits])
            encoded_query = self.encode_passages([query])

            # Compute cosine similarity between query and passages
            docs = util.semantic_search(encoded_query, encoded_passages, top_k=top_k)[0]
            passages = [hits[doc["corpus_id"]] for doc in docs]

        return passages
