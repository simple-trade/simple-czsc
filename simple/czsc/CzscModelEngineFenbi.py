# -*- encoding: utf-8 -*-

import numpy as np
from simple.logger.logger import LoggerFactory
logger = LoggerFactory.getLogger(__name__)


class CzscModelEngineFenbi:
    def __init__(self, stock_code, frequency, is_debug=False):
        self.is_debug = is_debug


    def human_result(self, result):
        return '分笔'

    def execute(self, hebing_df, fenxing_df, fenbi_df):

        knocking_price = fenxing_df.iloc[-1]['price'] 
        knocking_type = fenxing_df.iloc[-1]['type']
        knocking_index = fenxing_df.index[-1]

        if fenxing_df.shape[0] == 1: 
            
            fenbi_df.loc[knocking_index, ['confirm_time', 'price', 'type', 'status']] = [
                np.nan, knocking_price, knocking_type, 0]
            return 0 

        last_to_confirm_type = fenbi_df.iloc[-1]['type'] 
        last_to_confirm_price = fenbi_df.iloc[-1]['price'] 
        last_to_confirm_index = fenbi_df.index[-1] 

        if -1 == last_to_confirm_type: 
            if 1 == knocking_type: 
                if self.__distanceSatisfied(hebing_df, last_to_confirm_index, knocking_index) \
                        or (fenbi_df.shape[0] > 1 and knocking_price <= fenbi_df.iloc[-2]['price']):
                    
                    min_price_idx=self.__lowerBottomFenxingExistBetween(fenxing_df,fenbi_df.index[-1],knocking_index,hebing_df,fenbi_df)
                    if min_price_idx is None:
                        return 0
                    fenbi_df.iloc[-1]['confirm_time'] = knocking_index
                    fenbi_df.iloc[-1]['status'] = 1 
                    fenbi_df.loc[min_price_idx, ['confirm_time', 'price', 'type', 'status']] = [
                        np.nan, fenxing_df.loc[min_price_idx,'price'], 1, 0
                    ]
                    return 1
                else:  
                    return 0
            else:  
                if knocking_price >= last_to_confirm_price:
                 
                    fenbi_df.drop(axis=0, labels=[
                                  fenbi_df.index[-1]], inplace=True)
                    fenbi_df.loc[knocking_index, ['confirm_time', 'price', 'type', 'status']] = [
                        np.nan, knocking_price, knocking_type, 0
                    ]
                    return 2
                else: 
                    return 0

        if 1 == last_to_confirm_type: 
            if -1 == knocking_type: 
                if self.__distanceSatisfied(hebing_df, last_to_confirm_index, knocking_index) \
                        or (fenbi_df.shape[0] > 1 and knocking_price >= fenbi_df.iloc[-2]['price']):
                    
                    max_price_idx=self.__higherTopFenxingExistBetween(fenxing_df,fenbi_df.index[-1],knocking_index,hebing_df,fenbi_df)
                    if max_price_idx is None:
                        return 0
                    fenbi_df.iloc[-1]['confirm_time'] = knocking_index
                    fenbi_df.iloc[-1]['status'] = 1
                    fenbi_df.loc[max_price_idx, ['confirm_time', 'price', 'type', 'status']] = [
                        np.nan, fenxing_df.loc[max_price_idx,'price'], -1, 0
                    ]
                    return 1
                else:  
                    return 0
            else:  
                if knocking_price <= last_to_confirm_price: 
                   
                    fenbi_df.drop(axis=0, labels=[
                                  fenbi_df.index[-1]], inplace=True)

                    fenbi_df.loc[knocking_index, ['confirm_time', 'price', 'type', 'status']] = [
                        np.nan, knocking_price, knocking_type, 0
                    ]
                    return 2
                else: 
                    return 0

        raise Exception('Mars Area')

    def __distanceSatisfied(self, hebing_df, index1, index2):
        distance = hebing_df[(hebing_df.index >= index1) & (
            hebing_df.index <= index2)].shape[0]
        if distance >= 5:
            return True
        else:
            return False

    def __higherTopFenxingExistBetween(self, fenxing_df, last_fenbi_confirm_index, knocking_index, hebing_df,fenbi_df):
        tmp_df=fenxing_df[(fenxing_df.index >= last_fenbi_confirm_index) & (
            fenxing_df.index <= knocking_index)].loc[:, 'price'].infer_objects()
        tmp_df=tmp_df.reindex(index=tmp_df.index[::-1])
        max_price_idx = tmp_df.idxmax()
        if max_price_idx > last_fenbi_confirm_index and max_price_idx < knocking_index:
            max_price = fenxing_df.loc[max_price_idx,'price']
            N=5
            high_between_bottomfenxing_and_backwardN = hebing_df.loc[:fenbi_df.index[-1]].iloc[-N:]['high'].max()
            low_between_bottomfenxing_and_backwardN = hebing_df.loc[:fenbi_df.index[-1]].iloc[-N:]['low'].min()
            diff1=max_price - low_between_bottomfenxing_and_backwardN
            diff2=high_between_bottomfenxing_and_backwardN - low_between_bottomfenxing_and_backwardN
            if diff1 < 0 or diff2 < 0: raise Exception('Mars Area')
            vision_satisfied = diff1> diff2
            if vision_satisfied:
                return max_price_idx
            else:
                return None
        return knocking_index

    def __lowerBottomFenxingExistBetween(self, fenxing_df, last_fenbi_confirm_index, knocking_index, hebing_df,fenbi_df):
        
        tmp_df = fenxing_df[(fenxing_df.index >= last_fenbi_confirm_index) & (fenxing_df.index <= knocking_index)].loc[:, 'price'].infer_objects()
        tmp_df=tmp_df.reindex(index=tmp_df.index[::-1])
        min_price_index = tmp_df.idxmin()
        if min_price_index > last_fenbi_confirm_index and min_price_index < knocking_index:
            min_price = fenxing_df.loc[min_price_index,'price']
            N=5
            high_between_bottomfenxing_and_backwardN = hebing_df.loc[:fenbi_df.index[-1]].iloc[-N:]['high'].max()
            low_between_bottomfenxing_and_backwardN = hebing_df.loc[:fenbi_df.index[-1]].iloc[-N:]['low'].min()
            diff1=high_between_bottomfenxing_and_backwardN - min_price
            diff2=high_between_bottomfenxing_and_backwardN - low_between_bottomfenxing_and_backwardN
            if diff1 < 0 or diff2 < 0: raise Exception('Mars Area')
            vision_satisfied = diff1 > diff2
            if vision_satisfied:
                return min_price_index
            else:
                return None
        return knocking_index
