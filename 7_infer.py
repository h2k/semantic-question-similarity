import csv
import argparse

import numpy as np
import pickle as pkl

from os import remove
from os.path import join
from keras.models import load_model
from keras_self_attention import SeqWeightedAttention

from helpers import *

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--data-dir', default='data_dir')
  parser.add_argument('--doc2vec-dir', default='doc2vec_dir')
  parser.add_argument('--embeddings-dir', default='embeddings_dir')
  parser.add_argument('--model-path', default='checkpoints/epoch100.ckpt')
  args = parser.parse_args()

  doc2vec_model = load_doc2vec_model(join(args.doc2vec_dir, 'model'))
  embeddings_model, index2word, word2index, embeddings_matrix = load_fasttext_embedding(join(args.embeddings_dir, 'model'))
  char2index = load_characters_mapping(join(args.data_dir, 'characters.pkl'))

  model = load_model(args.model_path, custom_objects={'f1': f1, 'SeqWeightedAttention': SeqWeightedAttention})

  data = list()
  with open(join(args.data_dir, 'test_processed.csv'), 'r') as file:
    reader = csv.reader(file)
    for row in reader:
      data.append((map_sentence(row[0], doc2vec_model, word2index, char2index), map_sentence(row[1], doc2vec_model, word2index, char2index), int(row[2])))

  try:
    remove(join(args.data_dir, 'submit.csv'))
  except:
    pass

  with open(join(args.data_dir, 'submit.csv'), 'w') as file:
    writer = csv.writer(file)
    writer.writerow(['QuestionPairID', 'Prediction'])

    for idx, example in enumerate(data):
      print(idx, end='\r')
      prediction = model.predict([[np.array(example[0][0])], [np.array(example[0][1])], [np.array(example[0][2])], [np.array(example[1][0])], [np.array(example[1][1])], [np.array(example[1][2])]]).squeeze()
      if prediction >= 0.5:
        writer.writerow([example[2], 1])
      else:
        writer.writerow([example[2], 0])