# -*- encoding: utf-8 -*-

from simple.logger.logger import LoggerFactory
logger = LoggerFactory.getLogger(__name__)
class CzscModelEngineHebing:
    def __init__(self,stock_code,frequency,is_debug=False):
        pass
    def human_result(self, result):
        return '合并'
        
    def execute(self, 
        k_df, 
        hebing_df,
    ):
        hebing_df_size=hebing_df.shape[0]
        if hebing_df_size >= 2: 
            if self.__contain(hebing_df.iloc[-1]['high'],hebing_df.iloc[-1]['low'],k_df.iloc[-1]['high'],k_df.iloc[-1]['low']):
                if 1==self.__trend(hebing_df):
                    higher_index=k_df.index[-1] 
                    if hebing_df.iloc[-1]['high'] > k_df.iloc[-1]['high']:
                         higher_index = hebing_df.index[-1]
                    h = max(hebing_df.iloc[-1]['high'],k_df.iloc[-1]['high'])
                    l = max(hebing_df.iloc[-1]['low'],k_df.iloc[-1]['low'])
                    o,c = l,h 
                    hebing_df.drop(axis=0,labels=[hebing_df.index[-1]],inplace=True)
                    hebing_df.loc[higher_index,['current_time','open','close','high','low']]=[k_df.index[0],o,c,h,l] 
                    return 1
                else: 
                    lower_index=k_df.index[-1]
                    if hebing_df.iloc[-1]['low'] < k_df.iloc[-1]['low']:
                         lower_index = hebing_df.index[-1]
                    h = min(hebing_df.iloc[-1]['high'],k_df.iloc[-1]['high'])
                    l = min(hebing_df.iloc[-1]['low'],k_df.iloc[-1]['low'])
                    o,c = h,l 
                    hebing_df.drop(axis=0,labels=[hebing_df.index[-1]],inplace=True) 
                    hebing_df.loc[lower_index,['current_time','open','close','high','low']]=[k_df.index[0],o,c,h,l]
                    return 1
            else: 
                hebing_df.loc[k_df.index[0],['open','close','high','low']]=k_df.values[0]
                hebing_df.loc[k_df.index[0],['current_time']]=k_df.index[0]
                return 0
        elif hebing_df_size == 1: 
            if self.__contain(hebing_df.iloc[-1]['high'],hebing_df.iloc[-1]['low'],k_df.iloc[-1]['high'],k_df.iloc[-1]['low']): 
                higher_index=k_df.index[-1] 
                if hebing_df.iloc[-1]['high'] > k_df.iloc[-1]['high']: 
                        higher_index = hebing_df.index[-1]
                h = max(hebing_df.iloc[-1]['high'],k_df.iloc[-1]['high'])
                l = max(hebing_df.iloc[-1]['low'],k_df.iloc[-1]['low'])
                o,c = l,h 
                hebing_df.drop(axis=0,labels=[hebing_df.index[-1]],inplace=True)
                hebing_df.loc[higher_index,['current_time','open','close','high','low']]=[k_df.index[0],o,c,h,l] #设置新合并后的k线
                return 1
            else:
                hebing_df.loc[k_df.index[0],['open','close','high','low']]=k_df.values[0]
                hebing_df.loc[k_df.index[0],['current_time']]=k_df.index[0]
                return 0
        else:
            hebing_df.loc[k_df.index[0],['open','close','high','low']]=k_df.values[0]
            hebing_df.loc[k_df.index[0],['current_time']]=k_df.index[0]
            return 0


    def __contain(self, h1, l1, h2, l2):
        if (h1 >= h2 and l1 <= l2) or (h1 <= h2 and l1 >= l2):
            return True
        return False

    def __trend(self, hebing_df):
        if hebing_df.iloc[-1]['high'] > hebing_df.iloc[-2]['high'] and hebing_df.iloc[-1]['low'] > hebing_df.iloc[-2]['low']: 
            return 1
        if hebing_df.iloc[-1]['high'] < hebing_df.iloc[-2]['high'] and hebing_df.iloc[-1]['low'] < hebing_df.iloc[-2]['low']: 
            return -1
        return 1
