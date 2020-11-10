import os
import pandas as pd
from platform import system
from chrome import Chrome


def select_excel():
    """
    从当前目录 excels/ 下选取一个 xls
    :return:
    """
    root_dir = os.path.dirname(os.path.abspath(__file__))
    excels_dir = os.path.join(root_dir, 'excels')
    excels = []
    for file in os.listdir(excels_dir):
        file_path = os.path.join(excels_dir, file)
        if os.path.isfile(file_path):
            excels.append(file_path)
    if len(excels) > 0:
        print("选择要处理的excel：\n")
        for i in range(0, len(excels)):
            print("{index}: {file}\n".format(index=i, file=os.path.basename(excels[i])))
    while True:
        choose_index = input("请输入数字选择:\n")
        choose_index = int(choose_index)
        if choose_index < 0 or choose_index >= len(excels):
            print("请输入正确的数字选择:\n")
        else:
            break
    return excels[choose_index]


def read_excel(excel):
    """
    读取excel
    :param excel:
    :return:
    """
    read = pd.read_excel(excel)
    # 从第2行开始， 获取每行的每列
    data = read.iloc[2:-1, 0:-1]
    # print("获取到所有的值:\n{0}".format(data))  # 格式化输出
    return data.values


def get_save_png_dir():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = 'picture'
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    return os.path.join(root_dir, base_dir)
    

def write_excel(companies):
    root_dir = os.path.dirname(os.path.abspath(__file__))
    excels_dir = os.path.join(root_dir, 'excels')
    writer = pd.ExcelWriter('result.xlsx', engine='xlsxwriter')
    pd.DataFrame(companies).to_excel(writer, sheet_name='new', index=False)
    writer.save()


def get_driver_location():
    """
    不要挪到Chrome.class中， 因为通过pyinstaller打包成单个exe文件后，会使用temp路径
    最终导致取不到drvier路径
    :return:
    """
    os_type = system()
    root_dir = os.path.dirname(os.path.abspath(__file__))
    drivers_dir = os.path.join(root_dir, 'drivers')
    if os_type == 'Darwin':
        return os.path.join(drivers_dir, 'chromedriver_mac64')
    elif os_type == 'Windows':
        return os.path.join(drivers_dir, 'chromedriver_win32.exe')
    elif os_type == 'Linux':
        return os.path.join(drivers_dir, 'chromedriver_linux64')
    else:
        print('不支持的系统类型！')
        exit(-1)


if __name__ == "__main__":
    excel = select_excel()
    companies = read_excel(excel)
    chrome = Chrome(get_driver_location(), 'https://www.tianyancha.com/')
    processed = []
    all_count = len(companies)
    index = 0
    for com in companies:
        index += 1
        ret_com = chrome.save_pic(get_save_png_dir(), com)
        print('%{:.0f} 第{}个公司：{}'.format((index * 100.0 / all_count), index, com[2]))
        processed.append(ret_com)
    write_excel(processed)
    chrome.quit()
