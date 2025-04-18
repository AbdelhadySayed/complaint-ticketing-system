# from transformers import AutoTokenizer, T5Tokenizer
# from transformers import pipeline, T5ForConditionalGeneration, Seq2SeqTrainer, Seq2SeqTrainingArguments, AutoModelForSeq2SeqLM
# from transformers import BartTokenizer, BartForConditionalGeneration
# import textwrap
# import torch
# import re
# import os


# recommend_model_path = "C:/Users/ahmed/Desktop/project depi/BART_last_checkpoint"


# recommend_tokenizer = AutoTokenizer.from_pretrained(recommend_model_path)
# recommend_model = AutoModelForSeq2SeqLM.from_pretrained(recommend_model_path)

# ### 1- preprocessing the description for response generation

# # Contraction mapping
# CONTRACTION_MAP = {
#     "i've": "i have",
#     "i'm": "i am",
#     "don't": "do not",
#     "can't": "cannot",
#     "won't": "will not",
#     "it's": "it is",
#     "you're": "you are",
#     "they're": "they are",
#     "we're": "we are",
#     "that's": "that is",
#     "what's": "what is",
#     "who's": "who is",
#     "where's": "where is",
#     "when's": "when is",
#     "why's": "why is",
#     "how's": "how is",
#     "let's": "let us",
#     "he's": "he is",
#     "she's": "she is",
#     "there's": "there is",
#     "here's": "here is",
#     "isn't": "is not",
#     "aren't": "are not",
#     "wasn't": "was not",
#     "weren't": "were not",
#     "hasn't": "has not",
#     "haven't": "have not",
#     "hadn't": "had not",
#     "doesn't": "does not",
#     "didn't": "did not",
#     "wouldn't": "would not",
#     "shouldn't": "should not",
#     "couldn't": "could not",
#     "mustn't": "must not",
#     "i'll": "i will",
#     "you'll": "you will",
#     "he'll": "he will",
#     "she'll": "she will",
#     "we'll": "we will",
#     "they'll": "they will",
#     "it'll": "it will",
#     "that'll": "that will",
#     "there'll": "there will",
#     "this'll": "this will",
#     "what'll": "what will",
#     "who'll": "who will",
#     "where'll": "where will",
#     "when'll": "when will",
#     "why'll": "why will",
#     "how'll": "how will",
# }

# def expand_contractions(text, contraction_mapping=CONTRACTION_MAP):
#     """Expands contractions in the text."""
#     for contraction, expansion in contraction_mapping.items():
#         text = text.replace(contraction, expansion)
#     return text

# def preprocess_text(text):
#     """Cleans and preprocesses text while expanding contractions and preserving placeholders like {number}."""
#     if not isinstance(text, str):
#         return ""  # Handle cases where text is NaN or not a string

#     # Lowercasing
#     text = text.lower()

#     # Replace account numbers (assuming they are numeric sequences with 6+ digits)
#     text = re.sub(r'\b\d{6,}\b', '{number}', text)

#     # Expand contractions
#     text = expand_contractions(text)

#     # Remove special characters except `{}` placeholders
#     text = re.sub(r"[^\w\s{}]", "", text)

#     # Remove extra spaces
#     text = re.sub(r"\s+", " ", text).strip()
#     #print(text)
#     #print("==========")
#     return text


# ### preprocess the generated respone
# def preprocess_generated_response(response):
#     # Capitalize "i" to "I"
#     response = re.sub(r'\bi\b', 'I', response)

#     # Add punctuation after numbers in steps
#     response = re.sub(r'(\d) ', r'\1. ', response)

#     # Wrap text into readable paragraphs
#     formatted_response = textwrap.fill(response, width=80)

#     return formatted_response


# ### apply the recommenation model on the complaint description to recommend a resolution 
# def generate_response(description):
#     description = preprocess_text(description)

#     if len(description) ==0:
#         return None

#     inputs = recommend_tokenizer(description, return_tensors="pt", max_length=512, truncation=True)
#     output = recommend_model.generate(**inputs, max_length=512)
#     initial_response = recommend_tokenizer.decode(output[0], skip_special_tokens=True)
#     formatted_response = preprocess_generated_response(initial_response)

#     return formatted_response


# #print(generate_response("I want to cancel my order no 123456"))
