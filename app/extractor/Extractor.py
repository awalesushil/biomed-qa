"""
    Script to extract data from PMC text dump
"""
import re
import os

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
                        author_list.append(first_name + ' ' + last_name)
                    except AttributeError:
                        pass
        return author_list

    def __extract_date(self, history):
        """
            Extract date from XML file
        """
        if history:
            for date in history.find_all('date'):
                if date.attrs['date-type'] == 'accepted':
                    return date.day.text + '-' + date.month.text + '-' + date.year.text
        return ''

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
        metadata_dict['journal-title'] = metadata.find('journal-title').text
        metadata_dict['authors'] = self.___extract_authors(metadata.find('contrib-group'))
        metadata_dict['publication-date'] = self.__extract_date(metadata.find('history'))
        return metadata_dict

    def extract(self):
        """
            Extract text from PMC text dump
        """
        folders = os.listdir(self.path)
        for folder in folders:
            for file in tqdm(os.listdir(os.path.join(self.path, folder))):
                file_path = os.path.join(self.path, folder, file)
                document = BeautifulSoup(open(file_path, encoding="utf-8"), "html.parser")
                doc_dict['id'] = file.split('.')[0]
                doc_dict = self.extract_metadata(document.find('front'))
                doc_dict['abstract'] = self.__extract_paragraphs(document.find('abstract'))
                doc_dict['content'] = self.__extract_paragraphs(document.find('body'))
                yield doc_dict



if __name__ == "__main__":
    extractor = Extractor("xml_data_dump")
    for doc in extractor.extract():
        print(doc)
