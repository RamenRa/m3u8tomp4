import sys
import asyncio
import argparse
import os
import re
from typing import List, Tuple
import time
try:
    import ffmpeg  # 好像会更快
    ffmpeg_flag = True
except ModuleNotFoundError:
    ffmpeg_flag = False


def check_media(path: str, count) -> list:
    path = path.strip('"').replace(os.sep, '/')
    if count:
        try:
            int(count)
        except ValueError:
            print('请输入合法的整数')
            time.sleep(3)
            exit()

    if not os.path.exists(path):
        print(path, '不存在')
        time.sleep(3)
        exit()
    # folders = []
    # for root, dirs, files in os.walk(path):
    #     for dir_name in dirs:
    #         # 构造完整的文件夹路径
    #         full_path = os.path.join(root, dir_name)
    #         folders.append(full_path)
    folders = []
    for folder in os.listdir(path):
        old_m3u8 = os.path.join(path, folder, '.m3u8')
        old_txt = os.path.join(path, folder, '.txt')
        full_path = os.path.join(path, folder)
        if os.path.isdir(full_path):
            folders.append(full_path)
        if os.path.exists(old_m3u8):  # 删除之前生成的.m3u8或者.txt
            os.remove(old_m3u8)
        elif os.path.exists(old_txt):
            os.remove(old_txt)
    return folders


def tag_folder(folders: List[str], ext: str) -> List[str]:
    matching_folders = []
    if ext:
        # 历史遗留问题，保持以前用户的使用习惯
        pattern = re.compile(r'^\d+\.' + re.escape(ext) + r'$') \
            if not ext.startswith('.') \
            else re.compile(r'^\d+' + re.escape(ext) + r'$')
    else:
        # 如果扩展名为空，只匹配纯数字文件名
        pattern = re.compile(r'^\d+$')
    for folder in folders:
        numeric_files = [file for file in os.listdir(folder) if pattern.match(file)]
        if len(numeric_files) >= 5:  # 确保文件数大于等于5
            matching_folders.append(folder)
    return matching_folders


def classify_folders(folders: List[str], key_ext: str) -> Tuple[List[str], List[str], List[str], List[str]]:
    encrypted_folders = []
    unencrypted_folders = []
    key_files = []
    key_map = []

    for folder in folders:
        has_key_file = False
        current_key_files = []
        current_auxiliary_files = []
        has_added_aux_file = False  # 每个文件夹只允许一个m3u8文件

        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            if file.endswith('.' + key_ext) and not has_key_file:
                has_key_file = True
                current_key_files.append(file_path)
            if (len(file) > 10 or file.endswith('.m3u8')) and not has_added_aux_file:
                current_auxiliary_files.append(file_path)
                has_added_aux_file = True  # 每个文件夹只允许一个m3u8文件

        if has_key_file:
            encrypted_folders.append(folder)
            key_files.extend(current_key_files)
            key_map.extend(current_auxiliary_files)
        else:
            unencrypted_folders.append(folder)
    if len(encrypted_folders) == len(key_files) == len(key_map):  # 验证key和m3u8是否一一对应
        return encrypted_folders, unencrypted_folders, key_files, key_map
    else:
        print('加密视频的key文件和m3u8文件数目不一一对应')
        time.sleep(3)
        exit()


def ffmpeg_cmd(new_m3u8: str, output_file: str, function: str) -> None:
    if ffmpeg_flag:   # 好像会更快
        print("使用ffmpeg-python库处理", output_file)
        if function == "normal":
            (
                ffmpeg
                .input(new_m3u8, f='concat', safe=0)
                .output(output_file, c='copy')
                .run(capture_stderr=True)
            )
        elif function == "aes128":
            (
                ffmpeg
                .input(new_m3u8, allowed_extensions='ALL')
                .output(output_file, c='copy')
                .run(capture_stderr=True)
            )
    else:
        print('使用系统ffmpeg')
        if function == "normal":
            cmd = f'ffmpeg -f concat -safe 0 -i "{new_m3u8}" -c copy "{output_file}"'
            os.system(cmd)
        elif function == "aes128":
            cmd = f'ffmpeg -allowed_extensions ALL -i "{new_m3u8}" -c copy "{output_file}"'
            os.system(cmd)


async def cmd_pool(new_m3u8: str, output_file: str, function: str, semaphore: asyncio.Semaphore) -> None:
    output_file = output_file.replace('.m3u8_contents', '')
    async with semaphore:  # 使用信号量限制并发数量
        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, ffmpeg_cmd, new_m3u8, output_file, function)
        except ffmpeg.Error as e:
            print('ffmpeg error:', e.stderr.decode('utf8'))
            raise


# 按文件名排序
async def sort_func(folder: str) -> List[int]:
    file_list = []
    for dirpath, dirnames, filenames in os.walk(folder):
        for filename in filenames:
            if len(filename) < 10 and filename.isdigit():
                file_list.append(int(filename))
    file_list.sort()
    return file_list

