#!/usr/bin/env python3
# extract_timestamps.py

from bs4 import BeautifulSoup
import json
import re
from pathlib import Path

def parse_time_to_seconds(time_str):
    """将时间字符串转换为秒数"""
    # 格式: HH:MM:SS.ss 或 MM:SS.ss
    parts = time_str.split(':')
    
    if len(parts) == 3:  # HH:MM:SS.ss
        hours, minutes, seconds = parts
        seconds_parts = seconds.split('.')
        seconds_int = int(seconds_parts[0])
        milliseconds = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0
    elif len(parts) == 2:  # MM:SS.ss
        hours = 0
        minutes, seconds = parts
        seconds_parts = seconds.split('.')
        seconds_int = int(seconds_parts[0])
        milliseconds = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0
    else:
        return 0.0
    
    total_seconds = (int(hours) * 3600 + 
                    int(minutes) * 60 + 
                    seconds_int + 
                    milliseconds / 100.0)
    return round(total_seconds, 2)

def extract_timestamps_from_html(html_content):
    """从HTML内容中提取时间戳"""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    results = []
    
    # 查找所有包含时间戳的段落
    paragraphs = soup.find_all('p', class_='paragraph')
    
    for i, paragraph in enumerate(paragraphs, 1):
        # 查找句子元素
        sentences = paragraph.find_all('span', class_='sentence')
        
        for j, sentence in enumerate(sentences, 1):
            # 提取时间戳属性
            start_time = sentence.get('data-starttime')
            end_time = sentence.get('data-endtime')
            sentence_id = sentence.get('id', '')
            
            if start_time and end_time:
                # 提取文本内容
                text_parts = []
                for element in sentence.children:
                    if element.name == 'w':  # 单词
                        text_parts.append(element.get_text().strip())
                    elif element.name == 'd':  # 分隔符
                        text_parts.append(element.get_text().strip())
                
                sentence_text = ''.join(text_parts).strip()
                
                # 转换为秒数
                start_seconds = parse_time_to_seconds(start_time)
                end_seconds = parse_time_to_seconds(end_time)
                duration = round(end_seconds - start_seconds, 2)
                
                result = {
                    'sentence_id': sentence_id,
                    'sentence_number': f"{i}.{j}",
                    'audio_start': start_seconds,
                    'audio_end': end_seconds,
                    'duration': duration,
                    'text': sentence_text,
                    'time_format': {
                        'start': start_time,
                        'end': end_time
                    }
                }
                results.append(result)
    
    return results

def save_to_json(data, output_file):
    """保存为JSON文件"""
    output_data = {
        'metadata': {
            'total_sentences': len(data),
            'total_duration': sum(item['duration'] for item in data),
            'audio_range': {
                'start': data[0]['audio_start'] if data else 0,
                'end': data[-1]['audio_end'] if data else 0
            }
        },
        'sentences': data
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 时间戳已保存到: {output_file}")
    return output_file

def main():
    # 读取HTML文件
    html_file = "lesson_01.html"  # 替换为您的文件路径
    
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"错误: 文件不存在 {html_file}")
        return
    
    print("正在提取时间戳...")
    timestamps = extract_timestamps_from_html(html_content)
    
    if not timestamps:
        print("未找到时间戳数据")
        return
    
    print(f"✓ 找到 {len(timestamps)} 个句子时间戳")
    
    # 显示前几个结果
    print("\n前5个句子的时间戳:")
    print("-" * 80)
    for i, ts in enumerate(timestamps[:5], 1):
        print(f"{i:2d}. [{ts['audio_start']:6.2f}s-{ts['audio_end']:6.2f}s] {ts['text'][:50]}...")
    
    # 保存结果
    output_file = Path(html_file).stem + "_timestamps.json"
    save_to_json(timestamps, output_file)
    
    # 统计信息
    total_duration = sum(ts['duration'] for ts in timestamps)
    print(f"\n统计信息:")
    print(f"  总句子数: {len(timestamps)}")
    print(f"  总时长: {total_duration:.2f}秒")
    print(f"  音频范围: {timestamps[0]['audio_start']:.2f}s - {timestamps[-1]['audio_end']:.2f}s")

if __name__ == "__main__":
    main()