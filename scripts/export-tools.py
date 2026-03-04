#!/usr/bin/env python3
"""
中国文物保护单位数据导出工具
支持多种格式导出和数据转换
"""

import json
import csv
import os
import sys
import sqlite3
import logging
from typing import Dict, List, Optional
import pandas as pd

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataExporter:
    """数据导出器"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
    
    def export_to_csv(self, output_file: str = "cultural-heritage.csv"):
        """导出所有数据到单个CSV文件"""
        logger.info(f"开始导出数据到CSV: {output_file}")
        
        all_data = self._collect_all_data()
        
        if not all_data:
            logger.warning("没有找到数据")
            return False
        
        # 获取所有字段
        fieldnames = set()
        for item in all_data:
            fieldnames.update(item.keys())
        
        # 排序字段
        fieldnames = sorted(fieldnames)
        
        try:
            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_data)
            
            logger.info(f"已导出 {len(all_data)} 条数据到 {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"CSV导出失败: {str(e)}")
            return False
    
    def export_to_sqlite(self, output_file: str = "cultural-heritage.db"):
        """导出数据到SQLite数据库"""
        logger.info(f"开始导出数据到SQLite: {output_file}")
        
        all_data = self._collect_all_data()
        
        if not all_data:
            logger.warning("没有找到数据")
            return False
        
        try:
            conn = sqlite3.connect(output_file)
            cursor = conn.cursor()
            
            # 创建表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cultural_heritage (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    level TEXT,
                    category TEXT,
                    province TEXT,
                    city TEXT,
                    district TEXT,
                    address TEXT,
                    era TEXT,
                    established_year INTEGER,
                    protection_status TEXT,
                    latitude REAL,
                    longitude REAL,
                    area_size TEXT,
                    official_url TEXT,
                    description TEXT,
                    historical_value TEXT,
                    management_unit TEXT,
                    contact_phone TEXT,
                    opening_hours TEXT,
                    ticket_price TEXT,
                    accessibility TEXT,
                    sources TEXT,
                    last_updated TEXT,
                    data_quality TEXT,
                    contributors TEXT
                )
            ''')
            
            # 插入数据
            for item in all_data:
                # 处理数组字段
                sources = json.dumps(item.get('sources', []), ensure_ascii=False)
                contributors = json.dumps(item.get('contributors', []), ensure_ascii=False)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO cultural_heritage VALUES (
                        :id, :name, :level, :category, :province, :city, :district,
                        :address, :era, :established_year, :protection_status,
                        :latitude, :longitude, :area_size, :official_url,
                        :description, :historical_value, :management_unit,
                        :contact_phone, :opening_hours, :ticket_price,
                        :accessibility, :sources, :last_updated, :data_quality,
                        :contributors
                    )
                ''', {
                    'id': item.get('id'),
                    'name': item.get('name'),
                    'level': item.get('level'),
                    'category': item.get('category'),
                    'province': item.get('province'),
                    'city': item.get('city'),
                    'district': item.get('district'),
                    'address': item.get('address'),
                    'era': item.get('era'),
                    'established_year': item.get('established_year'),
                    'protection_status': item.get('protection_status'),
                    'latitude': item.get('latitude'),
                    'longitude': item.get('longitude'),
                    'area_size': item.get('area_size'),
                    'official_url': item.get('official_url'),
                    'description': item.get('description'),
                    'historical_value': item.get('historical_value'),
                    'management_unit': item.get('management_unit'),
                    'contact_phone': item.get('contact_phone'),
                    'opening_hours': item.get('opening_hours'),
                    'ticket_price': item.get('ticket_price'),
                    'accessibility': item.get('accessibility'),
                    'sources': sources,
                    'last_updated': item.get('last_updated'),
                    'data_quality': item.get('data_quality'),
                    'contributors': contributors
                })
            
            conn.commit()
            conn.close()
            
            logger.info(f"已导出 {len(all_data)} 条数据到SQLite数据库: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"SQLite导出失败: {str(e)}")
            return False
    
    def export_to_excel(self, output_file: str = "cultural-heritage.xlsx"):
        """导出数据到Excel文件"""
        logger.info(f"开始导出数据到Excel: {output_file}")
        
        try:
            all_data = self._collect_all_data()
            
            if not all_data:
                logger.warning("没有找到数据")
                return False
            
            # 使用pandas导出到Excel
            df = pd.DataFrame(all_data)
            
            # 创建Excel写入器
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # 按保护级别分sheet
                for level in ['national', 'provincial', 'municipal', 'county']:
                    level_data = [item for item in all_data if item.get('level') == level]
                    if level_data:
                        df_level = pd.DataFrame(level_data)
                        sheet_name = {
                            'national': '国家级',
                            'provincial': '省级',
                            'municipal': '市级',
                            'county': '县级'
                        }.get(level, level)
                        df_level.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # 所有数据汇总
                df.to_excel(writer, sheet_name='全部数据', index=False)
            
            logger.info(f"已导出 {len(all_data)} 条数据到Excel: {output_file}")
            return True
            
        except ImportError:
            logger.error("需要安装pandas和openpyxl: pip install pandas openpyxl")
            return False
        except Exception as e:
            logger.error(f"Excel导出失败: {str(e)}")
            return False
    
    def export_to_geojson(self, output_file: str = "cultural-heritage.geojson"):
        """导出数据到GeoJSON格式（用于地图可视化）"""
        logger.info(f"开始导出数据到GeoJSON: {output_file}")
        
        all_data = self._collect_all_data()
        
        if not all_data:
            logger.warning("没有找到数据")
            return False
        
        # 构建GeoJSON结构
        features = []
        for item in all_data:
            lat = item.get('latitude')
            lon = item.get('longitude')
            
            if lat is not None and lon is not None:
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    },
                    "properties": {
                        "id": item.get('id'),
                        "name": item.get('name'),
                        "level": item.get('level'),
                        "category": item.get('category'),
                        "province": item.get('province'),
                        "city": item.get('city'),
                        "address": item.get('address'),
                        "era": item.get('era'),
                        "protection_status": item.get('protection_status'),
                        "official_url": item.get('official_url')
                    }
                }
                features.append(feature)
        
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(geojson, f, ensure_ascii=False, indent=2)
            
            logger.info(f"已导出 {len(features)} 个地点到GeoJSON: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"GeoJSON导出失败: {str(e)}")
            return False
    
    def export_statistics(self, output_file: str = "statistics.json"):
        """导出统计数据"""
        logger.info(f"开始导出统计数据: {output_file}")
        
        all_data = self._collect_all_data()
        
        if not all_data:
            logger.warning("没有找到数据")
            return False
        
        # 计算统计数据
        stats = {
            "total_count": len(all_data),
            "by_level": {},
            "by_province": {},
            "by_category": {},
            "data_quality": {
                "high": 0,
                "medium": 0,
                "low": 0
            }
        }
        
        for item in all_data:
            # 按保护级别统计
            level = item.get('level', 'unknown')
            stats["by_level"][level] = stats["by_level"].get(level, 0) + 1
            
            # 按省份统计
            province = item.get('province', 'unknown')
            stats["by_province"][province] = stats["by_province"].get(province, 0) + 1
            
            # 按类别统计
            category = item.get('category', 'unknown')
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
            
            # 数据质量统计
            quality = item.get('data_quality', 'unknown')
            if quality in stats["data_quality"]:
                stats["data_quality"][quality] += 1
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            
            logger.info(f"已导出统计数据到: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"统计数据导出失败: {str(e)}")
            return False
    
    def _collect_all_data(self) -> List[Dict]:
        """收集所有数据"""
        all_data = []
        
        # 遍历所有数据目录
        data_dirs = [
            "national-level",
            "provincial-level", 
            "municipal-level",
            "county-level"
        ]
        
        for data_dir in data_dirs:
            dir_path = os.path.join(self.data_dir, data_dir)
            if os.path.exists(dir_path):
                for root, dirs, files in os.walk(dir_path):
                    for file in files:
                        if file.endswith('.json'):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                    if isinstance(data, list):
                                        all_data.extend(data)
                            except Exception as e:
                                logger.warning(f"读取文件失败 {file_path}: {str(e)}")
        
        return all_data

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='中国文物保护单位数据导出工具')
    parser.add_argument('--format', choices=['csv', 'sqlite', 'excel', 'geojson', 'stats'], 
                       default='csv', help='导出格式')
    parser.add_argument('--output', type=str, help='输出文件路径')
    parser.add_argument('--data-dir', type=str, default='data', help='数据目录')
    
    args = parser.parse_args()
    
    exporter = DataExporter(args.data_dir)
    
    # 设置输出文件
    if args.output:
        output_file = args.output
    else:
        format_map = {
            'csv': 'cultural-heritage.csv',
            'sqlite': 'cultural-heritage.db',
            'excel': 'cultural-heritage.xlsx',
            'geojson': 'cultural-heritage.geojson',
            'stats': 'statistics.json'
        }
        output_file = format_map.get(args.format, 'output.' + args.format)
    
    # 执行导出
    if args.format == 'csv':
        exporter.export_to_csv(output_file)
    elif args.format == 'sqlite':
        exporter.export_to_sqlite(output_file)
    elif args.format == 'excel':
        exporter.export_to_excel(output_file)
    elif args.format == 'geojson':
        exporter.export_to_geojson(output_file)
    elif args.format == 'stats':
        exporter.export_statistics(output_file)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()