"""
    Script to extract data from PMC text dump
"""
import re
import os
from datetime import datetime

from tqdm import tqdm
from bs4 import BeautifulSoup

class Extractor:
    """
        Extractor module to extract text from PMC text dump
    """
    def __init__(self, path):
        self.path = path

    def __clean(self, text):
        text = re.sub(r"\n", " ", text) # Remove new lines
        text = re.sub(r"<[^>]*>", "", text) # Remove html tags
        text = re.sub(r"\s+", " ", text) # Remove multiple spaces
        text = re.sub(r"\[( *\d+,*-* *)+\]", "", text) # Remove citations
        return text

    def __extract_paragraphs(self, element):
        """
            Extract text from p elements
        """
        if element:
            paragraphs = []
            for paragraph in element.find_all('p'):
                text = paragraph.text if paragraph else ''
                paragraphs.append(self.__clean(text))
            return paragraphs
        return []

    def ___extract_authors(self, authors):
        """
            Extract author from XML file
        """
        author_list = []
        if authors:
            for each in authors.find_all('contrib'):
                if each:
                    try:
                        first_name = each.find('given-names').text
                        last_name = each.find('surname').text
                        author_list.append({"name": first_name + ' ' + last_name})
                    except AttributeError:
                        pass
        return author_list

    def __extract_date(self, history):
        """
            Extract date from XML file
        """
        if history:
            for date in history.find_all('date'):
                if date and date.attrs['date-type'] == 'accepted':
                    date_str = date.year.text + '-' + date.month.text + '-' + date.day.text
                    date_str = datetime.strptime(date_str, "%Y-%m-%d").date()
                    return date_str.isoformat()
        return datetime.strptime('1900-01-01', "%Y-%m-%d").date().isoformat()

    def __extract_categories(self, categories):
        """
            Extract categories from XML file
        """
        category_list = []
        if categories:
            for category in categories.find_all('subject-group'):
                if category:
                    if category.attrs['subject-group-type'] == 'Discipline':
                        category_list.extend([each.text for each in category.find_all('subject')])
        return category_list

    def extract_metadata(self, metadata):
        """
            Extract metadata from XML file
        """
        metadata_dict = {}
        metadata_dict['title'] = metadata.find('article-title').text
        metadata_dict['categories'] = self.__extract_categories(metadata.find('article-categories'))
        metadata_dict['journal_title'] = metadata.find('journal-title').text
        metadata_dict['authors'] = self.___extract_authors(metadata.find('contrib-group'))
        metadata_dict['publication_date'] = self.__extract_date(metadata.find('history'))
        return metadata_dict

    def extract_to(self, index=None):
        """
            Extract text from PMC text dump
        """
        index_id = 5001
        folders = os.listdir(self.path)
        for folder in folders:
            for file in tqdm(os.listdir(os.path.join(self.path, folder))[:200]):

                file_path = os.path.join(self.path, folder, file)
                with open(file_path, encoding="utf-8") as doc_file:
                    document = BeautifulSoup(doc_file, "html.parser")

                doc_dict = self.extract_metadata(document.find('front'))
                doc_dict['pid'] = file.split('.')[0]

                abstract_paragraphs = self.__extract_paragraphs(document.find('abstract'))
                # Create new document for each abstract paragraph
                for paragraph in abstract_paragraphs:
                    if paragraph:
                        doc_dict['body'] = paragraph
                        doc_dict["id"] = index_id
                        index_id = index_id + 1
                        yield doc_dict if index is None else {
                            "_id": doc_dict["id"],
                            "_index": index,
                            "_source": doc_dict
                        }

                body_paragraphs = self.__extract_paragraphs(document.find('body'))
                # Create new document for each body paragraph
                for paragraph in body_paragraphs:
                    if paragraph:
                        doc_dict['body'] = paragraph
                        doc_dict["id"] = index_id
                        index_id = index_id + 1
                        yield doc_dict if index is None else {
                                "_id": doc_dict["id"],
                                "_index": index,
                                "_source": doc_dict
                            }
