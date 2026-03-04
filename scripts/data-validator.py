#!/usr/bin/env python3
"""
中国文物保护单位数据验证脚本
用于验证数据文件的格式和内容
"""

import json
import os
import sys
import logging
from typing import Dict, List, Set
import re

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataValidator:
    """数据验证器"""
    
    # 省份代码映射
    PROVINCE_CODES = {
        "11": "北京市", "12": "天津市", "13": "河北省", "14": "山西省", "15": "内蒙古自治区",
        "21": "辽宁省", "22": "吉林省", "23": "黑龙江省", "31": "上海市", "32": "江苏省",
        "33": "浙江省", "34": "安徽省", "35": "福建省", "36": "江西省", "37": "山东省",
        "41": "河南省", "42": "湖北省", "43": "湖南省", "44": "广东省", "45": "广西壮族自治区",
        "46": "海南省", "50": "重庆市", "51": "四川省", "52": "贵州省", "53": "云南省",
        "54": "西藏自治区", "61": "陕西省", "62": "甘肃省", "63": "青海省", "64": "宁夏回族自治区",
        "65": "新疆维吾尔自治区", "71": "台湾省", "81": "香港特别行政区", "82": "澳门特别行政区"
    }
    
    # 保护级别枚举
    PROTECTION_LEVELS = {
        "national", "provincial", "municipal", "county", 
        "historical", "cultural"
    }
    
    # 类别枚举
    CATEGORIES = {
        "ancient-buildings", "archaeological-sites", "ancient-tombs",
        "stone-carvings", "modern-historic", "revolutionary",
        "industrial", "agricultural", "water-conservancy",
        "transportation", "military", "religious", "residential",
        "gardens", "bridges", "towers", "others"
    }
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.unique_ids: Set[str] = set()
    
    def validate_file(self, file_path: str) -> bool:
        """验证单个数据文件"""
        logger.info(f"开始验证文件: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"JSON解析错误: {str(e)}")
            return False
        except Exception as e:
            self.errors.append(f"文件读取错误: {str(e)}")
            return False
        
        # 验证数据结构
        if not isinstance(data, list):
            self.errors.append("数据应该是一个数组")
            return False
        
        # 验证每条数据
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                self.errors.append(f"第{i+1}条数据不是字典格式")
                continue
            
            self._validate_item(item, i+1)
        
        # 输出验证结果
        self._print_results(file_path)
        
        return len(self.errors) == 0
    
    def _validate_item(self, item: Dict, index: int):
        """验证单个数据项"""
        
        # 必填字段检查
        required_fields = ["id", "name", "level", "province"]
        for field in required_fields:
            if field not in item:
                self.errors.append(f"第{index}条数据缺少必填字段: {field}")
        
        # 验证id
        if "id" in item:
            id_value = item["id"]
            if not isinstance(id_value, str):
                self.errors.append(f"第{index}条数据id不是字符串: {id_value}")
            elif len(id_value) < 3:
                self.errors.append(f"第{index}条数据id太短: {id_value}")
            elif id_value in self.unique_ids:
                self.errors.append(f"第{index}条数据id重复: {id_value}")
            else:
                self.unique_ids.add(id_value)
        
        # 验证保护级别
        if "level" in item:
            level = item["level"]
            if level not in self.PROTECTION_LEVELS:
                self.warnings.append(f"第{index}条数据保护级别未知: {level}")
        
        # 验证类别
        if "category" in item:
            category = item["category"]
            if category not in self.CATEGORIES:
                self.warnings.append(f"第{index}条数据类别未知: {category}")
        
        # 验证省份
        if "province" in item:
            province = item["province"]
            # 检查省份名称是否在有效列表中
            if province not in self.PROVINCE_CODES.values():
                self.warnings.append(f"第{index}条数据省份名称可能错误: {province}")
        
        # 验证经纬度
        if "latitude" in item:
            lat = item["latitude"]
            if not isinstance(lat, (int, float)):
                self.errors.append(f"第{index}条数据纬度格式错误: {lat}")
            elif lat < 15 or lat > 55:  # 中国纬度范围
                self.warnings.append(f"第{index}条数据纬度可能错误: {lat}")
        
        if "longitude" in item:
            lon = item["longitude"]
            if not isinstance(lon, (int, float)):
                self.errors.append(f"第{index}条数据经度格式错误: {lon}")
            elif lon < 70 or lon > 140:  # 中国经度范围
                self.warnings.append(f"第{index}条数据经度可能错误: {lon}")
        
        # 验证年份
        if "established_year" in item:
            year = item["established_year"]
            if not isinstance(year, int):
                self.errors.append(f"第{index}条数据建立年份格式错误: {year}")
            elif year < -3000 or year > 2100:  # 合理年份范围
                self.warnings.append(f"第{index}条数据建立年份可能错误: {year}")
        
        # 验证URL格式
        url_fields = ["official_url"]
        for field in url_fields:
            if field in item and item[field]:
                url = item[field]
                if not self._is_valid_url(url):
                    self.warnings.append(f"第{index}条数据{field}URL格式可能错误: {url}")
        
        # 验证数组字段
        array_fields = ["images", "videos", "documents", "sources", "contributors"]
        for field in array_fields:
            if field in item and item[field] is not None:
                if not isinstance(item[field], list):
                    self.errors.append(f"第{index}条数据{field}不是数组格式")
        
        # 验证日期格式
        if "last_updated" in item:
            date_str = item["last_updated"]
            if not self._is_valid_date(date_str):
                self.warnings.append(f"第{index}条数据最后更新日期格式错误: {date_str}")
    
    def _is_valid_url(self, url: str) -> bool:
        """验证URL格式"""
        url_pattern = re.compile(
            r'^(https?://)?'  # http:// or https://
            r'([a-zA-Z0-9.-]+)'  # 域名
            r'(\.[a-zA-Z]{2,})'  # 顶级域名
            r'(/.*)?$'  # 路径
        )
        return bool(url_pattern.match(url))
    
    def _is_valid_date(self, date_str: str) -> bool:
        """验证日期格式 YYYY-MM-DD"""
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        if not date_pattern.match(date_str):
            return False
        
        try:
            year, month, day = map(int, date_str.split('-'))
            if month < 1 or month > 12:
                return False
            if day < 1 or day > 31:
                return False
            return True
        except ValueError:
            return False
    
    def _print_results(self, file_path: str):
        """输出验证结果"""
        if self.errors:
            logger.error(f"文件 {file_path} 验证失败:")
            for error in self.errors:
                logger.error(f"  ❌ {error}")
        else:
            logger.info(f"文件 {file_path} 验证通过")
        
        if self.warnings:
            logger.warning("警告信息:")
            for warning in self.warnings:
                logger.warning(f"  ⚠️ {warning}")
        
        # 重置错误和警告
        self.errors.clear()
        self.warnings.clear()
        self.unique_ids.clear()

def validate_directory(directory: str) -> bool:
    """验证整个目录的数据文件"""
    logger.info(f"开始验证目录: {directory}")
    
    validator = DataValidator()
    all_valid = True
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                if not validator.validate_file(file_path):
                    all_valid = False
    
    if all_valid:
        logger.info("所有文件验证通过")
    else:
        logger.error("部分文件验证失败")
    
    return all_valid

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='中国文物保护单位数据验证工具')
    parser.add_argument('--file', type=str, help='验证单个数据文件')
    parser.add_argument('--dir', type=str, help='验证整个目录')
    parser.add_argument('--all', action='store_true', help='验证所有数据')
    
    args = parser.parse_args()
    
    if args.file:
        validator = DataValidator()
        validator.validate_file(args.file)
    elif args.dir:
        validate_directory(args.dir)
    elif args.all:
        # 验证所有数据目录
        data_dirs = [
            "data/national-level",
            "data/provincial-level", 
            "data/municipal-level",
            "data/county-level"
        ]
        
        all_valid = True
        for data_dir in data_dirs:
            if os.path.exists(data_dir):
                if not validate_directory(data_dir):
                    all_valid = False
        
        if all_valid:
            logger.info("✅ 所有数据验证通过")
        else:
            logger.error("❌ 部分数据验证失败")
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()