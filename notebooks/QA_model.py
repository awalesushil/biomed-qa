#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().system('pip install transformers')
get_ipython().system('pip install torch  torchvision -f https://download.pytorch.org/whl/torch_stable.html')
import torch
import string


# In[2]:


from transformers import AutoTokenizer, AutoModelForQuestionAnswering

tokenizer = AutoTokenizer.from_pretrained("franklu/pubmed_bert_squadv2")

model = AutoModelForQuestionAnswering.from_pretrained("franklu/pubmed_bert_squadv2")


# In[3]:


question = "Who ruled Macedonia"

context = """Macedonia was an ancient kingdom on the periphery of Archaic and Classical Greece, 
and later the dominant state of Hellenistic Greece. The kingdom was founded and initially ruled 
by the Argead dynasty, followed by the Antipatrid and Antigonid dynasties. Home to the ancient 
Macedonians, it originated on the northeastern part of the Greek peninsula. Before the 4th 
century BC, it was a small kingdom outside of the area dominated by the city-states of Athens, 
Sparta and Thebes, and briefly subordinate to Achaemenid Persia."""

context= context.translate(str.maketrans('', '', string.punctuation))

# 1. TOKENIZE THE INPUT
inputs = tokenizer.encode_plus(question, context, return_tensors="pt") 

# 2. OBTAIN MODEL SCORES
# the AutoModelForQuestionAnswering class includes a span predictor on top of the model. 
# the model returns answer start and end scores for each word in the text
output = model(**inputs)
answer_start = torch.argmax(output.start_logits)  # get the most likely beginning of answer with the argmax of the score
answer_end = torch.argmax(output.end_logits) + 1  # get the most likely end of answer with the argmax of the score

# 3. GET THE ANSWER SPAN
# once we have the most likely start and end tokens, we grab all the tokens between them
# and convert tokens back to words!
tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(inputs["input_ids"][0][answer_start:answer_end]))

