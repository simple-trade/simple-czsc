# -*- encoding: utf-8 -*-
'''
@File    :   logger.py
@Time    :   2020/03/18 22:08:18
'''
import logging
import os

class LoggerFactory:
    @staticmethod
    def getLogger(name, filepath='.', filename='simple.log'):

        name = name.split('.')[-1]  # 截取文件夹名

        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        # if not os.path.exists(filepath):
        #     os.makedirs(filepath)
        #     print('%s 文件夹不存在，创建完成', filepath)
        # 创建 handler 输出到文件
        # handler = logging.FileHandler(filepath + '/' + filename, mode='w')
        # handler.setLevel(logging.INFO)
        # handler.setFormatter(formatter)
        # handler 输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        # add the handlers to the logger
        # logger.addHandler(handler)
        logger.addHandler(ch)
        return logger
