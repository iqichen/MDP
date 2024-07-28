import os

# 目标目录
target_directory = r'E:\ILSVRC2012_selected'

# 获取目录下所有文件夹的列表
folders = [name for name in os.listdir(target_directory) if os.path.isdir(os.path.join(target_directory, name))]

# 遍历每个文件夹，重命名去掉"_selected"
for folder in folders:
    if folder.endswith('_selected'):
        old_name = os.path.join(target_directory, folder)
        new_name = os.path.join(target_directory, folder[:-9])  # 去掉末尾的"_selected"
        os.rename(old_name, new_name)
        print(f"重命名文件夹 {folder} 为 {folder[:-9]}")

print("操作完成。")
