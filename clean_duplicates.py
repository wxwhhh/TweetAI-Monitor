#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理重复推文数据脚本
"""

import json
import os
from datetime import datetime

def clean_duplicate_tweets(file_path):
    """
    清理指定文件中的重复推文
    
    :param file_path: JSON文件路径
    :return: 清理的重复数量
    """
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return 0
    
    # 读取现有数据
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"读取文件失败: {e}")
        return 0
    
    if not isinstance(data, list):
        print("数据格式错误，应该是列表")
        return 0
    
    print(f"原始数据条数: {len(data)}")
    
    # 按ID去重，保留第一次出现的
    seen_ids = set()
    unique_data = []
    duplicate_count = 0
    
    for item in data:
        tweet_id = item.get('id')
        if tweet_id:
            if tweet_id not in seen_ids:
                seen_ids.add(tweet_id)
                unique_data.append(item)
            else:
                duplicate_count += 1
                print(f"移除重复推文: {tweet_id} - {item.get('author', 'Unknown')}")
        else:
            # 没有ID的数据也保留
            unique_data.append(item)
    
    print(f"清理后数据条数: {len(unique_data)}")
    print(f"移除重复数据: {duplicate_count} 条")
    
    # 备份原文件
    backup_path = file_path + '.backup'
    try:
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"原文件已备份到: {backup_path}")
    except Exception as e:
        print(f"备份失败: {e}")
    
    # 写入清理后的数据
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(unique_data, f, ensure_ascii=False, indent=2)
        print(f"清理完成，数据已保存到: {file_path}")
    except Exception as e:
        print(f"保存失败: {e}")
        return 0
    
    return duplicate_count

def main():
    """主函数"""
    data_dir = "data"
    
    if not os.path.exists(data_dir):
        print(f"数据目录不存在: {data_dir}")
        return
    
    # 获取所有tweets文件
    tweet_files = []
    for filename in os.listdir(data_dir):
        if filename.startswith('tweets_') and filename.endswith('.json'):
            tweet_files.append(os.path.join(data_dir, filename))
    
    if not tweet_files:
        print("没有找到推文数据文件")
        return
    
    print(f"找到 {len(tweet_files)} 个推文数据文件")
    total_cleaned = 0
    
    for file_path in tweet_files:
        print(f"\n处理文件: {file_path}")
        cleaned = clean_duplicate_tweets(file_path)
        total_cleaned += cleaned
    
    print(f"\n总计清理重复数据: {total_cleaned} 条")

if __name__ == "__main__":
    main() 