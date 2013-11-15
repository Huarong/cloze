#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: huohuarong
# @Date:   2013-11-13 17:21:24
# @Last Modified by:   huohuarong
# @Last Modified time: 2013-11-15 18:59:17

from n_gram_model import NGramModel

def main():
    n_gram = NGramModel()
    n_gram.extract_QA('../../corpus/development_set.txt')
    return None


if __name__ == '__main__':
    main()