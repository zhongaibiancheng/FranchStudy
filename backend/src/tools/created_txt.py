import json

# 1. 读取JSON文件
def read_json_file(file_path):
    """读取JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except Exception as e:
        print(f"读取文件失败: {e}")
        return None

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
    data = read_json_file('./data/lessons/lesson_01.json')
    if data:
        extract_property_to_file(data, 'name.txt')