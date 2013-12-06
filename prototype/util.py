#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: hhr
# @Date:   2013-11-13 15:53:43
# @Last Modified by:   huohuarong
# @Last Modified time: 2013-11-15 20:19:34

import logging


def init_log(logname, filename, level=logging.DEBUG):
    # set up logging to file - see previous section for more details
    logging.basicConfig(level=level,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=filename,
                        filemode='a')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger().addHandler(console)
     
    # Now, define a couple of other loggers which might represent areas in your
    # application:
    logger = logging.getLogger(logname)
    return logger


# answer and stand_answer are txt file paths containing one choose one line with format like:
# 801) [d] everyone
def compute_accuracy(answer_path, stand_answer_path, logger):
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
            logger.info("compute_accuracy: wrong answer for sentence %s " % answers_list[i][0])
    accuracy = float(num_correct) / total
    logger.info("dev_set accuracy:")
    logger.info("total sentences: %d" % total)
    logger.info("number of correct: %d" % num_correct)
    logger.info("accuracy: %f" % accuracy)
    return None