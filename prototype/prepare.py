#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: huohuarong
# @Date:   2013-11-13 17:22:51
# @Last Modified by:   hhr
# @Last Modified time: 2013-11-14 20:23:20

import os
import os.path

import nltk
from nltk.tokenize import TreebankWordTokenizer
from nltk.corpus import PlaintextCorpusReader

from util import init_log

class PreProcessor(object):
    def __init__(self, gutenberg_files_root, prepared_training_data_root, corpus_root):
        self.logger = init_log('util', '../log/util.log')
        self.gutenberg_files_root = gutenberg_files_root
        self.prepared_training_data_root = prepared_training_data_root
        self.corpus_root = corpus_root

    def prepare_training_data(self, declare=True):
        if not (os.path.exists(self.prepared_training_data_root) and os.path.isdir(self.prepared_training_data_root)):
            os.mkdir(self.prepared_training_data_root)
        file_list = os.listdir(self.gutenberg_files_root)
        for filename in file_list:
            print filename
            file_path = os.path.join(self.gutenberg_files_root, filename)
            self.prepare_a_training_data(file_path, self.prepared_training_data_root, declare=declare)
        return

    def prepare_a_training_data(self, file_path, out_root, declare=True, bos_eos=False):
        position = 0
        f = open(file_path, 'r')
        if declare:
            position = self._skip_declare(f)

        f.seek(position)
        out_path = os.path.join(out_root, os.path.basename(f.name))

        if bos_eos:
            with open(out_path, 'w') as out_f:
                self._add_bos_eos(f, out_f)
        else:
            with open(out_path, 'w') as out_f:
                out_f.write(f.read())
        f.close()
        return


    def _skip_declare(self, f):
        """Skip all the declares of Project Gutenberg, which ends like this:
        '*END*THE SMALL PRINT! FOR PUBLIC DOMAIN ETEXTS*Ver.04.29.93*END*'
        I have verified that all the training data files include this declare.
        Return the postion of the real beginning."""
        found = False
        real_begin = 0
        while True:
            line = f.readline()
            if line.startswith('*END*THE SMALL PRINT!') or line.startswith('ENDTHE SMALL PRINT!'):
                found = True
                real_begin = f.tell()
                break
        if not found:
            self.logger.info("not found *END*THE SMALL PRINT! in %s" % f.name)
        return real_begin

    def _add_bos_eos(self, f, out_f):
        """
        Add '<BOS>' at the begining of a sentence, and '<EOS> at the end of a sentence'
        """
        content = f.read()
        content = content.replace('.', ' <EOS> . <BOS>')
        content = content.replace('!', ' <EOS> ! <BOS>')
        content = content.replace('?', ' <EOS> ? <BOS>')
        out_f.write(content)
        return

    def compute_frequence(self, n=1):
        if n == 1:
            self._compute_unigram_freqency()
        elif n == 2:
            self._compute_biagram_freqency()
        else:
            self.logger.error("Unsupport n of n-gram")
        return None


    def _compute_unigram_freqency(self):
        wordlists = PlaintextCorpusReader(self.prepared_training_data_root, '.*')
        tokenizer = TreebankWordTokenizer()
        total = len(wordlists.fileids())
        count = 0
        fdist = nltk.FreqDist()
        for fl in wordlists.fileids():
            count += 1
            fl_abs_path = os.path.join(self.prepared_training_data_root, fl)
            with open(fl_abs_path, 'r') as f:
                words = tokenizer.tokenize(f.read())
                fdist.update(words)
            print 'freqdist: %s of %s' % (count, total)

        with open(os.path.join(self.corpus_root, 'unigram_frequency.txt'), 'w') as f:
            f.writelines(['%s %s\n' % (word, freq) for (word, freq) in fdist.items()])
        return None

    def _compute_biagram_freqency(self):
        bigram_frequency_dir = os.path.join(self.corpus_root, 'bigram_frequency')
        if not os.path.exists(bigram_frequency_dir):
            os.mkdir(bigram_frequency_dir)
        wordlists = PlaintextCorpusReader(self.prepared_training_data_root, '.*')
        tokenizer = TreebankWordTokenizer()
        total = len(wordlists.fileids())
        count = 0
        for fl in wordlists.fileids():
            count += 1
            print 'freqdist: %s of %s' % (count, total)
            fl_abs_path = os.path.join(self.prepared_training_data_root, fl)
            with open(fl_abs_path, 'r') as f:
                words = tokenizer.tokenize(f.read())
                bi_words = nltk.bigrams(words)
                fdist = nltk.FreqDist(bi_words)
            with open(os.path.join(bigram_frequency_dir, fl), 'w') as f:
                f.writelines(['%s %s %s\n' % (word[0], word[1], freq) for (word, freq) in fdist.items()])
        return None



def main():
    p = PreProcessor('../corpus/Training_data', '../corpus/prepared_training_data', '../corpus')
    # p.prepare_training_data()
    # p.compute_frequence()
    p.compute_frequence(n=2)
    return


if __name__ == '__main__':
    main()