# 日付操作系 ライブラリ
import time

# WebDriver系
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_binary  # Adds chromedriver binary to path

import subs.datesub as datesub

# data, 辞書 インポート
import data.data as data
import data.data as dic
from data.data import room_data, room_datum

# 抽選予約情報 収集
def get_rsv_list(self):
    result_msg = ""

    for login_name in dic.card_ID:

        # ログイン
        result_msg += self._login(login_name)

        # ログインできなかったら コンティニュー
        if self.login_state == False:
            continue

        # 抽選申し込み状況・結果確認
        result_msg += _get_rsv_data(self, login_name)

        # 最後にログオフ
        result_msg += self._logoff()

    return result_msg

# 予約情報 収集
def _get_rsv_data( self, username ):

    result_msg = ""

    # ======= 抽選確認ループ =======

    # login時に 取得した申し込み数を取得
    rsvCount = dic.card_RSV[username]

    # 指定された 施設 の予約状況を確認
    url = "https://www.fureai-net.city.kawasaki.jp/user/view/user/rsvStatusList.html"
    self.driver.get(url)

    for page_offset in range(0, int(rsvCount), 5) :

        # 次の5件
        script_str = "javascript:$('offset').value = "
        script_str += str(page_offset)
        script_str += ";doSubmit('childForm', 'doPager');return false"

        self.driver.execute_script( script_str )
        # self.driver.execute_script("javascript:$('offset').value = 5;doSubmit('childForm', 'doPager');return false")

        print('[Page]{}/{}'.format(page_offset, rsvCount))

        # id="headerCount" # 26件

        # 予約テーブルの取得
        # 予約状況の取得
        #  class:'time-table1' は見出し行、'time-table2' は 予約状況
        table_elems = self.driver.find_elements_by_class_name("tablebg2")
        for table in table_elems:
            if not (("利用日時" in table.text)or("希望日時" in table.text)):
                continue

            # このテーブルだ！
            # テーブルの行単セットをまず取得
            trs = table.find_elements( By.TAG_NAME, 'tr' )
            for row in range( 1, len(trs) ):
                tr = trs[row]
                if tr.text == "":
                    continue

                # 5つの td で構成。0:午前, 1:午後, 2:夜
                #   利用日時, 館名／施設名, 館情報, 支払状況, 詳細内容
                ymd   = tr.find_element( By.ID, 'ymdLabel').text
                stime = tr.find_element( By.ID, 'stimeLabel').text
                etime = tr.find_element( By.ID, 'etimeLabel').text
                bname = tr.find_element( By.ID, 'bnamem').text
                iname = tr.find_element( By.ID, 'inamem').text
                state = tr.find_element( By.ID, 'stateLabel').text

                # ymd から y,m,d,w を取得
                year = datesub.get_year(ymd)
                month = datesub.get_month(ymd)
                day = datesub.get_day(ymd)
                week = datesub.get_weekstr(year,month,day)

                ymd = datesub.cnv_datestr(ymd)
                stime = stime.replace("時","")
                etime = etime.replace("時","")
                bname = bname.replace("市民館","")
                bname = bname.replace("分館","")
                iname = iname.replace("教室","")
                iname = iname.replace("室","")

                # よりよい場所があれば... レベル
                roomName = bname+"／"+iname
                rank = dic.chorus_ROOM[ roomName ]

                print( "日時：{}[{}~{}], 施設:{}/{}, 支払:{}".format( ymd,stime,etime,bname,iname,state ))

                # リストに追加
                #room_stat.append([curYear, curMonth, curDay, curWeek, room_str, rsvStat])
                #room_dataat = namedtuple('room_dataat', ('year', 'month', 'day', 'week', 'room', 'am', 'pm', 'night'))

                #('username','year', 'month', 'day', 'week', 'start','end','bname', 'iname', 'am', 'pm', 'night','rank')
                room_data.append(
                    room_datum(
                        type = '予約',
                        username = username,  # username
                        year = year,
                        month = month,
                        day = day,
                        week = week,
                        start = stime,
                        end = etime,
                        bname = bname,
                        iname = iname,
                        state = state,
                        am = '',
                        pm = '',
                        night = '',
                        rank = rank,
                        Tmanabu = '',
                        Tsato = '',
                        Tniimi = '',
                        Ttamamura = ''
                        )
                    )

                #print( room_data[-1] )

    return result_msg
