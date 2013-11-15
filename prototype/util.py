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

