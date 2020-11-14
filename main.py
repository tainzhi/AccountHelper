import os
import pandas as pd
import PySimpleGUI as sg
import threading
import util
from browser import TianYanCha
from browser import QiChaCha


def read_excel(excel_file):
    """
    读取excel, 调过第0,1 行, 提取列为 代码, 往来单位名称, 收件地址
    :param excel:
    :return:
    """
    read = pd.read_excel(excel_file, skiprows=[0, 1], usecols=['代码', '往来单位名称', '收件地址'])
    # 获取所有的行,所有的列
    data = read.iloc[0:, 0:]
    # print("获取到所有的值:\n{0}".format(data))  # 格式化输出
    return data.values


def write_excel(companies):
    root_dir = os.path.dirname(os.path.abspath(__file__))
    excels_dir = os.path.join(root_dir, 'excels')
    writer = pd.ExcelWriter('result.xlsx', engine='xlsxwriter')
    pd.DataFrame(companies).to_excel(writer, sheet_name='new', index=False)
    writer.save()


def handle_by_qcc(companies, window, result_list):
    chrome = QiChaCha(window)
    all_count = len(companies)
    index = 0
    for com in companies:
        index += 1
        ret_com = chrome.check_and_screenshot(com)
        result_list.append(ret_com)
    # print('%{:.0f} 第{}个公司：{}'.format((index * 100.0 / all_count), index, com[2]))
    chrome.quit()


def handle_by_tianyancha(companies, window, result_list):
    chrome = TianYanCha(window)
    index = 0
    for com in companies:
        index += 1
        ret_com = chrome.check_and_screenshot(com)
        result_list.append(ret_com)
    # print('%{:.0f} 第{}个公司：{}'.format((index * 100.0 / all_count), index, com[2]))
    chrome.quit()


def handle(excel, window):
    companies = read_excel(excel)
    # 登录企查查，并保存cookie
    qcc = QiChaCha(window)
    qcc.quit()
    # 登录天眼查，并保存cookie
    tianyancha = TianYanCha(window)
    tianyancha.quit()

    result_list = []

    # 企查查和天眼查两组
    # 每组 thread_count 个线程
    list_count = util.thread_count * 2
    splited_commpanes = util.Util.split_list_average_n(companies, list_count)
    # 前 thread_count组用 企查查查询
    # 后 thread_count组用 天眼查查询
    index = 0
    for com in splited_commpanes:
        t = threading.Thread(
            target= handle_by_qcc if (index < util.thread_count) else handle_by_tianyancha,
            args=(com, window, result_list),
            # 开启daemon线程
            daemon=True
        )
        t.start()
        index += 1
    print(result_list)


def run_ui(config):
    sg.theme('Light Brown 3')
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon = os.path.join(current_dir, 'account.icon')
    layout = [
        [sg.Text("选择一个excel文件")],
        [sg.FileBrowse(key="-browse-", initial_folder=current_dir,
                       file_types=(("excel", "*.xlsx"), ("ALL Files", "*.xlsx"))),
         sg.Input(key="-browsed-excel-", size=(63, 1), change_submits=True, default_text=config.get_recent_excel())],
        [sg.Text("加速等级"), sg.InputCombo(values=('normal', 'fast', 'faster'), size=(10, 3)),
         sg.Checkbox('是否截小图', size=(10, 5), default=True)],
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


def test_no_ui():
    excel_file = './excels/被函证单位信息表（小康动力）.xlsx'
    content = read_excel(excel_file)
    print(content)


if __name__ == "__main__":
    util.Util.set_up_log_config()
    config = util.Config()
    run_ui(config)
