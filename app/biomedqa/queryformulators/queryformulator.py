"""
    Query Formulator Model
"""
import re
import contractions

import spacy
from scispacy.abbreviation import AbbreviationDetector
from difflib import SequenceMatcher


class QueryFormulator:
    """
        Query Formulator Model
    """
    def __init__(self, medical, parser, stopWords):

        self.medical = medical # Medical NER and abreviations
        self.parser = parser # Dependency parsing and sentence tokenization

        self.stopWords = stopWords

    def clean_sentence(self, sentence):
        fixed_conts = contractions.fix(sentence) # Use contractions module to remove contractions and conjunctions
        finalSentence = re.sub(r'[!#$%&\*+,.;<>?@[\]^_{|}~]', '', fixed_conts.lower()) # Remove some specific punctuations  and lower the sentence
        finalSentence = re.sub(' +', ' ', finalSentence) # Remove possible double spaces

        return finalSentence     


    def get_medical_Entities(self, sentence_str):

        medical_sent = self.medical(sentence_str) # Parse the sentence using the medical spacy NLP
        medicalEntities = [X.text for X in medical_sent.ents] # Get the medical entities in str (text) form 
                                                              # X.label_ to know the class of the label (not needed)

        # Deal with abbreviations

        abbr_dictionary = dict(zip([X.text for X in medical_sent._.abbreviations], # Get the abbreviations (if there are)
                           [X._.long_form.text for X in medical_sent._.abbreviations] # Get the extended form of the abbreviation
                           ))


        # Include extended form:
        if len(abbr_dictionary) > 0:
          
          for i, term in enumerate(medicalEntities):            
            try:                              # Try to get the get the long form of the abbreviation if it is not already included in the entities 
              longV = abbr_dictionary[term] 
              if longV not in medicalEntities:
                medicalEntities = medicalEntities[:i] + [longV] + medicalEntities[i:]
            except KeyError:
                pass
        
        medicalEntities = self.shortenList(medicalEntities)         
        return medicalEntities
    
    
     # Delete repeated elements if they were expanded via the abbreviations
    def shortenList(self, medicalEntities):


      finalMedical = list()
      totalElements = len(medicalEntities)


      for i in range(totalElements):

        element = medicalEntities[i]
        counter = 0

        subList = medicalEntities[:i] + medicalEntities[i+1:]

        for subEl in subList:
          if element in subEl: counter = 1
        
        
        if counter == 0:
          finalMedical.append(element)
      

      return finalMedical
      

    def get_noun_chunks(self, sentence_parsed):
        
        # Get the name chunks --> get the chunks with parsedSentence.noun_chunks, 
        # then remove the stopWords (need to transform to set) and then make it string  --> keeping the original order

        nounChunks = [(' ').join(sorted(set(X.text.split(' ')) - self.stopWords, key=X.text.split(' ').index)) \
                      for X in list(sentence_parsed.noun_chunks)]
        

        return nounChunks
    

    def flattenCandidates(self, finalEntities):
      output = []      
      for word in finalEntities:
        if word.count(' ') >= 1: output.extend((word.split(' ')))
        else: output.append(word)
      return output
    


    ###########################################
    def expandEntities(self, med, chnk):

      # 1.1) In order for the matcher to work is important to imput the words depending on their size

      if len(med) != len(chnk):
        string1 = max(med, chnk, key = len)
        string2 = min(med, chnk, key = len)
      
      else:
        string1 = med
        string2 = chnk

      
      # If they are the same string, then they are the perfect match
      if string1 == string2:
        totalMatches = 10000
        return string1, totalMatches 
      
      else:
        # 1.2) Check if there is something to be matched https://www.pythonpip.com/python-tutorials/how-to-find-string-in-list-python/ --> worked better than regex matching
        longCnadidates = string1.split(' ')
        shortCandidates = string2.split(' ') if len(string2) > 1 and string2.isalnum() else ['$$$$']

        totalMatches = len([s for s in longCnadidates if any(xs in s for xs in shortCandidates)]) / len(longCnadidates) 

        # No match: --> then return the original entity
        if totalMatches == 0:                  
          return med, totalMatches 

        # Possible match:
        else:
          # 2) If matching was done then match the strings

          match = SequenceMatcher(None, string1,\
                          string2).find_longest_match\
                          (0, len(string1), 0, len(string2))
                
          # 3.1) Match the two strings
          result = string1[: match.a + match.size] + string2[match.b + match.size:] 


          # 3.2) Refine the results

          # 1) If the total match was the same as the short string, or the final match is shorter than the long string, then the end of the long string needs to be added
          if match.size == len(string2) and len(string1) >= len(result):         
            result += ' ' + string1[match.a + match.size:]
          
          # 2) If the last word of string 1 is not included then include it:
          elif len(string2) > 1:
            if string1[::-1][string1[::-1].find(' ')][::-1] !=  result[::-1][result[::-1].find(' ')][::-1]: # string1[::-1][string1[::-1].find(' ')][::-1] --> Find the last word of the string
              result += ' ' + string1[match.a + match.size:]    
            
          # 3) If the match with the second string doesn't start right at the beggining of the second string, include the first part of the second string 
          if match.b > 0:
            result = result[: match.a + match.size] + ' ' + string2[:match.b + 1] + ' ' + result[match.a + match.size:]
          
          
          # 4) Remove possible double spaces:
          result = re.sub(' +', ' ', result)    

          
          return result, totalMatches 

        # Result --> The matched sequence or empty if no matching was done
        # TotalMatches --> Maybe one entity matches more than a chunk, we will keep the one with the most matches


    # Since maybe an entity matches with more than one candidate, return the best candidate
    def getBestMatch(self, matches, intermediateDict):
      
      # 1) If matching were found, then get the best possible candidate
      if matches >= 1:  
        
        myList = list(intermediateDict.values())  # [[number, candidate]]

        if len(myList) == 1:

          expandedEntity = myList[0][1]
          chunkToDelete = list(intermediateDict.keys())[0]
        
        else:
          bestCand = sorted(myList, key=lambda item:item[0], reverse= True)  
          groupCand = bestCand[0] # [value, expandedEntity]
          
          chunkToDelete = list(intermediateDict.keys())[myList.index(groupCand)] # --> Get the name of the original chunk
          expandedEntity = groupCand[-1] # --> Get just the entity that was previously stored in intermediateDict      
        
        return expandedEntity, chunkToDelete


      # 2) If there are no matches then keep the original entity
      else:
        return "N/A", "N/A"
      

    # In this function, the list with the expanded entities and final chunks will be returned
    def loopOfExpansion(self, medical, chunks):

      finalList = []
      
      # Delete if there are empty entris
      medical = [med for med in medical if med]
      chunks = [chnk for chnk in chunks if chnk]
      

      # If there are no medical or noun chunks, return the opposite one
      if type(medical) == type(None):
        return chunks
      
      elif type(chunks) == type(None):
        return medical

      # 1) Get the lists len to see how the function will be implemented:
      medLen = len(medical)
      chnkLen = len(chunks)

      minLen = min(medLen, chnkLen)

      # Don't run the function if there are no chunks or entities
      if minLen == 0: 
        return max(medical, chunks, key = len) 
      

      # 2) If one of the list just has one element, iter only over the list with elements
      elif minLen == 1:
        matches = 0  # To track if no match is done
        intermediate = dict() # Link match to chunk

        if medLen == 1 and chnkLen == 1: # Trick to be able to iter when both lists just contain one item
          singleWord = medical[0]
          bigList = chunks
        
        else:
          singleWord = min(medical, chunks, key = len)[0] # Word belonging to the 1 item list
          bigList = max(medical, chunks, key = len)


        for word in bigList:

          cands, totalMatches  = self.expandEntities(word, singleWord)
          
          if totalMatches > 0:            
            intermediate[word] = [totalMatches, cands] 
            matches += 1   
              
        bestCand, deleteChunk = self.getBestMatch(matches, intermediate)

        # If no matching was done, then keep all the entities and name chunks
        if bestCand == "N/A" or deleteChunk == "N/A":
          finalList.append(singleWord)
          finalList.extend(bigList)
          bigList = []
          
        else:
          bigList.remove(deleteChunk)
          finalList.append(bestCand)
        
        totalFinal = [i for i in finalList + bigList if i] # Remove if there are entries which are (' ')
        return totalFinal
        
      # 3) When both lists have more than one element
      else:  
                  
        # 3.1) Iter over the medical entities and then over the name chunks
        for med in medical: 
          
          matches = 0  # To track if no match is done
          intermediate = dict() # Link match to chunk

          for chnk in chunks:

            # 3.2) Get the possible expansion

            cands, totalMatches  = self.expandEntities(med, chnk)

            if totalMatches > 0: # If matching is done added it the dictionary --> # Since, hipothetically, medical entities might match with more than 1 chunk, keep the best match depending on the amount of matched strings
              intermediate[chnk] = [totalMatches, cands] 
              matches += 1   


          bestCand, deleteChunk = self.getBestMatch(matches, intermediate)

          if bestCand == "N/A" or deleteChunk == "N/A":
            finalList.append(med)
        
          else:
            chunks.remove(deleteChunk)
            finalList.append(bestCand)

        
        totalFinal = test_list = [i for i in finalList + chunks if i] # Return the expanded entities + unused chunks --> remove empy spaces
        return totalFinal

    ###########################################
  

    def buildQuery(self, sentence):

      # Check the root of the sentence (get it and its childs) and also check the main subject of the sentence (get it and its childs too)
      
      # 1) Prepare the sentence  
      sentenceStr = self.clean_sentence(sentence) # Clean sentence in string format
      sentenceParsed = self.parser(sentenceStr) # Sentence as Spacy Doc


      # 2) Get the name chunks and the medical entities
      medEntities = self.get_medical_Entities(sentenceStr)
      nameChunks = self.get_noun_chunks(sentenceParsed)
      extendedEntities = self.loopOfExpansion(medEntities, nameChunks)      
      
      # 2) Parse the sentence using the en_core_web_sm parser, and get the words linked to the root (verb) and  entities:
      wordsOfInterest = list()  # Store the root or the main subject
      candidatesOfInterest = list() # Store the childs

      # 2.1) Get all the candidates in a list where each string is an entry
      myFlattenEntities = set(self.flattenCandidates(extendedEntities))

      for token in sentenceParsed:
  
        # If the token is the root or sentence main subject, get the dependent words upon it
        if token.dep_ == 'ROOT' or token.dep_ == 'nsubjt':

          children = [child.text for child in token.children if child.text not in myFlattenEntities] # Only include the children which are not an entity/chunk
          candidatesOfInterest.extend(children)
          if token.text not in myFlattenEntities: wordsOfInterest.extend([token.text])   # Only include the children which are not an entity/chunk
            
          # HEAD:
          if token.head.text not in myFlattenEntities: candidatesOfInterest.append(token.head.text)
                
      finalCanditates = set(wordsOfInterest).union(set(candidatesOfInterest)) -  self.stopWords


      # 3) Build the final sentence 
      finalSentence = (' ').join([word for word in sentenceStr.split(' ') if word in self.flattenCandidates(list(finalCanditates) + extendedEntities)])
      finalSentence = re.sub(' +', ' ', re.sub('[()]', '', finalSentence)) # Remove the parenthesis and possible double (or more) white spaces
      
      return str(finalSentence)
