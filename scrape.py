# 日付操作系 ライブラリ
import datetime
import calendar
import jpholiday
from dateutil.relativedelta import relativedelta
import time

# 環境変数取得のため
import os

# ログ操作系 ライブラリ
import traceback
import logging

# WebDriver系
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import chromedriver_binary  # Adds chromedriver binary to path

# import sys
# from pathlib import Path
# sys.path.append("../")

# 引数解析
import argparse    # 1. argparseをインポート


# メール送信に必要なライブラリ
# from email.utils import formatdate
# from email.mime.text import MIMEText
# import smtplib
import sendMail.sendMail as sendMail  # 自前
import subs.datesub as datesub 

# import printLogInfo # 自前

# data, 辞書 インポート
import data.data as data
import data.data as dic

class FureaiNet:
    def __init__(self, from_time, to_time):

        # 環境変数からの吸出し
        env_SMTP_USER   = os.getenv('SMTP_USER')
        env_SMTP_PASSWD = os.getenv('SMTP_PASSWD')
        env_FROM_ADDRESS = os.getenv('FROM_ADDRESS')
        env_TO_ADDRESS  = os.getenv('TO_ADDRESS')
        env_CC_ADDRESS  = os.getenv('CC_ADDRESS')
        env_BCC_ADDRESS = os.getenv('BCC_ADDRESS')
        env_FC_EXEC_MODE = os.getenv('FC_EXEC_MODE')

        # コマンドライン引数の吸出し
        parser = argparse.ArgumentParser(description='ふれあいネットチェッカー')    # 2. パーサを作る

        # 3. parser.add_argumentで受け取る引数を追加していく
        parser.add_argument('--smtp_user', help='SMTP login username', default=env_SMTP_USER )    # 必須の引数を追加
        parser.add_argument('--smtp_passwd', help='SMTP longin password', default=env_SMTP_PASSWD )
        parser.add_argument('--from_addr', help='from adress', default=env_FROM_ADDRESS)    # オプション引数（指定しなくても良い引数）を追加
        parser.add_argument('--to_addr', help='to adress', default=env_TO_ADDRESS)    # オプション引数（指定しなくても良い引数）を追加
        parser.add_argument('--cc_addr', help='cc adress', default=env_CC_ADDRESS)    # オプション引数（指定しなくても良い引数）を追加
        parser.add_argument('--bcc_addr', help='bcc adress', default=env_BCC_ADDRESS)    # オプション引数（指定しなくても良い引数）を追加
        parser.add_argument('--exec_mode', help='execute mode [lot/rsv/chk]', default=env_FC_EXEC_MODE)    # オプション引数（指定しなくても良い引数）を追加
        parser.add_argument('-a', '--arg4')   # よく使う引数なら省略形があると使う時に便利

        args = parser.parse_args()    # 4. 引数を解析

        print( args )

        self.SMTP_USER   = args.smtp_user
        self.SMTP_PASSWD = args.smtp_passwd
        self.FROM_ADDRESS = args.from_addr
        self.TO_ADDRESS  = args.to_addr
        self.CC_ADDRESS  = args.cc_addr
        self.BCC_ADDRESS = args.bcc_addr
        self.SUBJECT = '【ソレイユ】ふれあいネット 情報配信'
        self.BODY = 'pythonでメール送信 テスト'

        self.EXEC_MODE = args.exec_mode

        # rootロガーを取得
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        # ファイルへ出力するハンドラーを定義
        self.today = datetime.datetime.now()
        self.logFile = "_log\\Fureai-Net_{}.log".format( self.today.strftime("%Y%m%d_%H%M%S") )
        print('logFile:'+self.logFile)
        fh = logging.FileHandler( filename=self.logFile, mode='w', encoding='utf-8')
        fh.setLevel(logging.INFO)
        # fh.setFormatter(formatter)

        # rootロガーにハンドラーを登録する
        self.logger.addHandler(fh)

        # webdriver 初期化

        # Heroku以外ではNone
        options = Options()
        isHeroku = os.environ['IS_HEROKU']
        if isHeroku == "True":

            # chromeのパスを指定する。今回は環境変数から取得
            binary_location = os.environ['CHROME_BINARY_LOCATION']
            driver_path = os.environ['CHROME_DRIVER_PATH']
            options.binary_location = binary_location

            # headlessで使用する場合は以下の2行を利用する。
            options.add_argument('--headless')
            # options.add_argument('--disable-gpu')

            # webdriverを起動する。引数executable_pathにwebdriverのパスを指定する。
            # こちらも環境変数から取得
            self.driver = webdriver.Chrome(
                    options=options, executable_path=driver_path)
        else:
            options.add_argument('--headless')
            self.driver = webdriver.Chrome(options=options)

        self.time = time
        self.from_time = from_time
        self.to_time = to_time

        self.login_state = False

    # private method

    def _login(self, username):
        result_msg = ""

        # ログイン済みチェック
        if self.login_state == True:
            print('ログイン済み')
            result_msg += "ログイン済み"
            return result_msg

        # ログイン
        print("login: username:'{}'".format( username ))

        # 高機能 画面開く
        self.driver.get(
            "https://www.fureai-net.city.kawasaki.jp/user/view/user/homeIndex.html")
        # ログインボタン押下
        # self.driver.find_element_by_id('login_on').click()
        self.driver.execute_script("javascript:return doSubmit('childForm', 'doLogin');")

        # ログイン（情報入力＆ログイン）
        userid = dic.card_ID[username]
        passwd = dic.card_PW[userid]

        self.driver.find_element_by_id('userid').send_keys(str(userid))
        self.driver.find_element_by_id('passwd').send_keys(str(passwd))
        self.driver.find_element_by_id('doLogin').click()

        # 時間外チェック
        elements = self.driver.find_elements_by_id('MSG')
        for e in elements:
            chkmsg = e.text
            if "運用時間外" in chkmsg:
                print("----運用時間外----")
                result_msg += "運用時間外"
                self.login_state = False
                return result_msg

        # ログイン成功
        print("OK!")
        result_msg += "login OK!"
        self.login_state = True

        # マイページが表示されているので
        # 予約情報を取得
        # 抽選申し込み数を取得
        rsvCount = 0
        rsvCount_elem = self.driver.find_elements_by_id("rsvNum")
        if len(rsvCount_elem) > 0:
            rsvCount = rsvCount_elem[0].text
            print('[施設予約 件数] {}件'.format(rsvCount))
        
        # 抽選申し込み数を取得
        lotCount = 0
        lotCount_elem = self.driver.find_elements_by_id("lotNum")
        if len(lotCount_elem) > 0:
            lotCount = lotCount_elem[0].text
            print('[抽選申込 件数] {}件'.format(lotCount))

        dic.card_RSV[username] = rsvCount
        dic.card_LOT[username] = lotCount

        data.accountInf.append( data.accountInfo(username, userid, passwd, rsvCount, lotCount) )

        return result_msg

    def _logoff(self):
        result_msg = ""

        # ログイン済みチェック
        if self.login_state == False:
            print('(!) ログインしていません')
            result_msg += "未ログイン"
            return result_msg

        # ログイン
        print("logoff...")

        # ログアウト処理
        self.driver.find_element_by_id('doLogout').click()
        # self.driver.execute_script('return checkCartList();')
        
        print("OK!")
        result_msg += "logout."
        self.login_state = False

        return result_msg

    
    # 第１ループ
    def _first_loop( self, date_from, date_to ):
        result_msg = ""
        
        # 空き探索する場合
        if ("chk" in self.EXEC_MODE):
            print('0:空きサーチ2\n')
            result_msg += self._get_free_room2( date_from, date_to )
        
        # Reserve 各アカウントで収集
        if ("rsv" in self.EXEC_MODE):
            for login_name in dic.card_ID:
                print('アカウント:{}'.format(login_name))
                result_msg += self._login( login_name )
                
                # ログインできなかったら コンティニュー
                if self.login_state == False:
                    continue

                # 予約サーチする場合
                print('1:予約サーチ({})\n'.format(login_name))
                result_msg += self._get_reserve_list( login_name )
            
                # 最後にログオフ
                result_msg += self._logoff()

        # LOT 各アカウントで収集
        if ("lot" in self.EXEC_MODE):
            for login_name in dic.card_ID:
                print('アカウント:{}'.format(login_name))
                result_msg += self._login( login_name )
                
                # ログインできなかったら コンティニュー
                if self.login_state == False:
                    continue

                # 抽選結果確認する場合
                print('3:抽選サーチ({})\n'.format(login_name))
                result_msg += self._get_lot_list( login_name )
            
                # 最後にログオフ
                result_msg += self._logoff()

        return result_msg            

    # 抽選予約情報 収集
    def _get_lot_list( self, username ):

        result_msg = ""

        # ログイン済みチェック
        if self.login_state == False:
            print('ログインしていません')
            result_msg += "未ログイン"
            return result_msg

        # ======= 抽選確認ループ =======
        lotCount = dic.card_LOT[username]
        
        # 指定された 施設 の予約状況を確認
        url = "https://www.fureai-net.city.kawasaki.jp/user/view/user/lotStatusList.html"
        self.driver.get(url)
        for page_offset in range(0, int(lotCount), 5) :

            # 次の5件
            script_str = "javascript:$('offset').value = "
            script_str += str(page_offset)
            script_str += ";doSubmit('childForm', 'doPager');return false"

            self.driver.execute_script( script_str )
            # rsv:self.driver.execute_script("javascript:$('offset').value = 5;doSubmit('childForm', 'doPager');return false")
            # lot:                            javascript:$('offset').value = 10;doSubmit('childForm', 'doPager');return false

            print('[Page]{}/{}'.format(page_offset, lotCount))

            # id="headerCount" # 26件

            # 予約テーブルの取得
            # 予約状況の取得
            #  class:'time-table1' は見出し行、'time-table2' は 予約状況
            table_elems = self.driver.find_elements_by_class_name("tablebg2")
            for table in table_elems:

                # 所望のテーブル出ない場合は スキップ
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
                    # ymd   = tr.find_element( By.ID, 'ymdLabel').text
                    ymd   = tr.find_element( By.ID, 'useymdLabel').text
                    stime = tr.find_element( By.ID, 'stimeLabel').text
                    etime = tr.find_element( By.ID, 'etimeLabel').text
                    bname = tr.find_element( By.ID, 'bgcdnamem').text
                    iname = tr.find_element( By.ID, 'igcdnamem').text
                    state = tr.find_element( By.ID, 'lotStateLabel').text

                    ymd = datesub.cnv_datestr(ymd)
                    stime = stime.replace("時","")
                    stime = stime.replace("分","")
                    etime = etime.replace("時","")
                    bname = bname.replace("市民館","")
                    bname = bname.replace("分館","")

                    print( "日時：{}[{}~{}], 施設:{}/{}, 結果:{}".format( ymd,stime,etime,bname,iname,state ))
    
                    # リストに追加
                    data.lotInf.append(data.lotInfo(username, ymd,stime,etime,bname,iname,state))
        
        #print('')

        return result_msg

    # 予約情報 収集
    def _get_reserve_list( self, username ):

        result_msg = ""

        # ログイン済みチェック
        if self.login_state == False:
            print('ログインしていません')
            result_msg += "未ログイン"
            return result_msg

        # ======= 抽選確認ループ =======
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

                    ymd = datesub.cnv_datestr(ymd)
                    stime = stime.replace("時","")
                    etime = etime.replace("時","")
                    bname = bname.replace("市民館","")
                    bname = bname.replace("分館","")
                    iname = iname.replace("室","")
                    
                    # よりよい場所があれば... レベル
                    roomName = bname+"／"+iname
                    goodLevel = dic.chorus_ROOM[ roomName ]

                    #if ("岡上" in bname)or("宮前"in bname):
                    #    goodLevel = '△'
                    #elif ('9' in stime):
                    #    goodLevel = '▲'
                    #else:
                    #    goodLevel = '〇'

                    print( "日時：{}[{}~{}], 施設:{}/{}, 支払:{}".format( ymd,stime,etime,bname,iname,state ))
    
                    # リストに追加
                    data.rsvInf.append(data.rsvInfo(username, ymd,stime,etime,bname,iname,state,goodLevel))
        
        #print('')

        return result_msg

    # 空き施設確認
    def _get_free_room(self, date_from, date_to):

        result_msg = ""

        # ログイン済みチェック
        if self.login_state == False:
            print('ログインしていません')
            result_msg += "未ログイン"
            return result_msg

        # 施設ループ
        for index, room in enumerate(dic.chorus_ROOM.keys()):
            print("■ index:{0} room:{1}".format(index, room))
            cur_msg = self._search_free_by_room(room, date_from, date_to)
            result_msg += cur_msg

        return result_msg

    def _search_free_by_room(self, chorus_room, date_from, date_to):

        result_msg = ""

        # ログイン済みチェック
        if self.login_state == False:
            print('ログインしていません')
            result_msg += "未ログイン"
            return result_msg

        # 指定された 施設 の予約状況を確認
        url = "https://www.fureai-net.city.kawasaki.jp/user/view/user/rsvEmptyState.html?"
        url += "bcd=" + dic.room_bcd[chorus_room]
        url += "&icd=" + dic.room_icd[chorus_room]
        self.driver.get(url)

        # 施設名の取得
        room_elements = self.driver.find_elements_by_id("blabel")
        if len(room_elements) > 0:
            for rele in room_elements:
                bname_eles = rele.find_elements_by_id("bnamem")
                iname_eles = rele.find_elements_by_id("inamem")
                bname = bname_eles[0].text
                bname = bname.replace( "市民館","" )
                bname = bname.replace( "分館","" )
                iname = iname_eles[0].text
                iname = iname.replace( "室","" )
                print('■ 施設:{0}, 部屋:{1}'.format(bname, iname))
                room_str = '{0}/{1}'.format(bname, iname)
                if ("岡上" in bname)or("宮前"in bname):
                    goodLevel = '△'
                else:
                    goodLevel = '〇'


        # === 日付ループ ===
        curDate = date_from
        days = (date_to-date_from).days
        for dayCnt in range(days):  # 200日間チェック

            # 日付の更新 とりあえず先に更新しておく
            curDate = curDate + datetime.timedelta(days=1)

            curYear    = curDate.year
            curMonth   = curDate.month
            curDay     = curDate.day
            curWeek    = datesub.get_weekstr( curYear, curMonth, curDay )
            curHoliday = datesub.chk_holiday( curYear, curMonth, curDay )

            # 土日祝 以外は対象外
            if curDate >= date_to:
                print(date_to)
            if ((curWeek == "土") or (curWeek == "日") or (curHoliday != None)):

                # Webページ上の 対象施設の 日付の更新
                day_string = str(curYear)+","+str(curMonth)+","+str(curDay)
                script_str = "javascript:selectCalendarDate(" + \
                    day_string+");return false;"
                self.driver.execute_script(script_str)
                #print("# 日付：{0}/{1}({2}): 場所:{3}".
                #      format(month, day, curWeek, room_str), end="")

                # 予約状況の取得
                #  class:'time-table1' は見出し行、'time-table2' は 予約状況
                rsvStat = ["", "", ""]
                tds = self.driver.find_elements_by_class_name('time-table2')
                for i in range(len(tds)):  # 3つの td で構成。0:午前, 1:午後, 2:夜
                    td = tds[i]
                    sel_ele = td.find_element_by_id("sel")
                    #bcd_ele   = td.find_element_by_id("bcd")
                    tzone_ele = td.find_element_by_id("tzoneno")
                    state_ele = td.find_element_by_tag_name("img")

                    #sel_name    = sel_ele.get_attribute("name")
                    sel_value = sel_ele.get_attribute("value")
                    #bcd_name    = bcd_ele.get_attribute("name")
                    #bcd_value   = bcd_ele.get_attribute("value")
                    #tzone_name  = tzone_ele.get_attribute("name")
                    tzone_value = tzone_ele.get_attribute("value")
                    state_alt = state_ele.get_attribute("alt")

                    state = dic.state_tbl[state_alt]
                    tzone_str = dic.tzone_tbl[tzone_value]
                    rsvStat[i] = sel_value

                # リストに追加
                data.room_stat.append(
                    [curYear, curMonth, curDay, curWeek, room_str, rsvStat])
                #roomStat = namedtuple('roomStat', ('year', 'month', 'day', 'week', 'room', 'am', 'pm', 'night'))
                data.roomSt.append(data.roomStat(
                    curYear, curMonth, curDay, curWeek, 
                    room_str, 
                    rsvStat[0], rsvStat[1], rsvStat[2],
                    goodLevel
                    ))

                #print('')

        return result_msg

