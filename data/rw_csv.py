
import csv

# 名前付きタプル
from collections import namedtuple

try:
    from itertools import imap
except ImportError:  # Python 3
    imap = map

# with open('data.csv') as fp:
#     lst = list(csv.reader(fp))


def write_data(fname, data):

    with open(fname, 'w') as f:
        writer = csv.writer(f, lineterminator='\n')  # 改行コード（\n）を指定しておく
        # writer.writerow(list)     # list（1次元配列）の場合
        writer.writerows(data)    # 2次元配列も書き込める


def read_data(fname, data):

    with open(fname, 'r') as f:
        reader = csv.reader(f)
        # header = next(reader)  # ヘッダーを読み飛ばしたい時

        for row in reader:
            data.append(list(row))


def read_test():

    with open("data_file.txt", mode="rb") as infile:
        reader = csv.reader(infile)
        Data = namedtuple("Data", next(reader))  # get names from column headers
        for data in imap(Data._make, reader):
            print(data.foo)
