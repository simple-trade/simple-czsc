# -*- encoding: utf-8 -*-

from simple.czsc.CzscModelEngineZhongshu import CzscModelEngineZhongshu
from simple.czsc.CzscModelEngineXianduan import CzscModelEngineXianduan
from simple.czsc.CzscModelEngineFenbi import CzscModelEngineFenbi
from simple.czsc.CzscModelEngineFenxing import CzscModelEngineFenxing
from simple.czsc.CzscModelEngineHebing import CzscModelEngineHebing
from simple.czsc.CzscRealtimeModelEngineFenbi import CzscRealtimeModelEngineFenbi
from simple.czsc.CzscRealtimeModelEngineXianduan import CzscRealtimeModelEngineXianduan
from simple.czsc.CzscRealtimeModelEngineZhongshu import CzscRealtimeModelEngineZhongshu
import simple.factor as factor
import datetime
import pandas as pd
import numpy as np
from simple.logger.logger import LoggerFactory


logger = LoggerFactory.getLogger(__name__)

class CzscModelEngine:
    def __init__(
        self,
        stock_code,
        frequency,
        is_debug=False,
        realtime_drive_time='', 
        subscribe_factors=[],
    ):
        self.stock_code = stock_code
        self.frequency = frequency
        self.is_debug = is_debug
        self.realtime_drive_time = realtime_drive_time
        self.last_history_k_index = None 

        self.hebing_engine = CzscModelEngineHebing(stock_code, frequency)
        self.fenxing_engine = CzscModelEngineFenxing(stock_code, frequency)
        self.fenbi_engine = CzscModelEngineFenbi(stock_code, frequency)
        self.xianduan_engine = CzscModelEngineXianduan(stock_code, frequency)
        self.zhongshu_engine = CzscModelEngineZhongshu(stock_code, frequency)
        self.realtime_fenbi_engine = CzscRealtimeModelEngineFenbi(stock_code, frequency)
        self.realtime_xianduan_engine = CzscRealtimeModelEngineXianduan(stock_code, frequency)
        self.realtime_zhongshu_engine = CzscRealtimeModelEngineZhongshu(stock_code, frequency)

        self.stock_df = pd.DataFrame(columns=['open', 'close', 'high', 'low'])
        self.hebing_df = pd.DataFrame(columns=['current_time', 'open', 'close', 'high', 'low'])
        self.fenxing_df = pd.DataFrame(columns=['price', 'type']) 
       
        self.fenbi_df = pd.DataFrame(
            columns=[
                'confirm_time',
                'price', 
                'type', 
                'status', 
                'price2', 
            ]
        )

        self.xianduan_df = pd.DataFrame(
            columns=[
                'confirm_time',
                'start_point',
                'end_point',
                'dynamic_end_point', 
                'type', 
                'status', 
                'forward_break_point',
                'reverse_break_point',
                'fenbi_idx',  
                'fenbi_idx_snapshot',  
                'real_reverse_break_point', 
                'real_forward_break_point',
            ]
        )
        self.zhongshu_df = pd.DataFrame(
            columns=[
                'start_point', 
                'end_point', 
                'high_point', 
                'last_high_point', 
                'low_point',
                'last_low_point',
                'top_point', 
                'bottom_point',
                'type', 
                'status',
            ]
        )

        self.realtime_fenbi_df = self.fenbi_df.copy(deep=True)
        self.realtime_xianduan_df = self.xianduan_df.copy(deep=True)
        self.realtime_zhongshu_df = self.zhongshu_df.copy(deep=True)
        self.factor_result_dic = {}
        self.factor_engines = []
        if subscribe_factors:
            sub_ft_np = np.array(subscribe_factors)
            
            if (sub_ft_np == factor.factors['xianduansanmai']).any():
                self.factor_engines.append(factor.XianduanSanmai.XianduanSanmai(self))
            if (sub_ft_np == factor.factors['macd']).any():
                self.factor_engines.append(factor.Macd.Macd(self))
        logger.info(
            '初始化引擎完成 %s %s ，实时结构计算开始时间： %s ，因子订阅：%s',
            stock_code,
            frequency,
            '无限制' if ('' == self.realtime_drive_time) else self.realtime_drive_time,
            subscribe_factors,
        )

    
    def k_receive(self, k_df, is_realtime=False):  
        '''
            tick或k线数据接收
        '''
        if self.is_debug:
            logger.debug('============接收到【%s】k线============\n%s' % (('实时' if (is_realtime) else '历史'), k_df))
        starttime = datetime.datetime.now()
        k_df_ochl = k_df.loc[:, ['open', 'close', 'high', 'low']]
        self.stock_df.loc[k_df_ochl.index[0], :] = k_df_ochl.values[0]
        if not is_realtime:
            if not self.last_history_k_index is None and self.last_history_k_index == k_df_ochl.index[0]:
                logger.warn('当前k线【%s】【%s】历史结构计算已经执行过，不再重复执行', self.stock_code, self.last_history_k_index)
            else:
                self.__confirm_model(k_df_ochl)
                self.last_history_k_index = k_df_ochl.index[0]

        if self.realtime_drive_time == '' or k_df.index[-1] >= pd.to_datetime(self.realtime_drive_time).tz_localize('Asia/Shanghai'):
            self.__realtime_model(k_df_ochl)
            self.__execute_factors()

        endtime = datetime.datetime.now()
        if self.is_debug:
            logger.debug('计算一根k线耗时: %d ms' % ((endtime - starttime).seconds * 1000 + (endtime - starttime).microseconds / 1000))



    def __confirm_model(self, k_df):
        if self.is_debug:
            logger.debug('====开始历史结构计算====')

        hebing_result = self.hebing_engine.execute(k_df=k_df, hebing_df=self.hebing_df)
   
        if 1 == hebing_result:
            return

        fenxing_result = self.fenxing_engine.execute(self.hebing_df, self.fenxing_df)
        if 1 != fenxing_result:
            return

        fenbi_result = self.fenbi_engine.execute(self.hebing_df, self.fenxing_df, self.fenbi_df)
        if 1 != fenbi_result:
            return

        xianduan_result = self.xianduan_engine.execute(self.fenbi_df, self.xianduan_df)   
        if 2 != xianduan_result:
            return

        zhongshu_result = self.zhongshu_engine.execute(self.stock_df, self.xianduan_df, self.zhongshu_df)


    def __realtime_model(self, k_df):
        self.realtime_fenbi_df = self.realtime_fenbi_engine.execute(stock_df=self.stock_df, k_df=k_df, fenbi_df=self.fenbi_df)
        self.realtime_xianduan_df = self.xianduan_df.copy(deep=True)
        self.realtime_zhongshu_df = self.zhongshu_df.copy(deep=True)
        if not self.realtime_fenbi_df.empty and self.fenbi_df.shape[0] > 3 and not self.realtime_xianduan_df.empty:
            self.realtime_fenbi_df.loc[self.fenbi_df.index[-4], ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                self.fenbi_df.iloc[-4]['confirm_time'],
                self.fenbi_df.iloc[-4]['price'],
                self.fenbi_df.iloc[-4]['type'],
                self.fenbi_df.iloc[-4]['status'],
                np.nan,
            ]
            self.realtime_fenbi_df.loc[self.fenbi_df.index[-3], ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                self.fenbi_df.iloc[-3]['confirm_time'],
                self.fenbi_df.iloc[-3]['price'],
                self.fenbi_df.iloc[-3]['type'],
                self.fenbi_df.iloc[-3]['status'],
                np.nan,
            ]
            self.realtime_fenbi_df = self.realtime_fenbi_df.sort_index()

            self.realtime_xianduan_engine.execute(self.xianduan_engine, self.realtime_fenbi_df, self.realtime_xianduan_df)

            temp_fenbi_df = self.fenbi_df.copy(deep=True)
            temp_fenbi_df.drop(axis=0, index=temp_fenbi_df.index[-1], inplace=True)
            self.realtime_fenbi_df.drop(axis=0, index=self.realtime_fenbi_df.index[0:3], inplace=True)
            self.realtime_fenbi_df = pd.concat([temp_fenbi_df, self.realtime_fenbi_df], axis=0)
            self.realtime_zhongshu_engine.execute(self.zhongshu_engine, self.stock_df, self.realtime_xianduan_df, self.realtime_zhongshu_df)

    def __execute_factors(self):
        for e in self.factor_engines:
            self.factor_result_dic[e.get_factor_name()] = e.execute()

    def get_factor_result(self):
        return self.factor_result_dic

    
    def get_containers(self):
        return (
            self.hebing_df,
            self.fenxing_df,
            self.fenbi_df,
            self.xianduan_df,
            self.zhongshu_df,
            self.realtime_fenbi_df,
            self.realtime_xianduan_df,
            self.realtime_zhongshu_df,
        )

    def get_hebing_df(self):
        return self.hebing_df

    def get_fenxing_df(self):
        return self.fenxing_df

    def get_fenbi_df(self):
        return self.fenbi_df

    def get_xianduan_df(self):
        return self.xianduan_df

    def get_zhongshu_df(self):
        return self.zhongshu_df

    def get_realtime_fenbi_df(self):
        return self.realtime_fenbi_df

    def get_realtime_xianduan_df(self):
        return self.realtime_xianduan_df

    def get_realtime_zhongshu_df(self):
        return self.realtime_zhongshu_df

    def get_klines(self):
        return self.stock_df

    
    def print_containers(self):
        
        pd.set_option('display.max_columns', None)
        
        pd.set_option('display.max_rows', None)
        
        pd.set_option('display.width', 100000)
        
        pd.set_option('display.max_colwidth', 10000)

        logger.info('====zhongshu_df==== \n %s', self.zhongshu_df)
            
        logger.info('====realtime_zhongshu_df==== \n %s', self.realtime_zhongshu_df)
