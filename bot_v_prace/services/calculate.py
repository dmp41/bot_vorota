import csv
import os
import math
fl_name='prace.csv'
def coordin_prace(fl_name):
    with open(fl_name, encoding='utf-8') as csv_file:
        # считываем содержимое файла
        text = csv_file.readlines()
        # создаем reader объект и указываем в качестве разделителя символ ;
        rows = csv.reader(text, delimiter=',')
        # выводим каждую строку
        rows = list(rows)[1:20]
    long=rows[0][1:] #список значений длин в мм
    hight={i[0]:i[1:]for i in rows[1:]} # словарь высота : список цен (находим нужную по индексу длины)

    return hight,long


def prace(lg,ht):
    lg=str(math.ceil(int(lg)/100)*100)
    ht=str(math.ceil(int(ht)/100)*100)
    return pr_or[0][ht][pr_or[1].index(lg)]

pr_or=coordin_prace(os.path.join(os.getcwd(), fl_name))