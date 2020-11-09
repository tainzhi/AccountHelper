##  财务工具

## 使用方法

### 1 下载chrome驱动
- [chrome driver install](https://blog.csdn.net/n123456uo/article/details/91412740)
### 

## package to executable file
- download `pyinstaller` module
- in terminal window, type `pyinstaller -F main.py`, then the generated executable file is saved in `dist/`
- [pyinstaller不是交叉编译软件, 可以跨平台, 但是要在不同平台分别打包; 对运行性能没有直接影响](https://gitchat.csdn.net/activity/5c8f101aa7494e3e31a04743)
- 为了减小打包体积, 只import需要的module
- parameter
>- `-F`, generated single zip executable file; without `-F`, 生成一堆文件， 但运行速度快
>- `-W`, 禁止弹出控制台窗口
>- `--uac-admin`, `-m`, manifest File
>- `-i <icon File`, icon

## pipenv
- 改变source， 根目录下的`Pipfile`url为, 同时更改name, ide会自动弹出Notification提醒**pipenv update**
- 优点: 跨平台支持良好(不同平台不产生多余配置文件), 不产生env目录, 自动管理更新下载依赖包 
```
http://mirrors.aliyun.com/pypi/simple/

```

## 包错误
- [安装最新版本的上一个版本](https://blog.csdn.net/HsinglukLiu/article/details/109555299)

## Todo
- [添加执行icon和管理员权限盾牌](https://blog.csdn.net/laiyaoditude/article/details/85278037)
- 企查查多线程操作, 登录使用cookie
- python async
- python多线程线程池

## python 4中截屏方法
- [python class](https://www.runoob.com/python3/python3-class.html): Selenium支持跨平台(win10/mac)
- [python multi thread](https://www.runoob.com/python3/python3-multithreading.html)
- [python 4种截屏方法](https://www.jb51.net/article/168609.htm)
- [selenium反爬虫](https://blog.csdn.net/weixin_44685869/article/details/105602629?utm_medium=distribute.pc_relevant.none-task-blog-title-3&spm=1001.2101.3001.4242)