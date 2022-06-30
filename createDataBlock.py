import  requests
import os
from tqdm import tqdm
from Bio import Entrez
import requests
from bs4 import UnicodeDammit, BeautifulSoup # CLEAN XML/HTML TEXT TAGS
import json
import time



""" The goal is to get the information needed to build the Q&A system. For this, we have already downloaded the  txt files containing the whole article from PMC OA Bulk. \
Since the files don't share a common structure it has been nearly impossible to extract the title and abstract from there, for this reason we will use the E-Utilities Entrez \
API for retrieving these"""



""" 1) The Entrez API function efetch does not work properly when PMC ids are passed. For this reason we are converting them to PubMed ids through another PubMed API """


def transformPMCtoPUBMED_id(ids: list):

  if len(ids) > 1:
    ids = ','.join(ids)
  else:
    ids = str(ids[0])


  # Build the needed structure to make the request using the API --> https://www.ncbi.nlm.nih.gov/pmc/tools/id-converter-api/
  theURL = 'https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={}&format=json&tool={}&email={}'.format(ids,
                                                                                                            'my_tool', #NOT IMPORTANT
                                                                                                            'pablo.robles.de.zulueta@studium.uni-hamburg.de')

  myRequest = requests.get(theURL)

  # Get something back if there is:
  if (myRequest.status_code != 204 and
      myRequest.headers["content-type"].strip().startswith("application/json")):

    try:
      myContent = [code.get('pmid') for code in myRequest.json()['records']] #Sometimes the API fails to convert the PMC id, in those cases None will be returned
      return myContent

    except ValueError:
      pass



""" 2) Use Entrez API function efetch to get the article metadata from Pubmed """


# https://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.EFetch
# http://www.ncbi.nlm.nih.gov/account/ --> account to get the API key

def get_information(id_list, db):

    # Need to have the ids as a string, not as a list --> this is handled later in the function getTitleAndAbstract()
    if len(id_list) > 1:
        ids = ','.join(id_list) # efetch requires the ids to be a comma separated string
    else:
        ids = str(id_list[0])

    Entrez.email = 'pablo.robles.de.zulueta@studium.uni-hamburg.de'
    handle = Entrez.efetch(db = db,
                           rettype='null', #medline
                           retmode='xml',  #text
                           id=ids,
                           query_key = 'ce211c282446c6a50a893b496771671cb207' # A key has been obtained in order to be able to make 10 requests/second
                           )

    results = Entrez.read(handle, validate=False)
    return results


""" 3) Since the articles' bodies have already been bulk downloaded, the will get the information from the txt files locally stored. It should be noted that \
the ones whose sections were not separared by "===" (about 2%) have been deletedx   """

# Since we don't know the decoding and there was the following error: 'charmap' codec can't decode byte 0x9d
# To overcome this open with 'rb'


def getArticleBody(args,
                   pathWithFiles = r'C:\Users\pablo\Documents\2_PABLO\3. Máster\Hamburgo\2nd year\2022 SummerSemester\LT Project\Seminar\Bulk\Documents'
                  ):

    myName = args

    # Get the complete file name:
    myFile = os.path.join(pathWithFiles, myName)

    # Open the file
    with open(myFile, 'rb') as f:

        # 1) Read the file
        raw = f.read()

        # 2) Get the encoding
        encoding = UnicodeDammit(raw).original_encoding # (UnicodeDammit is more stable than #encoding = chardet.detect(raw)['encoding'])

        # 3) Decode the file to str
        decoded = raw.decode(encoding) #Decode into str format.

        #if len(decoded.split('====')) < 3:  --> THIS SHOULD BE TRUE SINCE WE CLEANED THE BODY
        return decoded.split('====')[2].replace('Body', '', 1)



""" 4) With all the other functions, now get the information for each of the articles and transform it into a dictionary"""

def getTitleAndAbstract(args):

    # FUNCTION IS INTENDED TO RECIEVE JUST 1 ID, SINCE IT WILL BE USED WITH MULTIPROCESSING

    # 1) Get the PMC id: --> PMCXXXXXXX.txt
    PMC_id = args

    if type(PMC_id) != list:
        PMC_id = [PMC_id]

    clean_PMC_id = list(map(lambda x: x.split('.')[0], PMC_id))

    # 2) Transform to PubMed id since PMC ids don't work well with efectch
    new_id = transformPMCtoPUBMED_id(clean_PMC_id)

    # 3) Check that all ids have been properly transformed:
    new_id_check = list(filter(None, new_id))

    # 3.1) If there are no ids, then don't try to extract the information
    totalIds = len(new_id_check)

    if totalIds == 0:
        pass


    else:

        # 4) Fetch the information from entrez
        myInfo = get_information(new_id_check, db = 'pubmed')

        # 5) Ensure that the retireved information is the same as the number of articles
        if totalIds == len(myInfo['PubmedArticle']):

            # 6) Get the information
            for num in range(len(myInfo['PubmedArticle'])):

                # 6.1) Get the title and the abstract --> Since they contain HTML tags we transform them to raw strings.
                title = BeautifulSoup(myInfo['PubmedArticle'][num]['MedlineCitation']['Article'].get('ArticleTitle', ''),
                                      "lxml").text


                # Be aware that some articles don't have abstract:
                abstract = myInfo['PubmedArticle'][num]['MedlineCitation']['Article'].get('Abstract', '')

                if len(dict(abstract)) != 0:  #Other solution if type(abstract) != Bio.Entrez.Parser.DictionaryElement:
                    abstract = BeautifulSoup(''.join(abstract.get('AbstractText', '')),
                                             "lxml").text


                # 6.2) Get the body from the txt files:
                body = getArticleBody(PMC_id[num])


                intermediateDict = {'PMC_id':clean_PMC_id[num],
                                    'title': title,
                                    'abstract': abstract,
                                    'body': body}


                return intermediateDict





if __name__ == "__main__":

    folderWithFiles = str(input('Write the target folder: '))
    finalPath = os.path.join(os.getcwd(), folderWithFiles)
    targetFiles = os.listdir(finalPath)


    start = time.time()


    for file in tqdm(targetFiles):
        infoDict = getTitleAndAbstract([file])


        with open(os.path.join(os.getcwd(), allDocs.json), 'a', encoding='utf-8') as f:
            json.dump(infoDict, f, ensure_ascii=False, indent=4)


    print('After {} the process has finished'.format(str(time.time() - start)))


    # Since indent has been used to create the JSON, this should be done when opening it:
    # with open(r'path.json', encoding='utf-8') as f:
    #    data = f.read()
    #    data = "[" + data.replace("}{", "},{") + "]"
    #    data_read = json.loads(data)
