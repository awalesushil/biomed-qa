"""
        Elasticsearch client to store and retrieve data from Elasticsearch
"""
import json

from elasticsearch import Elasticsearch, ElasticsearchException, helpers


class ElasticsearchClient:
    """
        Elasticsearch client to store and retrieve data from Elasticsearch
    """
    def __init__(self, config):
        '''
            Create an Elasticsearch Python client
            @params:
                config: Server configs
        '''
        self.conn = Elasticsearch(
                                [config['host']],
                                http_auth=(config['username'], config['password']),
                                port = config['port'],
                                timeout=300)
        self.config = config
        self.index = None
        if 'index' in config.keys():
            self.index = config['index']
            mappings = self.conn.indices.get_mapping(self.index)
            self.properties = mappings[self.index]["mappings"]["properties"]


    def create(self, index, schema_path):
        '''
            Creates a new index, if not exists, on the Elasticsearch server
            @params:
                index: Name of index to create
                schema_path: Path to JSON schema definition
        '''
        if self.conn.indices.exists(index):
            print("Index " + index + " already exists. Skipping creating index...")
            self.index = index
        else:
            try:
                schema = json.load(open(schema_path, "r", encoding="utf-8"))
                self.conn.indices.create(index=index, body=schema)
                print("Created a new index with name " + index)
                self.index = index
                mappings = self.conn.indices.get_mapping(self.index)
                self.properties = mappings[self.index]["mappings"]["properties"]
            except ElasticsearchException as err:
                print("Error === ", err)


    def get(self, doc_id):
        '''
            Returns a single document from the index with the identifier id
            @params:
                doc_id: Id of the document to be retrieved
        '''
        result = self.conn.get(index=self.config['index'], id=doc_id)

        doc = {
            "doc_id": id,
            "_source": result['_source']
        }

        return doc


    def insert(self, doc, doc_id):
        '''
            Adds new document to the index
            @params:
                doc: New document to be added to the index
                doc_id: Id for the document to be added
        '''
        try:
            self.conn.create(index=self.index, body=doc, id=doc_id)
        except ElasticsearchException as err:
            print("Exception === ", err)


    def __build_query(self, keys=None, values=None, func=None):

        if keys is not None:

            _keys = self.__parse_keys(keys)
            query = {"bool":{"must":[]}}

            index_list = []

            for k in _keys:
                if self.properties[k]["type"] == "nested":
                    index_list.append(k)
                    nested_query = {
                        "nested":{
                            "path": k,
                            "query":{"bool":{"must": []}}}
                        }
                    query["bool"]["must"].append(nested_query)

            for key, val in zip(keys, values):
                key_label = key.split(".")[0]
                if self.properties[key_label]["type"] == "nested":
                    match = {func: {key: val}}
                    index = index_list.index(key_label)
                    query['bool']['must'][index]['nested']['query']['bool']['must'].append(
                        match
                    )
                else:
                    match = {func: {key: val}}
                    query['bool']['must'].append(match)
        else:
            query = {"match_all":{}}
        return query


    def __parse_keys(self, keys):
        _keys_dict = {k.split(".")[0]: [] for k in keys}

        for key in [k.split(".") for k in keys]:
            if len(key) > 1:
                _keys_dict[key[0]].append(key[1])
        return _keys_dict

    def __process_result(self, results, key=None):
        docs = []
        for doc in results['hits']['hits']:
            if key:
                for each in doc['_source'][key]:
                    docs.append(each)
            else:
                docs.append(doc['_source'])
        return docs


    def search(self, where=None, values=None):
        '''
            Retrieve all documents from the index that satisfies the key-value constraints
            If the key-value pairs are not specified then all documents are retrieved
            @params:
                where: List of fields of the documents to match
                values: List of values for the selected fields
                key: Only retreive documents with selected key
        '''
        query = self.__build_query(where, values, func="match")
        _results  = self.conn.search(index=self.index, body=query)
        results = self.__process_result(_results)
        return results

    def format_doc(self, doc):
        """
            Format the document to be inserted into the index
        """
        _doc = {"field":[]}

        for key, val in doc.items():
            if key in ['title','body','abstract']:
                _doc[key] = val
            else:
                field = {"field_uid": key,"value": val}
                _doc["field"].append(field)
        return _doc


    def load(self, datapath):
        '''
            Bulk load all the data into index
            @params:
                data: data
        '''
        generator = self.__generator(datapath)
        try:
            helpers.bulk(self.conn, generator, self.index)
            print("Data loading successfull")
        except ElasticsearchException as err:
            print("Error === ", err)

    def __generator(self, datapath):
        '''
            Returns a single line of data without loading document into memory
            @params:
                data:   list of data
        '''
        # Load data from JSON file
        with open(datapath, encoding="utf-8") as file:
            data = file.read()
            data = "[" + data.replace("}{", "},{") + "]"
            for doc in data:
                yield {
                    "_index": self.index,
                    "_source": self.format_doc(doc)
                }
