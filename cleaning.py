# import os
# import tarfile
# import random
# import shutil

# # 原始tar文件夹的路径
# tar_folder = 'ILSVRC2012_img_train'

# # 解压后存放图片的文件夹路径
# output_folder = 'ILSVRC2012_extracted'

# # 如果输出文件夹不存在，则创建它
# if not os.path.exists(output_folder):
#     os.makedirs(output_folder)

# # 遍历每个tar文件
# for tar_file_name in os.listdir(tar_folder):
#     tar_file_path = os.path.join(tar_folder, tar_file_name)
    
#     # 打开tar文件
#     with tarfile.open(tar_file_path, 'r') as tar:
#         # 解压到临时文件夹
#         tmp_folder = os.path.join(output_folder, tar_file_name.split('.')[0])
#         tar.extractall(path=tmp_folder)
        
#         # 获取解压后的所有图片文件名
#         image_files = os.listdir(tmp_folder)
        
#         # 如果图片数量大于100，则随机选择100张图片
#         if len(image_files) > 10:
#             selected_images = random.sample(image_files, 10)
#         else:
#             selected_images = image_files
        
#         # 移动选中的图片到最终文件夹
#         final_folder = os.path.join(output_folder, tar_file_name.split('.')[0] + '_selected')
#         if not os.path.exists(final_folder):
#             os.makedirs(final_folder)
        
#         for image in selected_images:
#             shutil.move(os.path.join(tmp_folder, image), final_folder)
        
#         # 关闭tar文件对象
#         tar.close()
        
#         # 删除原始tar文件
#         os.remove(tar_file_path)
        
#         # 删除临时解压文件夹
#         shutil.rmtree(tmp_folder)

# print("完成！")

import os
import random
import shutil

# 解压后存放图片的文件夹路径
extracted_folder = 'ILSVRC2012_img_train'

# 处理后的图片存放文件夹路径
output_folder = 'ILSVRC2012_selected'

# 如果输出文件夹不存在，则创建它
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 遍历每个解压后的文件夹
for folder_name in os.listdir(extracted_folder):
    folder_path = os.path.join(extracted_folder, folder_name)
    
    # 确保处理的是真正的文件夹
    if not os.path.isdir(folder_path):
        continue
    
    # 获取解压后的所有图片文件名
    image_files = os.listdir(folder_path)
    
    # 如果图片数量大于10，则随机选择10张图片
    if len(image_files) > 10:
        selected_images = random.sample(image_files, 10)
    else:
        selected_images = image_files
    
    # 移动选中的图片到最终文件夹
    final_folder = os.path.join(output_folder, folder_name + '_selected')
    if not os.path.exists(final_folder):
        os.makedirs(final_folder)
    
    for image in selected_images:
        shutil.move(os.path.join(folder_path, image), final_folder)
    
    # 删除原始解压文件夹
    shutil.rmtree(folder_path)

print("完成！")
