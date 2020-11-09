## install driver

## usage
- 无头chrome,但是会被反爬虫 403 forbidden
- 打开新的tab后, 必须要切换tab, 否则无法找到想要的element
```python
from selenium import webdriver

option = webdriver.ChromeOptions()
option.add_argument('--headless')
option.add_argument('--disable-gpu')
driver = webdriver.Chrome(driver_location, options=option)

# 反爬虫
script = 'Object.defineProperty(navigator,"webdriver",{get:() => false,});'
driver.execute_script(script)

driver.maximize_window()

# 获取当前所有的打开的浏览器窗口
windowstabs = driver.window_handles
# 切换到新窗口
driver.switch_to.window(windowstabs[1])
# 再切换到之前的窗口
driver.switch_to.window(windowstabs[0])
# 关闭当前窗口
driver.close()

# 获取当前浏览器的窗口
currentab =driver.current_window_handle
```
# 定位到新打开的tab
```python
# 方式一
time.sleep(1)
search_window = driver.current_window_handle  # 此行代码用来定位当前页面

# 方式二
time.sleep(1)
driver.switch_to.window(driver.window_handles[0])
```
# 获取属性
```python
link = driver.find_element_by_css_selector(".name")
# 获取连接属性
a = link.get_attribute('href')
```

# 使用快捷键操作chrome
```python
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

#新建标签页
ActionChains(browser).key_down(Keys.CONTROL).send_keys("t").key_up(Keys.CONTROL).perform()
# 关闭标签页
ActionChains(browser).key_down(Keys.CONTROL).send_keys("w").key_up(Keys.CONTROL).perform()
```

