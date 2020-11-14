import os
import pandas as pd
from chrome import Chrome
import PySimpleGUI as sg
import threading
import util
import logging


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


def process_by_thread(companies, window):
    chrome = Chrome('https://www.tianyancha.com/', window)
    all_count = len(companies)
    index = 0
    for com in companies:
        index += 1
        ret_com = chrome.save_pic(util.Util.get_save_picture_dir(), com)
    # print('%{:.0f} 第{}个公司：{}'.format((index * 100.0 / all_count), index, com[2]))
    chrome.quit()


def thread_processing(excel, window):
    companies = read_excel(excel)
    # 登录，并保存cookie
    chrome = Chrome('https://www.tianyancha.com/', window)
    chrome.quit()
    # processed = []
    # processed.append(ret_com)
    # write_excel(processed)
    thread_count = 4
    splited_commpanes = util.Util.split_list_average_n(companies, thread_count)
    threads = []
    # 开启daemon线程
    for com in splited_commpanes:
        t = threading.Thread(
            target=process_by_thread,
            args=(com, window,),
            daemon=True
        )
        threads.append(t)
        t.start()


def process(excel_file, window):
    companies = read_excel(excel_file)
    chrome = Chrome('https://www.tianyancha.com/', window)
    processed = []
    all_count = len(companies)
    index = 0
    for com in companies:
        index += 1
        ret_com = chrome.save_pic(util.PathUtil.get_save_picture_dir(), com)
        print('%{:.0f} 第{}个公司：{}'.format((index * 100.0 / all_count), index, com[2]))
        processed.append(ret_com)
    write_excel(processed)
    chrome.quit()


def run_ui():
    logging.debug("run_ui")
    sg.theme('Light Brown 3')
    menu_def = [['&File', ['&Open', '&Save', 'E&xit', 'Properties']],
                ['&Edit', ['Paste', ['Special', 'Normal', ], 'Undo'], ], ['&Help', '&About...'], ]
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon = os.path.join(current_dir, 'account.icon')
    layout = [
        [sg.Menu(menu_def, tearoff=True)],
        [sg.Text("选择一个excel文件", size=(14, 1), font=('Helvetica 30')),
         sg.Input(key="-IN2-", size=(20, 10), font=('Helvetica 30'), change_submits=True),
         sg.FileBrowse(key="-IN-", initial_folder=current_dir,
                       file_types=(("excel", "*.xlsx"), ("ALL Files", "*.xlsx")))],
        [sg.Button("开始", key='Go')],
        [sg.Text(size=(35, 1), key='-STATE-')],
    ]
    window = sg.Window('财务助手', layout, size=(1000, 800), icon=icon,
                       no_titlebar=True,
                       default_element_size=(40, 1),
                       )
    while True:
        event, values = window.read()
        print(values["-IN2-"])
        if event == sg.WIN_CLOSED or event == "Exit":
            break
        elif event == '-Chrome State-':
            window['-STATE-'].update(values[event])
        elif event == "Go":
            excel_file = values["-IN-"]
            # 开启daemon线程
            thread = threading.Thread(
                target=process,
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
    run_ui()
