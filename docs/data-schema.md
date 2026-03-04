# 数据结构定义

## 文物保护单位数据模型

### 核心字段（必填）

| 字段名 | 类型 | 描述 | 示例 |
|--------|------|------|------|
| `id` | string | 唯一标识符 | "110101-001" |
| `name` | string | 文物保护单位名称 | "故宫" |
| `level` | string | 保护级别 | "national" |
| `category` | string | 类别 | "ancient-buildings" |
| `province` | string | 省份 | "北京市" |
| `city` | string | 城市 | "北京市" |
| `district` | string | 区县 | "东城区" |
| `address` | string | 详细地址 | "景山前街4号" |

### 详细信息字段

| 字段名 | 类型 | 描述 | 示例 |
|--------|------|------|------|
| `era` | string | 时代 | "明清时期" |
| `established_year` | integer | 建立年份 | 1420 |
| `protection_status` | string | 保护状况 | "完好" |
| `latitude` | float | 纬度 | 39.916345 |
| `longitude` | float | 经度 | 116.397155 |
| `area_size` | string | 占地面积 | "72万平方米" |
| `official_url` | string | 官方网站 | "http://www.dpm.org.cn" |
| `description` | string | 详细描述 | "明清两代的皇家宫殿..." |
| `historical_value` | string | 历史价值 | "中国现存规模最大、保存最完整的木质结构古建筑群" |

### 多媒体字段

| 字段名 | 类型 | 描述 |
|--------|------|------|
| `images` | array | 图片URL数组 |
| `videos` | array | 视频URL数组 |
| `documents` | array | 相关文档URL数组 |
| `3d_models` | array | 3D模型URL数组 |

### 管理信息字段

| 字段名 | 类型 | 描述 |
|--------|------|------|
| `management_unit` | string | 管理单位 |
| `contact_phone` | string | 联系电话 |
| `opening_hours` | string | 开放时间 |
| `ticket_price` | string | 门票价格 |
| `accessibility` | string | 交通指南 |

### 元数据字段

| 字段名 | 类型 | 描述 |
|--------|------|------|
| `sources` | array | 数据来源 |
| `last_updated` | string | 最后更新时间 |
| `data_quality` | string | 数据质量评级 |
| `contributors` | array | 贡献者列表 |

## 保护级别枚举

```json
{
  "national": "全国重点文物保护单位",
  "provincial": "省级文物保护单位", 
  "municipal": "市级文物保护单位",
  "county": "县级文物保护单位",
  "historical": "历史建筑",
  "cultural": "文化保护单位"
}
```

## 类别枚举

```json
{
  "ancient-buildings": "古建筑",
  "archaeological-sites": "古遗址",
  "ancient-tombs": "古墓葬",
  "stone-carvings": "石窟寺及石刻",
  "modern-historic": "近现代重要史迹",
  "revolutionary": "革命文物",
  "industrial": "工业遗产",
  "agricultural": "农业遗产",
  "water-conservancy": "水利遗产",
  "transportation": "交通遗产",
  "military": "军事遗产",
  "religious": "宗教建筑",
  "residential": "民居建筑",
  "gardens": "园林",
  "bridges": "桥梁",
  "towers": "塔幢",
  "others": "其他"
}
```

## 省份代码表

```json
{
  "11": "北京市",
  "12": "天津市",
  "13": "河北省",
  "14": "山西省",
  "15": "内蒙古自治区",
  "21": "辽宁省",
  "22": "吉林省",
  "23": "黑龙江省",
  "31": "上海市",
  "32": "江苏省",
  "33": "浙江省",
  "34": "安徽省",
  "35": "福建省",
  "36": "江西省",
  "37": "山东省",
  "41": "河南省",
  "42": "湖北省",
  "43": "湖南省",
  "44": "广东省",
  "45": "广西壮族自治区",
  "46": "海南省",
  "50": "重庆市",
  "51": "四川省",
  "52": "贵州省",
  "53": "云南省",
  "54": "西藏自治区",
  "61": "陕西省",
  "62": "甘肃省",
  "63": "青海省",
  "64": "宁夏回族自治区",
  "65": "新疆维吾尔自治区",
  "71": "台湾省",
  "81": "香港特别行政区",
  "82": "澳门特别行政区"
}
```

## 数据文件命名规范

### 国家级数据
```
data/national-level/{省份代码}.json
示例：data/national-level/11.json（北京市国家级文物）
```

### 省级数据
```
data/provincial-level/{省份代码}/{城市}.json
示例：data/provincial-level/44/guangzhou.json（广州市省级文物）
```

### 市级数据
```
data/municipal-level/{省份代码}/{城市}/{区县}.json
示例：data/municipal-level/44/guangzhou/tianhe.json（广州市天河区市级文物）
```

## JSON示例

```json
{
  "id": "110101-001",
  "name": "故宫",
  "level": "national",
  "category": "ancient-buildings",
  "province": "北京市",
  "city": "北京市",
  "district": "东城区",
  "address": "景山前街4号",
  "era": "明清时期",
  "established_year": 1420,
  "protection_status": "完好",
  "latitude": 39.916345,
  "longitude": 116.397155,
  "area_size": "72万平方米",
  "official_url": "http://www.dpm.org.cn",
  "description": "故宫，旧称紫禁城，是明清两代的皇家宫殿，位于北京中轴线的中心。故宫是中国古代宫廷建筑之精华，是世界上现存规模最大、保存最为完整的木质结构古建筑群之一。",
  "historical_value": "中国现存规模最大、保存最完整的木质结构古建筑群，1987年被列为世界文化遗产。",
  "images": [
    "https://example.com/forbidden-city-1.jpg",
    "https://example.com/forbidden-city-2.jpg"
  ],
  "management_unit": "故宫博物院",
  "contact_phone": "010-85007422",
  "opening_hours": "08:30-17:00（旺季），08:30-16:30（淡季）",
  "ticket_price": "旺季60元，淡季40元",
  "accessibility": "地铁1号线天安门东站/西站",
  "sources": ["国家文物局官网", "故宫博物院官网"],
  "last_updated": "2026-03-05",
  "data_quality": "high",
  "contributors": ["Frank"]
}
```

## 数据验证规则

1. **必填字段检查**：id、name、level、province必须存在
2. **格式验证**：经纬度范围、年份格式、URL格式
3. **一致性检查**：省份代码与省份名称匹配
4. **唯一性检查**：id在整个数据库中唯一

## 更新日志

- 2026-03-05：初始创建数据结构定义