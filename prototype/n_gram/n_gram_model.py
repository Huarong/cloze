#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import json
import os.path

sys.path.append('../')
from util import init_log
import config

class NGramModel(object):
    def __init__(self, n=2):
        self.qa_path = None
        self.n = n
        self.logger = init_log('ngram', os.path.join(config.LOG_DIR, 'ngram.log'))

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
        pattern = r"^(\d+)\).+\s([\w'-]+|[,.])\s_+\s(\w+|[,.])"
        reg = re.compile(pattern)
        r = reg.match(sentence)
        if not r:
            self.logger.error('extract_Q: can not find words in "%s"' % sentence)
            return None
        line_no = int(r.group(1))
        word_1 = r.group(2)
        try:
            i = word_1.index("'")
            word_1 = word_1[i:]
        except ValueError:
            pass
        word_2 = r.group(3)
        try:
            i = word_2.index("'")
            word_2 = word_2[:i]
        except ValueError:
            pass
        return (line_no, word_1, word_2)

    def extract_A(self, line):
        pattern = r'([a-e])\)\s(\w+)'
        reg = re.compile(pattern)
        line = line.strip()
        r = reg.match(line)
        if not r:
            self.logger.error('extract_A: can not find option in "%s"' % line)
            return None
        return (r.group(1), r.group(2))

