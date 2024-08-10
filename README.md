## 关于利用ffmpeg将m3u8切片转换成mp4的工具

只有转换功能，没有下载功能，本质上是一个txt编辑器

！！特别注意！！
如果你的的片段文件夹内原本的m3u8文件名称也是".m3u8"请自行备份。脚本运行会将其！！删除！！

### 直接使用：
***
* 需要系统环境变量ffmpeg可用 或者`pip install ffmpeg-python`

示例：
`python3 async_main.py --media "D:\Huawei Share\test" `

* 请保留路径的双引号 
### 自行打包exe
***
自行下载ffmpeg，并且编辑async_main_windows.spec文件的路径部分，指向到`ffmpeg.exe`
```
pip install pyinstaller
pyinstaller .\async_main_windows.spec
```
以上命令结束后，查看项目下的dit文件夹，找到可执行文件

### 文件夹示例
***
下图目录填写示例：E:/tes，视频1、视频2加密或未加密均可。

运行程序后将会在 E:/tes 下生成“视频1.mp4”、“视频2.mp4”。 
![示例1](https://github.com/RamenRa/m3u8tomp4/blob/main/old/%E7%A4%BA%E4%BE%8B1.PNG)

下图中1号文件，如果是加密视频则必须有

在U某浏览器中，可能存在3号文件。此时此刻，可以没有2号文件。
![示例2](https://github.com/RamenRa/m3u8tomp4/blob/main/old/%E7%A4%BA%E4%BE%8B2.PNG)
