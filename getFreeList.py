# 日付操作系 ライブラリ
import time
import datetime
from dateutil.relativedelta import relativedelta

# WebDriver系
# from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# import chromedriver_binary  # Adds chromedriver binary to path

import subs.datesub as datesub

# data, 辞書 インポート
import data.data as data
import data.data as dic
from data.data import room_data, room_datum
from data.data import chk_date, chk_datum


def make_chk_date_list():

    # 今日の日付を取得
    today = datetime.datetime.now()

    # 【開始日】
    #  今日の翌々月1日
    date_from = (today + relativedelta(months=2)).replace(day=1)

    # 【終了日】
    # 23日-30/31までは、４か月後の月末
    # 1日～28日までは 3カ月後の月末

    if today.day >= 17:
        addMonth = 5
    else:
        addMonth = 4

    # date_to = (today + relativedelta(months=addMonth)
    #             ).replace(day=1) - datetime.timedelta(days=1)
    date_to = (today + relativedelta(months=addMonth))

    lst = []
    for room in dic.check_ROOMs:

        # === 日付ループ ===
        t = date_from
        while t <= date_to:

            curWeek = datesub.get_weekstr(t.year, t.month, t.day)
            curHoliday = datesub.chk_holiday(t.year, t.month, t.day)

            # 土日祝 以外は対象外
            if ((curWeek in {"土", "日"}) or (curHoliday is not None)):

                lst.append(chk_datum(t.year, t.month, t.day, curWeek, room))

            t += datetime.timedelta(days=1)

    return lst


def chk_free_room(self, lst):
    result_msg = ""

    lstRoom = ""
    for tgt in lst:

        # 施設指定
        curRoom = tgt.room
        curYear = tgt.year
        curMonth = tgt.month
        curDay = tgt.day
        curWeek = tgt.week

        if curRoom != lstRoom:
            # 指定された 施設 の予約状況を確認
            url = "https://www.fureai-net.city.kawasaki.jp/user/view/user/homeIndex.html"
            self.driver.get(url)

            url = "https://www.fureai-net.city.kawasaki.jp/user/view/user/rsvNameSearch.html"
            self.driver.get(url)

            icd = dic.room_icd[curRoom]
            bname = curRoom.split('／')[0]
            iname = curRoom.split('／')[1]
            if "岡上" in bname:
                bname_key = bname + "分館"
            elif "サンピアン" in bname:
                bname_key = bname
            elif "教育文化" in bname:
                bname_key = bname
            else:
                bname_key = bname + "市民館"

            # vvv ちょっと待ってからスクリプト実行
            self.wait.until(EC.presence_of_element_located(
                (By.ID, "textKeyword")))
            self.driver.find_element_by_id('textKeyword').send_keys(bname_key)

            self.driver.execute_script("javascript:eventOnLoad()")
            # self.driver.find_element_by_id('doSearch').submit()
            self.driver.find_element_by_id('doSearch').click()

            self.driver.execute_script("javascript:eventOnLoad()")
            self.driver.find_element_by_id('doSelect').click()
            # self.driver.execute_script( "javascript:this.form.bcd.value = '1240';return true;")

            # チェックを全て解除
            self.driver.execute_script(
                "javascript:doCheck(false);return false;")
            # 特定の施設だけチェック

            chkboxs = self.driver.find_elements_by_name(
                'layoutChildBody:childForm:selectIcd')
            for chkbox in chkboxs:  # チェックボックスリストの中から該当する施設だけチェックする

                chkboxicd = chkbox.get_attribute("value")
                # print("icd:{}, chkboxicd:{}".format(icd,chkboxicd))

                if icd == chkboxicd:
                    print(bname, iname)
                    chkbox.click()

            # 表示の繁栄（リロード） ボタン押下
            self.driver.find_element_by_name(
                'layoutChildBody:childForm:doReload').click()

            # 施設名の取得

            print('■ 施設:{0}, 部屋:{1}'.format(bname, iname))
            # print('>> 期間： {0}/{1}～{2}/{3}'.format( date_from.month, date_from.day, date_to.month, date_to.day ))

            # room_str = '{0}/{1}'.format(bname, iname)
            rank = dic.chorus_ROOM[curRoom]

        lstRoom = curRoom

        # === 日付ループ ===

        # Webページ上の 対象施設の 日付の更新
        day_string = str(curYear) + "," + str(curMonth) + "," + str(curDay)
        script_str = "javascript:selectCalendarDate(" + \
            day_string + ");return false;"

        print('Script:' + script_str)

        # vvv ちょっと待ってからスクリプト実行
        # time.sleep(0.2)

        self.wait.until(EC.element_to_be_clickable(
            (By.CLASS_NAME, 'calclick')))
        self.driver.execute_script(script_str)
        # print("# 日付：{0}/{1}({2}): 場所:{3}".
        #      format(month, day, curWeek, room_str), end="")

        time.sleep(0.3)  # 待ちを入れてみる

        # 予約状況の取得
        #  class:'time-table1' は見出し行、'time-table2' は 予約状況
        rsvStat = ["", "", ""]
        tds = self.driver.find_elements_by_class_name('time-table2')
        for i in range(len(tds)):  # 3つの td で構成。0:午前, 1:午後, 2:夜
            td = tds[i]
            sel_ele = td.find_element_by_id("sel")
            # bcd_ele   = td.find_element_by_id("bcd")
            tzone_ele = td.find_element_by_id("tzoneno")
            state_ele = td.find_element_by_tag_name("img")

            # sel_name    = sel_ele.get_attribute("name")
            sel_value = sel_ele.get_attribute("value")
            # bcd_name    = bcd_ele.get_attribute("name")
            # bcd_value   = bcd_ele.get_attribute("value")
            # tzone_name  = tzone_ele.get_attribute("name")
            tzone_value = tzone_ele.get_attribute("value")
            state_alt = state_ele.get_attribute("alt")

            state = dic.state_tbl[state_alt]
            tzone_str = dic.tzone_tbl[tzone_value]
            # rsvStat[i] = sel_value
            rsvStat[i] = state

        # リストに追加
        # room_stat.append([curYear, curMonth, curDay, curWeek, room_str, rsvStat])
        # room_dataat = namedtuple('room_dataat', ('year', 'month', 'day', 'week', 'room', 'am', 'pm', 'night'))

        # (
        #         'type',
        #         'username',
        #         'year', 'month', 'day', 'week',
        #         'start','end',
        #         'bname', 'iname',
        #         'state',
        #         'am', 'pm', 'night',
        #         'rank'
        # )
        room_data.append(
            room_datum(
                type="空き",
                username='---',  # username
                year=curYear,
                month=curMonth,
                day=curDay,
                week=curWeek,
                start='',
                end='',
                bname=bname,
                iname=iname,
                state='---',
                am=rsvStat[0],
                pm=rsvStat[1],
                night=rsvStat[2],
                rank=rank,
                Tmanabu='',
                Tsato='',
                Tniimi='',
                Ttamamura=''
            )
        )

        # print( room_data[-1] )

    return result_msg


