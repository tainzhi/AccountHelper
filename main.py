import os
import pandas as pd
import PySimpleGUI as sg
import threading
import util
from browser import TianYanCha
from browser import QiChaCha
import logging
import numpy as np
import traceback


def read_excel(excel_file):
    """
    读取excel, 调过第0,1 行, 提取列为 代码, 往来单位名称, 收件地址
    :param excel:
    :return:
    """
    read = pd.read_excel(excel_file, skiprows=[0, 1], usecols=['代码', '往来单位名称', '收件地址'], keep_default_na=False)
    # 获取所有的行,所有的列
    data = read.iloc[0:, 0:]
    # print("获取到所有的值:\n{0}".format(data))  # 格式化输出
    not_blank = []
    # 某些行读取的为Nan Nan Nan空行处理掉
    for item in data.values:
        if item[0] != '' and item[1] != '' and item[2] != '':
            not_blank.append(item)
    return not_blank


def write_excel(excel_file, window):
    util.thread_count -= 1
    if util.thread_count > 0:
        return
    read = pd.read_excel(excel_file, keep_default_na=False)
    # 获取所有的行,所有的列
    original_data = read.iloc[0:, 0:].values
    # 最后一列添加空格
    new_data = np.insert(original_data, np.size(original_data, 1), '', axis=1)
    new_data[1][7] = "new address"
    index = 2
    for com in original_data[2:]:
        # for net_company in [['S00001', "baidu.com"], ['S00002', "com.baidu.com"]]:
        for net_company in util.haven_dealed_companies:
            if com[1] == net_company[0]:
                new_data[index][7] = net_company[-1]
        index += 1
    writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
    pd.DataFrame(new_data).to_excel(writer, index=False)
    writer.save()


def handle_by_qcc(companies, window, result_list, excel_file):
    chrome = QiChaCha(window)
    all_count = len(companies)
    index = 0
    try:
        for com in companies:
            index += 1
            ret_com = chrome.check_and_screenshot(com)
            if len(ret_com) != 0:
                result_list.append(ret_com)
            index = update_progress_bar(window, ret_com)
            update_info(window, index, com)
    except Exception as e:
        logging.getLogger("main").error(e.args)
        logging.getLogger("main").error('=====================================')
        logging.getLogger("main").error(traceback.format_exc())
    finally:
        write_excel(excel_file, window)
        chrome.quit()


def handle_by_tianyancha(companies, window, result_list, excel_file):
    chrome = TianYanCha(window)
    index = 0
    try:
        for com in companies:
            index += 1
            ret_com = chrome.check_and_screenshot(com)
            if len(ret_com) != 0:
                result_list.append(ret_com)
            index = update_progress_bar(window, ret_com)
            update_info(window, index, com)
    except Exception as e:
        logging.getLogger("main").error(e.args)
        logging.getLogger("main").error('=====================================')
        logging.getLogger("main").error(traceback.format_exc())
    finally:
        write_excel(excel_file, window)
        chrome.quit()


def update_info(window, index, com):
    state_info = "第{index}公司，{code} {name}".format(index=index, code=com[0], name=com[1])
    logging.getLogger("main").info(state_info)
    window.write_event_value('-run-state-', state_info)


def update_progress_bar(window, company):
    util.mutex.acquire()
    util.g_count += 1
    # 只保存已经从网页中查找到公司
    if len(company) != 0:
        util.haven_dealed_companies.append(company)
    util.mutex.release()
    progress_bar = window['-progress-']
    progress_bar.UpdateBar(util.g_count * 100.0 / util.g_sum)
    return util.g_count


def handle(excel, window):
    try:
        companies = check(excel, window, False)
        # 登录企查查，并保存cookie
        qcc = QiChaCha(window)
        qcc.quit()
        # 登录天眼查，并保存cookie
        tianyancha = TianYanCha(window)
        tianyancha.quit()

        result_list = []
        # 企查查和天眼查两组
        splited_commpanes = util.Util.split_list_average_n(companies, util.thread_count)
        # 前 thread_count /2 组用 企查查查询
        # 后 thread_count /2 组用 天眼查查询
        index = 0
        for com in splited_commpanes:
            t = threading.Thread(
                target= handle_by_qcc if (index < util.thread_count / 2) else handle_by_tianyancha,
                args=(com, window, result_list, excel),
                # 开启daemon线程
                daemon=True
            )
            t.start()
            index += 1
    except Exception as e:
        logging.getLogger("main").error(e.args)
        logging.getLogger("main").error('=====================================')
        logging.getLogger("main").error(traceback.format_exc())


