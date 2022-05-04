# -*- encoding: utf-8 -*-

import os


def fit(src_html_path, create_new_file=True):
    '''
    html文件自适应窗口大小
    '''
    target_path = src_html_path
    if create_new_file:
        target_path = '%s.replaced.html' % target_path

    file_src = open(src_html_path, "r")
    src_lines = file_src.readlines()
    chart_id = ''
    sec1_idx = -1
    sec2_idx = -1
    for idx, line in enumerate(src_lines):
        if chart_id == '' and line.find("class=\"chart-container\"") != -1:
            # print(line)
            first = line.find("\"")
            second = line.find("\"", first + 1)
            chart_id = line[first + 1 : second]
            # print(chart_id)
            continue
        if sec1_idx == -1 and line.find("echarts.init") != -1:
            # print(line)
            sec1_idx = idx
            continue
        if sec2_idx == -1 and line.find("setOption") != -1:
            # print(line)
            sec2_idx = idx
            break
    file_src.close()

    if sec1_idx == -1 or sec2_idx == -1:
        raise Exception('解析html错误')

    src_lines.insert(sec1_idx, sec1(chart_id=chart_id))
    src_lines.insert(sec2_idx + 2, sec2(chart_id=chart_id))

    file_target = open(target_path, "w")
    file_target.writelines(src_lines)
    file_target.close()


def sec1(chart_id):
    sec = (
        "/*sec1 start*/\n var worldMapContainer = document.getElementById('%s');\nworldMapContainer.style.width = window.innerWidth+'px';\nworldMapContainer.style.height = (window.innerHeight - 120)+'px';\n/*sec1 end*/\n"
        % (chart_id)
    )
    return sec


def sec2(chart_id):
    sec = "/*sec2 start*/\n window.onresize = function(){chart_%s.resize();}\n/*sec2 end*/\n" % chart_id
    return sec
