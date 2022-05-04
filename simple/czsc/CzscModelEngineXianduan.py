# -*- encoding: utf-8 -*-

import copy
from simple.logger.logger import LoggerFactory

logger = LoggerFactory.getLogger(__name__)

class CzscModelEngineXianduan:
    def __init__(self, stock_code, frequency):
        pass

    def human_result(self, result):
        return '线段'


    def execute(self, fenbi_df, xianduan_df, is_realtime=False 
                ):
        
        if is_realtime:
            confirmed_fenbi_df = fenbi_df
        else:
            confirmed_fenbi_df = fenbi_df.drop(axis=0, labels=[fenbi_df.index[-1]], inplace=False)
        
        if confirmed_fenbi_df.shape[0] < 2:
            return 0
        
        if confirmed_fenbi_df.shape[0] == 2:
            
            xianduan_df.loc[
                confirmed_fenbi_df.index[-2],
                [
                    'start_point',
                    'end_point',
                    'dynamic_end_point',
                    'type',
                    'status',
                    'forward_break_point',
                    'reverse_break_point',
                    'fenbi_idx',
                    'real_reverse_break_point',
                    'real_forward_break_point',
                ]
            ] = [
                [confirmed_fenbi_df.index[-2], confirmed_fenbi_df.iloc[-2]['price']],  
                [confirmed_fenbi_df.index[-1], confirmed_fenbi_df.iloc[-1]['price']],  
                [confirmed_fenbi_df.index[-1], confirmed_fenbi_df.iloc[-1]['price']],  
                confirmed_fenbi_df.iloc[-2]['type'],  
                0,  
                [confirmed_fenbi_df.index[-1], confirmed_fenbi_df.iloc[-1]['price']],  
                [confirmed_fenbi_df.index[-2], confirmed_fenbi_df.iloc[-2]['price']],  
                [confirmed_fenbi_df.index[-2], confirmed_fenbi_df.index[-1]],  
                [confirmed_fenbi_df.index[-2], confirmed_fenbi_df.iloc[-2]['price']],  
                [confirmed_fenbi_df.index[-1], confirmed_fenbi_df.iloc[-1]['price']]  
            ]
            return 1

        
        knocking_fenbi_idx = confirmed_fenbi_df.index[-1]  
        knocking_fenbi_price = confirmed_fenbi_df.iloc[-1]['price']  
        knocking_fenbi_type = confirmed_fenbi_df.iloc[-1]['type']  
        to_confirm_type = xianduan_df.iloc[-1]['type']  
        to_confirm_forward_break_price = xianduan_df.iloc[-1]['forward_break_point'][1]  
        to_confirm_reverse_break_price = xianduan_df.iloc[-1]['reverse_break_point'][1]  
        if to_confirm_type == -knocking_fenbi_type:  
            xianduan_df.iloc[-1]['forward_break_point'] = [knocking_fenbi_idx, knocking_fenbi_price]  
            xianduan_df.iloc[-1]['dynamic_end_point'] = [knocking_fenbi_idx, knocking_fenbi_price]  
            xianduan_df.iloc[-1]['fenbi_idx'].append(knocking_fenbi_idx)  
            if -1 == to_confirm_type:  
                if knocking_fenbi_price <= to_confirm_forward_break_price:  
                    xianduan_df.iloc[-1]['end_point'] = [knocking_fenbi_idx, knocking_fenbi_price]  
                    if is_realtime:  
                        xianduan_df.iloc[-1]['real_reverse_break_point'] = [
                            xianduan_df.iloc[-1]['reverse_break_point'][0],
                            xianduan_df.iloc[-1]['reverse_break_point'][1]]
                    return 3
                else:  
                    if is_realtime:  
                        xianduan_df.iloc[-1]['real_reverse_break_point'] = [
                            xianduan_df.iloc[-1]['reverse_break_point'][0],
                            xianduan_df.iloc[-1]['reverse_break_point'][1]]
                    return 4
            else:  
                if knocking_fenbi_price >= to_confirm_forward_break_price:  
                    xianduan_df.iloc[-1]['end_point'] = [knocking_fenbi_idx, knocking_fenbi_price]  
                    if is_realtime:  
                        xianduan_df.iloc[-1]['real_reverse_break_point'] = [
                            xianduan_df.iloc[-1]['reverse_break_point'][0],
                            xianduan_df.iloc[-1]['reverse_break_point'][1]]
                    return 3
                else:  
                    if is_realtime:  
                        xianduan_df.iloc[-1]['real_reverse_break_point'] = [
                            xianduan_df.iloc[-1]['reverse_break_point'][0],
                            xianduan_df.iloc[-1]['reverse_break_point'][1]]
                    return 4
        else:  
            if -1 == to_confirm_type:  
                if knocking_fenbi_price >= to_confirm_reverse_break_price:  
                    self.__break_xianduan(xianduan_df, knocking_fenbi_idx, confirmed_fenbi_df)
                    return 2
                else:  
                    if is_realtime:  
                        xianduan_df.iloc[-1]['real_reverse_break_point'] = [
                            xianduan_df.iloc[-1]['reverse_break_point'][0],
                            xianduan_df.iloc[-1]['reverse_break_point'][1]]
                    xianduan_df.iloc[-1]['reverse_break_point'] = [knocking_fenbi_idx, knocking_fenbi_price]  
                    xianduan_df.iloc[-1]['dynamic_end_point'] = [knocking_fenbi_idx, knocking_fenbi_price]  
                    xianduan_df.iloc[-1]['fenbi_idx'].append(knocking_fenbi_idx)  
                    return 4
            else:  
                if knocking_fenbi_price <= to_confirm_reverse_break_price:  
                    self.__break_xianduan(xianduan_df, knocking_fenbi_idx, confirmed_fenbi_df)
                    return 2
                else:  
                    if is_realtime:  
                        xianduan_df.iloc[-1]['real_reverse_break_point'] = [
                            xianduan_df.iloc[-1]['reverse_break_point'][0],
                            xianduan_df.iloc[-1]['reverse_break_point'][1]]
                    xianduan_df.iloc[-1]['reverse_break_point'] = [knocking_fenbi_idx, knocking_fenbi_price]  
                    xianduan_df.iloc[-1]['dynamic_end_point'] = [knocking_fenbi_idx, knocking_fenbi_price]  
                    xianduan_df.iloc[-1]['fenbi_idx'].append(knocking_fenbi_idx)  
                    return 4

    def __break_xianduan(self, xianduan_df, knocking_fenbi_idx, confirmed_fenbi_df):
        
        xianduan_df.iloc[-1]['fenbi_idx_snapshot'] = copy.deepcopy(xianduan_df.iloc[-1]['fenbi_idx'])  
        xianduan_df.iloc[-1]['confirm_time'] = knocking_fenbi_idx  
        xianduan_df.iloc[-1]['status'] = 1  
        
        xianduan_end_idx = xianduan_df.iloc[-1]['end_point'][0]
        xianduan_end_price = xianduan_df.iloc[-1]['end_point'][1]
        fenbi_idx_end_idx = xianduan_df.iloc[-1]['fenbi_idx'].index(xianduan_end_idx)  
        xianduan_df.iloc[-1]['fenbi_idx'] = xianduan_df.iloc[-1]['fenbi_idx'][:fenbi_idx_end_idx + 1]  
        

        
        xianduan_df.loc[
            xianduan_end_idx,
            [
                'start_point',
                'end_point',
                'dynamic_end_point',
                'type',
                'status',
                'forward_break_point',
                'reverse_break_point',
                'fenbi_idx',
                'real_reverse_break_point',
                'real_forward_break_point',
            ]
        ] = [
            [xianduan_end_idx, xianduan_end_price],  
            [confirmed_fenbi_df.index[-1], confirmed_fenbi_df.iloc[-1]['price']],  
            [confirmed_fenbi_df.index[-1], confirmed_fenbi_df.iloc[-1]['price']],  
            confirmed_fenbi_df.iloc[-2]['type'],  
            0,  
            [confirmed_fenbi_df.index[-1], confirmed_fenbi_df.iloc[-1]['price']],  
            [confirmed_fenbi_df.index[-2], confirmed_fenbi_df.iloc[-2]['price']],  
            [confirmed_fenbi_df.index[-2], confirmed_fenbi_df.index[-1]],  
            [confirmed_fenbi_df.index[-2], confirmed_fenbi_df.iloc[-2]['price']],  
            [confirmed_fenbi_df.index[-1], confirmed_fenbi_df.iloc[-1]['price']]  
        ]
        
