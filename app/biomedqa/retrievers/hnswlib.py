"""
    HNSWlib retriever
"""
import os
from hnswlib import Index


class HNSWlibRetriever:
    """
        HNSWlib retriever
    """
    def __init__(self, num_elements, dimension, path, metric='l2'):
        self.index = Index(space=metric, dim=dimension)
        self.num_elements = num_elements
        self.path = path

    def create(self):
        """
            Create the index
        """
        self.index.init_index(max_elements=self.num_elements, ef_construction=200, M=16)
        self.index.set_ef(50)

    def add(self, data, ids):
        """
            Add data to the index
        """
        self.index.add_items(data, ids)

    def search(self, query, k=10):
        """
            Search the index
        """
        return self.index.knn_query(query, k=k)

    def save(self):
        """
            Save the index
        """
        print("Saving index to " + self.path)
        self.index.save_index(self.path)

    def load(self):
        """
            Load the index
        """
        print("Loading index from " + self.path)
        self.index.load_index(self.path, max_elements=self.num_elements)
