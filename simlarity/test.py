import os

# 文件路径
file_path = '../tools/MODEL_INOUT_SHAPE.json'

# 检查文件是否存在
if os.path.exists(file_path):
    print(f"文件 '{file_path}' 存在。")
else:
    print(f"文件 '{file_path}' 不存在。")
