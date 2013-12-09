import collections
import os.path
import json

from nltk.tokenize import TreebankWordTokenizer
from nltk.classify import MaxentClassifier
from nltk.classify import NaiveBayesClassifier
from nltk.stem import PorterStemmer

import config
import util

class BiHopFeatures(object):
    qa_json = None

    def __init__(self,stem=None):
        self.logger = util.init_log('MaxEntropy', os.path.join(config.LOG_DIR, 'max_entropy.log'))
        self.answers_path = os.path.join(config.DATA_DIR, 'max_entropy_answers240.txt')
        self.max_entropy_answers = {}
        self.stem = 'Porter'
        if self.stem == 'Porter':
            self.stemmer = PorterStemmer()
            self.logger.info("using max entropy model with PorterStemmer algorithm")
            self.sents_root = os.path.join(config.CORPUS_DIR, 'Sents_porter')
        else:
            self.sents_root = os.path.join(config.CORPUS_DIR, 'Sents')


    def get_features(self, labels):
        label_features = []
        tokenizer = TreebankWordTokenizer()
        for label in labels:
            path = os.path.join(self.sents_root, '%s/%s.txt'  % (label[0].upper(), label))
            with open(path, 'r') as f:
                for line in f:
                    line = line.strip()
                    line = line[6:]
                    words = tokenizer.tokenize(line)
                    if self.stem == 'Porter':
                        words = [self.stemmer.stem(w.lower()) for w in words]
                    four_words = self.get_adjancent_four_words(label, words)
                    label_words = (dict((w, True) for w in four_words), label)
                    label_features.append(label_words)
        return label_features

    @staticmethod
    def get_adjancent_four_words(label, words):
        index = 0
        for i, w in enumerate(words):
            if label == w:
                index = i
                break
        four_words = []
        for j in (index - 2, index - 1, index + 1, index + 2):
            try:
                w = words[j]
                four_words.append(w)
            except IndexError:
                pass
        return four_words

    @classmethod
    def load_QA(cls):
        dev_set_json_path = os.path.join(config.DATA_DIR, 'dev_set.json')
        with open(dev_set_json_path, 'r') as f:
            cls.qa_json = json.load(f)
        return None

    def train_and_classify(self):
        count = 0
        for line_no, v in self.qa_json.iteritems():
            count += 1
            print "[%d]begin to train %s..." % (count, line_no)
            question = v['q']
            options = v['a']
            label_features = self.get_features(options.values())
            me_classifier = MaxentClassifier.train(label_features, algorithm='gis', trace=0, max_iter=20)
            # me_classifier = NaiveBayesClassifier.train(label_features)
            label_questions = self.bag_of_words(question)
            answer = me_classifier.classify(label_questions)
            option_no = None
            for o, a in options.iteritems():
                if a == answer:
                    option_no = o
                    break
            self.max_entropy_answers[int(line_no)] = (option_no, answer)
        return None

    def dump_answers(self):
        print self.max_entropy_answers
        max_entropy_answers_list = self.max_entropy_answers.items()
        print max_entropy_answers_list
        max_entropy_answers_list.sort(key=lambda x: x[0])
        with open(self.answers_path,'w') as f:
            f.writelines(['%s) [%s] %s\n' % (line_no, option_no, answer) for (line_no, (option_no, answer)) in max_entropy_answers_list])
        return None

    @staticmethod
    def bag_of_words(words):
        return dict([(word, True) for word in words])

def main():
    bi_hop = BiHopFeatures()
    print "begin to load QA"
    bi_hop.load_QA()
    print "begin to train and classify"
    bi_hop.train_and_classify()
    print "begin to dump answers"
    bi_hop.dump_answers()
    print "begin to compute accuracy"
    util.compute_accuracy(bi_hop.answers_path, config.STANDARD_ANSWER_240_PATH, bi_hop.logger)


if __name__ == '__main__':
    main()