# 空き施設確認
def get_free_list(self, date_from, date_to):

    result_msg = ""

    #  高機能画面表示
    url = "https://www.fureai-net.city.kawasaki.jp/"
    self.driver.get(url)
    url = "https://www.fureai-net.city.kawasaki.jp/user/view/user/homeIndex.html"
    self.driver.get(url)

    # 施設ループ
    for index, room in enumerate(dic.chorus_ROOM.keys()):
        print("■ index:{0} room:{1}".format(index, room))
        hmod = self.today.hour % 2
        rmod = index % 2
        print("--hmod~{}, rmod={}".format(hmod, rmod))

        # Heroku の場合は 処理時間を短くするため 1/2 に
        exec_flg = True
        if self.isHeroku == False:  # ローカル環境ではいつもチェック
            exec_flg = True

        if index <= 1:  # 麻生 と 多摩
            exec_flg = True
        elif (hmod == rmod):
            exec_flg = True

        # チェック開始
        if exec_flg:
            print("--- 実行")
            cur_msg = _search_free_by_room(self, room, date_from, date_to)
            result_msg += cur_msg
        else:
            print("--- スキップ")

    return result_msg


def _search_free_by_room(self, curRoom, date_from, date_to):

    result_msg = ""

    # 指定された 施設 の予約状況を確認
    url = "https://www.fureai-net.city.kawasaki.jp/user/view/user/rsvNameSearch.html"
    self.driver.get(url)

    # 施設指定
    icd = dic.room_icd[curRoom]
    bname = curRoom.split('／')[0]
    iname = curRoom.split('／')[1]
    if "岡上" in bname:
        bname_key = bname + "分館"
    else:
        bname_key = bname + "市民館"

    # vvv ちょっと待ってからスクリプト実行
    self.wait.until(EC.presence_of_element_located((By.ID, "textKeyword")))
    self.driver.find_element_by_id('textKeyword').send_keys(bname_key)

    self.driver.execute_script("javascript:eventOnLoad()")
    # self.driver.find_element_by_id('doSearch').submit()
    self.driver.find_element_by_id('doSearch').click()

    self.driver.execute_script("javascript:eventOnLoad()")
    self.driver.find_element_by_id('doSelect').click()
    # self.driver.execute_script( "javascript:this.form.bcd.value = '1240';return true;")

    # チェックを全て解除
    self.driver.execute_script("javascript:doCheck(false);return false;")
    # 特定の施設だけチェック

    chkboxs = self.driver.find_elements_by_name(
        'layoutChildBody:childForm:selectIcd')
    for chkbox in chkboxs:  # 3つの td で構成。0:午前, 1:午後, 2:夜

        chkboxicd = chkbox.get_attribute("value")
        # print("icd:{}, chkboxicd:{}".format(icd,chkboxicd))

        if icd == chkboxicd:
            print(bname, iname)
            chkbox.click()

    self.driver.find_element_by_name(
        'layoutChildBody:childForm:doReload').click()

    # 施設名の取得

    print('■ 施設:{0}, 部屋:{1}'.format(bname, iname))
    print('>> 期間： {0}/{1}～{2}/{3}'.format(date_from.month,
                                          date_from.day, date_to.month, date_to.day))

    # room_str = '{0}/{1}'.format(bname, iname)
    rank = dic.chorus_ROOM[curRoom]

    # === 日付ループ ===
    curDate = date_from
    days = (date_to - date_from).days
    for dayCnt in range(days):  # 200日間チェック

        # 日付の更新 とりあえず先に更新しておく
        curDate = curDate + datetime.timedelta(days=1)

        curYear = curDate.year
        curMonth = curDate.month
        curDay = curDate.day
        curWeek = datesub.get_weekstr(curYear, curMonth, curDay)
        curHoliday = datesub.chk_holiday(curYear, curMonth, curDay)

        # 土日祝 以外は対象外
        if curDate >= date_to:
            print('▲チェックは {}/{}まで'.format(date_to.month, date_to.day))

        # if ((curWeek == "土") or (curWeek == "日") or (curHoliday != None)):
        if ((curWeek in {"土", "日"}) or (curHoliday is not None)):

            # Webページ上の 対象施設の 日付の更新
            day_string = str(curYear) + "," + str(curMonth) + "," + str(curDay)
            script_str = "javascript:selectCalendarDate(" + \
                day_string + ");return false;"

            print('Script:' + script_str)

            # vvv ちょっと待ってからスクリプト実行
            # time.sleep(0.2)

            self.wait.until(EC.element_to_be_clickable(
                (By.CLASS_NAME, 'calclick')))
            self.driver.execute_script(script_str)
            # print("# 日付：{0}/{1}({2}): 場所:{3}".
            #      format(month, day, curWeek, room_str), end="")

            time.sleep(0.3)  # 待ちを入れてみる

            # 予約状況の取得
            #  class:'time-table1' は見出し行、'time-table2' は 予約状況
            rsvStat = ["", "", ""]
            tds = self.driver.find_elements_by_class_name('time-table2')
            for i in range(len(tds)):  # 3つの td で構成。0:午前, 1:午後, 2:夜
                td = tds[i]
                sel_ele = td.find_element_by_id("sel")
                # bcd_ele   = td.find_element_by_id("bcd")
                tzone_ele = td.find_element_by_id("tzoneno")
                state_ele = td.find_element_by_tag_name("img")

                # sel_name    = sel_ele.get_attribute("name")
                sel_value = sel_ele.get_attribute("value")
                # bcd_name    = bcd_ele.get_attribute("name")
                # bcd_value   = bcd_ele.get_attribute("value")
                # tzone_name  = tzone_ele.get_attribute("name")
                tzone_value = tzone_ele.get_attribute("value")
                state_alt = state_ele.get_attribute("alt")

                state = dic.state_tbl[state_alt]
                tzone_str = dic.tzone_tbl[tzone_value]
                # rsvStat[i] = sel_value
                rsvStat[i] = state

            # リストに追加
            # room_stat.append([curYear, curMonth, curDay, curWeek, room_str, rsvStat])
            # room_dataat = namedtuple('room_dataat', ('year', 'month', 'day', 'week', 'room', 'am', 'pm', 'night'))

            # (
            #         'type',
            #         'username',
            #         'year', 'month', 'day', 'week',
            #         'start','end',
            #         'bname', 'iname',
            #         'state',
            #         'am', 'pm', 'night',
            #         'rank'
            # )
            room_data.append(
                room_datum(
                    type="空き",
                    username='---',  # username
                    year=curYear,
                    month=curMonth,
                    day=curDay,
                    week=curWeek,
                    start='',
                    end='',
                    bname=bname,
                    iname=iname,
                    state='---',
                    am=rsvStat[0],
                    pm=rsvStat[1],
                    night=rsvStat[2],
                    rank=rank,
                    Tmanabu='',
                    Tsato='',
                    Tniimi='',
                    Ttamamura=''
                )
            )

            # print( room_data[-1] )

    return result_msg
