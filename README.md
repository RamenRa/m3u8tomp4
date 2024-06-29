## 关于利用ffmpeg将m3u8切片转换成mp4的工具

只有转换功能，没有下载功能，本质上是一个txt编辑器

！！特别注意！！
如果你的的片段文件夹内原本的m3u8文件名称也是".m3u8"请自行备份。脚本运行会将其！！删除！！

### 直接使用：
***
* 需要系统环境变量ffmpeg可用 或者 安装ffmpeg-python库

示例：`python3 async_main.py --media "D:\Huawei Share\test" `

* 请尽可能保留路径的双引号 
### 自行打包exe
***
请先编辑async_main_windows.spec的路径部分，并且自行下载ffmpeg到对应路径（github文件大小限制）
```
pip install pyinstaller
pyinstaller .\async_main_windows.spec
```
以上命令结束后，查看项目下的dit文件夹，找到可执行文件即可

### 文件夹示例
***
  ![示例1](https://github.com/RamenRa/m3u8tomp4/blob/main/old/%E7%A4%BA%E4%BE%8B1.PNG)
