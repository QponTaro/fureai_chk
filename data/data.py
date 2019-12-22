# 名前付きタプル
from collections import namedtuple


# 利用日時, 開始, 終了, 館名, 施設名, 支払状況
schedule = namedtuple('schedule',
                      (
                          'year',
                          'month',
                          'day',
                          'week',
                          'start',
                          'end',
                          'kind',
                          'bname',
                          'iname',
                          'state',
                          'rank'
                      )
                      )

scheduleList = []
scheduleList.append(schedule('2019', '4', '27', '土', '13',
                             '17', '練習', '麻生', '視聴覚室', '確定', '◎'))
scheduleList.append(schedule('2019', '5', '11', '土', '13',
                             '17', '練習', '多摩', '視聴覚室', '確定', '◎'))
scheduleList.append(schedule('2019', '5', '19', '日', '13',
                             '17', '練習', '高津', '第１音楽室', '確定', '◎'))
scheduleList.append(schedule('2019', '6', '15', '土', '13',
                             '17', '練習', '麻生', '視聴覚室', '確定', '◎'))
scheduleList.append(schedule('2019', '6', '23', '日', '13',
                             '17', '練習', '多摩', '視聴覚室', '確定', '◎'))
scheduleList.append(schedule('2019', '6', '2', '日', '13',
                             '17', '全体ヴォイトレ', '中原', '音楽室', '確定', '◎'))
scheduleList.append(schedule('2019', '4', '28', '土', '13',
                             '17', 'ヴォイトレ', '多摩', '視聴覚室', '確定', '◎'))
scheduleList.append(schedule('2019', '5', '6', '土', '13',
                             '17', 'ヴォイトレ', '多摩', '視聴覚室', '確定', '◎'))


# 練習日
# 4/27（土）麻生市民館視聴覚室　午後　新美先生
# 5/11（土）多摩市民館視聴覚室　午後　佐藤先生
# 5/19（日）高津市民館第一音楽室　午後　新美先生
# 6/15（土）麻生市民館視聴覚室　午後　新美先生
# 6/23（日）多摩市民館視聴覚室　午後　佐藤先生
#
# 全体ヴォイトレ
# 6/2（日）中原市民館音楽室　午後　玉村・佐藤先生
#
# 個人ヴォイトレ
# 4/28（日）多摩市民館視聴覚室　午後
# 5/6（月）多摩市民館視聴覚室　午後

def chk_schedule(year, month, day):
    for sc in scheduleList:
        if(sc.year == year) and (sc.month == month) and (sc.day == day):
            return sc
        else:
            return None


# アカウント情報
accountInfo = namedtuple('accountInfo',
                         ('username', 'userid', 'passwd', 'rsvCount', 'lotCount')
                         )
accountInf = []

room_datum = namedtuple('room_datum',
                        (
                            'type',
                            'username',
                            'year', 'month', 'day', 'week',
                            'start', 'end',
                            'bname', 'iname',
                            'state',
                            'am', 'pm', 'night',
                            'rank',
                            'Tmanabu', 'Tsato', 'Tniimi', 'Ttamamura'
                        )
                        )
room_data = []

rsv_datum = namedtuple('rsv_datum',
                       (
                           'username',
                           'year', 'month', 'day', 'week',
                           'room',
                           'zone'
                       )
                       )
rsv_list = []

chk_datum = namedtuple('chk_datum',
                       (
                           'year', 'month', 'day', 'week',
                           'room',
                       )
                       )
chk_date = []

# 利用日時, 開始, 終了, 館名, 施設名, 支払状況
# rsvInfo = namedtuple('rsvInfo',
#    ('username','year', 'month', 'day', 'week', 'start','end','bname', 'iname', 'state','rank')
#    )
# rsvInf = []

# 利用日時, 開始, 終了, 館名, 施設名, 支払状況
# lotInfo = namedtuple('lotInfo',
#    ('username','year', 'month', 'day', 'week', 'start','end','bname', 'iname', 'state')
#    )
# lotInf = []


# room_stat = [ ["Year", "Month", "Day", "Week", "room", ["AM", "PM", "Night"] ] ]

# card_LIST = ["歌の会","高橋良"]


# 辞書定義
card_ID = {
    "歌の会": "5040302",
    "ハワイアン": "5106148",
    "ソレイユ": "5053167",
    #    "高橋良": "1270978",
}
card_RSV = {
    "歌の会": 0,
    "ハワイアン": 0,
    "ソレイユ": 0,
    #    "高橋良": 0,
}
card_LOT = {
    "歌の会": 0,
    "ハワイアン": 0,
    "ソレイユ": 0,
    #    "高橋良 ": 0,
}
card_PW = {
    "5040302": "1950",
    "5106148": "5963",
    "5053167": "1995",
    "1270978": "9981",
}
chorus_TYPE = [
    "演奏・合唱",
    "演奏（電気楽器不可）・合唱",
    "歌・演奏（小音量）"
]
chorus_ID = {
    "演奏・合唱": "2-210-210010",
    "演奏（電気楽器不可）・合唱": "2-210-210020",
    "歌・演奏（小音量）": "2-210-210030"
}

room_bcd = {
    "中原／音楽": "1180",
    "中原／視聴覚": "1180",
    "麻生／視聴覚": "1240",
    "麻生／大会議": "1240",
    "高津／第１音楽": "1190",
    "高津／第２音楽": "1190",
    "高津／視聴覚": "1190",
    "多摩／視聴覚": "1230",
    "宮前／視聴覚": "1210",
    "岡上／集会": "1250",
    "サンピアンかわさき／音楽": "1030",
    "教育文化会館／視聴覚": "1130",
}

room_icd = {
    "中原／音楽": "1180100",
    "中原／視聴覚": "1180090",
    "麻生／視聴覚": "1240100",
    "麻生／大会議": "1240020",
    "高津／第１音楽": "1190110",
    "高津／第２音楽": "1190120",
    "高津／視聴覚": "1190140",
    "多摩／視聴覚": "1230130",
    "宮前／視聴覚": "1210100",
    "岡上／集会": "1250010",
    "サンピアンかわさき／音楽": "1030220",
    "教育文化会館／視聴覚": "1130340",
}


# チェック対象の施設リスト
check_ROOMs = [
    "麻生／視聴覚",
    "多摩／視聴覚",

    "中原／音楽",
    "高津／第１音楽",
    "高津／第２音楽",

    "高津／視聴覚",
    "中原／視聴覚",

    "宮前／視聴覚",
    "岡上／集会",
]

# 参照用 施設リスト
chorus_ROOM = {
    "麻生／視聴覚": "◎",
    "多摩／視聴覚": "◎",

    "中原／音楽": "〇",
    "高津／第１音楽": "〇",

    "高津／視聴覚": "△",
    "中原／視聴覚": "△",
    "宮前／視聴覚": "△",
    "岡上／集会": "△",

    "高津／第２音楽": "◆",
    "麻生／大会議": "？",
    "サンピアンかわさき／音楽": "★",
    "教育文化会館／視聴覚": "★",
}

tzone_tbl = {
    "10": "午前",
    "20": "午後",
    "30": "夜間"
}

sel_value_tbl = {
    "0": "X",
    "-1": "O"
}

state_tbl = {
    "空き": "空",
    "予約": "無",
    "保守日・主催事業": "保",
    "休館": "休",
    "一般開放": "開",
    "雨天": "雨",
    "受付期間外": "外",
    "取消処理中": "取",
    "開放予定": "予",
    "時間帯なし": "無",

    "カート追加選択中": "選",
    "カート追加済": "済",
    "カート追加不可": "不",
}
