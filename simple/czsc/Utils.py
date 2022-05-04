# -*- encoding: utf-8 -*-


def find_highest_point(index1, index2, k_df, reverse=True):
    tmp_df = k_df.loc[index1:index2, 'high'].infer_objects()
    if reverse:
        tmp_df.sort_index(inplace=True, ascending=False)
    max_price = tmp_df.max()
    max_time = tmp_df.idxmax()
    return [max_time, max_price]


def find_lowest_point(index1, index2, k_df, reverse=True):
    tmp_df = k_df.loc[index1:index2, 'low'].infer_objects()
    if reverse:
        tmp_df.sort_index(inplace=True, ascending=False)
    min_price = tmp_df.min()
    min_time = tmp_df.idxmin()
    return [min_time, min_price]

