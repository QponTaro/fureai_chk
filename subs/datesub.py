# 日付操作系 ライブラリ
import datetime
import calendar
import jpholiday
#from dateutil.relativedelta import relativedelta
#import time

# static method

#@staticmethod
def cnv_datestr( datestr ):
    # 2019年6月8日 土曜日
    year  = datestr[2:datestr.find("年")]
    month = datestr[datestr.find("年")+1:datestr.find("月")]
    day   = datestr[datestr.find("月")+1:datestr.find("日")]
    week  = datestr[datestr.find("曜日")-1:].replace("曜日","")
    datestr2 = "{:02d}/{:02d}({})".format( int(month), int(day), week)
    return datestr2

def get_year( datestr ):
    # 2019年6月8日 土曜日
    year  = datestr[0:datestr.find("年")]
    return int(year)

def get_month( datestr ):
    # 2019年6月8日 土曜日
    month = datestr[datestr.find("年")+1:datestr.find("月")]
    return int(month)

def get_day( datestr ):
    # 2019年6月8日 土曜日
    day   = datestr[datestr.find("月")+1:datestr.find("日")]
    return int(day)

#@staticmethod
def dates(year, month, day):
    mr = calendar.monthrange(year, month)
    return range(day, mr[1] + 1)

#@staticmethod
def get_weekstr(year, month, day):
    d = datetime.datetime(year, month, day, 0, 0, 0)
    week = ["月", "火", "水", "木", "金", "土", "日"]
    return week[d.weekday()]

#@staticmethod
def chk_holiday(year, month, day):
    # 何もない日はNoneが帰ってくる
    h = jpholiday.is_holiday_name(datetime.date(year, month, day))
    return h