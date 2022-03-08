# import difflib
# import editdistance
# import math
# import numpy as np
# import re
# import spacy
# import string
# import torch
# from nltk.tokenize import sent_tokenize
# from transformers import BertConfig, BertForSequenceClassification, BertTokenizer, BertForMaskedLM
# from transformers import glue_convert_examples_to_features
# from transformers.data.processors.utils import InputExample
# from wmd import WMD
#
#
# class Gruen:
#     def __init__(self, bert_cola_dir):
#         self.device = torch.device("cpu")
#
#         # Initialize LM model
#         self.lm_model = BertForMaskedLM.from_pretrained('bert-base-cased').to(self.device)
#         self.lm_model.eval()
#         self.lm_tokenizer = BertTokenizer.from_pretrained('bert-base-cased')
#
#         # Initialize CoLa model
#         config_class, model_class, tokenizer_class = (BertConfig, BertForSequenceClassification, BertTokenizer)
#         config = config_class.from_pretrained(bert_cola_dir, num_labels=2, finetuning_task='CoLA')
#         self.cola_tokenizer = tokenizer_class.from_pretrained(bert_cola_dir, do_lower_case=0)
#         self.cola_model = model_class.from_pretrained(bert_cola_dir, from_tf=bool('.ckpt' in 'bert-base-cased'),
#                                                       config=config).to(self.device)
#         self.cola_model.eval()
#
#     @staticmethod
#     def preprocess_candidates(candidate):
#         candidate = candidate.strip()
#         candidate = '. '.join(candidate.split('\n\n'))
#         candidate = '. '.join(candidate.split('\n'))
#         candidate = '.'.join(candidate.split('..'))
#         candidate = '. '.join(candidate.split('.'))
#         candidate = '. '.join(candidate.split('. . '))
#         candidate = '. '.join(candidate.split('.  . '))
#         while len(candidate.split('  ')) > 1:
#             candidate = ' '.join(candidate.split('  '))
#         myre = re.search(r'(\d+)\. (\d+)', candidate)
#         while myre:
#             candidate = 'UNK'.join(candidate.split(myre.group()))
#             myre = re.search(r'(\d+)\. (\d+)', candidate)
#         candidate = candidate.strip()
#
#         sentences = sent_tokenize(candidate)
#         processed_candidate = []
#         for sentence_i in sentences:
#             if len(sentence_i.translate(
#                     str.maketrans('', '', string.punctuation)).split()) > 1:  # More than one word.
#                 processed_candidate.append(sentence_i)
#
#         return processed_candidate
#
#     def get_lm_score(self, sentence):
#         def score_sentence(sentence, tokenizer, model):
#             # if len(sentence.strip().split()) <= 1:
#             #     return 10000
#             tokenize_input = tokenizer.tokenize(sentence)
#             if len(tokenize_input) > 510:
#                 tokenize_input = tokenize_input[:510]
#             input_ids = torch.tensor(tokenizer.encode(tokenize_input)).unsqueeze(0).to(self.device)
#             with torch.no_grad():
#                 loss = model(input_ids, labels=input_ids)[0]
#             return math.exp(loss.item())
#
#         if len(sentence) == 0:
#             return 0
#         score_i = 0.0
#         for x in sentence:
#             score_i += score_sentence(x, self.lm_tokenizer, self.lm_model)
#         score_i /= len(sentence)
#
#         return score_i
#
#     def get_cola_score(self, sentences):
#
#         def evaluate_cola(model, candidates, tokenizer, model_name):
#
#             def load_and_cache_examples(candidates, tokenizer):
#                 max_length = 128
#                 examples = [InputExample(guid=str(i), text_a=x) for i, x in enumerate(candidates)]
#                 features = glue_convert_examples_to_features(examples, tokenizer, label_list=["0", "1"],
#                                                              max_length=max_length, output_mode="classification")
#                 # Convert to Tensors and build dataset
#                 all_input_ids = torch.tensor([f.input_ids for f in features], dtype=torch.long)
#                 all_attention_mask = torch.tensor([f.attention_mask for f in features], dtype=torch.long)
#                 all_labels = torch.tensor([0 for f in features], dtype=torch.long)
#                 all_token_type_ids = torch.tensor([[0.0] * max_length for f in features], dtype=torch.long)
#                 dataset = torch.utils.data.TensorDataset(all_input_ids, all_attention_mask, all_token_type_ids,
#                                                          all_labels)
#                 return dataset
#
#             eval_dataset = load_and_cache_examples(candidates, tokenizer)
#             eval_dataloader = torch.utils.data.DataLoader(eval_dataset,
#                                                           sampler=torch.utils.data.SequentialSampler(eval_dataset),
#                                                           batch_size=1)
#             preds = None
#             for batch in tqdm(eval_dataloader, desc="Evaluating"):
#                 model.eval()
#                 batch = tuple(t.to(device) for t in batch)
#
#                 with torch.no_grad():
#                     inputs = {'input_ids': batch[0], 'attention_mask': batch[1], 'labels': batch[3]}
#                     if model_name.split('-')[0] != 'distilbert':
#                         inputs['token_type_ids'] = batch[2] if model_name.split('-')[0] in ['bert',
#                                                                                             'xlnet'] else None  # XLM, DistilBERT and RoBERTa don't use segment_ids
#                     outputs = model(**inputs)
#                     tmp_eval_loss, logits = outputs[:2]
#
#                 if preds is None:
#                     preds = logits.detach().cpu().numpy()
#                 else:
#                     preds = np.append(preds, logits.detach().cpu().numpy(), axis=0)
#             return preds[:, 1].tolist()
#
#         def convert_sentence_score_to_paragraph_score(sentence_score, sent_length):
#             paragraph_score = []
#             pointer = 0
#             for i in sent_length:
#                 if i == 0:
#                     paragraph_score.append(0.0)
#                     continue
#                 temp_a = sentence_score[pointer:pointer + i]
#                 paragraph_score.append(sum(temp_a) / len(temp_a))
#                 pointer += i
#             return paragraph_score
#
#         model_name = 'bert-base-cased'
#         saved_pretrained_CoLA_model_dir = './cola_model/' + model_name + '/'
#         tokenizer, model = load_pretrained_cola_model(model_name, saved_pretrained_CoLA_model_dir)
#         candidates = [y for x in sentences for y in x]
#         sent_length = [len(x) for x in sentences]
#         cola_score = evaluate_cola(model, candidates, tokenizer, model_name)
#         cola_score = convert_sentence_score_to_paragraph_score(cola_score, sent_length)
#         return cola_score
