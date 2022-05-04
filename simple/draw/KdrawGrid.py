# -*- encoding: utf-8 -*-

from pyecharts.charts import Bar
from pyecharts.charts import Kline
from pyecharts.charts import Line
from pyecharts.charts import Grid
from pyecharts.charts import Page
from pyecharts.charts import Scatter
from pyecharts.commons.utils import JsCode
from pyecharts import options as opts

import talib
import numpy as np
from pyecharts.render import make_snapshot
from snapshot_selenium import snapshot
from selenium.webdriver.chrome.options import Options

from pyecharts.globals import CurrentConfig, NotebookType

# 使用jupyter-lab时需要
# CurrentConfig.NOTEBOOK_TYPE = NotebookType.JUPYTER_LAB
# 可自定义pyecharts资源引用 https://pyecharts.org/#/zh-cn/assets_host
CurrentConfig.ONLINE_HOST = "https://assets.pyecharts.org/assets/"
'''
创建Grid

---

开平点位标记

points_slices=[
    [id,name,time,price,type],
    [id,name,time,price,type]
]

type:
 bl -> 开多
 bs -> 开空
 sl -> 平多
 ss -> 平空



---

long_short_range 多空区间，以markarea方式绘制
{
    long:[
        [startindex,endindex],
        [startindex,endindex],
        ...
    ],
    short:[
        [startindex,endindex],
        [startindex,endindex],
        ...
    ]
}


'''


