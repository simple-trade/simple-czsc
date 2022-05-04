# -*- encoding: utf-8 -*-

from pyecharts.charts import Bar
from pyecharts.charts import Kline
from pyecharts.charts import Line
from pyecharts.charts import Grid
from pyecharts.charts import Page
from pyecharts import options as opts

import talib
import numpy as np
import os

from pyecharts.render import make_snapshot
from snapshot_selenium import snapshot
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

from simple.draw.KdrawGrid import KdrawGrid
from simple.draw.HtmlAutoFit import fit as html_auto_fit

class KdrawRealtimeMultiPeriod:
    def __init__(self, base_name='', html_path='', pic_path='', extends_name='', grids=[],chromedriver_path=''):
        if len(grids) == 0:
            raise Exception('至少指定一个Grid')
        self.base_name = base_name
        self.html_path = html_path
        self.pic_path = pic_path
        self.extends_name = extends_name
        self.grids = grids
        self.chromedriver_path = chromedriver_path

    def gen_html(self):
        '''
        生成HTML
        '''
        if not os.path.exists(self.html_path):
            os.makedirs(self.html_path)
            print('%s 文件夹不存在，创建完成', self.html_path)
        html = '%s/%s-%s-multi.html' % (self.html_path, self.base_name, self.extends_name)
        page = Page(layout=Page.SimplePageLayout)
        for grid in self.grids:
            page.add(grid)

        page.render(path=html)
        html_auto_fit(html, create_new_file=False)
        return html

    def gen_pic(self):
        '''
        生成图片
        '''
        if not os.path.exists(self.pic_path):
            os.makedirs(self.pic_path)
            print('%s 文件夹不存在，创建完成', self.pic_path)
        pic = '%s/%s-%s-multi.png' % (self.pic_path, self.base_name, self.extends_name)
        page = Page(layout=Page.SimplePageLayout)
        for grid in self.grids:
            page.add(grid)
        # 生成图片
        chrome_options = Options()
        chrome_options.binary_location(self.chromedriver_path)
        chrome_options.add_argument('--headless')
        #     chrome_options.add_argument('--disable-gpu')
        make_snapshot(snapshot, page.render(), pic, is_remove_html=True)
        return pic
