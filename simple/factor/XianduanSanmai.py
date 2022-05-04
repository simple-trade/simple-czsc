# -*- encoding: utf-8 -*-

from simple.factor import factors
from simple.factor.FactorAbstract import FactorAbstract

class XianduanSanmai(FactorAbstract):
    def get_factor_name(self):
        return factors['xianduansanmai']

    '''
    返回：    
    [
        type, 
        start_point, 
        end_point 
    ]
    '''

    def execute(self):
        hebing_df, fenxing_df, fenbi_df, xianduan_df, zhongshu_df, realtime_fenbi_df, realtime_xianduan_df, realtime_zhongshu_df = self.czsc.get_containers()

        if realtime_xianduan_df.shape[0] < 4:
            return []

        if realtime_xianduan_df.iloc[-1]['type'] == -1:
            cond1 = realtime_xianduan_df.iloc[-4]['start_point'][1] < realtime_xianduan_df.iloc[-2]['start_point'][1]
            cond2 = realtime_xianduan_df.iloc[-1]['start_point'][1] > realtime_xianduan_df.iloc[-3]['start_point'][1]
            cond3 = realtime_xianduan_df.iloc[-1]['end_point'][1] > realtime_xianduan_df.iloc[-3]['start_point'][1]
            if cond1 and cond2 and cond3:
                return [1, realtime_xianduan_df.iloc[-1]['start_point'], realtime_xianduan_df.iloc[-1]['end_point']]
            else:
                return []
        else:
            cond1 = realtime_xianduan_df.iloc[-4]['start_point'][1] > realtime_xianduan_df.iloc[-2]['start_point'][1]
            cond2 = realtime_xianduan_df.iloc[-1]['start_point'][1] < realtime_xianduan_df.iloc[-3]['start_point'][1]
            cond3 = realtime_xianduan_df.iloc[-1]['end_point'][1] < realtime_xianduan_df.iloc[-3]['start_point'][1]
            if cond1 and cond2 and cond3:
                return [-1, realtime_xianduan_df.iloc[-1]['start_point'], realtime_xianduan_df.iloc[-1]['end_point']]
            else:
                return []
