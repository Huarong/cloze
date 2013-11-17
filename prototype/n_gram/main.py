#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import sys

from n_gram_model import NGramModel

sys.path.append('../')

import config

def main():
    n_gram = NGramModel()
    # n_gram.extract_QA('../../corpus/development_set.txt')
    # json_path = os.path.join(config.DATA_DIR, 'dev_set.json')
    # n_gram.compute_data_sparseness(json_path)
    n_gram.load_freq_dict()
    n_gram.compute_option_probability('dev_set.json')
    return None

if __name__ == '__main__':
    main()