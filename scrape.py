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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

# 名前付きタプル
from collections import namedtuple

# data, 辞書 インポート
import data.data as data
import data.data as dic
from data.data import room_data, room_datum
from data.data import rsv_list, rsv_datum

import data.rw_csv as rw_csv


from getLotList import get_lot_list
from getRsvList import get_rsv_list
from getFreeList import get_free_list, make_chk_date_list, chk_free_room

from reserve import reserve_room

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
        env_MAIL_SUBJECT = os.getenv('MAIL_SUBJECT','>>ふれあいネット情報<< (Local)')
        env_isHeroku = os.getenv('IS_HEROKU',False)
        if env_isHeroku == 'True':
            self.isHeroku = True
        else:
            self.isHeroku = False

        # コマンドライン引数の吸出し
        parser = argparse.ArgumentParser(description='ふれあいネットチェッカー')    # 2. パーサを作る

        # 3. parser.add_argumentで受け取る引数を追加していく
        parser.add_argument('--smtp_user', help='SMTP login username', default=env_SMTP_USER )    # 必須の引数を追加
        parser.add_argument('--smtp_passwd', help='SMTP longin password', default=env_SMTP_PASSWD )
        parser.add_argument('--from_addr', help='from adress', default=env_FROM_ADDRESS)    # オプション引数（指定しなくても良い引数）を追加
        parser.add_argument('--to_addr', help='to adress', default=env_TO_ADDRESS)    # オプション引数（指定しなくても良い引数）を追加
        parser.add_argument('--cc_addr', help='cc adress', default=env_CC_ADDRESS)    # オプション引数（指定しなくても良い引数）を追加
        parser.add_argument('--bcc_addr', help='bcc adress', default=env_BCC_ADDRESS)    # オプション引数（指定しなくても良い引数）を追加
        parser.add_argument('--mail_subject', help='mail subject', default=env_MAIL_SUBJECT)    # オプション引数（指定しなくても良い引数）を追加

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
        self.SUBJECT = args.mail_subject
        self.BODY = 'pythonでメール送信 テスト'

        self.EXEC_MODE = args.exec_mode

        # rootロガーを取得
        self.logger = logging.getLogger()
        # ログを標準出力に出力する
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
        self.logger.setLevel(logging.INFO)

        # ファイルへ出力するハンドラーを定義
        self.today = datetime.datetime.now()
        #self.logFile = "_log\\Fureai-Net_{}.log".format( self.today.strftime("%Y%m%d_%H%M%S") )
        self.logFile = "_log\\Fureai-Net_{}.log".format( self.today.strftime("%Y%m%d") )
        print('logFile:'+self.logFile)
        fh = logging.FileHandler( filename=self.logFile, mode='w', encoding='utf-8')
        fh.setLevel(logging.INFO)
        # fh.setFormatter(formatter)

        # rootロガーにハンドラーを登録する
        self.logger.addHandler(fh)

        # webdriver 初期化

        # Heroku以外ではNone
        options = Options()
        # isHeroku = os.getenv('IS_HEROKU',False)
        if self.isHeroku == True:

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

        else:  # PC環境
            #options.add_argument('--headless')
            self.driver = webdriver.Chrome(options=options)


        self.wait=WebDriverWait(self.driver,20)
        self.driver.implicitly_wait(30)


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
        url = "https://www.fureai-net.city.kawasaki.jp/user/view/user/homeIndex.html"
        self.driver.get(url)

        time.sleep(0.5)  # 待ちを入れてみる

        # ログインボタン押下
        # self.driver.find_element_by_id('login_on').click()
        self.driver.execute_script("javascript:return doSubmit('childForm', 'doLogin');")

        time.sleep(0.5)  # 待ちを入れてみる

        # ログイン（情報入力＆ログイン）
        userid = dic.card_ID[username]
        passwd = dic.card_PW[userid]

        self.driver.find_element_by_id('userid').send_keys(str(userid))
        self.driver.find_element_by_id('passwd').send_keys(str(passwd))
        self.driver.find_element_by_id('doLogin').click()

        time.sleep(0.5)  # 待ちを入れてみる

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

        time.sleep(0.5)  # 待ちを入れてみる

        # マイページが表示されているので
        # 予約情報を取得
        # 抽選申し込み数を取得
        rsvCount = 0
        rsvCount_elem = self.driver.find_elements_by_id("rsvNum")
        if len(rsvCount_elem) > 0:
            rsvCount = rsvCount_elem[0].text
            print('[施設予約 件数] {}件'.format(rsvCount))

        time.sleep(0.5)  # 待ちを入れてみる

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
            #result_msg += self._get_free_room2( date_from, date_to )

        # Reserve 各アカウントで収集
        if False:
        #if ("rsv" in self.EXEC_MODE):
            for login_name in dic.card_ID:
                print('アカウント:{}'.format(login_name))
                result_msg += self._login( login_name )

                # ログインできなかったら コンティニュー
                if self.login_state == False:
                    continue

                # 予約サーチする場合
                print('1:予約サーチ({})\n'.format(login_name))
                #result_msg += self._get_reserve_list( login_name )

                # 最後にログオフ
                result_msg += self._logoff()

        # LOT 各アカウントで収集
        if False:
        # if ("lot" in self.EXEC_MODE):
            for login_name in dic.card_ID:
                print('アカウント:{}'.format(login_name))
                result_msg += self._login( login_name )

                # ログインできなかったら コンティニュー
                if self.login_state == False:
                    continue

                # 抽選結果確認する場合
                print('3:抽選サーチ({})\n'.format(login_name))
                #result_msg += self._get_lot_list( login_name )

                # 最後にログオフ
                result_msg += self._logoff()

        return result_msg

    def _chk_mail_parameter(self):
        msg = '--- Mail Send Parameter ---\n'
        msg += 'SMTP_USER = {}\n'.format( self.SMTP_USER )
        msg += 'SMTP_PASSWD = {}\n'.format( self.SMTP_PASSWD)
        msg += 'FROM_ADDRESS = {}\n'.format( self.FROM_ADDRESS)
        msg += 'TO_ADDRESS = {}\n'.format( self.TO_ADDRESS)
        msg += 'CC_ADDRESS = {}\n'.format( self.CC_ADDRESS)
        msg += 'BCC_ADDRESS = {}\n'.format( self.BCC_ADDRESS)
        #print(msg)
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

        print('■ 現在時刻:{}:{}'.format(self.today.hour,self.today.time))



        # Heroku での 現在時刻に対応した 特殊処理
        if self.isHeroku == True:

            # =========================================
            # >>>> ここは Heroku の特殊処理 >>>>
            # =========================================

            # 実行時間による 処理制御

            # 1) 夜はやらない
            exclude_start = 0
            exclude_end = 6
            exclude_flg = False

            print('-- Heroku環境. 除外時刻:{}~{}'.format( exclude_start, exclude_end ))

            if ( exclude_start < self.today.hour) and (self.today.hour <= exclude_end):
                exclude_flg = True

            # 1) 除外条件に合致する場合は スキップ
            if exclude_flg == True:
                print('--> [スキップ]')
                return  # 抜けちゃう
            else:
                print('--> <実行>')

            # 2) rsv が付いていても 間引く
            if self.today.hour in  [6, 12, 16]:
                print('rsv 除外しない')
                pass
            else:
                self.EXEC_MODE = self.EXEC_MODE.replace("rsv", "")
                print('rsv 除外した　{}'.format(self.EXEC_MODE))

        # 3) 毎月 17~23日は 抽選状況チェックを追加
        if self.today.day in [17,18,19,20,21,22,23]:
            print('[抽選申込 期間]')
            self.EXEC_MODE = self.EXEC_MODE+'/lot'
        elif self.today.day in [24]:
            print('[抽選日]')
            self.EXEC_MODE = self.EXEC_MODE+'/lot'
        elif self.today.day in [25,26,27,28,29]:
            print('[確定 期間]')
            self.EXEC_MODE = self.EXEC_MODE+'/lot'
        else:
            print('--通常予約期間--')

        try:  # ===========================================
            # dataを読み込む
            FCHK_DATA = "data/fchk_data.csv"
            # rw_csv.read_data( FCHK_DATA, data.room_data )


            # メール送信パラメータチェック
            msg = self._chk_mail_parameter()
            #print(msg)
            self.logger.info(msg)

            # 今日の日付を取得
            today = datetime.datetime.now()

            # 開始日は今日の翌々月1日
            date_from = (today + relativedelta(months=2)
                       ).replace(day=1)


            # 23日-30/31までは、４か月後の月末
            # 1日～28日までは 3カ月後の月末
            if today.day >=17:
                addMonth = 5
            else:
                addMonth = 4
            date_to = (today + relativedelta(months=addMonth)
                       ).replace(day=1) - datetime.timedelta(days=1)

            # 取得開始
            msg = ''
            #msg = self._first_loop( date_from, date_to )

            # 空き探索する場合
            if ("chk" in self.EXEC_MODE):
                chk_list = make_chk_date_list()
                msg += chk_free_room(self,chk_list)
            #    msg += get_free_list(self, date_from, date_to)

            # RSV 各アカウントで収集
            if ("rsv" in self.EXEC_MODE):
                msg += get_rsv_list(self)

           # LOT 各アカウントで収集
            if ("lot" in self.EXEC_MODE):
                msg += get_lot_list(self)

            # 予約実行 予約リストで予約
            if ("dorsv" in self.EXEC_MODE):
                rsv_list.append(rsv_datum('歌の会', '2019', '11', '15', '', '麻生／視聴覚', '午後'))
                rsv_list.append(rsv_datum('歌の会', '2019', '12', '15', '', '高津／第２音楽', '午後'))
                msg = reserve_room(self, rsv_list)

            # =================================
            #   データ前処理
            # =================================

            # data をソート
            room_data2 = sorted( room_data, key=lambda x:(x[0],x[2],x[3],x[4]) )

            # dataを csv に 書き出す
            rw_csv.write_data( FCHK_DATA, room_data2 )

            # 各 要求ごとに 抽出
            chk_data = list( filter( lambda x: '空き' in x[0], room_data2 ) )
            rsv_data = list( filter( lambda x: '予約' in x[0], room_data2 ) )
            lot_data = list( filter( lambda x: '抽選' in x[0], room_data2 ) )

            chk_data2 = list( filter( lambda x: (x.pm in {'0','空'}) and (x.rank in {'〇', '◎', '◆'}), chk_data ) )
            rsv_data2 = list( filter( lambda x: (x.rank in {"〇","△","◆"}), rsv_data ) )


            # ログメッセージ
            # msg = ">> ふれあいネット <<\n"
            msg = "※{} 現在\n".format( today.strftime("%m/%d %H:%M"))
            mailMsg = ""

            # 空き情報２
            if ("chk" in self.EXEC_MODE) and (len(chk_data2)>0):
                print('>chk_start')
                # 期間
                # msg += "期間：{}～{}\n".format( date_from.strftime("%m-%d"), date_to.strftime("%m-%d"))
                # msg += "時間帯：午後（{}-{}時）の 空き会議室 \n".format( self.from_time, self.to_time )
                msg += "■ 空き会議室\n"

                # 収集リストの表示
                #for i in chk_data:
                #    if i.pm in {'0', '空'}:
                #        if i.rank in {'〇', '◎', '◆'}:
                            #('username','year', 'month', 'day', 'week', 'start','end',
                            # 'bname', 'iname',
                            # 'am', 'pm', 'night','rank')
                for i in chk_data2:
                            print( i )
                            msg += "{0} {1}/{2}{3} {4}~{5} {6}/{7}({8})\n".format(
                                i.username[0:1],
                                # str(i.year)[2:],
                                i.month, i.day, i.week,
                                i.start, i.end, i.bname, i.iname, i.rank )
                print('>chk_end')

            # 予約情報２
            if ("rsv" in self.EXEC_MODE):
                print('>rsv_start')
                # 期間
                msg += "■ 取りたい\n"

                # 収集リストの表示
                # 利用日時, 開始, 終了, 館名, 施設名, 支払状況
                #for i in rsv_data:
                #    if i.rank in {'◎'}:  # 最高の場所が確保できている
                #       pass
                #
                #    if i.rank in {"〇","△","◆"}:
                        # 最高ではない
                        # 今一つ
                        # 今一つか、ボイトレ用
                        #('username','year', 'month', 'day', 'week', 'start','end',
                        # 'bname', 'iname',
                        # 'am', 'pm', 'night','rank')
                for i in rsv_data2:
                    print( i )
                    msg += "{0} {1}/{2}{3} {4}~{5} {6}/{7}({8})\n".format(
                        i.username[0:1],
                        # str(i.year)[2:],
                        i.month, i.day, i.week,
                        i.start, i.end, i.bname, i.iname, i.rank )
                print('>rsv_end(1)')

            # 予約情報
            if ("rsv" in self.EXEC_MODE):
                print('>rsv_start')

                # 収集リストの表示
                # 期間
                msg += "■ 予約済 {}～{}\n".format( date_from.strftime("%m/%d"), date_to.strftime("%m/%d"))

                # 利用日時, 開始, 終了, 館名, 施設名, 支払状況
                for i in rsv_data:

                    print(i)
                    msg += "{0} {1}/{2}/{3} {4}~{5} {6}/{7}({8})\n".format(
                            i.username[0:1],
                            # str(i.year)[2:],
                            i.month, i.day, i.week,
                            i.start, i.end, i.bname, i.iname, i.rank )
                print('>rsv_end')

            # 抽選情報
            if ("lot" in self.EXEC_MODE):
                print('>lot_start')
                # 期間
                msg += "■ 抽選申込 {}～{}\n".format( date_from.strftime("%m-%d"), date_to.strftime("%m-%d"))

                # 収集リストの表示
                # 利用日時, 開始, 終了, 館名, 施設名, 支払状況
                for i in lot_data:
                    print(i)
                    msg += "{0} {1}/{2} {3}~{4} {5}/{6}({7})\n".format(
                        i.username[0:1],
                        # i.year,
                        i.month, i.day, i.start, i.end,
                        i.bname, i.iname, i.state )
                print('>lot_end')

            # 表示
            #print(msg)
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

