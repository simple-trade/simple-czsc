# -*- encoding: utf-8 -*-

from simple.logger.logger import LoggerFactory
logger = LoggerFactory.getLogger(__name__)

class CzscModelEngineFenxing:
    def __init__(self,stock_code,frequency,is_debug=False):
        self.is_debug = is_debug

    def human_result(self, result):
        return '分型'
    def execute(self, hebing_df,fenxing_df):
        if hebing_df.shape[0] < 3:
            return 0
        
        h0 = hebing_df.iloc[-3]['high']
        h1 = hebing_df.iloc[-2]['high']
        h2 = hebing_df.iloc[-1]['high']
        l0 = hebing_df.iloc[-3]['low']
        l1 = hebing_df.iloc[-2]['low']
        l2 = hebing_df.iloc[-1]['low']

        if h1 > h0 and h1 > h2 and l1 > l0 and l1 > l2: 
            fenxing_df.loc[hebing_df.index[-2],['price','type']]=[h1,-1] 
            return 1

        if h1 < h0 and h1 < h2 and l1 < l0 and l1 < l2: 
            fenxing_df.loc[hebing_df.index[-2],['price','type']]=[l1,1]
            return 1
        
        return 0


        