def check(excel, window, need_show_info):
    companies = read_excel(excel)
    util.g_sum = len(companies)
    # 已经处理的公司名单
    haven_dealed_companies_code = util.PathUtil.get_haven_delead_company_code()
    util.g_count = len(haven_dealed_companies_code)
    update_progress_bar(window, [])

    state_info = "总共 {all} 个公司， 已经处理截图了 {dealed} 个公司， 还有 {remain} 个公司待处理"\
        .format(all=len(companies), dealed=len(haven_dealed_companies_code), remain=len(companies) - len(haven_dealed_companies_code))
    logging.getLogger("main").info(state_info)
    window.write_event_value('-run-state-', state_info)

    new_companies = []
    for com in companies:
        if com[0] not in haven_dealed_companies_code:
            new_companies.append(com)
    if need_show_info:
        for com in new_companies:
            window.write_event_value('-run-state-', "未能处理的公司 {} {}".format(com[0], com[1]))
    return new_companies


def run_ui(config):
    sg.theme('Light Brown 3')
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon = os.path.join(current_dir, 'account.icon')
    layout = [
        [sg.Text("选择一个excel文件")],
        [sg.FileBrowse(key="-browse-", initial_folder=current_dir,
                       file_types=(("excel", "*.xlsx"), ("ALL Files", "*.xlsx"))),
         sg.Input(key="-browsed-excel-", size=(63, 1), change_submits=True, default_text=config.get_recent_excel())],
        [sg.Text("加速等级"), sg.InputCombo(key="-speed-", values=('normal', 'fast', 'faster'), size=(10, 3)),
         sg.Checkbox('是否截小图', size=(10, 5), default=True, key='-small-picture-')],
        [sg.Text("从第几行开始"),
         sg.Input(key='-start-row-', change_submits=True, size=(5, 1), justification='right', default_text='2')],
        [sg.Text("需要处理的列名称"),
         sg.Input(key='-col-0-', justification='center', size=(10, 1), pad=(1, 1), default_text="编号"),
         sg.Input(key='-col-1-', size=(10, 1), pad=(1, 1), justification='center', default_text="公司名称"),
         sg.Input(key='-col-2-', size=(10, 1), pad=(1, 1), justification='center', default_text="地址")],

        [sg.Button("开始", key='-start-'), sg.Button("检查", key='-check-')],
        [sg.Text("当前进度")],
        [sg.ProgressBar(100, orientation='h', size=(100, 20), key="-progress-")],
        [sg.Text("运行状态")],
        [sg.Multiline(key="-run-state-", default_text='---运行状态---', size=(70, 10), autoscroll=True)]
    ]
    window = sg.Window('财务助手', layout, size=(800, 600), icon=icon,
                       font=('Helvetica 18'),
                       default_element_size=(40, 1),
                       )
    last_run_state = '---运行状态---\n'
    while True:
        event, values = window.read()
        # 退出窗口程序
        if event == sg.WIN_CLOSED or event == "Exit":
            # 保存设置
            config.close()
            break
        # 选择excel后
        elif event == '-browsed-excel-' and values['-browsed-excel-'] is not None:
            # 保存最近的excel记录
            config.save_recent_excel(values['-browsed-excel-'])
        elif event == '-run-state-':
            window[event].update(last_run_state + values[event])
            last_run_state = last_run_state + values[event] + '\n'
        elif event == "-start-":
            excel_file = values["-browsed-excel-"]
            # 开启daemon线程
            thread = threading.Thread(
                target=handle,
                args=(excel_file, window,),
                daemon=True
            )
            thread.start()
        elif event == "-check-":
            excel_file = values["-browsed-excel-"]
            check(excel_file, window, True)


def test_no_ui():
    excel_file = './excels/被函证单位信息表（小康动力）.xlsx'
    write_excel(excel_file, None)


if __name__ == "__main__":
    util.Util.set_up_log_config()
    config = util.Config()
    run_ui(config)
    # test_no_ui()
