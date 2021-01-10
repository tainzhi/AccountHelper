from concurrent.futures import ThreadPoolExecutor
import threading
from db import Db

# 用于保存cookie
# 持久化设置
# 已经爬取的公司信息
db = Db()

# 是否对selenium截的全屏图裁剪, 默认截全屏图
IS_CROP_IMAGE = True

thread_pool = ThreadPoolExecutor(5)
# 默认有天眼查和企查查各1个线程， 总共两个线程
thread_count = 2

# 用于统计当前处理的计数器
g_count = 0
# 总共要处理的数目
g_sum = 0
mutex = threading.Lock()
handled_companies = dict()

# redis参数设置
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_PASSWORD = None

# 某些记性上，截取不到完整的地址，需要添加一些padding
other_padding = 200

divider = '=' * 50