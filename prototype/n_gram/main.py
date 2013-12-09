#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import sys

from n_gram_model import NGramModel

sys.path.append('../')

import config

def main():
    n_gram = NGramModel(n=22)
    n_gram.extract_QA('../../corpus/development_set.txt')
    json_path = os.path.join(config.DATA_DIR, 'dev_set.json')
    # n_gram.compute_data_sparseness(json_path)
    print "begin to load freq dict..."
    n_gram.load_freq_dict()
    print "begin to compute option probability..."
    n_gram.compute_option_probability(json_path)
    answer_path = os.path.join(config.DATA_DIR, 'answers240.txt')
    stand_answer_path = os.path.join(config.CORPUS_DIR, 'development_set_answers.txt')
    print "begin to compute accuracy..."
    n_gram.compute_accuracy(answer_path, stand_answer_path)
    print "complete!"
    return None

if __name__ == '__main__':
    main()