async def AES128(encrypted_folders: List[str], key_files: List[str], key_map: List[str], ts_end: str, semaphore: asyncio.Semaphore):
    async def find_head(m3u8: str) -> Tuple[str, int, List[int]]:
        change_line = []
        head_flag = False
        line_now = 0
        head = ''
        https_line = 0
        with open(m3u8, 'r', encoding='UTF-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                line_now += 1
                if not head_flag and "AES-128" in line:
                    index = line.find('URI=')
                    head = line[:index + 4]
                    https_line = line_now
                    head_flag = True
                if head_flag and "http" in line:
                    change_line.append(line_now)
        return head, https_line, change_line

    async def replace_m3u8(flist: List[str], aes128_line: int, new_head: str, file_sorted: List[int], path: str, ts_end: str, change_line: List[int]) -> str:
        flist[aes128_line - 1] = f"{new_head}\n"
        for u, i in enumerate(change_line[1:]):
            if u < len(file_sorted):
                flist[i - 1] = f"{path.replace(os.sep, '/')}/{file_sorted[u]}{ts_end}\n"
        new_m3u8 = os.path.join(path, ".m3u8").replace(os.sep, '/')
        with open(new_m3u8, 'w', encoding='UTF-8', errors='ignore') as f:
            f.writelines(flist)
        return new_m3u8

    async def process_folder(path: str, m3u8: str, key: str, ts_end: str, output_video: str):
        aes128_prior, aes128_line, change_line = await find_head(m3u8)  # 找出aes128开头内容、所在行和需要修改的行
        new_head = f"{aes128_prior}\"{key}\""
        file_sorted = await sort_func(path)   # 文件名排序
        with open(m3u8, 'r', encoding='UTF-8', errors='ignore') as f:   # 复制一份
            flist = f.readlines()
        new_m3u8 = await replace_m3u8(flist, aes128_line, new_head, file_sorted, path, ts_end, change_line)  # 产生基于本地文件的m3u8
        time.sleep(0.5)
        await cmd_pool(new_m3u8, output_video, "aes128", semaphore)   # 根据不同模式 创建转换任务
        if os.path.exists(path + '/.m3u8'):
            os.remove(path + '/.m3u8')

    # 提取数据 并创建执行异步任务列表
    async def process_all_folders():
        tasks = []
        for i in range(len(encrypted_folders)):
            path = encrypted_folders[i]
            video_name = os.path.basename(path)
            path_q = os.path.dirname(path) + "/"
            output_video = os.path.join(path_q, f"{video_name}.mp4").replace(os.sep, '/')
            if os.path.exists(output_video.replace('.m3u8_contents', '')):
                print(f'存在同名文件 {output_video}')
                continue
            m3u8 = key_map[i]
            key = key_files[i].replace(os.sep, '/')

            task = process_folder(path, m3u8, key, ts_end, output_video)
            tasks.append(task)
        await asyncio.gather(*tasks)  # 执行任务列表

    await process_all_folders()


async def Normal(unencrypted_folders, ts_end, semaphore):
    async def process_folder(path: str):
        file_list = await sort_func(path)
        tmp_txt = os.path.join(path, '.txt')
        video_name = os.path.basename(path.rstrip('/'))
        path_q = os.path.dirname(path) + "/"
        if os.path.exists(path_q + video_name.replace('.m3u8_contents', '') + '.mp4'):
            print('存在同名文件', path_q + video_name.replace('.m3u8_contents', '') + '.mp4')
            return

        with open(tmp_txt, 'w', encoding='UTF-8', errors='ignore') as f:
            for i in file_list:   # 片段路径写入txt中
                f.write(f"file '{path}/{i}{ts_end}'\n")
        output_video = os.path.join(path_q, f"{video_name}.mp4")
        await cmd_pool(tmp_txt, output_video, "normal", semaphore)  # 根据不同模式 创建转换任务

        if os.path.exists(tmp_txt):
            os.remove(tmp_txt)
    await asyncio.gather(*(process_folder(folder) for folder in unencrypted_folders))


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--media", metavar="<folder>", type=str, default=None,
                        help="Path to store downloaded media files [Default: %(default)s]")
    parser.add_argument("--ts_end", metavar="<ts_end>", type=str, default="", help="ts后缀 [Default: %(default)s]")
    parser.add_argument("--count", metavar="[number]", type=int, default=8,
                        help="Max ffmpeg loop [Default: %(default)s]")
    args = parser.parse_args()
    semaphore = asyncio.Semaphore(args.count)
    if not args.ts_end:
        print("---------没有指定ts后缀，默认为空---------")
        print("--------- 若想指定，请5秒内取消 ---------")
        time.sleep(5)
    if args.media:
        start_time = time.time()
        folder = check_media(args.media, args.count)  # 查找给定路径下的文件夹
        result = tag_folder(folder, args.ts_end)  # 选出文件名为纯数字且数量大于5个的文件夹
        encrypted_folders, unencrypted_folders, key_files, key_map = classify_folders(result, "key")  #
        if encrypted_folders:  # 有加密视频
            await AES128(encrypted_folders, key_files, key_map, args.ts_end, semaphore)
        if unencrypted_folders:
            await Normal(unencrypted_folders, args.ts_end, semaphore)
        end_time = time.time()
        print("用时： {:.2f} 秒".format(end_time - start_time))
    else:
        print("请提供 --media 参数")
        exit()

if __name__ == "__main__":
    assert sys.version_info >= (3, 7), "Script requires Python 3.7+."
    asyncio.run(main())









