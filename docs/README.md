# 中国文物保护单位数据库

一个结构化的中国全国文物保护单位数据库，包含国家级、省级、市级、县级文物保护单位信息。

## 📁 项目结构

```
china-cultural-heritage/
├── data/                    # 核心数据
│   ├── national-level/      # 全国重点文物保护单位
│   ├── provincial-level/    # 省级文物保护单位
│   ├── municipal-level/     # 市级文物保护单位
│   └── county-level/       # 县级文物保护单位
├── categories/              # 分类数据
│   ├── ancient-buildings/  # 古建筑
│   ├── archaeological-sites/ # 古遗址
│   ├── ancient-tombs/      # 古墓葬
│   ├── stone-carvings/     # 石窟寺及石刻
│   ├── modern-historic/    # 近现代重要史迹
│   └── other/              # 其他
├── regions/                 # 地区数据
│   ├── beijing/           # 北京
│   ├── shanghai/          # 上海
│   ├── guangdong/         # 广东
│   └── ...                # 其他省份
├── scripts/                # 自动化脚本
│   ├── data-scraper.py    # 数据抓取
│   ├── data-validator.py  # 数据验证
│   └── export-tools.py    # 导出工具
└── docs/                   # 文档
    ├── README.md          # 本文件
    ├── data-schema.md     # 数据结构定义
    └── contribution-guide.md # 贡献指南
```

## 🎯 项目目标

1. **全面性**：收录中国各级文物保护单位
2. **准确性**：基于官方数据源，定期更新
3. **结构化**：统一的数据格式，便于查询分析
4. **开放性**：开源数据，支持二次开发

## 📊 数据来源

- 国家文物局官网
- 各省市文物局网站
- 文化遗产保护相关出版物
- 学术研究资料

## 🔧 技术栈

- **数据格式**：JSON + CSV
- **编程语言**：Python（数据抓取和处理）
- **版本控制**：Git + GitHub
- **自动化**：GitHub Actions（定期更新）

## 🚀 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/lingdian1226/china-cultural-heritage.git
cd china-cultural-heritage
```

### 2. 查看数据
```bash
# 查看国家级文物保护单位
cat data/national-level/beijing.json
```

### 3. 运行数据更新脚本
```bash
python scripts/data-scraper.py --level national
```

## 🤝 贡献指南

欢迎贡献数据、代码或文档！请参考 `docs/contribution-guide.md`。

## 📄 许可证

本项目采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可证。

## 🔗 相关链接

- 国家文物局：http://www.ncha.gov.cn
- 中国文化遗产研究院：http://www.cach.org.cn
- 世界文化遗产名录：https://whc.unesco.org

## 📞 联系方式

如有问题或建议，请通过GitHub Issues提交。