# 空き施設確認
    def _get_free_room2(self, date_from, date_to):

        result_msg = ""

        # ログイン済みチェック
        if self.login_state == True:
            print('ログインしています')
            result_msg += "ログイン中"
            return result_msg

        #  高機能画面表示
        self.driver.get(
            "https://www.fureai-net.city.kawasaki.jp/user/view/user/homeIndex.html")
       

        # 施設ループ
        for index, room in enumerate(dic.chorus_ROOM.keys()):
            print("■ index:{0} room:{1}".format(index, room))
            cur_msg = self._search_free_by_room2(room, date_from, date_to)
            result_msg += cur_msg

        return result_msg

    def _search_free_by_room2(self, chorus_room, date_from, date_to):

        result_msg = ""

        # 指定された 施設 の予約状況を確認
        url = "https://www.fureai-net.city.kawasaki.jp/user/view/user/rsvNameSearch.html"
        self.driver.get(url)

        # 施設指定
        icd = dic.room_icd[chorus_room]
        bname = chorus_room.split('／')[0]
        iname = chorus_room.split('／')[1]
        if "岡上" in bname:
            bname_key = bname+"分館"
        else:
            bname_key = bname+"市民館"
        self.driver.find_element_by_id('textKeyword').send_keys(bname_key)
        
        self.driver.execute_script("javascript:eventOnLoad()")
        #self.driver.find_element_by_id('doSearch').submit()
        self.driver.find_element_by_id('doSearch').click()
        
        self.driver.execute_script("javascript:eventOnLoad()")
        self.driver.find_element_by_id('doSelect').click()
        #self.driver.execute_script( "javascript:this.form.bcd.value = '1240';return true;")

        # チェックを全て解除
        self.driver.execute_script("javascript:doCheck(false);return false;")
        # 特定の施設だけチェック

        chkboxs = self.driver.find_elements_by_name('layoutChildBody:childForm:selectIcd')
        for chkbox in chkboxs:  # 3つの td で構成。0:午前, 1:午後, 2:夜
            
            chkboxicd=chkbox.get_attribute("value") 
            print("icd:{}, chkboxicd:{}".format(icd,chkboxicd))

            if icd == chkboxicd:
                print( bname, iname )
                chkbox.click()
        
        self.driver.find_element_by_name('layoutChildBody:childForm:doReload').click()

        # 施設名の取得

        print('■ 施設:{0}, 部屋:{1}'.format(bname, iname))
        room_str = '{0}/{1}'.format(bname, iname)
        goodLevel = dic.chorus_ROOM[chorus_room]
        
        # === 日付ループ ===
        curDate = date_from
        days = (date_to-date_from).days
        for dayCnt in range(days):  # 200日間チェック

            # 日付の更新 とりあえず先に更新しておく
            curDate = curDate + datetime.timedelta(days=1)

            curYear    = curDate.year
            curMonth   = curDate.month
            curDay     = curDate.day
            curWeek    = datesub.get_weekstr( curYear, curMonth, curDay )
            curHoliday = datesub.chk_holiday( curYear, curMonth, curDay )

            # 土日祝 以外は対象外
            if curDate >= date_to:
                print(date_to)
            if ((curWeek == "土") or (curWeek == "日") or (curHoliday != None)):

                # Webページ上の 対象施設の 日付の更新
                day_string = str(curYear)+","+str(curMonth)+","+str(curDay)
                script_str = "javascript:selectCalendarDate(" + \
                    day_string+");return false;"
                self.driver.execute_script(script_str)
                #print("# 日付：{0}/{1}({2}): 場所:{3}".
                #      format(month, day, curWeek, room_str), end="")

                # 予約状況の取得
                #  class:'time-table1' は見出し行、'time-table2' は 予約状況
                rsvStat = ["", "", ""]
                tds = self.driver.find_elements_by_class_name('time-table2')
                for i in range(len(tds)):  # 3つの td で構成。0:午前, 1:午後, 2:夜
                    td = tds[i]
                    sel_ele = td.find_element_by_id("sel")
                    #bcd_ele   = td.find_element_by_id("bcd")
                    tzone_ele = td.find_element_by_id("tzoneno")
                    state_ele = td.find_element_by_tag_name("img")

                    #sel_name    = sel_ele.get_attribute("name")
                    sel_value = sel_ele.get_attribute("value")
                    #bcd_name    = bcd_ele.get_attribute("name")
                    #bcd_value   = bcd_ele.get_attribute("value")
                    #tzone_name  = tzone_ele.get_attribute("name")
                    tzone_value = tzone_ele.get_attribute("value")
                    state_alt = state_ele.get_attribute("alt")

                    state = dic.state_tbl[state_alt]
                    tzone_str = dic.tzone_tbl[tzone_value]
                    rsvStat[i] = sel_value

                # リストに追加
                data.room_stat.append(
                    [curYear, curMonth, curDay, curWeek, room_str, rsvStat])
                #roomStat = namedtuple('roomStat', ('year', 'month', 'day', 'week', 'room', 'am', 'pm', 'night'))
                data.roomSt.append(data.roomStat(
                    curYear, curMonth, curDay, curWeek, 
                    room_str, 
                    rsvStat[0], rsvStat[1], rsvStat[2],
                    goodLevel
                    ))

                #print('')

        return result_msg



    def _chk_mail_parameter(self):
        msg = '--- Mail Send Parameter ---\n'
        msg += 'SMTP_USER = {}\n'.format( self.SMTP_USER )
        msg += 'SMTP_PASSWD = {}\n'.format( self.SMTP_PASSWD)
        msg += 'FROM_ADDRESS = {}\n'.format( self.FROM_ADDRESS)
        msg += 'TO_ADDRESS = {}\n'.format( self.TO_ADDRESS)
        msg += 'CC_ADDRESS = {}\n'.format( self.CC_ADDRESS)
        msg += 'BCC_ADDRESS = {}\n'.format( self.BCC_ADDRESS)
        print(msg)
        return msg
    
    def _send_mail(self, body):
        # create_message(from_addr, to_addr, cc_addr, bcc_addr, subject, body):
        from_addr = self.FROM_ADDRESS
        to_addr = self.TO_ADDRESS
        cc_addr = self.CC_ADDRESS
        bcc_addr = self.BCC_ADDRESS
        subject = self.SUBJECT
        if body == "":
            body = self.BODY

        msg = sendMail.create_message(from_addr, to_addr, cc_addr, bcc_addr, subject, body)
        sendMail.send(self.SMTP_USER, self.SMTP_PASSWD, msg)

    # public method

    def run(self):
        try:

            # メール送信パラメータチェック
            msg = self._chk_mail_parameter()
            print(msg)
            self.logger.info(msg)

            # 今日の日付を取得
            today = datetime.datetime.now()
            
            # 開始日は今日
            date_from = today

            # 29日-30/31までは、４か月後の月末
            # 1日～28日までは 3カ月後の月末
            if today.day >=29:
                addMonth = 5
            else:
                addMonth = 4
            date_to = (date_from + relativedelta(months=addMonth)
                       ).replace(day=1) - datetime.timedelta(days=1)
            
            # 取得開始
            msg = self._first_loop( date_from, date_to )
            
            # ログメッセージ
            msg = ">> ふれあいネット 情報 <<\n"
            msg += "※{} 現在\n".format( today.strftime("%Y-%m-%d %H:%M:%S"))
            mailMsg = ""
            
            # 空き情報２
            if data.roomSt:
                # 期間
                msg += "----------\n"
                # msg += "期間：{}～{}\n".format( date_from.strftime("%Y-%m-%d"), date_to.strftime("%Y-%m-%d"))
                # msg += "時間帯：午後（{}-{}時）の 空き会議室 \n".format( self.from_time, self.to_time )
                msg += "よさそうな空き会議室リスト\n"
                msg += "----------\n"
                
                # 収集リストの表示
                roomSt2 = sorted(data.roomSt)
                #roomSt2 = sorted( self.roomSt, key=lambda x:(x[4],x[1]) )
                for i in roomSt2:
                    if i.pm == "0":
                        if i.goodLevel in {'〇', '◎', '◆'}:
                            print(i.year, i.month, i.day, i.week,
                                i.room, i.am, i.pm, i.night)
                            msg += "{0}/{1:02}/{2:02}({3}) {4}({5})\n".format(
                                str(i.year)[2:], i.month, i.day, i.week, i.room, i.goodLevel )

            # 予約情報２
            if data.rsvInf:
                # 期間
                msg += "----------\n"
                msg += "よりよい会議室があれば取りたいリスト\n"
                msg += "----------\n"
                
                # 収集リストの表示
                rsvInf2 = sorted( data.rsvInf, key=lambda x:(x[1],x[0]) )
                
                # 利用日時, 開始, 終了, 館名, 施設名, 支払状況
                for i in rsvInf2:
                    if i.goodLevel in {'◎'}:  # 最高の場所が確保できている
                        pass
                    elif i.goodLevel in {"〇","△","◆"}:
                            # 最高ではない
                            # 今一つ
                            # 今一つか、ボイトレ用
                        print(i.date, i.start, i.end, i.bname, i.iname, i.state)
                        msg += "{0} {1}{2}~{3} {4}/{5}({6})\n".format(i.username[0:1], 
                            i.date, i.start, i.end, i.bname, i.iname, i.goodLevel )
            
            # 予約情報
            if data.rsvInf:
                # 期間
                msg += "----------\n"
                msg += "期間：{}～{}の 予約状況\n".format( date_from.strftime("%Y-%m-%d"), date_to.strftime("%Y-%m-%d"))
                msg += "----------\n"
                
                # 収集リストの表示
                rsvInf2 = sorted( data.rsvInf, key=lambda x:(x[1],x[0]) )
                
                # 利用日時, 開始, 終了, 館名, 施設名, 支払状況
                for i in rsvInf2:
                    print(i.date, i.start, i.end, i.bname, i.iname, i.state)
                    msg += "{0} {1}{2}~{3} {4}/{5}({6})\n".format(i.username[0:1], 
                        i.date, i.start, i.end, i.bname, i.iname, i.goodLevel )

           # 抽選情報
            # if False:
            if data.lotInf:
                # 期間
                msg += "----------\n"
                msg += "期間：{}～{}の 抽選申込状況\n".format( date_from.strftime("%Y-%m-%d"), date_to.strftime("%Y-%m-%d"))
                msg += "----------\n"
                
                # 収集リストの表示
                lotInf2 = sorted( data.lotInf, key=lambda x:(x[1],x[0]) )
                
                # 利用日時, 開始, 終了, 館名, 施設名, 支払状況
                for i in lotInf2:
                    print(i.date, i.start, i.end, i.bname, i.iname, i.state)
                    msg += "{0} {1}{2}~{3} {4}/{5}({6})\n".format(
                        i.username[0:1], 
                        i.date, i.start, i.end, 
                        i.bname, i.iname, i.state )

            # 表示
            print(msg)
            self.logger.info(msg)
            mailMsg += msg
            msg = ""
            
            # 結果をメールで送信
            self._send_mail( mailMsg )

        except Exception:
            self.logger.error(traceback.format_exc())
            print("エクセプション発生！")

        finally:
            self.driver.close()
            self.driver.quit()
            print("終了。")

   

import sys  # main.py で必要

if __name__ == "__main__":

    def main(args):
        if len(args) == 4:
            FureaiNet(args[1], args[2]).run()
        else:
            FureaiNet(13, 17).run()

    main(sys.argv)

