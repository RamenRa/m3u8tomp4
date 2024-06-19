## 关于利用ffmpeg将m3u8切片转换成mp4的工具
***
只有转换功能，没有下载功能，本质上是一个txt编辑器

### 直接使用：
***
* 需要系统环境变量ffmpeg可用 或者 安装ffmpeg-python库

示例：`python3 async_main.py --media "D:\Huawei Share\test" `

* 请尽可能保留路径的双引号 
### 自行打包exe
***
```
pip install pyinstaller
# 请编辑async_main_windows.spec的路径部分
# 由于github文件大小限制请自行下载ffmpeg
pyinstaller .\async_main_windows.spec
```
以上命令结束后，查看项目下的dit文件夹，找到可执行文件即可
