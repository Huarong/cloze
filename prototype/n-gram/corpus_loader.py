#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: hhr
# @Date:   2013-11-11 18:40:36
# @Last Modified by:   hhr
# @Last Modified time: 2013-11-11 21:40:19

from nltk.corpus import PlaintextCorpusReader

corpus_root = '/home/hhr/myapps/cloze/corpus/Training_data'

wordlists = PlaintextCorpusReader(corpus_root, '04.*\.TXT')

print wordlists.fileids()

txt = word
print txt

print wordlists.words('04TOM10.TXT')

import time




