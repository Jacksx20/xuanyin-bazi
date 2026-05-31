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
    return (year - 4) % 10, (year - 4) % 12


def GetGanZhi_Month(year, month, day):
    year_gan = (year - 4) % 10
    month_gan_base = (year_gan % 5) * 2 + 2
    month_dz = (month + 1) % 12
    jieqi_day = _GetJieqiDay(year, month * 2 - 2 if month > 1 else 22)
    if day < jieqi_day:
        month_dz = (month_dz - 1) % 12
        month_gan = (month_gan_base + month_dz - 2) % 10
    else:
        month_gan = (month_gan_base + month_dz - 2) % 10
    return month_gan, month_dz


def GetGanZhi_Day(year, month, day):
    try:
        dt = datetime(year, month, day)
    except ValueError:
        return 0, 0
    base = datetime(1900, 1, 1)
    delta = (dt - base).days
    day_gan = (delta + 6) % 10
    day_dz = (delta + 0) % 12
    return day_gan, day_dz


def GetGanZhi_Hour(hour, day_gan, early_zi=2):
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
    jiazi_idx = (gan_idx * 6 + zhi_idx * 5) % 30
    pair_idx = jiazi_idx // 2
    return NAYIN_TABLE.get((pair_idx, jiazi_idx % 2), "未知")


def GetShenSha(gan_idx, zhi_idx, day_gan):
    result = []
    for name, mapping in SHENSHA_MAP.items():
        if day_gan in mapping and zhi_idx in mapping[day_gan]:
            result.append(name)
    if zhi_idx in [2, 3, 6, 7]:
        result.append("将星")
    if (gan_idx + zhi_idx) % 2 == 0 and zhi_idx in [3, 6, 9, 0]:
        result.append("福星贵人")
    return list(set(result))


def GetDaYun(year_gan, year_zhi, month_gan, month_zhi, gender, year):
    forward = (gender == 1 and year_gan % 2 == 0) or (gender == 0 and year_gan % 2 == 1)
    if forward:
        next_jieqi_idx = ((month - 1) * 2 + 1) if hasattr(GetDaYun, '_month') else 3
        steps_to_next = 3
    else:
        steps_to_next = 3
    start_age = steps_to_next
    start_year = year + start_age
    result = []
    cur_gan = month_gan
    cur_zhi = month_zhi
    for i in range(10):
        if i > 0:
            cur_gan = (cur_gan + (1 if forward else -1)) % 10
            cur_zhi = (cur_zhi + (1 if forward else -1)) % 12
        begin_year = start_year + i * 10 - 10
        end_year = begin_year + 9
        begin_age = start_age + i * 10 - 10
        end_age = begin_age + 9
        result.append({
            "干支": TIANGAN[cur_gan] + DIZHI[cur_zhi],
            "天干": TIANGAN[cur_gan],
            "地支": DIZHI[cur_zhi],
            "天干十神": SHISHEN_NAMES[0],
            "开始年份": begin_year,
            "结束年份": end_year,
            "开始年龄": begin_age,
            "结束年龄": end_age,
        })
    return result, start_age, start_year


def GetXingChongHeHui(pillars):
    result = {"年": {"天干": {}, "地支": {}}, "月": {"天干": {}, "地支": {}},
              "日": {"天干": {}, "地支": {}}, "时": {"天干": {}, "地支": {}}}
    chong_tg = [(0, 6), (1, 7), (2, 8), (3, 9), (4, 0), (5, 1), (6, 0), (7, 1), (8, 2), (9, 3)]
    chong_dz = [(0, 6), (1, 7), (2, 8), (3, 9), (4, 10), (5, 11), (6, 0), (7, 1), (8, 2), (9, 3), (10, 4), (11, 5)]
    he_dz = {(0, 1): "土", (2, 11): "木", (3, 10): "火", (4, 9): "金", (5, 8): "水", (6, 7): "土"}
    xing_dz = [(2, 5, 8), (1, 10, 7), (0, 3), (6, 6), (9, 9), (4, 4), (11, 11)]
    pos_names = ["年", "月", "日", "时"]
    for i in range(4):
        for j in range(i + 1, 4):
            gi, gj = pillars[i][0], pillars[j][0]
            for a, b in chong_tg:
                if (gi == a and gj == b) or (gi == b and gj == a):
                    result[pos_names[i]]["天干"].setdefault("冲", []).append(
                        {"柱": pos_names[j], "知识点": f"{TIANGAN[gi]}{TIANGAN[gj]}相冲"})
                    result[pos_names[j]]["天干"].setdefault("冲", []).append(
                        {"柱": pos_names[i], "知识点": f"{TIANGAN[gj]}{TIANGAN[gi]}相冲"})
            zi, zj = pillars[i][1], pillars[j][1]
            for a, b in chong_dz:
                if (zi == a and zj == b) or (zi == b and zj == a):
                    result[pos_names[i]]["地支"].setdefault("冲", []).append(
                        {"柱": pos_names[j], "知识点": f"{DIZHI[zi]}{DIZHI[zj]}相冲"})
                    result[pos_names[j]]["地支"].setdefault("冲", []).append(
                        {"柱": pos_names[i], "知识点": f"{DIZHI[zj]}{DIZHI[zi]}相冲"})
            pair = tuple(sorted([zi, zj]))
            if pair in he_dz or (pair[1], pair[0]) in he_dz:
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
    dayun, start_age, start_year = GetDaYun(yg, yz, mg, mz, gender, year)
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


def main():
    parser = argparse.ArgumentParser(description="玄音八字 - 八字命理计算引擎")
    parser.add_argument("--action", choices=["bazi", "huangli", "reverse"], required=True, help="操作类型")
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

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"结果已输出到: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()