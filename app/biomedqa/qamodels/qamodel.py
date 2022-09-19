"""
    Question Answering Model
"""

import string

import torch


class QAModel:
    """
        Question Answering Model
    """
    def __init__(self, tokenizer, model):
        self.tokenizer = tokenizer
        self.model = model

    def get_answers(self, question, passages):
        """
            Get answers from passages
        """
        answers = []
        for passage in passages:
            context = passage['body'].translate(str.maketrans("", "", string.punctuation))
            inputs = self.tokenizer.encode_plus(question, context, return_tensors="pt")

            # Obtain model scores
            output = self.model(**inputs)
            start = torch.argmax(output.start_logits)
            end = torch.argmax(output.end_logits) + 1

            # get answers
            tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0][start:end])
            answer = self.tokenizer.convert_tokens_to_string(tokens)
            answers.append(answer)
        return answers
