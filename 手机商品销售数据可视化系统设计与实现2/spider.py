from selenium import webdriver
from pymysql import *
import pandas as pd
from sqlalchemy import create_engine
import time
import re
import csv
import os
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

option = ChromeOptions()
# chrome.exe --remote-debugging-port=9223
option.add_experimental_option("debuggerAddress", "localhost:9223")
# option.add_experimental_option('excludeSwitches', ['enable-automation'])
# option.add_experimental_option('useAutomationExtension', False)

con = connect(host='localhost', user='root', password='root', database='phonedatainfos', port=3306)  # 获取链接对象

def spider_fn(key,max):
    def init():
        pass
    def init_db():
        if con:
            sqlDrop = '''
                            drop table if exists `products`;
                '''
            sql = '''
                    create table products(
                        id int primary key auto_increment,
                        title varchar(2555),
                        price varchar(255),
                        buy_len varchar(255),
                        img_src varchar(2555),
                        name varchar(255),
                        address varchar(255),
                        isFreeDelivery varchar(255),
                        href varchar(2555),
                        nameHref varchar (2555)
                    )
                '''
            cursor = con.cursor()
            cursor.execute(sqlDrop)
            cursor.execute(sql)
            con.commit()
    def search_product(key):
        driver.find_element(By.ID, "q").send_keys(key)
        driver.find_element(By.XPATH,'//button[@class="btn-search tb-bg"]').click()
        driver.maximize_window()
        if len(driver.window_handles) != 0:
            driver.switch_to.window(driver.window_handles[1])
        time.sleep(5)
    def get_product(count, max):
        items = driver.find_elements(By.XPATH,'//div[@class="tbpc-row tbpc-row-start"]/div')
        for div in items:
            count = count + 1
            try:
                title = div.find_element(By.XPATH, './/div[@class="title--qJ7Xg_90 "]/span').text
                price = div.find_element(By.XPATH, './/div[@class="priceInt--yqqZMJ5a"]').text + \
                        div.find_element(By.XPATH, './/div[@class="priceFloat--XpixvyQ1"]').text + '元'
                buy_len = div.find_element(By.XPATH, './/span[@class="realSales--XZJiepmt"]').text
                img_src = div.find_element(By.XPATH, './/img[@class="mainPic--Ds3X7I8z"]').get_attribute('src')
                name = div.find_element(By.XPATH, './/span[@class="shopNameText--DmtlsDKm"]').text
                address = div.find_element(By.XPATH, './/div[@class="procity--wlcT2xH9"]/span').text
                href = div.find_element(By.XPATH, './a').get_attribute(
                    'href')
                nameHref = div.find_element(By.XPATH, './/a[@class="shopName--hdF527QA"]').get_attribute(
                    'href')
                is_free = div.find_element(By.XPATH,
                                           './/div[@class="subIconWrapper--Vl8zAdQn adaptMod--txLgeDX4"]').get_attribute(
                    'title')
                if is_free.find('包邮') != -1:
                    isFreeDelivery = 1
                else:
                    isFreeDelivery = 0
                save_to_csv(title, price, buy_len, img_src, name, address, isFreeDelivery, href, nameHref)

            except:
                count = count - 1
            if count % 10 == 0:
                    print('已爬取%d条数据了' % count)

            if count >= max:
                    print('已爬取指定数据量到csv,即将导入数据库')
                    time.sleep(3)
                    return save_to_sql()
        else:
                driver.find_element(By.XPATH, '//button[@class="next-btn next-medium next-btn-normal next-pagination-item next-next"]').click()
                print('正在翻页。。。')
                time.sleep(5)
                get_product(count,max)
    def main(key):
        count = 0
        init()
        search_product(key)
        get_product(count,max)
    def save_to_csv(title, price, buy_len, img_src, name, address, isFreeDelivery, href, nameHref):
        with open('./data.csv', 'a', encoding='utf-8', newline='') as f:
            myWrite = csv.writer(f, dialect='excel', delimiter=',')
            myWrite.writerow([title, price, buy_len, img_src, name, address, isFreeDelivery, href, nameHref])
    def save_to_sql():
        # init_db()
        products = pd.read_csv("./data.csv")
        df = pd.DataFrame(products)
        conn = create_engine('mysql+pymysql://root:root@localhost:3306/phonedatainfos?charset=utf8')
        df = df_clean(df)
        df.to_sql('products', con=conn, index=False, if_exists='append')
        print('导入数据库成功~')
        cursor = con.cursor()
        cursor.execute('insert into history(keyword) values(%s)', key)
        con.commit()
    def df_clean(df):
        df['price'].replace(r'(\.\d*元)', '', regex=True, inplace=True)
        df['buy_len'].replace(r'(\+?人付款)', '', regex=True, inplace=True)
        df['buy_len'].replace(r'万', '0000', regex=True, inplace=True)
        df['address'] = df['address'].str.split(" ", 1)
        df['address'] = df["address"].str.get(0)
        df.fillna('湖南', inplace=True)
        return df

    main(key)
    # save_to_sql()

def startBrower():
    option = webdriver.ChromeOptions()
    option.add_experimental_option("debuggerAddress", "localhost:9223")
    # chrome.exe --remote-debugging-port=9223
    # option.add_experimental_option("excludeSwitches", ['enable-automation'])
    chrome_service = Service("chromedriver.exe")
    browser = webdriver.Chrome(options=option,service=chrome_service)
    return browser

if __name__ == '__main__':
    # chrome.exe - -remote - debugging - port = 9223
    key = '手机'
    max = 1000
    driver = startBrower()
    driver.get('https://www.taobao.com')
    spider_fn(key,max)
    # layout = [[sg.Button('close webriver')]]
    # window = sg.Window("Title", layout, finalize=True)
    # while True:
    #     event, values = window.read()
    #     if event in (sg.WINDOW_CLOSED, 'close webriver'):
    #         break
    #     print(event, values)

    # driver.close()
    # driver.quit()
    # 下载谷歌版本122.0.6261.95
