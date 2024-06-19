import os
import sys

path = "D:\Huawei Share\test\"

path = path.replace(os.sep, '/')
# if path[-1] != '/':  # 如果没有以'\'为结尾 就补齐
#     path = f"{path}/"

folders = []
for folder in os.listdir(path):
    full_path = os.path.join(path, folder)
    if os.path.isdir(full_path):
        folders.append(full_path)


print(folders)