class KdrawGrid:
    def __init__(
        self,
        title,
        data_df,
        fb_df,
        xd_df,
        zs_df,
        macd_or_natr='macd',
        grid_width=None,
        grid_height=None,
        datazoom_start='70',
        points=[],
        start_idx=None,
        long_short_range={},
        xd_reverse_points=[],
        xd_forward_points=[],
        precision=2,
        macd_normalized_df=None,
        target_point=[],
        ma_df=None,
        nav_df=None,
        second_type_bs_point=[],
        deviation_range={},
        rizhou_df=None,
        rizhou_signal_df=None,
        minor_draw=['macd'],
    ):
        # 精度处理
        data_df[['open', 'close', 'high', 'low']] = data_df[['open', 'close', 'high', 'low']].astype(float)
        data_df[['open', 'close', 'high', 'low']] = data_df[['open', 'close', 'high', 'low']].apply(lambda x: round(x, 2))
        fb_df[['price']] = fb_df[['price']].astype(float)
        fb_df[['price']] = fb_df[['price']].apply(lambda x: round(x, 2))

        if 'macd' in data_df.columns.values.tolist():
            data_df[['macd', 'dif', 'dea']] = data_df[['macd', 'dif', 'dea']].astype(float)
            data_df[['macd', 'dif', 'dea']] = data_df[['macd', 'dif', 'dea']].apply(lambda x: round(x, 2))

        if macd_normalized_df is not None:
            macd_normalized_df[['area']] = macd_normalized_df[['area']].astype(float)
            macd_normalized_df[['area']] = macd_normalized_df[['area']].apply(lambda x: round(x, 2))

        # 画图开始时间
        if not start_idx is None:
            data_df_slices = data_df[data_df.index >= start_idx]
            rizhou_df_slices = None if rizhou_df is None else rizhou_df[rizhou_df.index >= start_idx]
            rizhou_signal_df_slices = None if rizhou_signal_df is None else rizhou_signal_df[rizhou_df.index >= start_idx]
            fb_df_slices = fb_df[fb_df.index >= start_idx]
            xd_df_slices = xd_df[xd_df.index >= start_idx]
            zs_df_slices = zs_df[zs_df.index >= start_idx]
            points_slices = []
            if points:
                for p in points:
                    if p[2] >= start_idx:
                        points_slices.append(p)
            target_point_slices = []
            if target_point:
                for p in target_point:
                    if p[0] >= start_idx:
                        target_point_slices.append(p)
            rizhou_signal_slices = None if rizhou_signal_df_slices is None else rizhou_signal_df_slices['signal_point'].values
            ma_df_slices = None if ma_df is None else ma_df[ma_df.index >= start_idx]
            nav_df_slices = None if nav_df is None else nav_df[nav_df.index >= start_idx]

            second_type_bs_point_slices = []
            if second_type_bs_point:
                for p in second_type_bs_point:
                    if p[2] >= start_idx:
                        second_type_bs_point_slices.append(p)
        else:
            data_df_slices = data_df
            rizhou_df_slices = rizhou_df
            fb_df_slices = fb_df
            xd_df_slices = xd_df
            zs_df_slices = zs_df
            points_slices = points
            target_point_slices = target_point
            rizhou_signal_slices = None if rizhou_signal_df is None else rizhou_signal_df['signal_point'].values
            ma_df_slices = ma_df
            nav_df_slices = nav_df
            second_type_bs_point_slices = second_type_bs_point
        self.precision = precision
        self.title = title
        self.macd_or_natr = macd_or_natr
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.datazoom_start = datazoom_start
        self.long_short_range = long_short_range
        self.deviation_range = deviation_range
        self.macd_normalized_df = macd_normalized_df
        # K线
        self.kline = None
        # 分笔
        self.fb_line = None
        # 实时分笔
        self.realtime_fb_line = None
        # 线段
        self.xd_line = None
        # 实时线段
        self.realtime_xd_line = None
        # macd line，即dif、dea
        self.macd_line = None
        self.macd_bar = None
        # natr
        self.natr_line = None
        # 日周
        self.dailyk_line = None
        self.weekk_line = None
        # 买卖点标记
        self.scatter_point_bl = None
        self.scatter_point_bs = None
        self.scatter_point_sl = None
        self.scatter_point_ss = None
        # scatter_point
        self.scatter_point = None
        # 反转点连线
        self.xd_reverse_line = None
        # 正向点连线
        self.xd_forward_line = None
        # macd标准模型
        self.macd_normalized_scatter_red = None
        self.macd_normalized_scatter_green = None
        # 目标点
        self.scatter_target_point = None
        # 日周信号
        self.scatter_rizhou_signal_long = None
        self.scatter_rizhou_signal_short = None
        # MA
        self.ma_line_5 = None
        self.ma_line_10 = None
        # 净值
        self.nav_line = None

        # 模拟买卖点
        self.scatter_second_type_bs_point_bl = None
        self.scatter_second_type_bs_point_bs = None

        # 幅图
        self.minor_draw = minor_draw

        # 获取K线数据
        def get_K_data(df):
            kdata = df.loc[:, ['open', 'close', 'low', 'high']].to_dict('split')['data']
            xaxis = list(df.index.tolist())
            return xaxis, kdata

        # 获取分笔数据 用于line展示
        def get_fb_data(df):
            xddata = []
            xaxis = []
            if not df.empty and df.shape[0] > 0:
                complete_df = df[df['status'] == 1]
                xaxis = list(complete_df.index.tolist())
                xddata = list(complete_df.loc[:, 'price'])
            return xaxis, xddata

        # 获取实时分笔 用于line展示
        def get_realtime_fb_data(df):
            xddata = []
            xaxis = []
            if not df.empty and df.shape[0] > 0:
                complete_df = df[df['status'] == 1]
                if complete_df.shape[0] > 0:
                    # 先放入已完成分笔的最后一个
                    xaxis.append(complete_df.index[-1])
                    xddata.append(complete_df.iloc[-1]['price'])
                # 再追加所有实时分笔
                realtime_df = df[df['status'] == -1]
                xaxis.extend(list(realtime_df.index.tolist()))
                xddata.extend(list(realtime_df.loc[:, 'price']))
            return xaxis, xddata

        # 获取实时分笔极端行情price2
        def get_realtime_extreme_point(df):
            data = []
            for idx, row in df.iterrows():
                if not np.isnan(row['price2']):  # 如果price2不是nan，表示极端行情出现
                    data.append({'name': '极端行情', 'coord': [idx, row['price2']]})
            return data

        # 获取已完成的线段数据 用于line展示
        def get_xd_data(df):
            xddata = []
            xaxis = []
            if not df.empty and df.shape[0] > 0:
                complete_df = df[df['status'] == 1]
                if complete_df.shape[0] > 0:
                    xaxis = list(complete_df.index.tolist())
                    xddata = [i[1] for i in list(complete_df.loc[:, 'start_point'])]
                    # 追加最后一个结束点
                    xaxis.append(complete_df.iloc[-1]['end_point'][0])
                    xddata.append(complete_df.iloc[-1]['end_point'][1])
            # 精度处理
            xddata = [round(x, self.precision) for x in xddata]
            return xaxis, xddata

        # 获取实时线段 用于line展示
        def get_realtime_xd_data(df):
            xddata = []
            xaxis = []
            if not df.empty and df.shape[0] > 0:
                realtime_df = df[df['status'] == -1]
                if realtime_df.shape[0] > 0:
                    xaxis = list(realtime_df.index.tolist())
                    xddata = [i[1] for i in list(realtime_df.loc[:, 'start_point'])]
                    # 追加最后一个结束点
                    xaxis.append(realtime_df.iloc[-1]['end_point'][0])
                    xddata.append(realtime_df.iloc[-1]['end_point'][1])
            # 精度处理
            xddata = [round(x, self.precision) for x in xddata]
            return xaxis, xddata

        # 获取中枢数据
        def get_zs(zs_df_slices):
            data = []
            for idx, row in zs_df_slices.iterrows():
                data.append(
                    [
                        {
                            'name': '',
                            'coord': [row['start_point'][0], round(row['top_point'][1], self.precision)],
                            'itemStyle': {'color': 'rgba(196,204,211,0.5)'},
                        },  # 起始点时间、上沿价格
                        {'coord': [row['end_point'][0], round(row['bottom_point'][1], self.precision)]},  # 结束点时间、下沿价格
                    ]
                )
            return data

        # 获取中枢高低点数据
        def get_zs_high_low(zs_df_slices):
            data = []
            for idx, row in zs_df_slices.iterrows():
                data.append({'name': '', 'coord': [row['high_point'][0], round(row['high_point'][1], self.precision)]})  # 最高点时间、最高点价格
                data.append({'name': '', 'coord': [row['low_point'][0], round(row['low_point'][1], self.precision)]})  # 最低点时间、最低点价格
            return data

        # 获取MACD数据
        def get_macd_data(df):
            dif = []
            dea = []
            macd = []
            if 'dif' in df.columns.values:
                dif = [l for l in df.dif.iteritems()]
                dea = [l for l in df.dea.iteritems()]
                macd = [l for l in df.macd.iteritems()]
            return dif, dea, macd

        # 获取atr数据
        def get_natr_data(df):
            if 'natr' in df.columns.values:
                return [l for l in df.natr.iteritems()]
            return []

        # 获取日周数据dailyk
        def get_rizhou_data_dailyk(df):
            if df is None or 'dailyk' not in df.columns.values:
                return []
            return [l for l in df.dailyk.iteritems()]

        # 获取日周数据weekk
        def get_rizhou_data_weekk(df):
            if df is None or 'weekk' not in df.columns.values:
                return []
            return [l for l in df.weekk.iteritems()]

        # macd柱样式即数值设置
        def get_macd_yaxis_data(macd):
            data = []
            for t, v in macd:
                if v >= 0:  # 红柱
                    data.append(opts.BarItem(name='', value=v, itemstyle_opts=opts.ItemStyleOpts(color="#ef232a"),))
                else:  # 绿柱
                    data.append(opts.BarItem(name='', value=v, itemstyle_opts=opts.ItemStyleOpts(color="#14b143"),))
            return data

        def get_scatter_points_data(points_slices, _type):
            if not points_slices:
                return [], []
            pts = []
            for p in points_slices:
                if p[4] == _type:
                    pts.append(p)
            if not pts:
                return [], []
            xdata = [time[2] for time in pts]
            ydata = [[round(p[3], self.precision), p[1]] for p in pts]
            return xdata, ydata

        def get_long_short_markarea_data(long_short_range):
            '''
            多空数据
            '''
            data = []
            if 'long' in long_short_range:
                for l in long_short_range['long']:
                    # 如果时间超过k线最新时间，重新赋值，以避免出现循环画图的情况
                    ls_start_idx = l[0]
                    ls_end_idx = min(l[1], data_df_slices.index[-1])
                    data.append([{'name': '', 'itemStyle': {'color': 'rgba(255, 71, 0, 0.1)'}, 'xAxis': ls_start_idx}, {'xAxis': ls_end_idx}])  # 多
            if 'short' in long_short_range:
                for l in long_short_range['short']:
                    # 如果时间超过k线最新时间，重新赋值，以避免出现循环画图的情况
                    ls_start_idx = l[0]
                    ls_end_idx = min(l[1], data_df_slices.index[-1])
                    data.append([{'name': '', 'itemStyle': {'color': 'rgba(0, 255, 140, 0.1)'}, 'xAxis': ls_start_idx}, {'xAxis': ls_end_idx}])  # 空
            return data

        def get_xd_reverse_data(xd_reverse_points):
            if not xd_reverse_points:
                return [], []
            return [p[0] for p in xd_reverse_points], [round(p[1], self.precision) for p in xd_reverse_points]

        def get_macd_extremum_point(macd_normalized_df, _type):
            '''
            macd标准模型
            '''
            xdata = []
            ydata = []
            if macd_normalized_df is None or macd_normalized_df.shape[0] < 1:
                return xdata, ydata
            if 1 == _type:
                tmp_macd_normalized_df = macd_normalized_df[macd_normalized_df['type'] == 1]
            else:
                tmp_macd_normalized_df = macd_normalized_df[macd_normalized_df['type'] == -1]
            for idx, row in tmp_macd_normalized_df.iterrows():
                xdata.append(row['extremum_point'][0])
                ydata.append([round(row['extremum_point'][1], self.precision), row['area']])
            return xdata, ydata

        def get_scatter_target_point_data(target_point_slices):
            '''
            目标点
            '''
            if not target_point_slices:
                return [], []
            xdata = [p[0] for p in target_point_slices]
            ydata = [round(p[1], self.precision) for p in target_point_slices]
            return xdata, ydata

        def get_scatter_rizhou_signal_data(rizhou_signal_slices, _type):
            '''
            日周信号
            '''
            if rizhou_signal_slices is None or len(rizhou_signal_slices) <= 0:
                return [], []
            pts = []
            for p in rizhou_signal_slices:
                if p[2] == _type:
                    pts.append(p)
            if len(pts) <= 0:
                return [], []
            xdata = [p[0] for p in pts]
            ydata = [round(p[1], self.precision) for p in pts]
            return xdata, ydata

        # 获取ma数据
        def get_ma_data(ma_series):
            return list(ma_series.index), list(ma_series)

        def get_deviation_markarea_data(deviation_range):
            '''
            背驰时间窗口
            '''
            data = []
            if '1' in deviation_range:
                for l in deviation_range['1']:
                    # 如果时间超过k线最新时间，重新赋值，以避免出现循环画图的情况
                    ls_start_idx = l[0]
                    ls_end_idx = min(l[1], data_df_slices.index[-1])
                    # data.append([{'name': '', 'itemStyle': {'color': 'rgba(139,0,139, 0.0)'}, 'xAxis': ls_start_idx}, {'xAxis': ls_end_idx}])  # 背离
            if '2' in deviation_range:
                for l in deviation_range['2']:
                    # 如果时间超过k线最新时间，重新赋值，以避免出现循环画图的情况
                    ls_start_idx = l[0]
                    ls_end_idx = min(l[1], data_df_slices.index[-1])
                    data.append([{'name': '', 'itemStyle': {'color': 'rgba(255,255,0, 0.12)'}, 'xAxis': ls_start_idx}, {'xAxis': ls_end_idx}])  # 背驰
            if '3' in deviation_range:
                for l in deviation_range['3']:
                    # 如果时间超过k线最新时间，重新赋值，以避免出现循环画图的情况
                    ls_start_idx = l[0]
                    ls_end_idx = min(l[1], data_df_slices.index[-1])
                    data.append([{'name': '', 'itemStyle': {'color': 'rgba(128,0,128, 0.12)'}, 'xAxis': ls_start_idx}, {'xAxis': ls_end_idx}])  # 背离 + 背驰
            if '-1' in deviation_range:
                for l in deviation_range['-1']:
                    # 如果时间超过k线最新时间，重新赋值，以避免出现循环画图的情况
                    ls_start_idx = l[0]
                    ls_end_idx = min(l[1], data_df_slices.index[-1])
                    # data.append([{'name': '', 'itemStyle': {'color': 'rgba(139,0,139, 0.0)'}, 'xAxis': ls_start_idx}, {'xAxis': ls_end_idx}])  # 背离
            if '-2' in deviation_range:
                for l in deviation_range['-2']:
                    # 如果时间超过k线最新时间，重新赋值，以避免出现循环画图的情况
                    ls_start_idx = l[0]
                    ls_end_idx = min(l[1], data_df_slices.index[-1])
                    data.append([{'name': '', 'itemStyle': {'color': 'rgba(0,255,0, 0.12)'}, 'xAxis': ls_start_idx}, {'xAxis': ls_end_idx}])  # 背驰
            if '-3' in deviation_range:
                for l in deviation_range['-3']:
                    # 如果时间超过k线最新时间，重新赋值，以避免出现循环画图的情况
                    ls_start_idx = l[0]
                    ls_end_idx = min(l[1], data_df_slices.index[-1])
                    data.append([{'name': '', 'itemStyle': {'color': 'rgba(30,144,255, 0.12)'}, 'xAxis': ls_start_idx}, {'xAxis': ls_end_idx}])  # 背离 + 背驰
            return data

        ## 主图 k线
        kx, ky = get_K_data(data_df_slices)
        self.kline = (
            Kline()
            .add_xaxis(xaxis_data=kx)  # 时间轴
            .add_yaxis(
                series_name="K线",
                yaxis_index=0,
                y_axis=ky,  # y轴数据
                itemstyle_opts=opts.ItemStyleOpts(color="#ec0000", color0="#00da3c", border_color="#ec0000", border_color0="#00da3c",),
            )
            # 背驰区域
            .set_series_opts(markarea_opts=opts.MarkAreaOpts(data=get_deviation_markarea_data(self.deviation_range),))
            .set_global_opts(
                title_opts=opts.TitleOpts(title=self.title,),  # 标题
                xaxis_opts=opts.AxisOpts(
                    type_="category", axistick_opts=opts.AxisTickOpts(is_show=False), axislabel_opts=opts.LabelOpts(is_show=False),  # 分组  # 不显示横坐标点  # 不显示横轴坐标
                ),
                yaxis_opts=opts.AxisOpts(is_scale=True, splitarea_opts=opts.SplitAreaOpts(is_show=False, areastyle_opts=opts.AreaStyleOpts(opacity=1)),),
                datazoom_opts=[  # 缩放组件
                    opts.DataZoomOpts(is_show=False, type_="inside", xaxis_index=[0, 1], range_start=self.datazoom_start, range_end=100,),
                    opts.DataZoomOpts(is_show=True, xaxis_index=[0, 1], type_="slider", pos_top="bottom", range_start=self.datazoom_start, range_end=100,),
                ],
                tooltip_opts=opts.TooltipOpts(  # 提示框
                    trigger="axis",
                    axis_pointer_type="cross",
                    background_color="rgba(245, 245, 245, 0.8)",
                    border_width=1,
                    border_color="#ccc",
                    textstyle_opts=opts.TextStyleOpts(color="#000"),
                ),
                # brush_opts=opts.BrushOpts(x_axis_index="all", brush_link="all", out_of_brush={"colorAlpha": 0.1}, brush_type="lineX",),  # 刷选
                axispointer_opts=opts.AxisPointerOpts(is_show=True, link=[{"xAxisIndex": "all"}],),  # 光标
                # toolbox_opts=opts.ToolboxOpts(pos_left='75%', feature=opts.ToolBoxFeatureOpts(data_zoom={"show": False,})),
            )
        )

        ## 主图 分笔
        fbx, fby = get_fb_data(fb_df_slices)
        self.fb_line = (
            Line()
            .add_xaxis(xaxis_data=fbx)
            .add_yaxis(series_name="分笔", linestyle_opts=opts.LineStyleOpts(color='#d48265',), y_axis=fby)
            .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
        )

        rfbx, rfby = get_realtime_fb_data(fb_df_slices)
        self.realtime_fb_line = (
            Line()
            .add_xaxis(xaxis_data=rfbx)
            .add_yaxis(series_name="实时分笔", linestyle_opts=opts.LineStyleOpts(color='#d48265', type_='dashed',), y_axis=rfby)
            .set_series_opts(markpoint_opts=opts.MarkPointOpts(data=get_realtime_extreme_point(fb_df_slices), symbol='pin', symbol_size='30'),)  # 极端行情price2
            .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
        )

        ## 主图 线段
        xdx, xdy = get_xd_data(xd_df_slices)
        ls_mk_data = get_long_short_markarea_data(self.long_short_range)
        zs_data = get_zs(zs_df_slices)
        zs_data.extend(ls_mk_data)  # 中枢 + 多空区域
        self.xd_line = (
            Line()
            .add_xaxis(xaxis_data=xdx)
            .add_yaxis(series_name="线段", linestyle_opts=opts.LineStyleOpts(color='#2f4554',), y_axis=xdy,)
            .set_series_opts(
                markarea_opts=opts.MarkAreaOpts(data=zs_data,),  # 中枢 + 多空区域
                markpoint_opts=opts.MarkPointOpts(data=get_zs_high_low(zs_df_slices), symbol='arrow', symbol_size='10'),  # 中枢最高点最低点标记
                itemstyle_opts=opts.ItemStyleOpts(color='#2f4554',),
            )
            .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
        )

        ## 主图 实时线段
        rxdx, rxdy = get_realtime_xd_data(xd_df_slices)
        self.realtime_xd_line = (
            Line()
            .add_xaxis(xaxis_data=rxdx)
            .add_yaxis(series_name="实时线段", linestyle_opts=opts.LineStyleOpts(color='#2f4554', type_='dashed',), y_axis=rxdy,)
            .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
        )

        ## 幅图1 macd数据
        dif, dea, macd = get_macd_data(data_df_slices)
        self.macd_bar = (
            Bar()
            .add_xaxis(xaxis_data=[t for t, v in macd])
            .add_yaxis(series_name='macd', yaxis_data=get_macd_yaxis_data(macd))
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(type_="category", axislabel_opts=opts.LabelOpts(is_show=False),),  # 不限显示刻度标签（时间）
                legend_opts=opts.LegendOpts(is_show=False),  # 不显示图例
            )
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))  # 不显示标记
        )
        # # 幅图1 dif dea
        self.macd_line = (
            Line()
            .add_xaxis(xaxis_data=[t for t, v in dea])
            .add_yaxis(
                series_name="dea",
                y_axis=[v for t, v in dea],
                is_smooth=True,
                label_opts=opts.LabelOpts(is_show=False),
                linestyle_opts=opts.LineStyleOpts(color="#0484E8"),
                is_symbol_show=False,
            )
            .add_yaxis(
                series_name="dif",
                y_axis=[v for t, v in dif],
                is_smooth=True,
                label_opts=opts.LabelOpts(is_show=False),
                linestyle_opts=opts.LineStyleOpts(color="#E7DA05"),
                is_symbol_show=False,
            )
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(type_="category", axislabel_opts=opts.LabelOpts(is_show=False),),  # 不限显示刻度标签（时间）
                legend_opts=opts.LegendOpts(is_show=False),  # 不显示图例
            )
        )

        ## 幅图2 natr
        natr = get_natr_data(data_df_slices)
        self.natr_line = (
            Line()
            .add_xaxis(xaxis_data=[t for t, v in natr])
            .add_yaxis(
                series_name="natr",
                y_axis=[v for t, v in natr],
                is_smooth=True,
                label_opts=opts.LabelOpts(is_show=False),
                linestyle_opts=opts.LineStyleOpts(color="#0484E8"),
                is_symbol_show=False,
            )
            .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category",), legend_opts=opts.LegendOpts(is_show=False),)  # 不显示图例
        )

        ## 幅图2 dailyk
        dailyk = get_rizhou_data_dailyk(rizhou_df_slices)
        self.dailyk_line = (
            Line()
            .add_xaxis(xaxis_data=[t for t, v in dailyk])
            .add_yaxis(
                series_name="dailyk",
                y_axis=[v for t, v in dailyk],
                is_smooth=True,
                label_opts=opts.LabelOpts(is_show=False),
                linestyle_opts=opts.LineStyleOpts(color="#ec0000"),
                is_symbol_show=False,
            )
            .set_series_opts(markline_opts=opts.MarkLineOpts(is_silent=True, data=[{'yAxis': 0}, {'yAxis': 100}]))
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(type_="category", axislabel_opts=opts.LabelOpts(is_show=False),),  # 不限显示刻度标签（时间）
                legend_opts=opts.LegendOpts(is_show=False),  # 不显示图例
            )
        )
        ## 幅图2 weekk
        weekk = get_rizhou_data_weekk(rizhou_df_slices)
        self.weekk_line = (
            Line()
            .add_xaxis(xaxis_data=[t for t, v in weekk])
            .add_yaxis(
                series_name="weekk",
                y_axis=[v for t, v in weekk],
                is_smooth=True,
                label_opts=opts.LabelOpts(is_show=False),
                linestyle_opts=opts.LineStyleOpts(color="#ffa500"),
                is_symbol_show=False,
            )
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(type_="category", axislabel_opts=opts.LabelOpts(is_show=False),),  # 不限显示刻度标签（时间）
                legend_opts=opts.LegendOpts(is_show=False),  # 不显示图例
            )
        )

        xdata, ydata = get_scatter_points_data(points_slices, 'bl')
        if xdata:
            self.scatter_point_bl = (
                Scatter()
                .add_xaxis(xdata)
                .add_yaxis(
                    series_name='开多',
                    y_axis=ydata,
                    label_opts=opts.LabelOpts(
                        is_show=True,
                        formatter=JsCode("function(params){return params.value[2] + ' : ' + params.value[1];}"),
                        position='bottom',
                        color='#9c009c',
                    ),
                    color='#9c009c',
                    symbol='triangle',
                    symbol_rotate=0,
                    itemstyle_opts=opts.ItemStyleOpts(color='#9c009c'),
                )
            )

        xdata, ydata = get_scatter_points_data(points_slices, 'bs')
        if xdata:
            self.scatter_point_bs = (
                Scatter()
                .add_xaxis(xdata)
                .add_yaxis(
                    series_name='开空',
                    y_axis=ydata,
                    label_opts=opts.LabelOpts(
                        is_show=True, formatter=JsCode("function(params){return params.value[2] + ' : ' + params.value[1];}"), position='top', color='#006600',
                    ),
                    color='#006600',
                    symbol='arrow',
                    symbol_rotate=180,
                    itemstyle_opts=opts.ItemStyleOpts(color='#006600'),
                )
            )

        xdata, ydata = get_scatter_points_data(points_slices, 'sl')
        if xdata:
            self.scatter_point_sl = (
                Scatter()
                .add_xaxis(xdata)
                .add_yaxis(
                    series_name='平多',
                    y_axis=ydata,
                    label_opts=opts.LabelOpts(
                        is_show=True, formatter=JsCode("function(params){return params.value[2] + ' : ' + params.value[1];}"), position='top', color='#9c009c',
                    ),
                    color='#9c009c',
                    symbol='triangle',
                    symbol_rotate=180,
                )
            )

        xdata, ydata = get_scatter_points_data(points_slices, 'ss')
        if xdata:
            self.scatter_point_ss = (
                Scatter()
                .add_xaxis(xdata)
                .add_yaxis(
                    series_name='平空',
                    y_axis=ydata,
                    label_opts=opts.LabelOpts(
                        is_show=True,
                        formatter=JsCode("function(params){return params.value[2] + ' : ' + params.value[1];}"),
                        position='bottom',
                        color='#006600',
                    ),
                    color='#006600',
                    symbol='arrow',
                    symbol_rotate=0,
                )
            )

        ## 反转点连线
        rxdx, rxdy = get_xd_reverse_data(xd_reverse_points)
        if rxdx:
            self.xd_reverse_line = (
                Line()
                .add_xaxis(xaxis_data=rxdx)
                .add_yaxis(
                    series_name="反转点",
                    linestyle_opts=opts.LineStyleOpts(
                        # color='#2f4554',
                        type_='dashed',
                    ),
                    is_step='end',
                    y_axis=rxdy,
                )
                .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
            )

        ## 正向点连线
        rxdx, rxdy = get_xd_reverse_data(xd_forward_points)
        if rxdx:
            self.xd_forward_line = (
                Line()
                .add_xaxis(xaxis_data=rxdx)
                .add_yaxis(
                    series_name="正向点",
                    linestyle_opts=opts.LineStyleOpts(
                        # color='#2f4554',
                        type_='dashed',
                    ),
                    is_step='end',
                    y_axis=rxdy,
                )
                .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
            )

        ## macd标准模型-红柱标记
        xdata, ydata = get_macd_extremum_point(self.macd_normalized_df, 1)
        self.macd_normalized_scatter_red = (
            Scatter()
            .add_xaxis(xdata)
            .add_yaxis(
                series_name='macd标准模型',
                y_axis=ydata,
                label_opts=opts.LabelOpts(is_show=True, formatter=JsCode("function(params){return params.value[2];}"), position='top', color='#ef232a',),
                itemstyle_opts=opts.ItemStyleOpts(color='#ef232a'),
                symbol='circle',
                symbol_size=1,
                symbol_rotate=0,
            )
        )
        ## macd标准模型-绿柱标记
        xdata, ydata = get_macd_extremum_point(self.macd_normalized_df, -1)
        self.macd_normalized_scatter_green = (
            Scatter()
            .add_xaxis(xdata)
            .add_yaxis(
                series_name='macd标准模型',
                y_axis=ydata,
                label_opts=opts.LabelOpts(is_show=True, formatter=JsCode("function(params){return params.value[2];}"), position='bottom', color='#14b143',),
                itemstyle_opts=opts.ItemStyleOpts(color='#14b143'),
                symbol='circle',
                symbol_size=1,
                symbol_rotate=0,
            )
        )

        # 目标点
        xdata, ydata = get_scatter_target_point_data(target_point_slices)
        if xdata:
            self.scatter_target_point = (
                Scatter()
                .add_xaxis(xdata)
                .add_yaxis(
                    series_name='目标点',
                    y_axis=ydata,
                    label_opts=opts.LabelOpts(formatter=JsCode("function(params){return params.value[1];}"), position='top', color='#ffa500',),
                    color='#ffa500',
                    symbol='circle',
                    symbol_rotate=0,
                    symbol_size=5,
                )
            )

        xdata, ydata = get_scatter_rizhou_signal_data(rizhou_signal_slices, 1)
        if xdata:
            self.scatter_rizhou_signal_long = (
                Scatter()
                .add_xaxis(xdata)
                .add_yaxis(
                    series_name='日周多',
                    y_axis=ydata,
                    # label_opts=opts.LabelOpts(formatter=JsCode("function(params){return params.value[1];}"), position='top', color='#5c50e6',),
                    color='#f200ff',
                    symbol='diamond',
                    symbol_rotate=0,
                    symbol_size=15,
                )
            )
        xdata, ydata = get_scatter_rizhou_signal_data(rizhou_signal_slices, -1)
        if xdata:
            self.scatter_rizhou_signal_short = (
                Scatter()
                .add_xaxis(xdata)
                .add_yaxis(
                    series_name='日周空',
                    y_axis=ydata,
                    # label_opts=opts.LabelOpts(formatter=JsCode("function(params){return params.value[1];}"), position='top', color='#007aff',),
                    color='#0000ff',
                    symbol='diamond',
                    symbol_rotate=0,
                    symbol_size=15,
                )
            )

        ## ma
        if ma_df_slices is not None:
            ## ma5
            maxdx, maxdy = get_ma_data(ma_df_slices.ma5)
            self.ma_line_5 = (
                Line()
                .add_xaxis(xaxis_data=maxdx)
                .add_yaxis(
                    series_name="MA5",
                    linestyle_opts=opts.LineStyleOpts(
                        # color='#2f4554',
                        type_='dashed',
                    ),
                    label_opts=opts.LabelOpts(is_show=False),
                    is_symbol_show=False,
                    y_axis=maxdy,
                )
                .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
            )

            ## ma10
            maxdx, maxdy = get_ma_data(ma_df_slices.ma10)
            self.ma_line_10 = (
                Line()
                .add_xaxis(xaxis_data=maxdx)
                .add_yaxis(
                    series_name="MA10",
                    linestyle_opts=opts.LineStyleOpts(
                        # color='#2f4554',
                        type_='dashed',
                    ),
                    label_opts=opts.LabelOpts(is_show=False),
                    is_symbol_show=False,
                    y_axis=maxdy,
                )
                .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
            )

        ## 净值
        if nav_df_slices is not None:
            self.nav_line = (
                Line()
                .add_xaxis(xaxis_data=list(nav_df_slices.index))
                .add_yaxis(
                    series_name="净值",
                    xaxis_index=0,
                    yaxis_index=3,
                    linestyle_opts=opts.LineStyleOpts(
                        # color='#2f4554',
                        type_='dashed',
                    ),
                    label_opts=opts.LabelOpts(is_show=False),
                    is_symbol_show=False,
                    y_axis=list(nav_df_slices.nav),
                )
            )

        # 模拟买卖点-开多
        xdata, ydata = get_scatter_points_data(second_type_bs_point_slices, 'bl')
        if xdata:
            self.scatter_second_type_bs_point_bl = (
                Scatter()
                .add_xaxis(xdata)
                .add_yaxis(
                    series_name='模拟多',
                    y_axis=ydata,
                    # label_opts=opts.LabelOpts(
                    #     is_show=True, formatter=JsCode("function(params){return params.value[2] + ' : ' + params.value[1];}"), position='bottom', color='#9c009c',
                    # ),
                    color='#9c009c',
                    symbol='circle',
                    symbol_rotate=0,
                    itemstyle_opts=opts.ItemStyleOpts(color='#9c009c'),
                )
            )
        # 模拟买卖点-开空
        xdata, ydata = get_scatter_points_data(second_type_bs_point_slices, 'bs')
        if xdata:
            self.scatter_second_type_bs_point_bs = (
                Scatter()
                .add_xaxis(xdata)
                .add_yaxis(
                    series_name='模拟空',
                    y_axis=ydata,
                    # label_opts=opts.LabelOpts(
                    #     is_show=True, formatter=JsCode("function(params){return params.value[2] + ' : ' + params.value[1];}"), position='top', color='#006600',
                    # ),
                    color='#006600',
                    symbol='circle',
                    itemstyle_opts=opts.ItemStyleOpts(color='#006600'),
                )
            )

    # 主图
    def __get_main_chart(self):
        overlap = self.kline.overlap(self.fb_line)
        overlap = overlap.overlap(self.realtime_fb_line)
        overlap = overlap.overlap(self.xd_line)
        overlap = overlap.overlap(self.realtime_xd_line)
        if self.scatter_point_bl is not None:
            overlap = overlap.overlap(self.scatter_point_bl)
        if self.scatter_point_bs is not None:
            overlap = overlap.overlap(self.scatter_point_bs)
        if self.scatter_point_sl is not None:
            overlap = overlap.overlap(self.scatter_point_sl)
        if self.scatter_point_ss is not None:
            overlap = overlap.overlap(self.scatter_point_ss)
        if self.xd_reverse_line is not None:
            overlap = overlap.overlap(self.xd_reverse_line)
        if self.xd_forward_line is not None:
            overlap = overlap.overlap(self.xd_forward_line)
        if self.scatter_target_point is not None:
            overlap = overlap.overlap(self.scatter_target_point)
        if self.scatter_rizhou_signal_long is not None:
            overlap = overlap.overlap(self.scatter_rizhou_signal_long)
        if self.scatter_rizhou_signal_short is not None:
            overlap = overlap.overlap(self.scatter_rizhou_signal_short)
        if self.ma_line_5 is not None:
            overlap = overlap.overlap(self.ma_line_5)
        if self.ma_line_10 is not None:
            overlap = overlap.overlap(self.ma_line_10)
        if self.scatter_second_type_bs_point_bl is not None:
            overlap = overlap.overlap(self.scatter_second_type_bs_point_bl)
        if self.scatter_second_type_bs_point_bs is not None:
            overlap = overlap.overlap(self.scatter_second_type_bs_point_bs)
        return overlap

    # 幅图1
    def __get_macd_chart(self):
        overlap1 = self.macd_line.overlap(self.macd_bar)
        overlap1 = overlap1.overlap(self.macd_normalized_scatter_red)
        overlap1 = overlap1.overlap(self.macd_normalized_scatter_green)
        return overlap1

    # 幅图2
    def __get_natr_chart(self):
        return self.natr_line

    # 幅图2
    def __get_rizhou_chart(self):
        overlap2 = self.dailyk_line.overlap(self.weekk_line)
        return overlap2

    # 暴露Grid
    def get_grid(self):
        if self.grid_width and self.grid_height:
            grid = Grid(init_opts=opts.InitOpts(width=self.grid_width, height=self.grid_height))  # 设置容器宽高
        else:
            grid = Grid()

        main_ov = self.__get_main_chart()
        macd_ov = self.__get_macd_chart()
        natr_ov = self.__get_natr_chart()
        rizhou_ov = self.__get_rizhou_chart()

        if self.minor_draw:
            if 'macd' in self.minor_draw and 'rizhou' in self.minor_draw:
                grid.add(main_ov, grid_opts=opts.GridOpts(pos_left="left", pos_top='10%', pos_right='50px', height="50%"))
                grid.add(macd_ov, grid_opts=opts.GridOpts(pos_left="left", pos_top='60%', pos_right='50px', height="15%"))
                grid.add(rizhou_ov, grid_opts=opts.GridOpts(pos_left="left", pos_top='75%', pos_right='50px', height="15%"))
            else:
                grid.add(main_ov, grid_opts=opts.GridOpts(pos_left="left", pos_top='10%', pos_right='50px', height="60%"))
                if 'macd' == self.macd_or_natr:
                    grid.add(macd_ov, grid_opts=opts.GridOpts(pos_left="left", pos_top='70%', pos_right='50px', height="20%"))
                elif 'natr' == self.macd_or_natr:
                    grid.add(natr_ov, grid_opts=opts.GridOpts(pos_left="left", pos_top='70%', pos_right='50px', height="20%"))
                elif 'rizhou' == self.macd_or_natr:
                    grid.add(rizhou_ov, grid_opts=opts.GridOpts(pos_left="left", pos_top='70%', pos_right='50px', height="20%"))
        else:
            grid.add(main_ov, grid_opts=opts.GridOpts(pos_left="left", pos_top='10%', pos_right='50px', height="60%"))
            if 'macd' == self.macd_or_natr:
                grid.add(macd_ov, grid_opts=opts.GridOpts(pos_left="left", pos_top='70%', pos_right='50px', height="20%"))
            elif 'natr' == self.macd_or_natr:
                grid.add(natr_ov, grid_opts=opts.GridOpts(pos_left="left", pos_top='70%', pos_right='50px', height="20%"))
            elif 'rizhou' == self.macd_or_natr:
                grid.add(rizhou_ov, grid_opts=opts.GridOpts(pos_left="left", pos_top='70%', pos_right='50px', height="20%"))

        return grid
