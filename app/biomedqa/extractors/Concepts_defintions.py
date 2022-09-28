#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd 
import numpy as np 
from tqdm import tqdm


# In[2]:


definitions=[]
with open('C:\\Users\\Sara9\\Documents\\Universidad Alemania\\NLPProject\\data\\Definitions.txt', encoding="utf8") as f:
    line = f.readline()
    definitions.append(line)
    while line:
        line = f.readline()
        definitions.append(line)


# It can be observed that there are concepts with more than one definition, we only want one definition per concept. 

# In[ ]:


definitions


# In[ ]:


concept_terms=[]
with open('C:\\Users\\Sara9\\Documents\\Universidad Alemania\\NLPProject\\data\\ConceptTerms.txt', encoding="utf8") as f:
    line = f.readline()
    concept_terms.append(line)
    while line:
        line = f.readline()
        concept_terms.append(line)


# we are going to work only with English terms, so it is neccesary to remove Chinese terms. 

# In[ ]:


english_terms =[]
for i in range(len(concept_terms)): 
  if 'CHS' not in concept_terms[i]: 
    english_terms.append(concept_terms[i])


# In[ ]:


len(english_terms)


# In[ ]:


english_terms


# In[ ]:


len(concept_final)


# In[ ]:


len(definitions)


# In[ ]:


one_concept =[]
concepts_included =[]
for i in tqdm(range(len(english_terms))):
  x = english_terms[i].split("|")
  if x[0] not in concepts_included: 
    concepts_included.append(x[0])
    one_concept.append(english_terms[i])


# In[ ]:


with open('concepts_english.txt', 'w', encoding="utf8" ) as filehandle:
    for listitem in one_concept:
        filehandle.write('%s\n' % listitem)


# In[ ]:


one_definition =[]
definitions_included =[]
for i in tqdm(range(len(definitions))):
  x = definitions[i].split("|")
  if x[1] not in definitions_included: 
    definitions_included.append(x[1])
    one_definition.append(definitions[i])


# In[ ]:


with open('definitions.txt', 'w', encoding="utf8" ) as filehandle:
    for listitem in one_definition:
        filehandle.write('%s\n' % listitem)


# ### Read txt files created before

# In[12]:


one_definition=[]
with open('C:\\Users\\Sara9\\Documents\\Universidad Alemania\\NLPProject\\data\\definitions.txt', encoding="utf8") as f:
    line = f.readline()
    one_definition.append(line)
    while line:
        line = f.readline()
        one_definition.append(line)


# In[13]:


one_definition


# In[14]:


codes = []
for i in tqdm(range(len(one_definition))):
    x = one_definition[i].split("|")
    codes.append(x[1])


# In[15]:


english_terms=[]
with open('C:\\Users\\Sara9\\Documents\\Universidad Alemania\\NLPProject\\data\\concepts_english.txt', encoding="utf8") as f:
    for line in f.readlines(): 
        if line != '\n':
            english_terms.append(line)


# In[16]:


english_codes = []
for i in tqdm(range(len(english_terms))):
    x = english_terms[i].split("|")
    english_codes.append(x[0])


# In[17]:


indexes = []
with open('final.txt', 'w', encoding="utf8" ) as f:
    for i in tqdm(range(len(codes))): 
        try: 
            index_words = english_codes.index(codes[i])
            word = english_terms[index_words].split("|")[2]
            definition = one_definition[i].split("|")[2]
            line = str(word) +':' + ' '+ str(definition) + '\n'
            f.write(line)
        except: 
            pass


# In[ ]:




