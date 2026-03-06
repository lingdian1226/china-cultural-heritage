#!/usr/bin/env python3
"""第一批全国重点文物保护单位数据导入"""
import json
import os

# 省份代码映射
PROVINCE_CODE = {
    "北京": "11", "天津": "12", "河北": "13", "山西": "14", "内蒙古": "15",
    "辽宁": "21", "吉林": "22", "黑龙江": "23", "上海": "31", "江苏": "32",
    "浙江": "33", "安徽": "34", "福建": "35", "江西": "36", "山东": "37",
    "河南": "41", "湖北": "42", "湖南": "43", "广东": "44", "广西": "45",
    "海南": "46", "重庆": "50", "四川": "51", "贵州": "52", "云南": "53",
    "西藏": "54", "陕西": "61", "甘肃": "62", "青海": "63", "宁夏": "64",
    "新疆": "65"
}

PROVINCE_FULL = {
    "11": "北京市", "12": "天津市", "13": "河北省", "14": "山西省", "15": "内蒙古自治区",
    "21": "辽宁省", "22": "吉林省", "23": "黑龙江省", "31": "上海市", "32": "江苏省",
    "33": "浙江省", "34": "安徽省", "35": "福建省", "36": "江西省", "37": "山东省",
    "41": "河南省", "42": "湖北省", "43": "湖南省", "44": "广东省", "45": "广西壮族自治区",
    "46": "海南省", "50": "重庆市", "51": "四川省", "52": "贵州省", "53": "云南省",
    "54": "西藏自治区", "61": "陕西省", "62": "甘肃省", "63": "青海省", "64": "宁夏回族自治区",
    "65": "新疆维吾尔自治区"
}

# 类别映射 (根据国家文物局统一分类)
# 1-33: 近现代重要史迹 (modern-historic)
# 34-47: 石窟寺及石刻 (stone-carvings) — 原"石窟寺"类
# 48-135: 古建筑+石刻+其他 — 需细分
# 136-161: 古遗址 (archaeological-sites)
# 162-180: 古墓葬 (ancient-tombs)

# 第一批180项完整数据
BATCH1 = [
    # === 近现代重要史迹及代表性建筑 (1-33) ===
    {"seq": 1, "id_num": "1-0001-5-001", "name": "三元里平英团遗址", "era": "1841年", "province": "广东", "city": "广州市", "district": "", "category": "modern-historic"},
    {"seq": 2, "id_num": "1-0002-5-002", "name": "金田起义地址", "era": "1851年", "province": "广西", "city": "桂平县", "district": "金田村", "category": "modern-historic"},
    {"seq": 3, "id_num": "1-0003-5-003", "name": "太平天国忠王府", "era": "1860－1863年", "province": "江苏", "city": "苏州市", "district": "", "category": "modern-historic"},
    {"seq": 4, "id_num": "1-0004-5-004", "name": "韶山冲毛主席旧居", "era": "1893年", "province": "湖南", "city": "湘潭县", "district": "韶山冲", "category": "modern-historic"},
    {"seq": 5, "id_num": "1-0005-5-005", "name": "江孜宗山抗英遗址", "era": "1904年", "province": "西藏", "city": "江孜县", "district": "", "category": "modern-historic"},
    {"seq": 6, "id_num": "1-0006-5-006", "name": "黄花岗七十二烈士墓", "era": "1911年", "province": "广东", "city": "广州市", "district": "", "category": "modern-historic"},
    {"seq": 7, "id_num": "1-0007-5-007", "name": "武昌起义军政府旧址", "era": "1911年", "province": "湖北", "city": "武汉市", "district": "", "category": "modern-historic"},
    {"seq": 8, "id_num": "1-0008-5-008", "name": "北京大学红楼", "era": "1918年", "province": "北京", "city": "北京市", "district": "东城区", "category": "modern-historic"},
    {"seq": 9, "id_num": "1-0009-5-009", "name": "上海中山故居", "era": "1919年", "province": "上海", "city": "上海市", "district": "", "category": "modern-historic"},
    {"seq": 10, "id_num": "1-0010-5-010", "name": "中国社会主义青年团中央机关旧址", "era": "1920－1921年", "province": "上海", "city": "上海市", "district": "", "category": "modern-historic"},
    {"seq": 11, "id_num": "1-0011-5-011", "name": "中国共产党第一次全国代表大会会址", "era": "1921年", "province": "上海", "city": "上海市", "district": "", "category": "modern-historic"},
    {"seq": 12, "id_num": "1-0012-5-012", "name": "广州农民运动讲习所旧址", "era": "1926年", "province": "广东", "city": "广州市", "district": "", "category": "modern-historic"},
    {"seq": 13, "id_num": "1-0013-5-013", "name": "八一起义指挥部旧址", "era": "1927年", "province": "江西", "city": "南昌市", "district": "", "category": "modern-historic"},
    {"seq": 14, "id_num": "1-0014-5-014", "name": "秋收起义文家市会师旧址", "era": "1927年", "province": "湖南", "city": "浏阳县", "district": "", "category": "modern-historic"},
    {"seq": 15, "id_num": "1-0015-5-015", "name": "海丰红宫、红场旧址", "era": "1927－1928年", "province": "广东", "city": "海丰县", "district": "", "category": "modern-historic"},
    {"seq": 16, "id_num": "1-0016-5-016", "name": "广州公社旧址", "era": "1927年", "province": "广东", "city": "广州市", "district": "", "category": "modern-historic"},
    {"seq": 17, "id_num": "1-0017-5-017", "name": "井冈山革命遗址", "era": "1927－1929年", "province": "江西", "city": "宁冈县", "district": "", "category": "modern-historic"},
    {"seq": 18, "id_num": "1-0018-5-018", "name": "古田会议会址", "era": "1929年", "province": "福建", "city": "上杭县", "district": "古田村", "category": "modern-historic"},
    {"seq": 19, "id_num": "1-0019-5-019", "name": "中山陵", "era": "1929年", "province": "江苏", "city": "南京市", "district": "", "category": "modern-historic"},
    {"seq": 20, "id_num": "1-0020-5-020", "name": "瑞金革命遗址", "era": "1931－1934年", "province": "江西", "city": "瑞金县", "district": "", "category": "modern-historic"},
    {"seq": 21, "id_num": "1-0021-5-021", "name": "遵义会议会址", "era": "1935年", "province": "贵州", "city": "遵义市", "district": "", "category": "modern-historic"},
    {"seq": 22, "id_num": "1-0022-5-022", "name": "泸定桥", "era": "1935年", "province": "四川", "city": "泸定县", "district": "", "category": "modern-historic"},
    {"seq": 23, "id_num": "1-0023-5-023", "name": "延安革命遗址", "era": "1937－1947年", "province": "陕西", "city": "延安市", "district": "", "category": "modern-historic"},
    {"seq": 24, "id_num": "1-0024-5-024", "name": "卢沟桥", "era": "1937年", "province": "北京", "city": "北京市", "district": "丰台区", "category": "modern-historic"},
    {"seq": 25, "id_num": "1-0025-5-025", "name": "平型关战役遗址", "era": "1937年", "province": "山西", "city": "繁峙县", "district": "", "category": "modern-historic"},
    {"seq": 26, "id_num": "1-0026-5-026", "name": "八路军总司令部旧址", "era": "1938年", "province": "山西", "city": "武乡县", "district": "", "category": "modern-historic"},
    {"seq": 27, "id_num": "1-0027-5-027", "name": "新四军军部旧址", "era": "1938－1941年", "province": "安徽", "city": "泾县", "district": "", "category": "modern-historic"},
    {"seq": 28, "id_num": "1-0028-5-028", "name": "八路军重庆办事处旧址", "era": "1938－1946年", "province": "重庆", "city": "重庆市", "district": "", "category": "modern-historic"},
    {"seq": 29, "id_num": "1-0029-5-029", "name": "冉庄地道战遗址", "era": "1942年", "province": "河北", "city": "保定市", "district": "", "category": "modern-historic"},
    {"seq": 30, "id_num": "1-0030-5-030", "name": "天安门", "era": "明清", "province": "北京", "city": "北京市", "district": "", "category": "modern-historic"},
    {"seq": 31, "id_num": "1-0031-5-031", "name": "鲁迅墓", "era": "近代", "province": "上海", "city": "上海市", "district": "虹口区", "category": "modern-historic"},
    {"seq": 32, "id_num": "1-0032-5-032", "name": "中苏友谊纪念塔", "era": "1957年", "province": "辽宁", "city": "大连市", "district": "", "category": "modern-historic"},
    {"seq": 33, "id_num": "1-0033-5-033", "name": "人民英雄纪念碑", "era": "1958年", "province": "北京", "city": "北京市", "district": "天安门广场", "category": "modern-historic"},

    # === 石窟寺 (34-47) → 石窟寺及石刻 ===
    {"seq": 34, "id_num": "1-0034-4-001", "name": "云冈石窟", "era": "北魏", "province": "山西", "city": "大同市", "district": "", "category": "stone-carvings"},
    {"seq": 35, "id_num": "1-0035-4-002", "name": "莫高窟", "era": "北魏至元", "province": "甘肃", "city": "敦煌县", "district": "", "category": "stone-carvings"},
    {"seq": 36, "id_num": "1-0036-4-003", "name": "榆林窟", "era": "北魏至元", "province": "甘肃", "city": "安西县", "district": "", "category": "stone-carvings"},
    {"seq": 37, "id_num": "1-0037-4-004", "name": "龙门石窟", "era": "北魏至唐", "province": "河南", "city": "洛阳市", "district": "", "category": "stone-carvings"},
    {"seq": 38, "id_num": "1-0038-4-005", "name": "麦积山石窟", "era": "北魏至明", "province": "甘肃", "city": "天水市", "district": "", "category": "stone-carvings"},
    {"seq": 39, "id_num": "1-0039-4-006", "name": "炳灵寺石窟", "era": "北魏至明", "province": "甘肃", "city": "临夏市", "district": "", "category": "stone-carvings"},
    {"seq": 40, "id_num": "1-0040-4-007", "name": "响堂山石窟", "era": "东魏、北齐至元", "province": "河北", "city": "邯郸市", "district": "", "category": "stone-carvings"},
    {"seq": 41, "id_num": "1-0041-4-008", "name": "克孜尔千佛洞", "era": "唐至宋", "province": "新疆", "city": "拜城县", "district": "", "category": "stone-carvings"},
    {"seq": 42, "id_num": "1-0042-4-009", "name": "库木吐喇千佛洞", "era": "唐至宋", "province": "新疆", "city": "库车县", "district": "", "category": "stone-carvings"},
    {"seq": 43, "id_num": "1-0043-4-010", "name": "皇泽寺摩崖造像", "era": "唐", "province": "四川", "city": "广元县", "district": "", "category": "stone-carvings"},
    {"seq": 44, "id_num": "1-0044-4-011", "name": "广元千佛崖摩崖造像", "era": "唐、宋", "province": "四川", "city": "广元县", "district": "", "category": "stone-carvings"},
    {"seq": 45, "id_num": "1-0045-4-012", "name": "北山摩崖造像", "era": "唐、宋", "province": "四川", "city": "大足县", "district": "", "category": "stone-carvings"},
    {"seq": 46, "id_num": "1-0046-4-013", "name": "宝顶山摩崖造像", "era": "宋", "province": "四川", "city": "大足县", "district": "", "category": "stone-carvings"},
    {"seq": 47, "id_num": "1-0047-4-014", "name": "石钟山石窟", "era": "南诏、大理", "province": "云南", "city": "剑川县", "district": "", "category": "stone-carvings"},

    # === 古建筑及历史纪念建筑物 (48-124) → 多数归为古建筑 ===
    # 石刻部分 (48-60 部分)
    {"seq": 48, "id_num": "1-0048-3-001", "name": "太室阙", "era": "东汉", "province": "河南", "city": "登封县", "district": "", "category": "stone-carvings"},
    {"seq": 49, "id_num": "1-0049-3-002", "name": "少室阙", "era": "东汉", "province": "河南", "city": "登封县", "district": "", "category": "stone-carvings"},
    {"seq": 50, "id_num": "1-0050-3-003", "name": "启母阙", "era": "东汉", "province": "河南", "city": "登封县", "district": "", "category": "stone-carvings"},
    {"seq": 51, "id_num": "1-0051-3-004", "name": "冯焕阙", "era": "东汉", "province": "四川", "city": "渠县", "district": "", "category": "stone-carvings"},
    {"seq": 52, "id_num": "1-0052-3-005", "name": "平阳府君阙", "era": "东汉", "province": "四川", "city": "绵阳县", "district": "", "category": "stone-carvings"},
    {"seq": 53, "id_num": "1-0053-3-006", "name": "沈府君阙", "era": "东汉", "province": "四川", "city": "渠县", "district": "", "category": "stone-carvings"},
    {"seq": 54, "id_num": "1-0054-3-007", "name": "孝堂山郭氏墓石祠", "era": "东汉", "province": "山东", "city": "济南市", "district": "", "category": "stone-carvings"},
    {"seq": 55, "id_num": "1-0055-3-008", "name": "嘉祥武氏墓群石刻", "era": "东汉", "province": "山东", "city": "济宁市", "district": "", "category": "stone-carvings"},
    {"seq": 56, "id_num": "1-0056-3-009", "name": "高颐墓阙及石刻", "era": "东汉", "province": "四川", "city": "雅安县", "district": "", "category": "stone-carvings"},
    {"seq": 57, "id_num": "1-0057-3-010", "name": "褒斜道石门及其摩崖石刻", "era": "汉至宋", "province": "陕西", "city": "汉中市", "district": "", "category": "stone-carvings"},

    # 古建筑 (58-124)
    {"seq": 58, "id_num": "1-0058-3-011", "name": "安济桥", "era": "隋", "province": "河北", "city": "赵县", "district": "", "category": "ancient-buildings"},
    {"seq": 59, "id_num": "1-0059-3-012", "name": "安平桥", "era": "南宋", "province": "福建", "city": "晋江县", "district": "", "category": "ancient-buildings"},
    {"seq": 60, "id_num": "1-0060-3-013", "name": "永通桥", "era": "金", "province": "河北", "city": "赵县", "district": "", "category": "ancient-buildings"},
    {"seq": 61, "id_num": "1-0061-3-014", "name": "嵩岳寺塔", "era": "北魏", "province": "河南", "city": "登封县", "district": "", "category": "ancient-buildings"},
    {"seq": 62, "id_num": "1-0062-3-015", "name": "四门塔", "era": "东魏", "province": "山东", "city": "济南市", "district": "", "category": "ancient-buildings"},
    {"seq": 63, "id_num": "1-0063-3-016", "name": "大雁塔", "era": "唐", "province": "陕西", "city": "西安市", "district": "", "category": "ancient-buildings"},
    {"seq": 64, "id_num": "1-0064-3-017", "name": "小雁塔", "era": "唐", "province": "陕西", "city": "西安市", "district": "", "category": "ancient-buildings"},
    {"seq": 65, "id_num": "1-0065-3-018", "name": "崇圣寺三塔", "era": "唐、五代", "province": "云南", "city": "大理市", "district": "", "category": "ancient-buildings"},
    {"seq": 66, "id_num": "1-0066-3-019", "name": "房山云居寺塔及石经", "era": "隋、唐、辽、金", "province": "北京", "city": "北京市", "district": "房山区", "category": "ancient-buildings"},
    {"seq": 67, "id_num": "1-0067-3-020", "name": "兴教寺塔", "era": "唐", "province": "陕西", "city": "长安县", "district": "", "category": "ancient-buildings"},
    {"seq": 68, "id_num": "1-0068-3-021", "name": "苏州云岩寺塔", "era": "五代", "province": "江苏", "city": "苏州市", "district": "", "category": "ancient-buildings"},
    {"seq": 69, "id_num": "1-0069-3-022", "name": "祐国寺塔", "era": "北宋", "province": "河南", "city": "开封市", "district": "", "category": "ancient-buildings"},
    {"seq": 70, "id_num": "1-0070-3-023", "name": "定县开元寺塔", "era": "北宋", "province": "河北", "city": "定县", "district": "", "category": "ancient-buildings"},
    {"seq": 71, "id_num": "1-0071-3-024", "name": "佛宫寺释迦塔", "era": "辽", "province": "山西", "city": "应县", "district": "", "category": "ancient-buildings"},
    {"seq": 72, "id_num": "1-0072-3-025", "name": "六和塔", "era": "南宋", "province": "浙江", "city": "杭州市", "district": "", "category": "ancient-buildings"},
    {"seq": 73, "id_num": "1-0073-3-026", "name": "广惠寺华塔", "era": "金", "province": "河北", "city": "正定县", "district": "", "category": "ancient-buildings"},
    {"seq": 74, "id_num": "1-0074-3-027", "name": "妙应寺白塔", "era": "元", "province": "北京", "city": "北京市", "district": "西城区", "category": "ancient-buildings"},
    {"seq": 75, "id_num": "1-0075-3-028", "name": "真觉寺金刚宝座", "era": "明", "province": "北京", "city": "北京市", "district": "海淀区", "category": "ancient-buildings"},
    {"seq": 76, "id_num": "1-0076-3-029", "name": "海宝塔", "era": "清", "province": "宁夏", "city": "银川市", "district": "", "category": "ancient-buildings"},
    {"seq": 77, "id_num": "1-0077-3-030", "name": "义慈惠石柱", "era": "北齐", "province": "河北", "city": "易县", "district": "", "category": "others"},
    {"seq": 78, "id_num": "1-0078-3-031", "name": "赵州陀罗尼经幢", "era": "北宋", "province": "河北", "city": "宁晋县", "district": "", "category": "ancient-buildings"},
    {"seq": 79, "id_num": "1-0079-3-032", "name": "南禅寺大殿", "era": "唐", "province": "山西", "city": "五台县", "district": "", "category": "ancient-buildings"},
    {"seq": 80, "id_num": "1-0080-3-033", "name": "佛光寺", "era": "唐至清", "province": "山西", "city": "五台县", "district": "", "category": "ancient-buildings"},
    {"seq": 81, "id_num": "1-0081-3-034", "name": "大昭寺", "era": "唐", "province": "西藏", "city": "拉萨市", "district": "", "category": "ancient-buildings"},
    {"seq": 82, "id_num": "1-0082-3-035", "name": "昌珠寺", "era": "唐", "province": "西藏", "city": "乃东县", "district": "", "category": "ancient-buildings"},
    {"seq": 83, "id_num": "1-0083-3-036", "name": "光孝寺", "era": "五代至明", "province": "广东", "city": "广州市", "district": "", "category": "ancient-buildings"},
    {"seq": 84, "id_num": "1-0084-3-037", "name": "独乐寺", "era": "辽", "province": "河北", "city": "蓟县", "district": "", "category": "ancient-buildings"},
    {"seq": 85, "id_num": "1-0085-3-038", "name": "晋祠", "era": "宋", "province": "山西", "city": "太原市", "district": "", "category": "ancient-buildings"},
    {"seq": 86, "id_num": "1-0086-3-039", "name": "奉国寺", "era": "辽", "province": "辽宁", "city": "义县", "district": "", "category": "ancient-buildings"},
    {"seq": 87, "id_num": "1-0087-3-040", "name": "清净寺", "era": "宋", "province": "福建", "city": "泉州市", "district": "", "category": "ancient-buildings"},
    {"seq": 88, "id_num": "1-0088-3-041", "name": "善化寺", "era": "辽、金", "province": "山西", "city": "大同市", "district": "", "category": "ancient-buildings"},
    {"seq": 89, "id_num": "1-0089-3-042", "name": "隆兴寺", "era": "宋", "province": "河北", "city": "正定县", "district": "", "category": "ancient-buildings"},
    {"seq": 90, "id_num": "1-0090-3-043", "name": "保国寺", "era": "北宋", "province": "浙江", "city": "宁波市", "district": "", "category": "ancient-buildings"},
    {"seq": 91, "id_num": "1-0091-3-044", "name": "华严寺", "era": "辽、金、清", "province": "山西", "city": "大同市", "district": "", "category": "ancient-buildings"},
    {"seq": 92, "id_num": "1-0092-3-045", "name": "白马寺", "era": "金至清", "province": "河南", "city": "洛阳市", "district": "", "category": "ancient-buildings"},
    {"seq": 93, "id_num": "1-0093-3-046", "name": "永乐宫", "era": "元", "province": "山西", "city": "芮城县", "district": "", "category": "ancient-buildings"},
    {"seq": 94, "id_num": "1-0094-3-047", "name": "武当山金殿", "era": "元、明", "province": "湖北", "city": "光化县", "district": "", "category": "ancient-buildings"},
    {"seq": 95, "id_num": "1-0095-3-048", "name": "萨迦寺", "era": "元", "province": "西藏", "city": "萨迦县", "district": "", "category": "ancient-buildings"},
    {"seq": 96, "id_num": "1-0096-3-049", "name": "广胜寺", "era": "元、明", "province": "山西", "city": "洪洞县", "district": "", "category": "ancient-buildings"},
    {"seq": 97, "id_num": "1-0097-3-050", "name": "观星台", "era": "元", "province": "河南", "city": "登封县", "district": "", "category": "ancient-buildings"},
    {"seq": 98, "id_num": "1-0098-3-051", "name": "居庸关云台", "era": "元", "province": "北京", "city": "北京市", "district": "昌平区", "category": "ancient-buildings"},
    {"seq": 99, "id_num": "1-0099-3-052", "name": "曲阜孔庙及孔府", "era": "金至清", "province": "山东", "city": "曲阜市", "district": "", "category": "ancient-buildings"},
    {"seq": 100, "id_num": "1-0100-3-053", "name": "故宫", "era": "明、清", "province": "北京", "city": "北京市", "district": "", "category": "ancient-buildings"},
    {"seq": 101, "id_num": "1-0101-3-054", "name": "万里长城－八达岭", "era": "明", "province": "北京", "city": "北京市", "district": "延庆区", "category": "ancient-buildings"},
    {"seq": 102, "id_num": "1-0102-3-055", "name": "万里长城－山海关", "era": "明", "province": "河北", "city": "秦皇岛市", "district": "", "category": "ancient-buildings"},
    {"seq": 103, "id_num": "1-0103-3-056", "name": "万里长城－嘉峪关", "era": "明", "province": "甘肃", "city": "酒泉市", "district": "", "category": "ancient-buildings"},
    {"seq": 104, "id_num": "1-0104-3-057", "name": "西安城墙", "era": "明", "province": "陕西", "city": "西安市", "district": "", "category": "ancient-buildings"},
    {"seq": 105, "id_num": "1-0105-3-058", "name": "天坛", "era": "明", "province": "北京", "city": "北京市", "district": "崇文区", "category": "ancient-buildings"},
    {"seq": 106, "id_num": "1-0106-3-059", "name": "北海及团城", "era": "明、清", "province": "北京", "city": "北京市", "district": "西城区", "category": "ancient-buildings"},
    {"seq": 107, "id_num": "1-0107-3-060", "name": "布达拉宫", "era": "明至民国", "province": "西藏", "city": "拉萨市", "district": "", "category": "ancient-buildings"},
    {"seq": 108, "id_num": "1-0108-3-061", "name": "噶丹寺", "era": "明初至清", "province": "西藏", "city": "拉萨市", "district": "", "category": "ancient-buildings"},
    {"seq": 109, "id_num": "1-0109-3-062", "name": "扎什伦布寺", "era": "明初至清", "province": "西藏", "city": "日喀则县", "district": "", "category": "ancient-buildings"},
    {"seq": 110, "id_num": "1-0110-3-063", "name": "智化寺", "era": "明", "province": "北京", "city": "北京市", "district": "东城区", "category": "ancient-buildings"},
    {"seq": 111, "id_num": "1-0111-3-064", "name": "塔尔寺", "era": "明", "province": "青海", "city": "湟中县", "district": "", "category": "ancient-buildings"},
    {"seq": 112, "id_num": "1-0112-3-065", "name": "沈阳故宫", "era": "清", "province": "辽宁", "city": "沈阳市", "district": "", "category": "ancient-buildings"},
    {"seq": 113, "id_num": "1-0113-3-066", "name": "国子监", "era": "清", "province": "北京", "city": "北京市", "district": "东城区", "category": "ancient-buildings"},
    {"seq": 114, "id_num": "1-0114-3-067", "name": "雍和宫", "era": "清", "province": "北京", "city": "北京市", "district": "东城区", "category": "ancient-buildings"},
    {"seq": 115, "id_num": "1-0115-3-068", "name": "普宁寺", "era": "清", "province": "河北", "city": "承德市", "district": "", "category": "ancient-buildings"},
    {"seq": 116, "id_num": "1-0116-3-069", "name": "普乐寺", "era": "清", "province": "河北", "city": "承德市", "district": "", "category": "ancient-buildings"},
    {"seq": 117, "id_num": "1-0117-3-070", "name": "普陀宗乘之庙", "era": "清", "province": "河北", "city": "承德市", "district": "", "category": "ancient-buildings"},
    {"seq": 118, "id_num": "1-0118-3-071", "name": "须弥福寿之庙", "era": "清", "province": "河北", "city": "承德市", "district": "", "category": "ancient-buildings"},
    {"seq": 119, "id_num": "1-0119-3-072", "name": "武侯祠", "era": "清", "province": "四川", "city": "成都市", "district": "", "category": "ancient-buildings"},
    {"seq": 120, "id_num": "1-0120-3-073", "name": "杜甫草堂", "era": "清", "province": "四川", "city": "成都市", "district": "", "category": "ancient-buildings"},
    {"seq": 121, "id_num": "1-0121-3-074", "name": "拙政园", "era": "明、清", "province": "江苏", "city": "苏州市", "district": "", "category": "ancient-buildings"},
    {"seq": 122, "id_num": "1-0122-3-075", "name": "颐和园", "era": "清", "province": "北京", "city": "北京市", "district": "海淀区", "category": "ancient-buildings"},
    {"seq": 123, "id_num": "1-0123-3-076", "name": "避暑山庄", "era": "清", "province": "河北", "city": "承德市", "district": "", "category": "ancient-buildings"},
    {"seq": 124, "id_num": "1-0124-3-077", "name": "留园", "era": "清", "province": "江苏", "city": "苏州市", "district": "", "category": "ancient-buildings"},

    # === 石刻及其他 (125-135) ===
    {"seq": 125, "id_num": "1-0125-4-001", "name": "西安碑林", "era": "汉至近代", "province": "陕西", "city": "西安市", "district": "", "category": "stone-carvings"},
    {"seq": 126, "id_num": "1-0126-4-002", "name": "爨宝子碑", "era": "东晋", "province": "云南", "city": "曲靖县", "district": "", "category": "stone-carvings"},
    {"seq": 127, "id_num": "1-0127-4-003", "name": "爨龙颜碑", "era": "南朝", "province": "云南", "city": "陆良县", "district": "", "category": "stone-carvings"},
    {"seq": 128, "id_num": "1-0128-4-004", "name": "药王山石刻", "era": "隋至明", "province": "陕西", "city": "铜川市", "district": "", "category": "stone-carvings"},
    {"seq": 129, "id_num": "1-0129-4-005", "name": "段氏与三十七部会盟碑", "era": "大理", "province": "云南", "city": "曲靖县", "district": "", "category": "stone-carvings"},
    {"seq": 130, "id_num": "1-0130-4-006", "name": "重修护国寺感应塔碑", "era": "西夏", "province": "甘肃", "city": "武威县", "district": "", "category": "stone-carvings"},
    {"seq": 131, "id_num": "1-0131-4-007", "name": "苏州文庙内宋代石刻", "era": "南宋", "province": "江苏", "city": "苏州市", "district": "", "category": "stone-carvings"},
    {"seq": 132, "id_num": "1-0132-4-008", "name": "溪州铜柱", "era": "五代", "province": "湖南", "city": "永顺县", "district": "", "category": "others"},
    {"seq": 133, "id_num": "1-0133-4-009", "name": "峨眉山圣寿万年寺铜铁佛像", "era": "宋至明", "province": "四川", "city": "峨眉县", "district": "", "category": "others"},
    {"seq": 134, "id_num": "1-0134-4-010", "name": "沧州铁狮子", "era": "后周", "province": "河北", "city": "沧县", "district": "", "category": "others"},
    {"seq": 135, "id_num": "1-0135-4-011", "name": "保圣寺罗汉塑像", "era": "北宋", "province": "江苏", "city": "苏州市", "district": "", "category": "others"},

    # === 古遗址 (136-161) ===
    {"seq": 136, "id_num": "1-0136-1-001", "name": "周口店遗址", "era": "旧石器时代", "province": "北京", "city": "北京市", "district": "房山区", "category": "archaeological-sites"},
    {"seq": 137, "id_num": "1-0137-1-002", "name": "丁村遗址", "era": "旧石器时代", "province": "山西", "city": "临汾县", "district": "", "category": "archaeological-sites"},
    {"seq": 138, "id_num": "1-0138-1-003", "name": "仰韶村遗址", "era": "新石器时代", "province": "河南", "city": "渑池县", "district": "", "category": "archaeological-sites"},
    {"seq": 139, "id_num": "1-0139-1-004", "name": "半坡遗址", "era": "新石器时代", "province": "陕西", "city": "西安市", "district": "", "category": "archaeological-sites"},
    {"seq": 140, "id_num": "1-0140-1-005", "name": "城子崖遗址", "era": "新石器时代", "province": "山东", "city": "章丘县", "district": "", "category": "archaeological-sites"},
    {"seq": 141, "id_num": "1-0141-1-006", "name": "郑州商代遗址", "era": "商", "province": "河南", "city": "郑州市", "district": "", "category": "archaeological-sites"},
    {"seq": 142, "id_num": "1-0142-1-007", "name": "殷墟", "era": "殷", "province": "河南", "city": "安阳市", "district": "", "category": "archaeological-sites"},
    {"seq": 143, "id_num": "1-0143-1-008", "name": "丰镐遗址", "era": "周", "province": "陕西", "city": "长安市", "district": "", "category": "archaeological-sites"},
    {"seq": 144, "id_num": "1-0144-1-009", "name": "临淄齐国故城", "era": "周", "province": "山东", "city": "益都县", "district": "", "category": "archaeological-sites"},
    {"seq": 145, "id_num": "1-0145-1-010", "name": "曲阜鲁国故城", "era": "周至汉", "province": "山东", "city": "曲阜市", "district": "", "category": "archaeological-sites"},
    {"seq": 146, "id_num": "1-0146-1-011", "name": "侯马晋国遗址", "era": "东周", "province": "山西", "city": "侯马市", "district": "", "category": "archaeological-sites"},
    {"seq": 147, "id_num": "1-0147-1-012", "name": "楚纪南故城", "era": "东周", "province": "湖北", "city": "江陵县", "district": "", "category": "archaeological-sites"},
    {"seq": 148, "id_num": "1-0148-1-013", "name": "郑韩故城", "era": "东周", "province": "河南", "city": "新郑县", "district": "", "category": "archaeological-sites"},
    {"seq": 149, "id_num": "1-0149-1-014", "name": "赵邯郸故城", "era": "战国", "province": "河北", "city": "邯郸市", "district": "", "category": "archaeological-sites"},
    {"seq": 150, "id_num": "1-0150-1-015", "name": "燕下都遗址", "era": "战国", "province": "河北", "city": "易县", "district": "", "category": "archaeological-sites"},
    {"seq": 151, "id_num": "1-0151-1-016", "name": "阿房宫遗址", "era": "秦", "province": "陕西", "city": "西安市", "district": "", "category": "archaeological-sites"},
    {"seq": 152, "id_num": "1-0152-1-017", "name": "汉长安城遗址", "era": "西汉", "province": "陕西", "city": "西安市", "district": "", "category": "archaeological-sites"},
    {"seq": 153, "id_num": "1-0153-1-018", "name": "汉魏洛阳故城", "era": "东汉至北魏", "province": "河南", "city": "洛阳市", "district": "", "category": "archaeological-sites"},
    {"seq": 154, "id_num": "1-0154-1-019", "name": "高昌故城", "era": "高昌", "province": "新疆", "city": "吐鲁番县", "district": "", "category": "archaeological-sites"},
    {"seq": 155, "id_num": "1-0155-1-020", "name": "雅尔湖故城", "era": "高昌", "province": "新疆", "city": "吐鲁番县", "district": "", "category": "archaeological-sites"},
    {"seq": 156, "id_num": "1-0156-1-021", "name": "大明宫遗址", "era": "唐", "province": "陕西", "city": "西安市", "district": "", "category": "archaeological-sites"},
    {"seq": 157, "id_num": "1-0157-1-022", "name": "太和城遗址", "era": "南诏", "province": "云南", "city": "大理市", "district": "", "category": "archaeological-sites"},
    {"seq": 158, "id_num": "1-0158-1-023", "name": "渤海国上京龙泉府遗址", "era": "渤海", "province": "黑龙江", "city": "宁安县", "district": "", "category": "archaeological-sites"},
    {"seq": 159, "id_num": "1-0159-1-024", "name": "辽上京遗址", "era": "辽", "province": "内蒙古", "city": "巴林左旗", "district": "", "category": "archaeological-sites"},
    {"seq": 160, "id_num": "1-0160-1-025", "name": "辽中京遗址", "era": "辽", "province": "内蒙古", "city": "宁城县", "district": "", "category": "archaeological-sites"},
    {"seq": 161, "id_num": "1-0161-1-026", "name": "古格王国遗址", "era": "约十世纪", "province": "西藏", "city": "扎达县", "district": "", "category": "archaeological-sites"},

    # === 古墓葬 (162-180) ===
    {"seq": 162, "id_num": "1-0162-2-001", "name": "黄帝陵", "era": "传说时代", "province": "陕西", "city": "黄陵县", "district": "", "category": "ancient-tombs"},
    {"seq": 163, "id_num": "1-0163-2-002", "name": "孔林", "era": "东周", "province": "山东", "city": "曲阜县", "district": "", "category": "ancient-tombs"},
    {"seq": 164, "id_num": "1-0164-2-003", "name": "秦始皇陵", "era": "秦", "province": "陕西", "city": "临潼县", "district": "", "category": "ancient-tombs"},
    {"seq": 165, "id_num": "1-0165-2-004", "name": "茂陵", "era": "西汉", "province": "陕西", "city": "兴平县", "district": "", "category": "ancient-tombs"},
    {"seq": 166, "id_num": "1-0166-2-005", "name": "霍去病墓", "era": "西汉", "province": "陕西", "city": "兴平县", "district": "", "category": "ancient-tombs"},
    {"seq": 167, "id_num": "1-0167-2-006", "name": "辽阳壁画墓群", "era": "汉至晋", "province": "辽宁", "city": "辽阳市", "district": "", "category": "ancient-tombs"},
    {"seq": 168, "id_num": "1-0168-2-007", "name": "洞沟古墓群", "era": "高句丽", "province": "吉林", "city": "集安县", "district": "", "category": "ancient-tombs"},
    {"seq": 169, "id_num": "1-0169-2-008", "name": "封氏墓群", "era": "北魏至隋", "province": "河北", "city": "吴桥县", "district": "", "category": "ancient-tombs"},
    {"seq": 170, "id_num": "1-0170-2-009", "name": "昭陵", "era": "唐", "province": "陕西", "city": "礼泉县", "district": "", "category": "ancient-tombs"},
    {"seq": 171, "id_num": "1-0171-2-010", "name": "乾陵", "era": "唐", "province": "陕西", "city": "乾县", "district": "", "category": "ancient-tombs"},
    {"seq": 172, "id_num": "1-0172-2-011", "name": "顺陵", "era": "唐", "province": "陕西", "city": "咸阳市", "district": "", "category": "ancient-tombs"},
    {"seq": 173, "id_num": "1-0173-2-012", "name": "六顶山古墓群", "era": "渤海", "province": "吉林", "city": "敦化县", "district": "", "category": "ancient-tombs"},
    {"seq": 174, "id_num": "1-0174-2-013", "name": "藏王墓", "era": "七世纪", "province": "西藏", "city": "琼结县", "district": "", "category": "ancient-tombs"},
    {"seq": 175, "id_num": "1-0175-2-014", "name": "王建墓", "era": "五代前蜀", "province": "四川", "city": "成都市", "district": "", "category": "ancient-tombs"},
    {"seq": 176, "id_num": "1-0176-2-015", "name": "岳飞墓", "era": "南宋", "province": "浙江", "city": "杭州市", "district": "", "category": "ancient-tombs"},
    {"seq": 177, "id_num": "1-0177-2-016", "name": "明孝陵", "era": "明", "province": "江苏", "city": "南京市", "district": "", "category": "ancient-tombs"},
    {"seq": 178, "id_num": "1-0178-2-017", "name": "十三陵", "era": "明", "province": "北京", "city": "北京市", "district": "昌平区", "category": "ancient-tombs"},
    {"seq": 179, "id_num": "1-0179-2-018", "name": "清东陵", "era": "清", "province": "河北", "city": "遵化县", "district": "", "category": "ancient-tombs"},
    {"seq": 180, "id_num": "1-0180-2-019", "name": "清西陵", "era": "清", "province": "河北", "city": "易县", "district": "", "category": "ancient-tombs"},
]

