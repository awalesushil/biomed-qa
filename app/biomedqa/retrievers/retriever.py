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
    def __init__(self, passage_model):
        self.conn = ElasticsearchClient(
                    json.load(open("/code/app/config.json", encoding="utf-8"))
                )
        self.passage_model = passage_model

    def encode_passages(self, passages):
        """
            Encode passages using the sentence transformer
        """
        passages = [p[1] for p in passages]
        passages = self.passage_model.encode(passages, show_progress_bar=False)
        return passages

    def bm25(self, keywords):
        """
            Elasticsearch BM25 retrieval
        """
        return self.conn.search(where=["abstract","title","body"], values=[keywords]*3)

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
        docs = self.bm25(query)[:10]
        titles, passages = self.tokenize(docs)
        query_embeddings = self.passage_model.encode(query, convert_to_tensor=True)
        passage_embeddings = self.encode_passages(passages)
        hits = util.semantic_search(query_embeddings, passage_embeddings, top_k=10)[0]
        passages = [
                {"title": titles[hit["corpus_id"]],
                "passage": passages[hit["corpus_id"]]} for hit in hits
            ]

        return passages
