# 贡献指南

欢迎为中国文物保护单位数据库贡献数据、代码或文档！

## 📋 贡献方式

### 1. 数据贡献
- 添加新的文物保护单位信息
- 更新现有数据
- 修正错误信息

### 2. 代码贡献
- 改进数据抓取脚本
- 添加数据验证工具
- 开发数据可视化功能

### 3. 文档贡献
- 完善文档说明
- 添加使用示例
- 翻译文档

## 🚀 快速开始

### 步骤1：Fork仓库
1. 访问 https://github.com/lingdian1226/china-cultural-heritage
2. 点击右上角的 "Fork" 按钮
3. 克隆你的Fork到本地：
```bash
git clone https://github.com/你的用户名/china-cultural-heritage.git
cd china-cultural-heritage
```

### 步骤2：创建分支
```bash
git checkout -b add-data-for-beijing
```

### 步骤3：添加或修改数据

#### 添加新的文物保护单位
1. 找到对应的数据文件：
   - 国家级：`data/national-level/{省份代码}.json`
   - 省级：`data/provincial-level/{省份代码}/{城市}.json`
   - 市级：`data/municipal-level/{省份代码}/{城市}/{区县}.json`

2. 按照数据格式添加新条目：
```json
{
  "id": "110101-002",
  "name": "天坛",
  "level": "national",
  "category": "ancient-buildings",
  "province": "北京市",
  "city": "北京市",
  "district": "东城区",
  "address": "天坛路甲1号",
  "era": "明清时期",
  "established_year": 1420,
  "protection_status": "完好",
  "latitude": 39.882806,
  "longitude": 116.410956,
  "description": "天坛是明清两代皇帝祭天、祈谷的场所...",
  "sources": ["国家文物局官网"],
  "last_updated": "2026-03-05",
  "contributors": ["你的名字"]
}
```

#### 更新现有数据
1. 找到需要更新的数据文件
2. 修改相应字段
3. 更新 `last_updated` 字段

### 步骤4：验证数据
```bash
# 运行数据验证脚本
python scripts/data-validator.py --file 你修改的文件.json
```

### 步骤5：提交更改
```bash
git add .
git commit -m "添加北京市天坛数据"
git push origin add-data-for-beijing
```

### 步骤6：创建Pull Request
1. 访问你的GitHub仓库页面
2. 点击 "Compare & pull request"
3. 填写PR描述：
   - 说明你添加/修改的内容
   - 提供数据来源
   - 描述验证过程

## 📝 数据质量要求

### 必填信息
- 准确的名称和地址
- 正确的保护级别
- 准确的经纬度坐标
- 可靠的数据来源

### 推荐信息
- 高质量图片
- 详细的历史描述
- 开放时间和门票信息
- 交通指南

### 数据来源要求
1. **官方来源优先**：国家文物局、各省市文物局官网
2. **学术来源**：权威出版物、学术论文
3. **实地考察**：亲自拍摄的照片和记录
4. **禁止使用**：未经核实的信息、版权不明的图片

## 🔍 数据验证

### 自动验证
```bash
# 验证单个文件
python scripts/data-validator.py --file data/national-level/11.json

# 验证整个目录
python scripts/data-validator.py --dir data/national-level

# 验证所有数据
python scripts/data-validator.py --all
```

### 验证规则
1. **格式检查**：JSON格式正确性
2. **必填字段**：id、name、level、province必须存在
3. **数据范围**：经纬度在合理范围内
4. **唯一性**：id在整个数据库中唯一
5. **一致性**：省份代码与省份名称匹配

## 🎯 贡献者奖励

### 贡献者等级
- **铜级**：贡献10个以上有效数据
- **银级**：贡献50个以上有效数据
- **金级**：贡献100个以上有效数据或重要代码贡献

### 贡献者权益
- 在贡献者名单中列出
- 获得贡献者徽章
- 参与项目决策讨论

## ❓ 常见问题

### Q: 如何获取准确的经纬度坐标？
A: 可以使用百度地图、高德地图的坐标拾取工具，或实地使用GPS设备。

### Q: 数据来源不明确怎么办？
A: 尽量寻找官方来源，如无法找到，请在sources字段注明"待核实"。

### Q: 图片版权如何处理？
A: 优先使用自己拍摄的照片，或使用明确标注为CC协议的图片。

### Q: 如何批量添加数据？
A: 可以先创建CSV文件，然后使用`scripts/csv-to-json.py`转换工具。

## 📞 联系方式

如有问题或建议：
1. 通过GitHub Issues提交
2. 加入项目讨论群（如有）
3. 联系项目维护者

## 📄 许可证说明

所有贡献的数据默认采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可证。

## 更新日志

- 2026-03-05：初始创建贡献指南