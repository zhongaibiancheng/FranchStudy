import json

import re

def convert_time_format(time_str):
    """
    将 HH:MM:SS,mmm 格式的时间转换为 SS.mmm 格式
    
    参数:
        time_str: 原始时间字符串，格式为 HH:MM:SS,mmm
    
    返回:
        转换后的时间字符串，格式为 SS.mmm
    """
    try:
        # 使用正则表达式匹配时间格式
        pattern = r'(\d{2}):(\d{2}):(\d{2}),(\d{3})'
        match = re.match(pattern, time_str)
        
        if match:
            hours = int(match.group(1))
            minutes = int(match.group(2))
            seconds = int(match.group(3))
            milliseconds = int(match.group(4))
            
            # 计算总秒数
            total_seconds = hours * 3600 + minutes * 60 + seconds
            
            # 格式化为 SS.mmm，去除末尾的0
            result = f"{total_seconds}.{milliseconds:03d}"
            
            # 去除末尾的0
            if result.endswith('000'):
                result = result[:-4]  # 移除.000
            elif result.endswith('00'):
                result = result[:-1]  # 移除最后一个0
            elif result.endswith('0'):
                result = result[:-1]  # 移除0
            
            return result
        else:
            return f"错误: 时间格式不正确 - {time_str}"
    
    except Exception as e:
        return f"错误: {str(e)}"

def convert_srt_timeline(timeline_str):
    """
    转换完整的时间轴格式 00:00:23,960 --> 00:00:28,200
    """
    print(timeline_str)
    try:
        parts = timeline_str.split(' --> ')
        if len(parts) == 2:
            start_time = convert_time_format(parts[0].strip())
            end_time = convert_time_format(parts[1].strip())
            return {
                'audio_start':start_time,
                'audio_end':end_time
            }
        else:
            return convert_time_format(timeline_str)
    except Exception as e:
        return f"错误: {str(e)}"
    
def update_json_file(in_path, out_path):
    """更新JSON文件中的时间轴信息"""
    try:
        # 1. 读取输入文件
        with open(in_path, 'r', encoding='utf-8') as file:
            in_data = json.load(file)
        
        # 2. 读取输出文件
        with open(out_path, 'r', encoding='utf-8') as out_file:
            out_data = json.load(out_file)
        
        # 3. 处理数据匹配逻辑
        match_found = False
        for data in in_data:
            # 确保out_data中有'text'键且为列表
            if 'text' not in out_data or not isinstance(out_data['text'], list):
                print("错误：out_data中缺少'text'列表")
                return False
                
            for out_item in out_data['text']:
                # 添加键存在性检查
                if ('line' not in data or 'french_full' not in out_item or 
                    'timeline' not in data):
                    print("警告：缺少必要的键，跳过当前项")
                    continue
                
                print(f"比较: {data['line']} 和 {out_item['french_full']}")
                
                # 进行字符串匹配
                if data['line'] in out_item['french_full']:
                    result = convert_srt_timeline(data['timeline'])
                    out_item['audio_start'] = result['audio_start']
                    out_item['audio_end'] = result['audio_end']
                    match_found = True
                    print(f"找到匹配并更新时间戳: {result}")
                    continue
        
        # 4. 将修改后的数据写入新文件（或覆盖原文件）
        if match_found:
            # 使用'w'模式重新打开文件进行写入
            with open(out_path, 'w', encoding='utf-8') as out_file:
                json.dump(out_data, out_file, ensure_ascii=False, indent=4)
            print(f"数据已成功写入文件: {out_path}")
            return True
        else:
            print("未找到匹配项，文件未修改")
            return False
            
    except FileNotFoundError as e:
        print(f"文件未找到: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"JSON格式错误: {e}")
        return False
    except KeyError as e:
        print(f"键错误: {e}，请检查JSON结构")
        return False
    except Exception as e:
        print(f"处理过程中出错: {e}")
        return False

# 2. 提取属性值并写入文件
def extract_property_to_file(json_data, output_file):
    """提取JSON中的属性值并写入文件"""
    try:
        # 检查属性是否存在
        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as file:
            for rec in json_data['text']:
                file.write(rec['french_full'])
                file.write('\n')
                print(f"✓ 记录 '{rec}' 已写入文件: {output_file}")
            
    except Exception as e:
        print(f"写入文件失败: {e}")
        return False

# 使用示例
if __name__ == "__main__":
    # 读取并提取属性
    data = update_json_file('./lesson_01_01.srt.json','lesson_01_01.json')
