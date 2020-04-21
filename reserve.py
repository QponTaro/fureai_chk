# 日付操作系 ライブラリ
# import time

# WebDriver系
# from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# import chromedriver_binary  # Adds chromedriver binary to path

# import subs.datesub as datesub

# data, 辞書 インポート
# import data.data as data
import data.data as dic
# from data.data import room_data, room_datum


def reserve_room(self, rsv_list):
    result_msg = ""

    for login_name in ['歌の会']:

        # ログイン
        result_msg += self._login(login_name)

        # ログインできなかったら コンティニュー
        if self.login_state is False:
            continue

        # 抽選申し込み状況・結果確認
        result_msg += _reserve_room(self, rsv_list)

        # 最後にログオフ
        result_msg += self._logoff()

    return result_msg

# 日付リスト で指定された 予約を実行


def _reserve_room(self, rsv_list):

    result_msg = ""
    for rsv_data in rsv_list:

        # ログインしていることが前提

        # マイページを開く
        script_str = "javascript:return doMenuBtn('MYPAGE');"
        # vvv ボタンが押せるまで待って スクリプト実行
        self.wait.until(EC.element_to_be_clickable((By.ID, 'goBtn')))
        self.driver.execute_script(script_str)

        # 指定の施設を開く
        # chorus_room = rsv_data.bname+"／"+rsv_data.iname
        chorus_room = rsv_data.room
        icd = dic.room_icd[chorus_room]
        bcd = dic.room_bcd[chorus_room]

        url = "https://www.fureai-net.city.kawasaki.jp/user/view/user/rsvEmptyState.html?"
        url = url + "bcd=" + bcd + "&icd=" + icd
        self.driver.get(url)

        # Webページ上の 対象施設の 日付の更新
        rsvYear = rsv_data.year
        rsvMonth = rsv_data.month
        rsvDay = rsv_data.day

        day_string = str(rsvYear) + "," + str(rsvMonth) + "," + str(rsvDay)
        script_str = "javascript:selectCalendarDate(" + \
            day_string + ");return false;"

        print('Script:' + script_str)

        # vvv ちょっと待ってからスクリプト実行
        # time.sleep(0.2)

        self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'calclick')))
        self.driver.execute_script(script_str)

        # === ここまでで 施設・日時が 表示された ===
        if rsv_data.zone == '夜間':
            script_str = 'return doSelectBtn(this, 0, 0, 2);'
        if rsv_data.zone == '午後':
            script_str = 'return doSelectBtn(this, 0, 0, 1);'
        if rsv_data.zone == '午前':
            script_str = 'return doSelectBtn(this, 0, 0, 0);'

        # 該当する 午前・午後・夜間 のボタンをクリックし カート追加済みにする
        self.wait.until(EC.element_to_be_clickable((By.ID, 'emptyStateIcon')))
        self.driver.execute_script(script_str)

        # 予約カートに追加 ボタンを押す
        script_str = "javascript: this.form.itemindex.value = '0'; return true;"
        self.wait.until(EC.element_to_be_clickable((By.ID, 'doAddCart')))
        self.driver.execute_script(script_str)

        # 予約カートの内容を確認ボタンを押す
        script_str = "return confirmSelCart(-1);"
        self.wait.until(EC.element_to_be_clickable((By.ID, 'jumpRsvCartList')))
        self.driver.execute_script(script_str)

        # --- 必要なパラメータの ローカル変数への 登録 ---
        chorus_room = rsv_data.bname + "／" + rsv_data.iname

        # print( room_data[-1] )

    return result_msg
