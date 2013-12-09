#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import json
import os.path

from nltk.tokenize import TreebankWordTokenizer

sys.path.append('../')
from util import init_log
import config

class NGramModel(object):
    def __init__(self, n=2):
        self.qa_path = None
        self.n = n
        self.logger = init_log('ngram', os.path.join(config.LOG_DIR, 'ngram.log'))
        self.__uni_freq_path = os.path.join(config.CORPUS_DIR, 'unigram_frequency.txt')
        self.__bi_freq_path = os.path.join(config.CORPUS_DIR, 'bigram_frequency.txt')
        self.__hop_bi_freq_path = os.path.join(config.CORPUS_DIR, 'hop_bigram_frequency.txt')
        self.uni_freq_dict = {}
        self.bi_freq_dict = {}
        self.hop_bi_freq_dict = {}
        self.num_p_zero = 0

    def config(self):
        pass

    def extract_QA(self, qa_path):
        qa_dict = {}
        line_no = 0
        q_no = 0
        with open(qa_path, 'r') as f:
            for line in f:
                line.strip()
                line_no += 1
                line_no = line_no % 8
                if line_no == 1:
                    if not line:
                        break
                    words = self.extract_Q(line)
                    print words
                    q_no = words[0]
                    qa_dict[q_no] = {'q': words[1:], 'a': {}}
                elif 2 <= line_no <= 6:
                    option = self.extract_A(line)
                    qa_dict[q_no]['a'][option[0]] = option[1]
                else:
                    continue
        json_path = os.path.join(config.DATA_DIR, 'dev_set.json')
        with open(json_path, 'w') as f:
            json.dump(qa_dict, f, indent=2, ensure_ascii=False)
        return None

    def _judge_Q_or_A(self, sentence):
        pattern_q = '^\d+.+'
        pattern_a = '\s+'
        r_q = re.match(pattern_q, sentence)
        r_a = re.match(pattern_a, sentence)
        if r_a:
            return 'a'
        elif r_q:
            return 'q'
        else:
            self.logger.error('_judge_Q_or_A: unrecognize sentence type')
            return None

    def extract_Q(self, sentence):
        tokenizer = TreebankWordTokenizer()
        tokens = tokenizer.tokenize(sentence)
        line_no = int(tokens[0])
        space_index = 0;
        for i in range(len(tokens)):
            if tokens[i].startswith('____'):
                space_index = i;
        try:
            w1 = tokens[space_index - 2]
        except IndexError:
            w1 = 0
        try:
            w2 = tokens[space_index - 1]
        except IndexError:
            w2 = 0
        try:
            w3 = tokens[space_index + 1]
        except IndexError:
            w3 = 0
        try:
            w4 = tokens[space_index + 2]
        except IndexError:
            w4 = 0

        if self.n == 22:
            return (line_no, w1, w2, w3, w4)
        else:
            return (line_no, w2, w3)

        # pattern = r"^(\d+)\).+\s([\w'-]+|[,.])\s_+\s(\w+|[,.])"
        # reg = re.compile(pattern)
        # r = reg.match(sentence)
        # if not r:
        #     self.logger.error('extract_Q: can not find words in "%s"' % sentence)
        #     return None
        # line_no = int(r.group(1))
        # word_1 = r.group(2)
        # try:
        #     i = word_1.index("'")
        #     word_1 = word_1[i:]
        # except ValueError:
        #     pass
        # word_2 = r.group(3)
        # try:
        #     i = word_2.index("'")
        #     word_2 = word_2[:i]
        # except ValueError:
        #     pass
        # return (line_no, word_1, word_2)

    def extract_A(self, line):
        pattern = r'([a-e])\)\s(.+)'
        reg = re.compile(pattern)
        line = line.strip()
        r = reg.match(line)
        if not r:
            self.logger.error('extract_A: can not find option in "%s"' % line)
            return None
        return (r.group(1), r.group(2).lower())


    def compute_data_sparseness(self, json_path):
        if self.n == 22:
            self.compute_hop_2gram_sparseness(json_path)
        else:
            self.compute_2gram_sparseness(json_path)
        return None

    def compute_2gram_sparseness(self, json_path):
        bi_freq_set = set()
        not_found = set()
        to_find = set()

        with open(os.path.join(config.CORPUS_DIR, "bigram_frequency.txt"), 'r') as f:
            for line in f:
                line = line.strip()
                w1, w2, freq = line.split()
                bi_freq_set.add("%s %s" % (w1, w2))

        with open(json_path, 'r') as f:
            json_obj = json.load(f)
            total_word_pair = len(json_obj)
            for v in json_obj.values():
                w1, w2 = v['q']
                options = v['a'].values()
                for op in options:
                    to_find.add("%s %s" % (w1, op))
                    to_find.add("%s %s" % (op, w2))
        not_found = to_find.difference(bi_freq_set)
        num_not_found = len(not_found)
        num_to_find = len(to_find)
        sparseness_rate = float(num_not_found) / num_to_find
        self.logger.info("compute_data_sparseness:")
        self.logger.info("expect to find word pairs %d, could not find %d" % (num_to_find, num_not_found))
        self.logger.info("the bi word pair data sparseness rate is %f" % sparseness_rate)
        self.logger.info("they are:")
        count = 0
        for e in not_found:
            count += 1
            self.logger.info("%d %s" % (count, e))
        return None

    def compute_hop_2gram_sparseness(self, json_path):
        bi_freq_set1 = set()
        bi_freq_set2 = set()
        not_found1 = set()
        not_found2 = set()
        to_find_hop1 = set()
        to_find_hop2 = set()

        with open(os.path.join(config.CORPUS_DIR, "bigram_frequency.txt"), 'r') as f:
            for line in f:
                line = line.strip()
                w1, w2, freq = line.split()
                bi_freq_set1.add("%s %s" % (w1, w2))

        with open(os.path.join(config.CORPUS_DIR, 'hop_bigram_frequency.txt'), 'r') as f:
            for line in f:
                line = line.strip()
                w1, w2, freq = line.split()
                bi_freq_set2.add("%s %s" % (w1, w2))

        with open(json_path, 'r') as f:
            json_obj = json.load(f)
            total_word_pair = len(json_obj)
            for v in json_obj.values():
                w1, w2, w3, w4 = v['q']
                options = v['a'].values()
                for op in options:
                    to_find_hop1.add("%s %s" % (w2, op))
                    to_find_hop1.add("%s %s" % (op, w3))
                    to_find_hop2.add("%s %s" % (w1, op))
                    to_find_hop2.add("%s %s" % (op, w4))

        not_found1 = to_find_hop1.difference(bi_freq_set1)
        not_found2 = to_find_hop2.difference(bi_freq_set2)

        num_not_found1 = len(not_found1)
        num_not_found2 = len(not_found2)
        num_to_find1 = len(to_find_hop1)
        num_to_find2 = len(to_find_hop2)

        sparseness_rate1 = float(num_not_found1) / num_to_find1
        sparseness_rate2 = float(num_not_found2) / num_to_find2
        total_sparseness_rate = float(num_not_found1 + num_not_found2) / (num_to_find1 + num_to_find2)

        self.logger.info("compute_data_sparseness:")
        count = 0
        for e in not_found1:
            count += 1
            self.logger.info("%d [hop1]could not find %s" % (count, e))
        for e in not_found2:
            count += 1
            self.logger.info("%d [hop2]could not find %s" % (count, e))
        self.logger.info("expect to find [word pairs] %d, could not find %d" % (num_to_find1, num_not_found1))
        self.logger.info("the sparseness rate is %f" % sparseness_rate1)
        self.logger.info("expect to find [hop word pairs] %d, could not find %d" % (num_to_find2, num_not_found2))
        self.logger.info("the sparseness rate is %f" % sparseness_rate2)
        self.logger.info("the total sparseness rate is %f" % total_sparseness_rate)
        return None

    def load_freq_dict(self):
        self.load_uni_freq_dict(self.__uni_freq_path)
        if self.n == 22:
            self.load_bi_freq_dict(self.__bi_freq_path, self.bi_freq_dict)
            self.load_bi_freq_dict(self.__hop_bi_freq_path, self.hop_bi_freq_dict)
        else:
            self.load_bi_freq_dict()
        return None


    def load_uni_freq_dict(self, freq_path):
        uni_freq_dict = {}
        with open(freq_path, 'r') as uni_f:
            for line in uni_f:
                line = line.strip()
                word, freq = line.split()
                uni_freq_dict[word] = freq
        self.uni_freq_dict = uni_freq_dict
        return None

    def load_bi_freq_dict(self, freq_path, freq_dict):
        freq_dict.clear()
        with open(freq_path, 'r') as bi_f:
            for line in bi_f:
                line = line.strip()
                w1, w2, freq = line.split()
                freq_dict['%s %s' % (w1, w2)] = freq
        return None

    def compute_option_probability(self, json_path):
        option_probability_dict = {}
        max_probability_dict = {}
        with open(json_path, 'r') as f:
            json_obj = json.load(f)
        for sent_no, qa in json_obj.items():
            q = qa['q']
            a = qa['a']
            option_dict = {}
            max_probability = ('a', 0.0)
            for no, option in a.items():
                if self.n == 22:
                    p = self.compute_sentence_probability([q[0], q[1], option, q[2], q[3]])
                else:
                    p = self.compute_sentence_probability([q[0], option, q[1]])
                option_dict[no] = p
                if p > max_probability[1]:
                    max_probability = (no, p)
            option_probability_dict[sent_no] = option_dict
            max_probability_dict[sent_no] = max_probability
        with open(os.path.join(config.DATA_DIR, 'dev_options_probability.json'), 'w') as f:
            json.dump(option_probability_dict, f)

        # choose the best option
        with open(os.path.join(config.DATA_DIR, 'dev_max_probability.json'), 'w') as f:
            json.dump(max_probability_dict, f)
        # save a copy with correct answers' format
        with open(os.path.join(config.DATA_DIR, 'answers200.txt'), 'w') as f:
            answers_list = max_probability_dict.items()
            answers_list.sort(key=lambda x: int(x[0]))
            f.writelines(["%s) [%s] %s\n" % (sent_no, no, option) for sent_no, (no, option) in answers_list])
        return None

    # answer and stand_answer are txt file paths containing one choose one line with format like:
    # 801) [d] everyone
    def compute_accuracy(self, answer_path, stand_answer_path):
        answers_list = []
        stand_answers_list = []
        with open(answer_path, 'r') as f:
            for line in f:
                line = line.strip()
                sent_no, no, option = line.split()
                answers_list.append((sent_no[:-1], no[1:-1]))
        with open(stand_answer_path, 'r') as f:
            for line in f:
                line = line.strip()
                sent_no, no, option = line.split()
                stand_answers_list.append((sent_no[:-1], no[1:-1]))

        answers_list.sort(key= lambda x: int(x[0]))
        stand_answers_list.sort(key= lambda x: int(x[0]))

        assert(len(answers_list) == len(stand_answers_list))
        total = len(stand_answers_list)
        num_correct = 0
        for i in range(total):
            assert(answers_list[i][0] == stand_answers_list[i][0])
            if answers_list[i][1] == stand_answers_list[i][1]:
                num_correct += 1
            else:
                self.logger.info("compute_accuracy: wrong answer for sentence %s " % answers_list[i][0])
        accuracy = float(num_correct) / total
        self.logger.info("dev_set accuracy:")
        self.logger.info("total sentences: %d" % total)
        self.logger.info("number of correct: %d" % num_correct)
        self.logger.info("accuracy: %f" % accuracy)
        return None


    def compute_sentence_probability(self, word_list):
        if self.n == 22:
            p1 = self.compute_bi_sentence_probability(word_list)
            p2 = self.compute_hop_bi_sentence_probability(word_list)
            return p1 * p2
        else:
            return self.compute_bi_sentence_probability(word_list)


    # This is not the real sentence probablity.
    # For the beging and end of five sentence are the same, we can ignore them
    # word_list include the option word
    def compute_bi_sentence_probability(self, word_list):
        p = 1.0
        for i in range(len(word_list) - 1):
            p *= self.compute_conditional_probability(word_list[i], word_list[i + 1], self.bi_freq_dict, smooth='plus1')
            if p == 0.0:
                return 0.0
        return p

    # word_list include the option word
    def compute_hop_bi_sentence_probability(self, word_list):
        p = 1.0
        p1 = self.compute_conditional_probability(word_list[0], word_list[2], self.hop_bi_freq_dict, smooth='plus1')
        p2 = self.compute_conditional_probability(word_list[2], word_list[4], self.hop_bi_freq_dict, smooth='plus1')
        p = p1 * p2
        return p

    # compute p(w2|w1)
    # c12: the frequency of word pair w1, w2
    # c1: the frequency of w2
    def compute_conditional_probability(self, w1, w2, bi_freq_dict, smooth=None):
        try:
            c1 = self.uni_freq_dict[w1]
        except KeyError:
            self.logger.error("compute_conditional_probability: word '%s' not exist in unigram frequency" % w1)
            c1 = 0
        try:
            c12 = bi_freq_dict["%s %s" % (w1, w2)]
        except KeyError:
            self.logger.error("compute_conditional_probability: word pair '%s %s' not exist in bigram frequency" % (w1, w2))
            c12 = 0
        if smooth == 'plus1':
            p = (1 + float(c12)) / (float(c1) + len(self.uni_freq_dict))
        else:
            try:
                p = float(c12) / float(c1)
            except ZeroDivisionError:
                p = 0.0
        return p

    def report(self):
        pass