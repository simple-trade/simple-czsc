# -*- encoding: utf-8 -*-

from simple.logger.logger import LoggerFactory
logger = LoggerFactory.getLogger(__name__)
class CzscRealtimeModelEngineXianduan:
    def __init__(self, stock_code, frequency, is_debug=False):
        self.is_debug = is_debug

    def execute(self, xianduan_engine, realtime_fenbi_df, realtime_xianduan_df):
        confirmed_xianduan_size = realtime_xianduan_df.shape[0] - 1 
        
        cal_count = realtime_fenbi_df.shape[0]-3
        for i in range(cal_count):
            end_index = i+4 
            current_realtime_fenbi_df = realtime_fenbi_df.iloc[0:end_index, :] 
            xianduan_engine.execute(current_realtime_fenbi_df, realtime_xianduan_df,True)

        all_xianduan_size = realtime_xianduan_df.shape[0]
        realtime_xianduan_size = all_xianduan_size - confirmed_xianduan_size 
        
        for i in range(realtime_xianduan_size):
            idx = -(i + 1)
            realtime_xianduan_df.iloc[idx]['status'] = -1
