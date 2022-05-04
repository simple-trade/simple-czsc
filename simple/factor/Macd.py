# -*- encoding: utf-8 -*-

import numpy as np
import pandas as pd
import talib as ta
import datetime
from simple.factor import factors
from simple.czsc import CzscModelEngine
from simple.factor.FactorAbstract import FactorAbstract
from simple.logger.logger import LoggerFactory

logger = LoggerFactory.getLogger(__name__)


'''

'''


class Macd(FactorAbstract):
    def __init__(self, czsc: CzscModelEngine):
        super(Macd, self).__init__(czsc=czsc)
        self.macd_df = pd.DataFrame(columns=['macd', 'dif', 'dea'])
        self.last_index = datetime.datetime.now()

        self.normalized_df = pd.DataFrame(columns=['start_point', 'end_point', 'type', 'area', 'extremum_point', 'status'])
        self.realtime_normalized_df = None

    def get_factor_name(self):
        return factors['macd']

    def execute(self):
        klines = self.czsc.get_klines()
        self.__cal_macd(klines)
        self.__cal_normalized_df(klines)
        return {'macd_df': self.macd_df, 'normalized_df': self.realtime_normalized_df}

    def __cal_macd(self, klines):
        if klines.shape[0] > 33:
            closes = klines.iloc[-34:].close.values.astype('float')
        else:
            closes = klines.close.values.astype('float')

        _dif, _dea, _macd = ta.MACDEXT(closes, fastperiod=12, fastmatype=1, slowperiod=26, slowmatype=1, signalperiod=9, signalmatype=1)
        if klines.index[-1] == self.last_index:
            self.macd_df.loc[self.macd_df.index[-1], 'macd'] = 2 * _macd[-1]
            self.macd_df.loc[self.macd_df.index[-1], 'dif'] = _dif[-1]
            self.macd_df.loc[self.macd_df.index[-1], 'dea'] = _dea[-1]
        else:
            self.macd_df.loc[klines.index[-1], ['macd', 'dif', 'dea']] = [2 * _macd[-1], _dif[-1], _dea[-1]]
            self.last_index = klines.index[-1]

    def __cal_normalized_df(self, klines):
        if self.macd_df.shape[0] < 2:
            return
        macd_2 = self.macd_df.iloc[-2]['macd']
        if np.isnan(macd_2):
            return
        if self.normalized_df.shape[0] < 1:
            if macd_2 <= 0:
                self.__add_normalized(klines, -1, macd_2)
            else:
                self.__add_normalized(klines, 1, macd_2)
        else:
            if macd_2 <= 0 and self.normalized_df.iloc[-1]['type'] == 1:
                self.normalized_df.iloc[-1]['status'] = 1
                self.__add_normalized(klines, -1, macd_2)
            elif macd_2 >= 0 and self.normalized_df.iloc[-1]['type'] == -1:
                self.normalized_df.iloc[-1]['status'] = 1
                self.__add_normalized(klines, 1, macd_2)
            else:
                self.__update_normalized(klines, macd_2)

        self.realtime_normalized_df = self.normalized_df.copy(deep=True)
        macd_1 = self.macd_df.iloc[-1]['macd']
        if macd_1 <= 0 and self.realtime_normalized_df.iloc[-1]['type'] == 1:
            self.__add_normalized_realtime(klines, -1, macd_1)
        elif macd_1 >= 0 and self.realtime_normalized_df.iloc[-1]['type'] == -1:
            self.__add_normalized_realtime(klines, 1, macd_1)
        else:
            self.__update_normalized_realtime(klines, macd_1)

    def __add_normalized(self, klines, _type, macd_2):
        self.normalized_df.loc[klines.index[-2], ['start_point', 'end_point', 'type', 'area', 'extremum_point', 'status']] = [
            [klines.index[-2], macd_2],
            [klines.index[-2], macd_2],
            _type,
            macd_2,
            [klines.index[-2], macd_2],
            0,
        ]

    def __update_normalized(self, klines, macd_2):
        extremum_macd = self.normalized_df.iloc[-1]['extremum_point'][1]
        _type = self.normalized_df.iloc[-1]['type']
        if (macd_2 <= extremum_macd and _type == -1) or (macd_2 >= extremum_macd and _type == 1):
            self.normalized_df.iloc[-1]['extremum_point'][0] = klines.index[-2]
            self.normalized_df.iloc[-1]['extremum_point'][1] = macd_2

        self.normalized_df.loc[self.normalized_df.index[-1], 'area'] = self.normalized_df.iloc[-1]['area'] + macd_2
        self.normalized_df.iloc[-1]['end_point'][0] = klines.index[-2]
        self.normalized_df.iloc[-1]['end_point'][1] = macd_2

    def __add_normalized_realtime(self, klines, _type, macd_1):
        realtime_index = klines.index[-1]
        self.realtime_normalized_df.loc[realtime_index, ['start_point', 'end_point', 'type', 'area', 'extremum_point', 'status']] = [
            [realtime_index, macd_1],
            [realtime_index, macd_1],
            _type,
            macd_1,
            [realtime_index, macd_1],
            -1,
        ]

    def __update_normalized_realtime(self, klines, macd_1):
        extremum_macd = self.realtime_normalized_df.iloc[-1]['extremum_point'][1]
        _type = self.realtime_normalized_df.iloc[-1]['type']
        if (macd_1 <= extremum_macd and _type == -1) or (macd_1 >= extremum_macd and _type == 1):
            self.realtime_normalized_df.iloc[-1]['extremum_point'][0] = klines.index[-1]
            self.realtime_normalized_df.iloc[-1]['extremum_point'][1] = macd_1
        self.realtime_normalized_df.loc[self.realtime_normalized_df.index[-1], 'area'] = self.realtime_normalized_df.iloc[-1]['area'] + macd_1
        self.realtime_normalized_df.iloc[-1]['end_point'][0] = klines.index[-1]
        self.realtime_normalized_df.iloc[-1]['end_point'][1] = macd_1
