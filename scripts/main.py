"""
玄音八字 - 自包含八字命理计算引擎
依赖: pip install lunisolar-calendar
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from math import floor

try:
    from lunisolar_calendar import LunarDate, SolarDate
    HAS_LUNAR = True
except ImportError:
    HAS_LUNAR = False

TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
WUXING_TG = ["木", "木", "火", "火", "土", "土", "金", "金", "水", "水"]
WUXING_DZ = ["水", "土", "木", "木", "土", "火", "火", "土", "金", "金", "土", "水"]
YINYANG_TG = ["阳", "阴", "阳", "阴", "阳", "阴", "阳", "阴", "阳", "阴"]
YINYANG_DZ = ["阳", "阴", "阳", "阴", "阳", "阴", "阳", "阴", "阳", "阴", "阳", "阴"]
SHENGXIAO = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
CANGGAN = [
    [9], [5, 9, 7], [0, 2, 4], [1], [4, 1, 9], [2, 6, 4],
    [3, 5], [5, 3, 1], [6, 8, 4], [7], [4, 7, 3], [8, 0]
]
NAYIN_TABLE = {
    (0, 0): "海中金", (0, 1): "海中金", (1, 0): "炉中火", (1, 1): "炉中火",
    (2, 0): "大林木", (2, 1): "大林木", (3, 0): "路旁土", (3, 1): "路旁土",
    (4, 0): "剑锋金", (4, 1): "剑锋金", (5, 0): "山头火", (5, 1): "山头火",
    (6, 0): "涧下水", (6, 1): "涧下水", (7, 0): "城头土", (7, 1): "城头土",
    (8, 0): "白蜡金", (8, 1): "白蜡金", (9, 0): "杨柳木", (9, 1): "杨柳木",
    (10, 0): "泉中水", (10, 1): "泉中水", (11, 0): "屋上土", (11, 1): "屋上土",
    (12, 0): "霹雳火", (12, 1): "霹雳火", (13, 0): "松柏木", (13, 1): "松柏木",
    (14, 0): "长流水", (14, 1): "长流水", (15, 0): "沙中金", (15, 1): "沙中金",
    (16, 0): "山下火", (16, 1): "山下火", (17, 0): "平地木", (17, 1): "平地木",
    (18, 0): "壁上土", (18, 1): "壁上土", (19, 0): "金箔金", (19, 1): "金箔金",
    (20, 0): "覆灯火", (20, 1): "覆灯火", (21, 0): "天河水", (21, 1): "天河水",
    (22, 0): "大驿土", (22, 1): "大驿土", (23, 0): "钗钏金", (23, 1): "钗钏金",
    (24, 0): "桑柘木", (24, 1): "桑柘木", (25, 0): "大溪水", (25, 1): "大溪水",
    (26, 0): "沙中土", (26, 1): "沙中土", (27, 0): "天上火", (27, 1): "天上火",
    (28, 0): "石榴木", (28, 1): "石榴木", (29, 0): "大海水", (29, 1): "大海水",
}
SHISHEN_NAMES = ["比肩", "劫财", "食神", "伤官", "偏财", "正财", "七杀", "正官", "偏印", "正印"]
JIEQI_NAMES = [
    "小寒", "大寒", "立春", "雨水", "惊蛰", "春分",
    "清明", "谷雨", "立夏", "小满", "芒种", "夏至",
    "小暑", "大暑", "立秋", "处暑", "白露", "秋分",
    "寒露", "霜降", "立冬", "小雪", "大雪", "冬至"
]
JIEQI_APPROX = [
    (1, 6), (1, 20), (2, 4), (2, 19), (3, 6), (3, 21),
    (4, 5), (4, 20), (5, 6), (5, 21), (6, 6), (6, 21),
    (7, 7), (7, 23), (8, 7), (8, 23), (9, 8), (9, 23),
    (10, 8), (10, 23), (11, 7), (11, 22), (12, 7), (12, 22)
]
YI_JIN = {
    1: "祭祀,解除,断蚁,会亲友", 2: "祭祀,祈福,求嗣,解除", 3: "祭祀,祈福,求嗣,开光",
    4: "祭祀,祈福,求嗣,开光", 5: "祭祀,祈福,出行,嫁娶", 6: "祭祀,祈福,求嗣,开光",
    7: "祭祀,祈福,求嗣,开光", 8: "祭祀,出行,嫁娶,修造", 9: "祭祀,出行,修造,动土",
    10: "祭祀,出行,修造,动土", 11: "祭祀,祈福,求嗣,开光", 12: "祭祀,祈福,求嗣,开光"
}
JI_JIN = {
    1: "嫁娶,开市,动土", 2: "动土,破土", 3: "动土,破土,嫁娶",
    4: "动土,破土", 5: "动土,破土,安葬", 6: "动土,破土,安葬",
    7: "动土,破土,安葬", 8: "破土,安葬", 9: "破土,安葬,嫁娶",
    10: "破土,安葬", 11: "破土,安葬,嫁娶", 12: "破土,安葬"
}
SHENSHA_MAP = {
    "天乙贵人": {0: [1, 9], 1: [0, 8], 2: [1, 9], 3: [0, 8], 4: [1, 9], 5: [0, 8], 6: [1, 9], 7: [0, 8], 8: [1, 9], 9: [0, 8]},
    "文昌": {0: [9], 1: [0], 2: [3], 3: [4], 4: [5], 5: [6], 6: [7], 7: [8], 8: [9], 9: [0]},
    "将星": {0: [0], 1: [1], 2: [2], 3: [3], 4: [4], 5: [5], 6: [6], 7: [7], 8: [8], 9: [9]},
}


def GetGanZhi_Year(year):
    """
    计算年柱天干地支
    以公元4年为甲子年（基准年）
    天干索引: 甲(0)乙(1)丙(2)丁(3)戊(4)己(5)庚(6)辛(7)壬(8)癸(9)
    地支索引: 子(0)丑(1)寅(2)卯(3)辰(4)巳(5)午(6)未(7)申(8)酉(9)戌(10)亥(11)
    """
    return (year - 4) % 10, (year - 4) % 12


def GetGanZhi_Month(year, month, day):
    """
    计算月柱天干地支
    使用五虎遁月法：根据年干推算月干基准
    月支从寅月开始（正月建寅）
    考虑节气交接：未过节气则属于上一月
    
    节气规律：
    - 每月月首节气：小寒(1月6日)、立春(2月4日)、惊蛰(3月6日)、清明(4月5日)、立夏(5月6日)...
    - 月支对应：子(11月)、丑(12月)、寅(1月)、卯(2月)、辰(3月)、巳(4月)...
    """
    year_gan = (year - 4) % 10
    month_gan_base = (year_gan % 5) * 2
    jieqi_idx = ((month - 1) % 12) * 2
    jieqi_day = _GetJieqiDay(year, jieqi_idx)
    actual_month = month
    if day < jieqi_day:
        actual_month = month - 1 if month > 1 else 12
    month_zhi = actual_month % 12
    month_gan = (month_gan_base + actual_month - 1) % 10
    return month_gan, month_zhi


def GetGanZhi_Day(year, month, day):
    """
    计算日柱天干地支
    以1900年1月1日为基准日（甲戌日）
    甲(0)戌(10) -> 天干偏移0，地支偏移10
    """
    try:
        dt = datetime(year, month, day)
    except ValueError:
        return 0, 0
    base = datetime(1900, 1, 1)
    delta = (dt - base).days
    day_gan = (delta + 0) % 10
    day_dz = (delta + 10) % 12
    return day_gan, day_dz


def GetGanZhi_Hour(hour, day_gan, early_zi=2):
    """
    计算时柱天干地支
    使用五鼠遁时法：根据日干推算时干基准
    时辰划分：子时(23-1点)、丑时(1-3点)、寅时(3-5点)...
    early_zi: 1=早子时(23点归次日), 2=晚子时(23点归当日, 默认)
    """
    dz = ((hour + 1) // 2) % 12
    gan_base = (day_gan % 5) * 2
    hour_gan = (gan_base + dz) % 10
    if early_zi == 1 and hour == 23:
        next_day_gan = (day_gan + 1) % 10
        gan_base = (next_day_gan % 5) * 2
        hour_gan = (gan_base + dz) % 10
    return hour_gan, dz


def _GetJieqiDay(year, jq_idx):
    jq_idx = jq_idx % 24
    m, d = JIEQI_APPROX[jq_idx]
    return d


def GetJieqi(year, month, day):
    idx = (month - 1) * 2
    d1 = _GetJieqiDay(year, idx)
    d2 = _GetJieqiDay(year, idx + 1)
    if day < d1:
        prev_idx = (idx - 1) % 24
        return JIEQI_NAMES[prev_idx]
    elif day < d2:
        return JIEQI_NAMES[idx]
    else:
        return JIEQI_NAMES[idx + 1] if idx + 1 < 24 else JIEQI_NAMES[0]


def GetShiShen(day_gan, other_gan):
    """
    计算十神关系
    根据日干与其他天干的五行生克关系和阴阳属性判断
    十神：比肩、劫财、食神、伤官、偏财、正财、七杀、正官、偏印、正印
    """
    day_wx = WUXING_TG[day_gan]
    other_wx = WUXING_TG[other_gan]
    day_yy = YINYANG_TG[day_gan]
    other_yy = YINYANG_TG[other_gan]
    same_yy = (day_yy == other_yy)
    wx_list = ["木", "火", "土", "金", "水"]
    d_idx = wx_list.index(day_wx)
    o_idx = wx_list.index(other_wx)
    rel = (o_idx - d_idx) % 5
    if rel == 0:
        return "比肩" if same_yy else "劫财"
    elif rel == 1:
        return "食神" if same_yy else "伤官"
    elif rel == 2:
        return "偏财" if same_yy else "正财"
    elif rel == 3:
        return "七杀" if same_yy else "正官"
    else:
        return "偏印" if same_yy else "正印"


def GetNayin(gan_idx, zhi_idx):
    """
    计算纳音五行
    六十甲子纳音：每两个干支为一组，共30组
    如甲子乙丑海中金、丙寅丁卯炉中火等
    """
    jiazi_idx = (gan_idx * 6 + zhi_idx * 5) % 30
    pair_idx = jiazi_idx // 2
    return NAYIN_TABLE.get((pair_idx, jiazi_idx % 2), "未知")


def GetShenSha(gan_idx, zhi_idx, day_gan):
    """
    计算神煞
    主要神煞：天乙贵人、文昌、将星、福星贵人等
    根据日干和地支的组合关系判断
    """
    result = []
    for name, mapping in SHENSHA_MAP.items():
        if day_gan in mapping and zhi_idx in mapping[day_gan]:
            result.append(name)
    if zhi_idx in [2, 3, 6, 7]:
        result.append("将星")
    if (gan_idx + zhi_idx) % 2 == 0 and zhi_idx in [3, 6, 9, 0]:
        result.append("福星贵人")
    return list(set(result))


def GetDaYun(year_gan, year_zhi, month_gan, month_zhi, gender, year, day_gan):
    """
    计算大运
    根据性别和年干阴阳判断顺逆：
    - 阳男阴女：顺行
    - 阴男阳女：逆行
    大运从月柱开始，每步大运10年
    """
    forward = (gender == 1 and year_gan % 2 == 0) or (gender == 0 and year_gan % 2 == 1)
    start_age = 1
    start_year = year + start_age
    result = []
    cur_gan = month_gan
    cur_zhi = month_zhi
    for i in range(10):
        if i > 0:
            cur_gan = (cur_gan + (1 if forward else -1)) % 10
            cur_zhi = (cur_zhi + (1 if forward else -1)) % 12
        begin_year = start_year + i * 10
        end_year = begin_year + 9
        begin_age = start_age + i * 10
        end_age = begin_age + 9
        shishen = GetShiShen(day_gan, cur_gan)
        result.append({
            "干支": TIANGAN[cur_gan] + DIZHI[cur_zhi],
            "天干": TIANGAN[cur_gan],
            "地支": DIZHI[cur_zhi],
            "天干十神": shishen,
            "开始年份": begin_year,
            "结束年份": end_year,
            "开始年龄": begin_age,
            "结束年龄": end_age,
        })
    return result, start_age, start_year


def GetXingChongHeHui(pillars):
    """
    计算四柱间的刑冲合会关系
    天干相冲：甲庚冲、乙辛冲、丙壬冲、丁癸冲
    地支六冲：子午、丑未、寅申、卯酉、辰戌、巳亥
    地支六合：子丑合土、寅亥合木、卯戌合火、辰酉合金、巳申合水、午未合土
    地支自刑：辰辰、午午、酉酉、亥亥
    """
    result = {"年": {"天干": {}, "地支": {}}, "月": {"天干": {}, "地支": {}},
              "日": {"天干": {}, "地支": {}}, "时": {"天干": {}, "地支": {}}}
    chong_tg = {0: 6, 1: 7, 2: 8, 3: 9, 4: 0, 5: 1, 6: 0, 7: 1, 8: 2, 9: 3}
    chong_dz = {0: 6, 1: 7, 2: 8, 3: 9, 4: 10, 5: 11, 6: 0, 7: 1, 8: 2, 9: 3, 10: 4, 11: 5}
    he_dz = {(0, 1): "土", (2, 11): "木", (3, 10): "火", (4, 9): "金", (5, 8): "水", (6, 7): "土"}
    pos_names = ["年", "月", "日", "时"]
    for i in range(4):
        for j in range(i + 1, 4):
            gi, gj = pillars[i][0], pillars[j][0]
            if chong_tg.get(gi) == gj:
                result[pos_names[i]]["天干"].setdefault("冲", []).append(
                    {"柱": pos_names[j], "知识点": f"{TIANGAN[gi]}{TIANGAN[gj]}相冲"})
                result[pos_names[j]]["天干"].setdefault("冲", []).append(
                    {"柱": pos_names[i], "知识点": f"{TIANGAN[gj]}{TIANGAN[gi]}相冲"})
            zi, zj = pillars[i][1], pillars[j][1]
            if chong_dz.get(zi) == zj:
                result[pos_names[i]]["地支"].setdefault("冲", []).append(
                    {"柱": pos_names[j], "知识点": f"{DIZHI[zi]}{DIZHI[zj]}相冲"})
                result[pos_names[j]]["地支"].setdefault("冲", []).append(
                    {"柱": pos_names[i], "知识点": f"{DIZHI[zj]}{DIZHI[zi]}相冲"})
            pair = (min(zi, zj), max(zi, zj))
            if pair in he_dz:
                result[pos_names[i]]["地支"].setdefault("合", []).append(
                    {"柱": pos_names[j], "知识点": f"{DIZHI[zi]}{DIZHI[zj]}相合"})
                result[pos_names[j]]["地支"].setdefault("合", []).append(
                    {"柱": pos_names[i], "知识点": f"{DIZHI[zj]}{DIZHI[zi]}相合"})
            if zi == zj and zi in [6, 9, 4, 11]:
                result[pos_names[i]]["地支"].setdefault("刑", []).append(
                    {"柱": pos_names[j], "知识点": f"{DIZHI[zi]}{DIZHI[zj]}相刑"})
                result[pos_names[j]]["地支"].setdefault("刑", []).append(
                    {"柱": pos_names[i], "知识点": f"{DIZHI[zj]}{DIZHI[zi]}相刑"})
    return result


def GetPillarInfo(gan, zhi, day_gan, position):
    shishen = "日主" if position == "日" else GetShiShen(day_gan, gan)
    canggan_list = CANGGAN[zhi]
    canggan_info = []
    for idx, cg in enumerate(canggan_list):
        label = ["主气", "中气", "余气"][idx] if idx < 3 else f"气{idx}"
        canggan_info.append({
            label: {
                "天干": TIANGAN[cg],
                "五行": WUXING_TG[cg],
                "十神": GetShiShen(day_gan, cg)
            }
        })
    shensha = GetShenSha(gan, zhi, day_gan)
    return {
        "天干": {
            "天干": TIANGAN[gan],
            "五行": WUXING_TG[gan],
            "阴阳": YINYANG_TG[gan],
            "十神": shishen
        },
        "地支": {
            "地支": DIZHI[zhi],
            "五行": WUXING_DZ[zhi],
            "阴阳": YINYANG_DZ[zhi],
            "藏干": canggan_info
        },
        "纳音": GetNayin(gan, zhi),
        "神煞": shensha
    }


def Action_BaziDetail(gender, solar_datetime, early_zi=2):
    """
    八字排盘主函数
    计算完整的八字信息，包括四柱、五行、十神、神煞、刑冲合会、大运等
    
    参数:
        gender: 性别 (1=男, 0=女)
        solar_datetime: 公历时间 (ISO格式)
        early_zi: 早晚子时处理 (1=早子时, 2=晚子时, 默认晚子时)
    
    返回:
        包含完整八字信息的字典
    """
    dt = datetime.fromisoformat(solar_datetime)
    year, month, day, hour = dt.year, dt.month, dt.day, dt.hour
    yg, yz = GetGanZhi_Year(year)
    mg, mz = GetGanZhi_Month(year, month, day)
    dg, dz = GetGanZhi_Day(year, month, day)
    hg, hz = GetGanZhi_Hour(hour, dg, early_zi)
    pillars = [(yg, yz), (mg, mz), (dg, dz), (hg, hz)]
    bazi_str = f"{TIANGAN[yg]}{DIZHI[yz]} {TIANGAN[mg]}{DIZHI[mz]} {TIANGAN[dg]}{DIZHI[dz]} {TIANGAN[hg]}{DIZHI[hz]}"
    result = {
        "性别": "男" if gender == 1 else "女",
        "阳历": dt.strftime("%Y年%m月%d日 %H:%M:%S"),
        "八字": bazi_str,
        "生肖": SHENGXIAO[yz],
        "日主": TIANGAN[dg],
        "日主五行": WUXING_TG[dg],
        "年柱": GetPillarInfo(yg, yz, dg, "年"),
        "月柱": GetPillarInfo(mg, mz, dg, "月"),
        "日柱": GetPillarInfo(dg, dz, dg, "日"),
        "时柱": GetPillarInfo(hg, hz, dg, "时"),
        "刑冲合会": GetXingChongHeHui(pillars),
    }
    dayun, start_age, start_year = GetDaYun(yg, yz, mg, mz, gender, year, dg)
    result["大运"] = {
        "起运年龄": start_age,
        "大运": dayun
    }
    wuxing_count = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    for gan, zhi in pillars:
        wuxing_count[WUXING_TG[gan]] += 1
        wuxing_count[WUXING_DZ[zhi]] += 1
    result["五行统计"] = wuxing_count
    return result


def Action_HuangLi(solar_datetime=None):
    if solar_datetime:
        dt = datetime.fromisoformat(solar_datetime)
    else:
        dt = datetime.now()
    year, month, day = dt.year, dt.month, dt.day
    yg, yz = GetGanZhi_Year(year)
    mg, mz = GetGanZhi_Month(year, month, day)
    dg, dz = GetGanZhi_Day(year, month, day)
    ganzhi = f"{TIANGAN[yg]}{DIZHI[yz]} {TIANGAN[mg]}{DIZHI[mz]} {TIANGAN[dg]}{DIZHI[dz]}"
    jieqi = GetJieqi(year, month, day)
    weekday_names = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    weekday = weekday_names[dt.weekday()]
    yi = YI_JIN.get(month, "祭祀,解除")
    ji = JI_JIN.get(month, "嫁娶,动土")
    caishen_pos = ["东北", "西南", "正北", "正东", "东南", "正南", "西南", "正西", "东北", "正北"]
    caishen = caishen_pos[dg % 10]
    result = {
        "公历": f"{year}年{month}月{day}日 {weekday}",
        "干支": ganzhi,
        "生肖": SHENGXIAO[yz],
        "节气": jieqi,
        "财神方位": caishen,
        "宜": yi,
        "忌": ji,
    }
    if HAS_LUNAR:
        try:
            solar = SolarDate(year, month, day)
            lunar = solar.to_lunar_date()
            result["农历"] = f"农历{lunar.year}年{lunar.month}月{lunar.day}日"
        except Exception:
            result["农历"] = "需安装lunisolar-calendar"
    else:
        result["农历"] = "需安装lunisolar-calendar获取农历"
    return result


def Action_ReverseBazi(bazi_str):
    parts = bazi_str.strip().split()
    if len(parts) != 4:
        return {"error": "八字格式应为: 年柱 月柱 日柱 时柱 (如: 庚午 壬午 辛亥 甲午)"}
    pillars = []
    for p in parts:
        if len(p) != 2:
            return {"error": f"无效柱: {p}"}
        tg = p[0]
        dz = p[1]
        if tg not in TIANGAN or dz not in DIZHI:
            return {"error": f"无效天干地支: {p}"}
        pillars.append((TIANGAN.index(tg), DIZHI.index(dz)))
    yg, yz, mg, mz, dg, dz, hg, hz = [x for pair in pillars for x in pair]
    results = []
    base_year = 4
    for offset in range(0, 6000, 60):
        year = base_year + offset + yg
        if year < 1800 or year > 2100:
            continue
        for month in range(1, 13):
            try:
                cmg, cmz = GetGanZhi_Month(year, month, 15)
                if cmg != mg or cmz != mz:
                    continue
                for day in range(1, 32):
                    try:
                        cdg, cdz = GetGanZhi_Day(year, month, day)
                        if cdg != dg or cdz != dz:
                            continue
                        for h in range(0, 24, 2):
                            chg, chz = GetGanZhi_Hour(h, cdg)
                            if chg == hg and chz == hz:
                                results.append(f"{year}-{month:02d}-{day:02d} {h:02d}:00:00")
                    except ValueError:
                        continue
            except Exception:
                continue
    return {"八字": bazi_str, "对应公历时间": results}


WX_CHARACTER = {
    "木": {"阳": "刚直不阿、积极向上", "阴": "柔顺温和、灵活变通"},
    "火": {"阳": "热情奔放、光明磊落", "阴": "细腻敏感、礼数周到"},
    "土": {"阳": "笃实厚重、包容大度", "阴": "谨慎保守、思虑周密"},
    "金": {"阳": "果断刚毅、重义轻财", "阴": "精明细腻、追求完美"},
    "水": {"阳": "聪慧灵动、足智多谋", "阴": "沉静内敛、洞察力强"},
}
WX_VIRTUE = {"木": "仁", "火": "礼", "土": "信", "金": "义", "水": "智"}
WX_ORGAN = {"木": ("肝", "胆"), "火": ("心", "小肠"), "土": ("脾", "胃"), "金": ("肺", "大肠"), "水": ("肾", "膀胱")}
WX_ILLNESS_HI = {"木": "肝气郁结、头痛眩晕", "火": "心火旺盛、失眠烦躁", "土": "脾胃湿热、消化不良", "金": "肺热咳嗽、皮肤干燥", "水": "肾阳过亢、水肿"}
WX_ILLNESS_LO = {"木": "肝血不足、视力下降", "火": "心血不足、面色苍白", "土": "脾胃虚弱、食欲不振", "金": "肺气不足、易感冒", "水": "肾气不足、腰膝酸软"}
SS_TRAIT = {
    "比肩": ("固执己见、竞争心重", "独立自主、同辈缘好", "依赖心重、缺乏主见"),
    "劫财": ("冲动莽撞、争夺好斗", "果敢有魄力、善合作", "胆小怕事、不善交际"),
    "食神": ("懒散享乐、缺乏进取", "温和有福、才华内敛", "劳碌辛苦、缺乏享受"),
    "伤官": ("叛逆傲慢、口无遮拦", "才华横溢、思维敏捷", "拘谨保守、缺乏创意"),
    "偏财": ("挥霍无度、投机冒险", "交际广泛、财运灵活", "守财吝啬、缺乏机缘"),
    "正财": ("守旧吝啬、缺乏魄力", "勤俭务实、收入稳定", "财来财去、不善理财"),
    "七杀": ("暴躁偏激、压力重重", "魄力过人、权威显赫", "胆小怯懦、缺乏主见"),
    "正官": ("拘泥守规、缺乏变通", "正直守纪、仕途可期", "不服约束、目无法纪"),
    "偏印": ("孤僻古怪、多疑敏感", "偏才出众、悟性极高", "缺乏灵感、思维迟钝"),
    "正印": ("依赖心重、缺乏独立", "学业有成、仁慈宽厚", "知识浅薄、缺乏靠山"),
}
SS_INDUSTRY = {
    "正官": "公务员、行政管理、法律、审计",
    "七杀": "军警、外科医生、创业、竞争行业",
    "正印": "教育、学术、出版、公益",
    "偏印": "技术、研发、玄学、心理咨询",
    "食神": "文艺、餐饮、旅游、教育",
    "伤官": "设计、表演、律师、自由职业",
    "正财": "金融、会计、零售、制造业",
    "偏财": "投资、贸易、中介、公关",
    "比肩": "体育、竞争性行业、合伙经营",
    "劫财": "销售、中介、竞争性行业",
}
SS_SPOUSE_M = {
    "比肩": "独立自主、同辈感", "劫财": "强势好胜、争执多", "食神": "温和贤惠、善持家",
    "伤官": "才华出众、个性强", "偏财": "善交际、理财灵活", "正财": "贤惠持家、稳重",
    "七杀": "霸道强势、有魄力", "正官": "端庄正派、守规矩", "偏印": "聪慧但孤僻", "正印": "仁慈善良、善照顾",
}
SS_SPOUSE_F = {
    "比肩": "独立自主、同辈感", "劫财": "强势好胜、争执多", "食神": "温和体贴、善照顾",
    "伤官": "才华出众、管束严", "偏财": "事业型、善经营", "正财": "事业稳定、有责任感",
    "七杀": "有权威、责任感强", "正官": "正直有担当、事业心", "偏印": "聪明但不够体贴", "正印": "温和善良、善持家",
}
SHENSHA_DESC = {
    "天乙贵人": "一生有贵人提携，遇难呈祥 ▲",
    "文昌": "聪明好学，文才出众，利考试 ▲",
    "将星": "有领导才能，威严果断 ▲",
    "福星贵人": "福禄双全，一生平安 ▲",
    "驿马": "奔波变动，宜出外发展 ─",
    "桃花": "人缘魅力，感情丰富 ─",
    "华盖": "性情孤高，喜艺术宗教 ─",
    "劫煞": "竞争损耗，防意外破财 ▼",
    "空亡": "虚幻不实，缘薄 ▼",
}


def _JudgeWangShuai(day_gan, month_zhi, pillars, wuxing_count):
    day_wx = WUXING_TG[day_gan]
    wx_order = ["木", "火", "土", "金", "水"]
    d_idx = wx_order.index(day_wx)
    month_wx = WUXING_DZ[month_zhi]
    de_ling = month_wx in [day_wx, wx_order[(d_idx + 4) % 5]]
    sheng_fu = wuxing_count[day_wx] + wuxing_count[wx_order[(d_idx + 4) % 5]]
    ke_xie = 0
    for i in range(5):
        if i != d_idx and i != (d_idx + 4) % 5:
            ke_xie += wuxing_count[wx_order[i]]
    if de_ling and sheng_fu > ke_xie:
        level = "偏旺"
    elif not de_ling and ke_xie > sheng_fu:
        level = "偏弱"
    else:
        level = "中和"
    return level, de_ling, sheng_fu, ke_xie


def _GetGeJu(month_zhi, month_gan, day_gan, pillars):
    canggan = CANGGAN[month_zhi]
    for cg in canggan:
        ss = GetShiShen(day_gan, cg)
        if ss in ["正官", "七杀", "正印", "偏印", "食神", "伤官", "正财", "偏财"]:
            for gan, _ in pillars:
                if gan == cg and gan != day_gan:
                    return f"{ss}格"
            return f"{ss}格(不透)"
    return "无格"


def Action_Report(gender, solar_datetime, early_zi=2):
    data = Action_BaziDetail(gender, solar_datetime, early_zi)
    dt = datetime.fromisoformat(solar_datetime)
    year, month, day, hour = dt.year, dt.month, dt.day, dt.hour
    yg, yz = GetGanZhi_Year(year)
    mg, mz = GetGanZhi_Month(year, month, day)
    dg, dz = GetGanZhi_Day(year, month, day)
    hg, hz = GetGanZhi_Hour(hour, dg, early_zi)
    pillars = [(yg, yz), (mg, mz), (dg, dz), (hg, hz)]
    wuxing_count = data["五行统计"]
    lines = []
    lines.append("# 玄音八字 · 命理分析报告\n")
    lines.append("## 基础信息\n")
    lines.append(f"| 项目 | 内容 |")
    lines.append(f"|------|------|")
    lines.append(f"| 性别 | {data['性别']} |")
    lines.append(f"| 阳历 | {data['阳历']} |")
    lines.append(f"| 八字 | **{data['八字']}** |")
    lines.append(f"| 生肖 | {data['生肖']} |")
    lines.append(f"| 日主 | **{data['日主']}**（{data['日主五行']}） |")
    lines.append("")
    lines.append("## 四柱详析\n")
    lines.append("| 柱位 | 天干 | 五行 | 十神 | 地支 | 五行 | 藏干 | 纳音 |")
    lines.append("|------|------|------|------|------|------|------|------|")
    pos_names = ["年柱", "月柱", "日柱", "时柱"]
    pos_labels = ["年", "月", "日", "时"]
    for pn, pl in zip(pos_names, pos_labels):
        p = data[pn]
        cg_str = "/".join([list(v.values())[0]["天干"] for v in p["地支"]["藏干"]])
        lines.append(f"| {pl} | {p['天干']['天干']} | {p['天干']['五行']} | {p['天干']['十神']} | {p['地支']['地支']} | {p['地支']['五行']} | {cg_str} | {p['纳音']} |")
    lines.append("")
    wx_sorted = sorted(wuxing_count.items(), key=lambda x: -x[1])
    lines.append("## 五行统计\n")
    lines.append("| 五行 | 木 | 火 | 土 | 金 | 水 |")
    lines.append("|------|----|----|----|----|----|")
    lines.append(f"| 次数 | {wuxing_count['木']} | {wuxing_count['火']} | {wuxing_count['土']} | {wuxing_count['金']} | {wuxing_count['水']} |")
    wx_max = wx_sorted[0]
    wx_min = wx_sorted[-1]
    lines.append(f"\n最旺: **{wx_max[0]}**({wx_max[1]})  最弱: **{wx_min[0]}**({wx_min[1]})\n")
    level, de_ling, sheng_fu, ke_xie = _JudgeWangShuai(dg, mz, pillars, wuxing_count)
    lines.append("## 日主旺衰\n")
    de_str = "得令" if de_ling else "失令"
    lines.append(f"日主**{data['日主']}**({data['日主五行']})，{de_str}，生扶力量={sheng_fu}，克泄力量={ke_xie}")
    if level == "偏旺":
        lines.append(f"→ 日主**偏旺**，宜以克泄耗为用，取食伤泄秀或财官制衡")
    elif level == "偏弱":
        lines.append(f"→ 日主**偏弱**，宜以生扶为用，取印星生身或比劫助身")
    else:
        lines.append(f"→ 日主**中和**，命局平衡度好，行运适应面广")
    lines.append("")
    geju = _GetGeJu(mz, mg, dg, pillars)
    lines.append("## 格局\n")
    lines.append(f"**{geju}**\n")
    ss_count = {}
    for pn in pos_names:
        if pn == "日柱":
            continue
        ss = data[pn]["天干"]["十神"]
        ss_count[ss] = ss_count.get(ss, 0) + 1
    lines.append("## 性格倾向\n")
    day_wx = data["日主五行"]
    day_yy = YINYANG_TG[dg]
    lines.append(f"日主{data['日主']}({day_wx})，{WX_VIRTUE[day_wx]}德为先，性格基调：{WX_CHARACTER[day_wx][day_yy]}")
    top_ss = sorted(ss_count.items(), key=lambda x: -x[1])[:3]
    if top_ss:
        ss_desc = "、".join([f"{s}(适中: {SS_TRAIT[s][1]})" for s, _ in top_ss])
        lines.append(f"主要十神：{ss_desc}")
    lines.append("")
    lines.append("## 事业方向\n")
    if top_ss:
        ind_desc = "；".join([f"{s}→{SS_INDUSTRY[s]}" for s, _ in top_ss[:2]])
        lines.append(f"十神取象：{ind_desc}")
    wx_industry = {"木": "农林、教育、文化", "火": "能源、IT、电子", "土": "房地产、建筑、农业", "金": "金融、机械、法律", "水": "物流、传媒、旅游"}
    lines.append(f"五行取行业：{day_wx}→{wx_industry.get(day_wx, '综合')}")
    lines.append("")
    lines.append("## 财运分析\n")
    has_zhengcai = "正财" in ss_count
    has_piancai = "偏财" in ss_count
    has_shishang = "食神" in ss_count or "伤官" in ss_count
    if has_zhengcai and has_shishang:
        lines.append("食伤生财，才华可转化为财富，宜穏健经营 ▲")
    elif has_piancai:
        lines.append("偏财明显，财运灵活但波动大，宜短线操作忌贪 ─")
    elif has_zhengcai:
        lines.append("正财为主，收入穏定，宜勤俭持家 ▲")
    else:
        lines.append("财星不显，财运需待大运流年触发 ─")
    if level == "偏旺" and not has_zhengcai and not has_piancai:
        lines.append("身旺财弱，有力无财，待财运到时发力")
    elif level == "偏弱" and (has_zhengcai or has_piancai):
        lines.append("财多身弱，宜合作求财，不宜独担")
    lines.append("")
    lines.append("## 感情婚姻\n")
    dz_ss = GetShiShen(dg, CANGGAN[dz][0])
    spouse_map = SS_SPOUSE_M if gender == 1 else SS_SPOUSE_F
    lines.append(f"日支（配偶宫）藏干主气十神为**{dz_ss}**，配偶倾向：{spouse_map.get(dz_ss, '待分析')}")
    xch = data["刑冲合会"]
    if "冲" in xch.get("日", {}).get("地支", {}):
        lines.append("⚠ 日支逢冲，婚姻宫不稳，宜晚婚或异地姻缘 ▼")
    if gender == 0 and "伤官" in ss_count and "正官" in ss_count:
        lines.append("⚠ 女命伤官见官，感情多波折，宜找年龄差距大者 ▼")
    lines.append("")
    lines.append("## 健康提示\n")
    lines.append(f"最旺五行{wx_max[0]}过旺易致：{WX_ILLNESS_HI.get(wx_max[0], '待分析')}")
    lines.append(f"最弱五行{wx_min[0]}过弱易致：{WX_ILLNESS_LO.get(wx_min[0], '待分析')}")
    organ = WX_ORGAN.get(day_wx, ("", ""))
    lines.append(f"日主五行对应脏腑：{organ[0]}/{organ[1]}，需重点保养")
    lines.append("")
    lines.append("## 神煞\n")
    lines.append("| 柱位 | 神煞 |")
    lines.append("|------|------|")
    for pn, pl in zip(pos_names, pos_labels):
        ss_list = data[pn].get("神煞", [])
        ss_str = "、".join(ss_list) if ss_list else "—"
        lines.append(f"| {pl} | {ss_str} |")
    lines.append("")
    important_ss = []
    for pn in pos_names:
        for s in data[pn].get("神煞", []):
            if s in SHENSHA_DESC and s not in [x[0] for x in important_ss]:
                important_ss.append((s, SHENSHA_DESC[s]))
    if important_ss:
        lines.append("重点神煞解读：")
        for s, d in important_ss:
            lines.append(f"- **{s}**：{d}")
    lines.append("")
    lines.append("## 刑冲合会\n")
    has_relation = False
    for pos in ["年", "月", "日", "时"]:
        for part in ["天干", "地支"]:
            for rel_type, items in xch.get(pos, {}).get(part, {}).items():
                for item in items:
                    lines.append(f"- {pos}柱{part}·{rel_type}：{item['知识点']}（与{item['柱']}柱）")
                    has_relation = True
    if not has_relation:
        lines.append("四柱间无明显刑冲合会关系")
    lines.append("")
    lines.append("## 大运走势\n")
    dayun_data = data["大运"]
    lines.append(f"起运年龄：{dayun_data['起运年龄']}岁\n")
    lines.append("| 大运 | 年龄 | 年份 | 干支 |")
    lines.append("|------|------|------|------|")
    for dy in dayun_data["大运"]:
        lines.append(f"| {dy['干支']} | {dy['开始年龄']}-{dy['结束年龄']} | {dy['开始年份']}-{dy['结束年份']} | {dy['天干']}{dy['地支']} |")
    lines.append("")
    current_year = datetime.now().year
    current_age = current_year - year
    for dy in dayun_data["大运"]:
        if dy["开始年份"] <= current_year <= dy["结束年份"]:
            lines.append("## 当前运势\n")
            lines.append(f"当前{current_year}年，{current_age}岁，行**{dy['干支']}**大运")
            dy_gan = TIANGAN.index(dy["天干"])
            dy_ss = GetShiShen(dg, dy_gan)
            lines.append(f"大运天干十神为**{dy_ss}**")
            if level == "偏旺" and dy_ss in ["食神", "伤官", "正财", "偏财", "正官", "七杀"]:
                lines.append("→ 为喜用，此运事业顺利、财运亨通 ▲")
            elif level == "偏弱" and dy_ss in ["正印", "偏印", "比肩", "劫财"]:
                lines.append("→ 为喜用，此运得助有力、穏步上升 ▲")
            else:
                lines.append("→ 需结合流年具体分析 ─")
            break
    lines.append("")
    lines.append("---")
    lines.append("> 以上分析基于传统八字命理学，仅供参考。命运掌握在自己手中，积极心态与努力才是改变人生的关键。")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="玄音八字 - 八字命理计算引擎")
    parser.add_argument("--action", choices=["bazi", "huangli", "reverse", "report"], required=True, help="操作类型")
    parser.add_argument("--gender", type=int, choices=[0, 1], help="性别: 1=男, 0=女")
    parser.add_argument("--datetime", type=str, help="公历时间(ISO格式): 1990-06-15T12:00:00+08:00")
    parser.add_argument("--bazi", type=str, help="八字(用于反查): 庚午 壬午 辛亥 甲午")
    parser.add_argument("--early-zi", type=int, choices=[1, 2], default=2, help="早晚子时: 1=次日, 2=当日(默认)")
    parser.add_argument("--output", type=str, help="输出文件路径")
    args = parser.parse_args()

    if args.action == "bazi":
        if not args.gender or not args.datetime:
            parser.error("bazi操作需要 --gender 和 --datetime")
        result = Action_BaziDetail(args.gender, args.datetime, args.early_zi)
    elif args.action == "huangli":
        result = Action_HuangLi(args.datetime)
    elif args.action == "reverse":
        if not args.bazi:
            parser.error("reverse操作需要 --bazi")
        result = Action_ReverseBazi(args.bazi)
    elif args.action == "report":
        if not args.gender or not args.datetime:
            parser.error("report操作需要 --gender 和 --datetime")
        report_text = Action_Report(args.gender, args.datetime, args.early_zi)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(report_text)
            print(f"报告已输出到: {args.output}")
        else:
            print(report_text)
        return

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"结果已输出到: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()