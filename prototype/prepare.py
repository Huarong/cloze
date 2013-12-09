#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path

import nltk
from nltk.tokenize import TreebankWordTokenizer
from nltk.corpus import PlaintextCorpusReader
from nltk.stem import PorterStemmer

from util import init_log

class PreProcessor(object):
    def __init__(self, gutenberg_files_root, prepared_training_data_root, corpus_root, stem=None):
        if not os.path.exists('../log'):
            os.mkdir('../log')
        self.logger = init_log('util', '../log/util.log')
        self.gutenberg_files_root = gutenberg_files_root
        self.prepared_training_data_root = prepared_training_data_root
        self.corpus_root = corpus_root
        self.bigram_frequency_dir = os.path.join(self.corpus_root, 'bigram_frequency')
        self.hop_bigram_frequency_dir = os.path.join(self.corpus_root, 'hop_bigram_frequency')
        # stem algorithm can be "Poter"
        self.stem = stem
        if self.stem == 'Porter':
            self.bigram_frequency_dir = os.path.join(self.corpus_root, 'bigram_frequency_porter')
            self.hop_bigram_frequency_dir = os.path.join(self.corpus_root, 'hop_bigram_frequency_porter')

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

    def compute_frequency(self, n=1):
        if n == 1:
            self._compute_unigram_frequency()
        elif n == 2:
            self._compute_biagram_frequency()
        elif n == 22:
            self._compute_hop_biagram_frequency()
        else:
            self.logger.error("Unsupport n of n-gram")
        return None


    def _compute_unigram_frequency(self):
        frequence_file_path = os.path.join(self.corpus_root, 'unigram_frequency.txt')

        mystem = self.stem
        if mystem == "Porter":
            self.logger.info("using stemming algorithm PorterStemmer in _compute_unigram_frequency")
            stemmer = PorterStemmer()
            frequence_file_path = os.path.join(self.corpus_root, 'unigram_frequency_poter.txt')

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
                # stemming
                if mystem == 'Porter':
                    words = [stemmer.stem(w) for w in words]

                fdist.update(words)
            print 'freqdist: %s of %s' % (count, total)

        with open(frequence_file_path, 'w') as f:
            f.writelines(['%s %s\n' % (word, freq) for (word, freq) in fdist.items()])

        type_num = len(fdist)
        self.logger.info("The total type number is: %d" % type_num)
        return None


    def _compute_biagram_frequency_base(self, t, freq_dir):
        mystem = self.stem
        if mystem == "Porter":
            self.logger.info("using stemming algorithm PorterStemmer in _compute_bigram_frequency")
            stemmer = PorterStemmer()

        if not os.path.exists(freq_dir):
            os.mkdir(freq_dir)
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
                # stemming
                if mystem == "Porter":
                    words = [stemmer.stem(w) for w in words]

                if t == 'b':
                    bi_words = nltk.bigrams(words)
                    fdist = nltk.FreqDist(bi_words)
                elif t == 'h':
                    tri_words = nltk.trigrams(words)
                    # the second word is hoped
                    hop_bi_words = [(a, c) for (a, b, c) in tri_words]
                    fdist = nltk.FreqDist(hop_bi_words)
                else:
                    self.logger.error("unknown bigrams type %s" % t)
                    return -1
            with open(os.path.join(freq_dir, fl), 'w') as f:
                f.writelines(['%s %s %s\n' % (word[0], word[1], freq) for (word, freq) in fdist.items()])
        return None

    def _compute_biagram_frequency(self):
        self._compute_biagram_frequency_base('b', self.bigram_frequency_dir)
        self._merge_bigram_frequency('b', self.bigram_frequency_dir)
        if self.stem == 'Porter':
            self._sort_by_freq('unorder_bigram_frequency_porter.txt', 'bigram_frequency_porter.txt')
        else:
            self._sort_by_freq('unorder_bigram_frequency.txt', 'bigram_frequency.txt')
        return None

    def _compute_hop_biagram_frequency(self):
        self._compute_biagram_frequency_base('h', self.hop_bigram_frequency_dir)
        self._merge_bigram_frequency('h', self.hop_bigram_frequency_dir)
        if self.stem == 'Porter':
            self._sort_by_freq('unorder_hop_bigram_frequency_porter.txt', 'hop_bigram_frequency_porter.txt')
        else:
            self._sort_by_freq('unorder_hop_bigram_frequency.txt', 'hop_bigram_frequency.txt')
        return None

    def _merge_bigram_frequency(self, t, freq_dir):
        file_list = os.listdir(freq_dir)
        freq_dic = {}
        total = len(file_list)
        count = 0
        for fl in file_list:
            count += 1
            print "merge %d of %d" % (count, total)
            real_path = os.path.join(freq_dir, fl)
            with open(real_path, 'r') as f:
                for line in f:
                    e = line.split()
                    word_pair = "%s %s" % (e[0], e[1])
                    freq = e[2]
                    freq_dic[word_pair] = freq_dic.get(word_pair, 0) + int(freq)
        if t == 'b':
            if self.stem == 'Porter':
                unorder_frequency_file = 'unorder_bigram_frequency_porter.txt'
            else:
                unorder_frequency_file = 'unorder_bigram_frequency.txt'
        elif t == 'h':
            if self.stem == 'Porter':
                unorder_frequency_file = 'unorder_hop_bigram_frequency_porter.txt'
            else:
                unorder_frequency_file = 'unorder_hop_bigram_frequency.txt'
        else:
            self.logger.error("unknown bigrams type %s" % t)
            return -1
        with open(os.path.join(self.corpus_root, unorder_frequency_file), 'w') as f:
            f.writelines(['%s %s\n' % (word_pair, freq) for (word_pair, freq) in freq_dic.items()])

        type_num_2 = len(freq_dic)
        self.logger.info("The total 2 gram type number is: %d" % type_num_2)
        return None

    def _sort_by_freq(self, unorder_frequency_file, order_freqency_file):
        freq_list = []
        with open(os.path.join(self.corpus_root, unorder_frequency_file), 'r') as f:
            for line in f:
                t = line.strip().split()
                word_pair = "%s %s" % (t[0], t[1])
                freq = t[2]
                freq_list.append((word_pair, freq))

        freq_list.sort(key=lambda x: x[1], reverse=True)

        with open(os.path.join(self.corpus_root, order_freqency_file), 'w') as f:
            f.writelines(["%s %s\n" % (word_pair, freq) for (word_pair, freq) in freq_list])
        return None



def main():
    p = PreProcessor('../corpus/Training_data', '../corpus/prepared_training_data', '../corpus', stem='Porter')
    # p.prepare_training_data()
    p.compute_frequency(n=1)
    p.compute_frequency(n=22)
    return None


if __name__ == '__main__':
    main()