# -*- encoding: utf-8 -*-

class CzscRealtimeModelEngineZhongshu:


    def __init__(self, stock_code, frequency, is_debug=False):
        self.is_debug = is_debug


    def execute(self, zhongshu_engine,stock_df,realtime_xianduan_df,realtime_zhongshu_df):

        to_execute_base_xianduan_df = realtime_xianduan_df

        realtime_count = to_execute_base_xianduan_df[to_execute_base_xianduan_df['status']==-1].shape[0]

        for i in range(realtime_count):
            idx = i - realtime_count + 1
            if idx == 0:
                to_execute_xianduan_df=to_execute_base_xianduan_df
            else:
                to_execute_xianduan_df=to_execute_base_xianduan_df.iloc[:idx,:]
            zhongshu_engine.execute(stock_df, to_execute_xianduan_df,realtime_zhongshu_df,True)
        