def build_item(raw):
    code = PROVINCE_CODE[raw["province"]]
    return {
        "id": raw["id_num"],
        "name": raw["name"],
        "level": "national",
        "batch": 1,
        "category": raw["category"],
        "province": PROVINCE_FULL[code],
        "city": raw["city"],
        "district": raw.get("district", ""),
        "address": "",
        "era": raw["era"],
        "description": "",
        "historical_value": "",
        "sources": ["维基百科-第一批全国重点文物保护单位"],
        "last_updated": "2026-03-06",
        "data_quality": "basic",
        "contributors": ["iBo"]
    }

def main():
    # Group by province
    by_province = {}
    for raw in BATCH1:
        code = PROVINCE_CODE[raw["province"]]
        by_province.setdefault(code, []).append(build_item(raw))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "national-level")
    os.makedirs(out_dir, exist_ok=True)

    total = 0
    for code, items in sorted(by_province.items()):
        path = os.path.join(out_dir, f"{code}.json")
        # Load existing if present (to preserve detailed entries)
        existing = {}
        if os.path.exists(path):
            with open(path) as f:
                for item in json.load(f):
                    existing[item["id"]] = item

        # Merge: keep existing detailed entries, add new basic ones
        for item in items:
            if item["id"] not in existing:
                existing[item["id"]] = item
            else:
                # Update batch field if missing
                if "batch" not in existing[item["id"]]:
                    existing[item["id"]]["batch"] = 1

        merged = sorted(existing.values(), key=lambda x: x["id"])
        with open(path, "w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)

        print(f"  {PROVINCE_FULL[code]} ({code}.json): {len(merged)} items")
        total += len(merged)

    print(f"\n✅ 第一批共 {total} 项已写入 {out_dir}/")

if __name__ == "__main__":
    main()
