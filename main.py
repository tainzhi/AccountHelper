import os
import pandas as pd

import chrome


def select_excel():
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
    choose_index = -1
    while True:
        choose_index = input("请输入数字选择:\n")
        choose_index = int(choose_index)
        if choose_index < 0 or choose_index >= len(excels):
            print("请输入正确的数字选择:\n")
        else:
            break
    return excels[choose_index]


def read_excel(excel):
    read = pd.read_excel(excel)
    # 从第2行开始， 获取每行的第3列， 序号，代码，单位，收件地址
    data = read.iloc[2:,[0,1,2,3]]
    # print("获取到所有的值:\n{0}".format(data))  # 格式化输出
    return data.values

def write_excel():
    writer = pd.ExcelWriter('new_name.xlsx', engine='xlsxwriter')
    df1 = pd.DataFrame({'Names': ['Andreas', 'George', 'Steve',
                                  'Sarah', 'Joanna', 'Hanna'],
                        'Age': [21, 22, 20, 19, 18, 23]})

    df2 = pd.DataFrame({'Names': ['Pete', 'Jordan', 'Gustaf',
                                  'Sophie', 'Sally', 'Simone'],
                        'Age': [22, 21, 19, 19, 29, 21]})

    df3 = pd.DataFrame({'Names': ['Ulrich', 'Donald', 'Jon',
                                  'Jessica', 'Elisabeth', 'Diana'],
                        'Age': [21, 21, 20, 19, 19, 22]})

    dfs = {'Group1': df1, 'Group2': df2, 'Group3': df3}
    writer = pd.ExcelWriter('NamesAndAges.xlsx', engine='xlsxwriter')

    for sheet_name in dfs.keys():
        dfs[sheet_name].to_excel(writer, sheet_name=sheet_name, index=False)
    writer.save()


if __name__ == "__main__":
    excel = select_excel()
    companies = read_excel(excel)
    chrome = chrome.Chrome('https://www.tianyancha.com/')
    for com in companies:
        chrome.save_pic(com)
    chrome.quit()

