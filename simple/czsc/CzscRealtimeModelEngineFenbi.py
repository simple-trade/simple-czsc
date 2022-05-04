# -*- encoding: utf-8 -*-

import pandas as pd
import numpy as np
from simple.czsc.Utils import find_highest_point, find_lowest_point

from simple.logger.logger import LoggerFactory

logger = LoggerFactory.getLogger(__name__)


class CzscRealtimeModelEngineFenbi:
    def __init__(self, stock_code, frequency, is_debug=False):
        self.is_debug = is_debug

    def execute(self, stock_df, k_df, fenbi_df):
        realtime_fenbi_df = pd.DataFrame(columns=['confirm_time', 'price', 'type', 'status', 'price2'])

        if fenbi_df.shape[0] < 2:
            return realtime_fenbi_df
        
        forward_price = fenbi_df.iloc[-1]['price']
        forward_type = fenbi_df.iloc[-1]['type']
        forward_index = fenbi_df.index[-1]
        reverse_price = fenbi_df.iloc[-2]['price']
        reverse_type = fenbi_df.iloc[-2]['type']
        reverse_index = fenbi_df.index[-2]

        b_f_a_k_h_p = find_highest_point(forward_index, k_df.index[-1], stock_df)
        
        b_f_a_k_l_p = find_lowest_point(forward_index, k_df.index[-1], stock_df)

        if 1 == fenbi_df.iloc[-1]['type']:  
 
            if b_f_a_k_h_p[1] < reverse_price and b_f_a_k_l_p[1] == forward_price and b_f_a_k_l_p[0] == forward_index:

                realtime_fenbi_df.loc[reverse_index, ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                    k_df.index[-1],
                    reverse_price,
                    reverse_type,
                    -1,
                    np.nan,
                ]
                realtime_fenbi_df.loc[forward_index, ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                    k_df.index[-1],
                    forward_price,
                    forward_type,
                    -1,
                    np.nan,
                ]
                return realtime_fenbi_df

            if b_f_a_k_h_p[1] < reverse_price and b_f_a_k_l_p[1] <= forward_price and b_f_a_k_l_p[0] != forward_index:

                realtime_fenbi_df.loc[reverse_index, ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                    k_df.index[-1],
                    reverse_price,
                    reverse_type,
                    -1,
                    np.nan,
                ]
                realtime_fenbi_df.loc[b_f_a_k_l_p[0], ['confirm_time', 'price', 'type', 'status', 'price2']] = [k_df.index[-1], b_f_a_k_l_p[1], 1, -1, np.nan]
                return realtime_fenbi_df

            if b_f_a_k_h_p[1] >= reverse_price and b_f_a_k_l_p[1] == forward_price and b_f_a_k_l_p[0] == forward_index:

                if b_f_a_k_h_p[0] == b_f_a_k_l_p[0]:  
                    realtime_fenbi_df.loc[reverse_index, ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                        k_df.index[-1],
                        reverse_price,
                        reverse_type,
                        -1,
                        np.nan,
                    ]
                    realtime_fenbi_df.loc[b_f_a_k_l_p[0], ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                        k_df.index[-1],
                        b_f_a_k_l_p[1],
                        1,
                        -1,
                        b_f_a_k_h_p[1],
                    ]
                    return realtime_fenbi_df

                realtime_fenbi_df.loc[reverse_index, ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                    k_df.index[-1],
                    reverse_price,
                    reverse_type,
                    -1,
                    np.nan,
                ]
                realtime_fenbi_df.loc[forward_index, ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                    k_df.index[-1],
                    forward_price,
                    forward_type,
                    -1,
                    np.nan,
                ]
                realtime_fenbi_df.loc[b_f_a_k_h_p[0], ['confirm_time', 'price', 'type', 'status', 'price2']] = [k_df.index[-1], b_f_a_k_h_p[1], -1, -1, np.nan]
                return realtime_fenbi_df

            if b_f_a_k_h_p[1] >= reverse_price and b_f_a_k_l_p[1] <= forward_price and b_f_a_k_l_p[0] != forward_index:

                if b_f_a_k_l_p[0] < b_f_a_k_h_p[0]:
                    realtime_fenbi_df.loc[reverse_index, ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                        k_df.index[-1],
                        reverse_price,
                        reverse_type,
                        -1,
                        np.nan,
                    ]
                    realtime_fenbi_df.loc[b_f_a_k_l_p[0], ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                        k_df.index[-1],
                        b_f_a_k_l_p[1],
                        1,
                        -1,
                        np.nan,
                    ]
                    realtime_fenbi_df.loc[b_f_a_k_h_p[0], ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                        k_df.index[-1],
                        b_f_a_k_h_p[1],
                        -1,
                        -1,
                        np.nan,
                    ]
                    return realtime_fenbi_df

                if b_f_a_k_l_p[0] > b_f_a_k_h_p[0]:
                    realtime_fenbi_df.loc[reverse_index, ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                        k_df.index[-1],
                        reverse_price,
                        reverse_type,
                        -1,
                        np.nan,
                    ]
                    realtime_fenbi_df.loc[forward_index, ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                        k_df.index[-1],
                        forward_price,
                        forward_type,
                        -1,
                        np.nan,
                    ]
                    realtime_fenbi_df.loc[b_f_a_k_h_p[0], ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                        k_df.index[-1],
                        b_f_a_k_h_p[1],
                        -1,
                        -1,
                        np.nan,
                    ]
                    realtime_fenbi_df.loc[b_f_a_k_l_p[0], ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                        k_df.index[-1],
                        b_f_a_k_l_p[1],
                        1,
                        -1,
                        np.nan,
                    ]

                    if forward_index == b_f_a_k_h_p[0]:
                        realtime_fenbi_df.drop(axis=0, index=reverse_index, inplace=True)
                    return realtime_fenbi_df

                if b_f_a_k_l_p[0] == b_f_a_k_h_p[0]:
                    realtime_fenbi_df.loc[reverse_index, ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                        k_df.index[-1],
                        reverse_price,
                        reverse_type,
                        -1,
                        np.nan,
                    ]
                    realtime_fenbi_df.loc[b_f_a_k_l_p[0], ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                        k_df.index[-1],
                        b_f_a_k_l_p[1],
                        1,
                        -1,
                        b_f_a_k_h_p[1],
                    ]
                    return realtime_fenbi_df

            raise Exception('Mars Area')
        else:  
            if b_f_a_k_l_p[1] > reverse_price and b_f_a_k_h_p[1] == forward_price and b_f_a_k_h_p[0] == forward_index:

                realtime_fenbi_df.loc[reverse_index, ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                    k_df.index[-1],
                    reverse_price,
                    reverse_type,
                    -1,
                    np.nan,
                ]
                realtime_fenbi_df.loc[forward_index, ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                    k_df.index[-1],
                    forward_price,
                    forward_type,
                    -1,
                    np.nan,
                ]
                return realtime_fenbi_df

            if b_f_a_k_l_p[1] > reverse_price and b_f_a_k_h_p[1] >= forward_price and b_f_a_k_h_p[0] != forward_index:

                realtime_fenbi_df.loc[reverse_index, ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                    k_df.index[-1],
                    reverse_price,
                    reverse_type,
                    -1,
                    np.nan,
                ]
                realtime_fenbi_df.loc[b_f_a_k_h_p[0], ['confirm_time', 'price', 'type', 'status', 'price2']] = [k_df.index[-1], b_f_a_k_h_p[1], -1, -1, np.nan]
                return realtime_fenbi_df

            if b_f_a_k_l_p[1] <= reverse_price and b_f_a_k_h_p[1] == forward_price and b_f_a_k_h_p[0] == forward_index:

                if b_f_a_k_h_p[0] == b_f_a_k_l_p[0]:  
                    realtime_fenbi_df.loc[reverse_index, ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                        k_df.index[-1],
                        reverse_price,
                        reverse_type,
                        -1,
                        np.nan,
                    ]
                    realtime_fenbi_df.loc[b_f_a_k_h_p[0], ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                        k_df.index[-1],
                        b_f_a_k_h_p[1],
                        -1,
                        -1,
                        b_f_a_k_l_p[1],
                    ]
                    return realtime_fenbi_df

                realtime_fenbi_df.loc[reverse_index, ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                    k_df.index[-1],
                    reverse_price,
                    reverse_type,
                    -1,
                    np.nan,
                ]
                realtime_fenbi_df.loc[forward_index, ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                    k_df.index[-1],
                    forward_price,
                    forward_type,
                    -1,
                    np.nan,
                ]
                realtime_fenbi_df.loc[b_f_a_k_l_p[0], ['confirm_time', 'price', 'type', 'status', 'price2']] = [k_df.index[-1], b_f_a_k_l_p[1], 1, -1, np.nan]
                return realtime_fenbi_df

            
            if b_f_a_k_l_p[1] <= reverse_price and b_f_a_k_h_p[1] >= forward_price and b_f_a_k_h_p[0] != forward_index:

                if b_f_a_k_h_p[0] < b_f_a_k_l_p[0]:
                    realtime_fenbi_df.loc[reverse_index, ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                        k_df.index[-1],
                        reverse_price,
                        reverse_type,
                        -1,
                        np.nan,
                    ]
                    realtime_fenbi_df.loc[b_f_a_k_h_p[0], ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                        k_df.index[-1],
                        b_f_a_k_h_p[1],
                        -1,
                        -1,
                        np.nan,
                    ]
                    realtime_fenbi_df.loc[b_f_a_k_l_p[0], ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                        k_df.index[-1],
                        b_f_a_k_l_p[1],
                        1,
                        -1,
                        np.nan,
                    ]
                    return realtime_fenbi_df

                if b_f_a_k_h_p[0] > b_f_a_k_l_p[0]:
                    realtime_fenbi_df.loc[reverse_index, ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                        k_df.index[-1],
                        reverse_price,
                        reverse_type,
                        -1,
                        np.nan,
                    ]
                    realtime_fenbi_df.loc[forward_index, ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                        k_df.index[-1],
                        forward_price,
                        forward_type,
                        -1,
                        np.nan,
                    ]
                    realtime_fenbi_df.loc[b_f_a_k_l_p[0], ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                        k_df.index[-1],
                        b_f_a_k_l_p[1],
                        1,
                        -1,
                        np.nan,
                    ]
                    realtime_fenbi_df.loc[b_f_a_k_h_p[0], ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                        k_df.index[-1],
                        b_f_a_k_h_p[1],
                        -1,
                        -1,
                        np.nan,
                    ]

                    if forward_index == b_f_a_k_l_p[0]:  
                        realtime_fenbi_df.drop(axis=0, index=reverse_index, inplace=True)
                    return realtime_fenbi_df

                if b_f_a_k_l_p[0] == b_f_a_k_h_p[0]:
                    realtime_fenbi_df.loc[reverse_index, ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                        k_df.index[-1],
                        reverse_price,
                        reverse_type,
                        -1,
                        np.nan,
                    ]
                    realtime_fenbi_df.loc[b_f_a_k_h_p[0], ['confirm_time', 'price', 'type', 'status', 'price2']] = [
                        k_df.index[-1],
                        b_f_a_k_h_p[1],
                        -1,
                        -1,
                        b_f_a_k_l_p[1],
                    ]
                    return realtime_fenbi_df

            raise Exception('Mars Area')
