import time
from selenium import webdriver#导入库
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from const_config import qqid,qqpw
option=webdriver.ChromeOptions()
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36";
option.add_argument("user-agent=" + USER_AGENT);
option.add_argument("--headless");
option.add_argument("--ignore-certificate-errors")  # 忽略证书错误
option.add_argument("disable-extensions")  # 禁用扩展
option.add_argument("--disable-gpu")  # 谷歌文档提到需要加上这个属性来规避bug
option.add_argument("--hide-scrollbars")  # 隐藏滚动条, 应对一些特殊页面
option.add_argument("blink-settings=imagesEnabled=false")  # 不加载图片, 提升速度
url='https://y.qq.com'
def get_cookie():
    driver = webdriver.Chrome(options=option)
    #print(1)
    driver.get(url)#打开浏览器预设网址
    driver.find_element(By.CSS_SELECTOR,'#app > div > div.mod_header > div > div.header__opt > span > a').click()
    #print(2)
    time.sleep(2)
    driver.switch_to.frame('login_frame')
    driver.switch_to.frame('ptlogin_iframe')
    driver.find_element(By.CSS_SELECTOR,'#switcher_plogin').click()
    user=driver.find_element(By.CSS_SELECTOR,'#u')
    user.send_keys(qqid)
    pas=driver.find_element(By.CSS_SELECTOR,'#p')
    pas.send_keys(qqpw)
    pas.send_keys(Keys.RETURN)
    #print(3)
    time.sleep(2)
    driver.refresh()
    time.sleep(2)
    str=''
    for cookie in driver.get_cookies():
        str=str+cookie['name']+'='+cookie['value']+'; '
    with open('cookie.txt','w') as f:
        f.write(str)
        f.close()
    print('cookie:',str)
    #print(4)
    driver.quit()

if __name__=='__main__':
    get_cookie()
