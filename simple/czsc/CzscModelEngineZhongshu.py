# -*- encoding: utf-8 -*-

from simple.logger.logger import LoggerFactory
logger = LoggerFactory.getLogger(__name__)
class CzscModelEngineZhongshu:
    def __init__(self,stock_code,frequency,is_debug=False):
        self.is_debug=is_debug
        pass

    def human_result(self,result):
        return '中枢'

    def execute(self, stock_df, xianduan_df,zhongshu_df,is_realtime=False):

        if is_realtime:
            confirmed_xianduan_df = xianduan_df
        else:
            confirmed_xianduan_df = xianduan_df.drop(axis=0,labels=[xianduan_df.index[-1]],inplace=False)
        if confirmed_xianduan_df.shape[0] < 3: 
            return -1
        
        
        if -1 == confirmed_xianduan_df.iloc[-1]['type']:       
            if zhongshu_df.shape[0] > 0 and zhongshu_df.iloc[-1]['status']==0 and confirmed_xianduan_df.iloc[-1]['end_point'][1]>zhongshu_df.iloc[-1]['top_point'][1]: 
                zhongshu_df.iloc[-1]['status']=1 
                
                zhongshu_df.iloc[-1]['end_point']=confirmed_xianduan_df.iloc[-2]['start_point'] 
                
                lowest_point = self.__find_lowest_point(zhongshu_df.iloc[-1]['start_point'][0],zhongshu_df.iloc[-1]['end_point'][0],stock_df)
                zhongshu_df.iloc[-1]['low_point']=lowest_point
                highest_point = self.__find_highest_point(zhongshu_df.iloc[-1]['start_point'][0],zhongshu_df.iloc[-1]['end_point'][0],stock_df)
                zhongshu_df.iloc[-1]['high_point']=highest_point
                if self.is_debug:
                    logger.info(zhongshu_df)
                return 2
            else: 
                pass

            
            low1_point=confirmed_xianduan_df.iloc[-1]['end_point'] 
            low2_point=confirmed_xianduan_df.iloc[-3]['end_point'] 
            high1_point=confirmed_xianduan_df.iloc[-1]['start_point']
            high2_point=confirmed_xianduan_df.iloc[-3]['start_point']
            
            bottom_point = low1_point if(low1_point[1]>low2_point[1]) else low2_point
            top_point = high1_point if(high1_point[1]<high2_point[1]) else high2_point
            
            is_create_zhongshu=False
            if zhongshu_df.shape[0]<1:
                if bottom_point[1] < top_point[1]:
                    is_create_zhongshu=True
            else:
                if zhongshu_df.iloc[-1]['status']==1 and low2_point[1] > zhongshu_df.iloc[-1]['top_point'][1] and bottom_point[1] < top_point[1]: 
                    is_create_zhongshu=True
            if is_create_zhongshu:
                
                
                highest_point = self.__find_highest_point(high2_point[0],low1_point[0],stock_df)
                lowest_point = self.__find_lowest_point(high2_point[0],low1_point[0],stock_df)
                
                _type = 1
                if zhongshu_df.shape[0]>=1:
                    if bottom_point[1] > zhongshu_df.iloc[-1]['top_point'][1]: _type = 1
                    if top_point[1] < zhongshu_df.iloc[-1]['bottom_point'][1]: _type = -1
                
                zhongshu_df.loc[high2_point[0],
                    ['start_point', 
                    'end_point', 
                    'high_point', 
                    'last_high_point', 
                    'low_point', 
                    'last_low_point', 
                    'top_point', 
                    'bottom_point', 
                    'type', 
                    'status' 
                    ]
                ] = [high2_point,low1_point,highest_point,highest_point,lowest_point,lowest_point,top_point,bottom_point,_type,0]
                if self.is_debug:
                    logger.info(zhongshu_df)
                return 1
            
            
            
            if zhongshu_df.shape[0] > 0 and zhongshu_df.iloc[-1]['status']==0:
                zhongshu_df.iloc[-1]['end_point']=confirmed_xianduan_df.iloc[-1]['end_point']
                lowest_point = self.__find_lowest_point(zhongshu_df.iloc[-1]['start_point'][0],zhongshu_df.iloc[-1]['end_point'][0],stock_df)
                if lowest_point[1] <= zhongshu_df.iloc[-1]['low_point'][1]: 
                    zhongshu_df.iloc[-1]['low_point']=lowest_point
            return 3

        else:  
            if zhongshu_df.shape[0] > 0 and zhongshu_df.iloc[-1]['status']==0 and confirmed_xianduan_df.iloc[-1]['end_point'][1]<zhongshu_df.iloc[-1]['bottom_point'][1]: 
                zhongshu_df.iloc[-1]['status']=1 
                
                zhongshu_df.iloc[-1]['end_point']=confirmed_xianduan_df.iloc[-2]['start_point'] 
                
                lowest_point = self.__find_lowest_point(zhongshu_df.iloc[-1]['start_point'][0],zhongshu_df.iloc[-1]['end_point'][0],stock_df)
                zhongshu_df.iloc[-1]['low_point']=lowest_point
                highest_point = self.__find_highest_point(zhongshu_df.iloc[-1]['start_point'][0],zhongshu_df.iloc[-1]['end_point'][0],stock_df)
                zhongshu_df.iloc[-1]['high_point']=highest_point
                if self.is_debug:
                    logger.info(zhongshu_df)
                return 2
            else: 
                pass

            
            high1_point=confirmed_xianduan_df.iloc[-1]['end_point'] 
            high2_point=confirmed_xianduan_df.iloc[-3]['end_point'] 
            low1_point=confirmed_xianduan_df.iloc[-1]['start_point']
            low2_point=confirmed_xianduan_df.iloc[-3]['start_point']
            
            bottom_point = low1_point if(low1_point[1]>low2_point[1]) else low2_point
            top_point = high1_point if(high1_point[1]<high2_point[1]) else high2_point
            
            is_create_zhongshu=False
            if zhongshu_df.shape[0]<1:
                if bottom_point[1] < top_point[1]:
                    is_create_zhongshu=True
            else:
                if zhongshu_df.iloc[-1]['status']==1 and high2_point[1] < zhongshu_df.iloc[-1]['bottom_point'][1] and bottom_point[1] < top_point[1]: 
                    is_create_zhongshu=True
            if is_create_zhongshu:
                
                
                
                highest_point = self.__find_highest_point(low2_point[0],high1_point[0],stock_df)
                lowest_point = self.__find_lowest_point(low2_point[0],high1_point[0],stock_df)
                
                _type = -1
                if zhongshu_df.shape[0]>=1:
                    if bottom_point[1] > zhongshu_df.iloc[-1]['top_point'][1]: _type = 1
                    if top_point[1] < zhongshu_df.iloc[-1]['bottom_point'][1]: _type = -1
                
                zhongshu_df.loc[low2_point[0],
                    ['start_point', 
                    'end_point', 
                    'high_point', 
                    'last_high_point', 
                    'low_point', 
                    'last_low_point', 
                    'top_point', 
                    'bottom_point', 
                    'type', 
                    'status' 
                    ]
                ]=[low2_point,high1_point,highest_point,highest_point,lowest_point,lowest_point,top_point,bottom_point,_type,0]
                if self.is_debug:
                    logger.info(zhongshu_df)
                return 1
            
            
            
            if zhongshu_df.shape[0] > 0 and zhongshu_df.iloc[-1]['status']==0: 
                zhongshu_df.iloc[-1]['end_point']=confirmed_xianduan_df.iloc[-1]['end_point']
                highest_point = self.__find_highest_point(zhongshu_df.iloc[-1]['start_point'][0],zhongshu_df.iloc[-1]['end_point'][0],stock_df)
                if highest_point[1] >= zhongshu_df.iloc[-1]['high_point'][1]: 
                    zhongshu_df.iloc[-1]['high_point']=highest_point
            return 3


    def __find_highest_point(self,  index1,index2,stock_df):
        tmp_df=stock_df.loc[index1:index2,'high'].infer_objects()
        max_price = tmp_df.max()
        max_time = tmp_df.idxmax()
        return [max_time,max_price]


    def __find_lowest_point(self, index1,index2,stock_df):
        tmp_df=stock_df.loc[index1:index2,'low'].infer_objects()
        min_price = tmp_df.min()
        min_time = tmp_df.idxmin()
        return [min_time,min_price]