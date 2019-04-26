# 名前付きタプル
from collections import namedtuple



# 利用日時, 開始, 終了, 館名, 施設名, 支払状況
practiceInfo = namedtuple('practiceInfo', ('year', 'month', 'day', 'start', 'end', 'bname', 'iname', 'state', 'goodLevel'))
practiceInf = []


# アカウント情報
accountInfo = namedtuple('accountInfo',('username','userid','passwd','rsvCount','lotCount'))
accountInf = []

# 利用日時, 開始, 終了, 館名, 施設名, 支払状況
rsvInfo = namedtuple('rsvInfo', ('username','date','start','end','bname', 'iname', 'state','goodLevel'))
rsvInf = []

# 利用日時, 開始, 終了, 館名, 施設名, 支払状況
lotInfo = namedtuple('lotInfo', ('username','date','start','end','bname', 'iname', 'state'))
lotInf = []


roomStat = namedtuple('roomStat', ('year', 'month', 'day', 'week', 'room', 'am', 'pm', 'night','goodLevel'))
roomSt = []
room_stat = [["Year", "Month", "Day", "Week", "room", ["AM", "PM", "Night"]]]

reserveData = []

# 辞書定義
card_LIST = ["歌の会","高橋良"]

card_ID = {
    "歌の会": "5040302",
    "ハワイアン": "5106148",
    "ソレイユ": "5053167",
    "高橋良": "1270978",
}
card_RSV = {
    "歌の会": 0,
    "ハワイアン": 0,
    "ソレイユ": 0,
    "高橋良": 0,
}
card_LOT = {
    "歌の会": 0,
    "ハワイアン": 0,
    "ソレイユ": 0,
    "高橋良 ": 0,
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
    "高津／第１音楽": "1190",
    "高津／第２音楽": "1190",
    "高津／視聴覚": "1190",
    "多摩／視聴覚": "1230",
    "宮前／視聴覚": "1210",
    "岡上／集会": "1250"
}

room_icd = {
    "中原／音楽": "1180100",
    "中原／視聴覚": "1180090",
    "麻生／視聴覚": "1240100",
    "高津／第１音楽": "1190110",
    "高津／第２音楽": "1190120",
    "高津／視聴覚": "1190140",
    "多摩／視聴覚": "1230130",
    "宮前／視聴覚": "1210100",
    "岡上／集会": "1250010"
}

# 施設リスト
chorus_ROOM = {
    "麻生／視聴覚":"◎",
    "多摩／視聴覚":"◎",

    "中原／音楽":"〇",
    "高津／第１音楽":"〇",

    "高津／視聴覚":"△",
    "中原／視聴覚":"△",
    "宮前／視聴覚":"△",
    "岡上／集会":"△",

    "高津／第２音楽":"◆",
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
    "受付期間外": "外",
    "予約": "無",
    "空き": "空",
    "休館": "休"
}
