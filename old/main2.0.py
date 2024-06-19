import os
import time
# import shutil

# 例：    D:/XXX/ZZZ/0.TS
path = r'D:/Huawei Share/iphone/UCDownloads/video'
ts_end = ''   # 一般情况填写 .ts 分段视频没有后缀就不填
# 分段视频0.ts，1.ts,.....,100.ts 就填 ts_end = '.ts'
# -----------没有扩展名就不修改 ts_end -------------------

if path == '':
    print('没有输入目录')
    exit(0)
for x in path:
    if x == '\\':
        print('输入的路径含有"\\",即将退出')
        time.sleep(3)
        exit(0)
if path[-1] != '/':   # 如果没有以’/‘为结尾 就补齐
    path = path + '/'

#-------变量-(一般不需要修改)--------------
key = ''  # 当前操作的key
m3u8 = ''  # 当前操作的m3u8
line_now = 0  # 当前所在行
https_line = 0  # https key 所在行
head_flag = False   # 标记 https key 行是否修改完成
change_line = []   # 需要修改的https行的集合，需要指向ts段
head = ''
new_head = ''  # 修改后的https key
cmd = ''
success = 1
cmd_file_name = []  # ffmepg 处理的文件名字
#--------------------------

# def copy_file(source_file, destination_file):
#     try:
#         # 复制文件
#         shutil.copy2(source_file, destination_file)
#         print("文件复制成功！")
#     except FileNotFoundError:
#         print("找不到源文件或目标目录不存在。")
#     except PermissionError:
#         print("权限不足，无法复制文件。")
#     except Exception as e:
#         print("发生错误：", str(e))

def selce_dir():
    global path
    key_count = path.count('/')  # 遍历出来的文件夹没有‘/’结尾
    final_dir = []  # 所有的文件夹
    key_video = []  # 加密视频文件夹
    video = []    # 无加密视频文件夹
    m3u8_list = []   # 所有m3u8文件集合
    m3u8_name = ''  # 当前m3u8文件名字
    key_name = ''   # 当前key文件名字
    key_name_list = []  # 所有key文件名集合


# ----防止寻找多级子目录下的文件，只寻找指定目录的一级子目录-----------
    for path_root, file_dir, files in os.walk(path):
        for dir in file_dir:
            dir_list = os.path.join(path_root, dir).replace('\\', "/")   # 遍历出来的文件路径 "\" 替换成 "/"
            key_t = dir_list.count('/')  # 在结尾加入‘/’
            if key_t == key_count:
                final_dir.append(dir_list + "/")
    print('当前目录共有', len(final_dir), '个文件夹')
    for r in range(0, len(final_dir)):
        swith = [False, False, False, False, False, False, False, False]  # swith[7]
        swith_flag = 0
        swith_done = True
        for path_root, file_dir, files in os.walk(final_dir[r]):
            for i in files:
                if i.isdigit() and swith_done:  # 如果文件名可以转换为int
                    swith[swith_flag] = True       # 每有一个文件名可以转换成纯数字，就做标记
                    swith_flag += 1
                    if swith_flag == 7:     # 文件夹内有7个文件可以转换成纯数字就视为片段文件夹，且后续不在进入
                        swith_done = False
                if os.path.splitext(i)[-1] == ".key":
                    swith[7] = True
                    key_name = i
                if i == 'new.m3u8':
                    os.remove(path_root+'new.m3u8')  # 之前的txt还在就删除
                    continue
                if len(i) > 10 or os.path.splitext(i)[-1] == ".m3u8":
                    m3u8_name = i
            if swith[6]:  # 至少有7个纯数字文件 则认为这是存放ts 的文件夹
                if swith[7]:  # 如果目录中包含.key则认为是加密的
                    # print('加密ts 在这个文件夹', final_dir[r])
                    key_video.append(final_dir[r])
                    m3u8_list.append(m3u8_name)
                    key_name_list.append(key_name)
                else:
                    # 否则就是未加密的
                    video.append(final_dir[r])

    print('加密视频共有', len(key_video), '个')
    print('无加密视频共有', len(video), '个')
    print('---------------------------------------')
    time.sleep(3)
    return key_video, m3u8_list, key_name_list, video

key_video_path, m3u8_list, key_name_list, video = selce_dir()
# print("key_video_path", key_video_path)

def No_Key():
    global path, cmd, path_q
    file_list = []
    for dirpath, dirnames, filenames in os.walk(path):  # dirpath, dirnames, filenames = os.walk(path)
        for filename in filenames:
            if len(filename) < 10:
                file_list.append(filename)
    file_list = sorted([int(n) for n in file_list if n.isdigit()])  # 提取文件名 转成int 不符合条件的丢弃 最后升序排列
    tmp_txt = path + 't.txt'
    if os.path.exists(tmp_txt):
        os.remove(tmp_txt)   # 之前的txt还在就删除
    f = open(path + 't.txt', 'w+', encoding='UTF-8', errors='ignore')  # 新建一个文本 将flist全部写入
    for i in file_list:
        f.writelines('file  ' + "'" + str(i) + ts_end + "'" + '\n')
    f.close()
    if os.path.exists(path_q + video_name + '.mp4'):
        print('存在同名视频 跳过', video_name)
    else:
        cmd = 'ffmpeg -f concat -safe 0 -i "' + path + 't.txt"' + ' -c copy "' + path_q + 'new.mp4"'
        cmd_run()
    if os.path.exists(tmp_txt):     # 删除完成后生成的t.txt
        os.remove(tmp_txt)

def cmd_run():
    global success
    print(cmd)
    print(os.popen(cmd).read())  # 运cmd命令)  # 打印cmd控制台输出
    time.sleep(0.1)
    # 重命名回来
    os.rename(path_q + 'new.mp4', path_q + video_name + '.mp4')
    time.sleep(0.5)
    os.rename(path, path_q + video_name)
    print('第', success, '个视频合并成功')
    success += 1
    time.sleep(3)
    cmd_file_name.append(video_name)  # 添加视频名字到列表 后续验证

def cute_name():
    k = 0
    cute_potion = []
    for i in path:
        k += 1
        if i == '/':
            cute_potion.append(k)
    video_name = path[cute_potion[-2]:cute_potion[-1]-1]  # 倒数第二个“/”和倒数第一“/”,中间组成视频名字
    path_q = path[:cute_potion[-2]]    # 视频文件夹路径
    return video_name, path_q

def AES128():
    global path, path_q, line_now, head_flag,https_line,head,new_head,cmd,change_line
    line_now = 0  # 清零当前行
    change_line.clear()
    head_flag = False  # 标记 https key 行是否修改完成
    if os.path.exists(path + 't.txt'):
        os.remove(path + 't.txt')  # 之前的txt还在就删除
    # 先只读模式打开文件 查找需要修改的行 并且作为list
    f = open(path+m3u8, 'r+', encoding='UTF-8', errors='ignore')
    for line in f.readlines():                # 逐行读取数据
        line = line.strip()                #去掉每行头尾空白
        line_now += 1
        if not head_flag:  # 减少 ‘AES-128’查找次数
            if "AES-128" in line:
                # print('现在是第', line_now, '行')   # #EXT-X-KEY:METHOD=AES-128,所在行
                index = line.find('URI=')  # U所在的具体位置
                head = line[:(index + 4)]  # 切割https key 的头
                https_line = line_now    # #EXT-X-KEY:METHOD=AES-128,所在行
                head_flag = True   # 标记头已修改
            else:
                pass
        if head_flag and (line_now-https_line) % 2 == 0: # https://xxxxxxx0.ts 所在行
            change_line.append(line_now+1)   # list下标从0开始，txt行数从1开始，因此需要+1
    f.close()
    sum_line = line_now

    time.sleep(0.1)
    new_head = head + '"' + key + '"'  # m3u8中新的key指向，指向目录的.key文件
    file_list = []
    for dirpath, dirnames, filenames in os.walk(path):  #
        for filename in filenames:
            if len(filename) < 10:
                file_list.append(filename)
    file_list_int = sorted([int(n) for n in file_list if n.isdigit()])  # 提取文件名 转成int 不符合条件的丢弃 最后升序排列
    # copy_file(path + m3u8, path + 'new.m3u8')  # 复制出来 path + 'new.m3u8'
    # 只读模式打开文件 将所有内容写入flist 然后修改指定行  最后在统一写入path + 'new.m3u8'
    f = open(path + m3u8, 'r', encoding='UTF-8', errors='ignore')
    flist = f.readlines()  # 原文本逐行读取存到flist
    #-----------开始修改文本内容----------------------------
    flist[https_line-1] = new_head + '\n'   # 修改https_line行的key，指向.key文件
    u = 0
    for i in range(sum_line):    # 逐行修改 ts 文件指向
        if i == change_line[u]:
            flist[i] = str(file_list_int[u]) + ts_end + '\n'  # flist[i] 当前所在的行
            u += 1
            if u == len(file_list_int) - 1:
                break


    f.close()
    #-----------修改完毕----------------------------
    f = open(path + 'new.m3u8', 'w+', encoding='UTF-8', errors='ignore')   # 新建一个文本 将flist全部写入
    f.writelines(flist)
    f.close()

    time.sleep(0.5)
    if os.path.exists(path_q + video_name + '.mp4'):
        print('文件存在 跳过', video_name)
    else:
        cmd = 'ffmpeg -allowed_extensions ALL -i "' + path + 'new.m3u8" -c copy "' + path_q + 'new.mp4"'
        cmd_run()
    if os.path.exists(path + 'new.m3u8'):
        os.remove(path + 'new.m3u8')


success_key_video = []
if key_video_path:
    for i in range(len(key_video_path)):
        path = key_video_path[i]
        video_name, path_q = cute_name()  # 获取视频文件夹 后续以文件夹名字作为视频名字
        m3u8 = m3u8_list[i]
        key = key_name_list[i]
        AES128()
        success_key_video.append(video_name)

success_Nokey_video = []
if video:
    for i in range(len(video)):
        path = video[i]
        video_name, path_q = cute_name()  # 获取视频文件夹 后续以文件夹名字作为视频名字
        No_Key()
        success_Nokey_video.append(video_name)
print(' ')
print('---------------------------------------------------------')

if success_key_video:
    print('加密视频:')
    for fi in success_key_video:
        print(fi)
if success_Nokey_video:
    print('无加密视频：')
    for fi in success_Nokey_video:
        print(fi)
print('\n程序执行结束')
time.sleep(5)
exit(0)
