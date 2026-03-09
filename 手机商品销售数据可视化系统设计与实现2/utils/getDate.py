from .query import querys
import pandas as pd
import numpy as np
import math
def getAllProducts():
    def map_fn(item):
        item = list(item)
        item[2] = item[2].replace('元','')
        item[3] = item[3].replace('+人看过','')
        return item

    sql = 'select * from products'
    dataAll = querys(sql,[],'select')
    dataAll = list(map(map_fn,dataAll))
    return dataAll

def getAllUsers():
    sql = 'select * from user'
    dataAll = querys(sql,[],'select')
    return dataAll

def getPriceMean():
    df = pd.DataFrame(
        getAllProducts(),
        columns=['id','title','price','buy_len','img_src','name','address','isFreeDelivery','href','nameHref']
    )
    df["price"] = pd.factorize(df["price"])[0].astype(int)
    return df['price'].mean()

def getMaxAddress():
    df = pd.DataFrame(
        getAllProducts(),
        columns=['id', 'title', 'price', 'buy_len', 'img_src', 'name', 'address', 'isFreeDelivery', 'href','nameHref']
    )
    dic = {

    }
    for i in list(df['address']):
        if dic.get(i,-1) == -1:
            dic[i] = 1
        else:
            dic[i] = dic[i] + 1
    maxCity = ''
    max = 0
    for city,count in dic.items():
        if int(count) > max:
            max = count
            maxCity = city
    return maxCity

def get_history():
    sql = '''select keyword from history order by id desc'''
    return querys(sql,[],'select')

def get_free_delvery():
    df = pd.DataFrame(
        getAllProducts(),
        columns=['id', 'title', 'price', 'buy_len', 'img_src', 'name', 'address', 'isFreeDelivery', 'href','nameHref']
    )
    df['isFreeDelivery'] = df['isFreeDelivery'].astype(np.int64)
    return df['isFreeDelivery'].astype(np.int64).mean()

def get_priceDataTwo():
    allData = getAllProducts()
    cityPriceDic = {}
    for i in allData:
        if cityPriceDic.get(i[6],-1) == -1:
            print(i[6])
            cityPriceDic[i[6]] = int(i[2])
        else:
            cityPriceDic[i[6]] += int(i[2])
    return list(cityPriceDic.keys()),list(cityPriceDic.values())

def get_priceData():
    df = pd.DataFrame(
        getAllProducts(),
        columns=['id', 'title', 'price', 'buy_len', 'img_src', 'name', 'address', 'isFreeDelivery', 'href','nameHref']
    )
    row = []
    df['price'] = df['price'].astype(np.int64)
    maxPrice = df['price'].max()
    for i in range(20):
        row.append(int(maxPrice / 20 * (i+1)))

    column = get_priceData_utilTwo(getAllProducts(),row)
    return row,column

def get_priceData_utilTwo(lis,row):
    column = [0 for x in range(20)]
    for i in lis:
        for index,item in enumerate(row):
            if int(i[2]) <= item:
                column[index] = column[index] + 1
                break
    return column

def get_buy_lenData():
    df = pd.DataFrame(
        getAllProducts(),
        columns=['id', 'title', 'price', 'buy_len', 'img_src', 'name', 'address', 'isFreeDelivery', 'href','nameHref']
    )
    df['buy_len'] = df['buy_len'].apply(lambda x: x.replace('人看过',''))
    df['buy_len'] = df['buy_len'].apply(lambda x: x.replace('+人看过',''))
    row = []
    df['buy_len'] = df['buy_len'].astype(np.int64)
    meanPrice = int(df['buy_len'].mean())
    for i in range(20):
        row.append(int(meanPrice / 20 * (i + 1)))
    column = get_priceData_util(getAllProducts(), row)
    return row,column

def get_priceData_util(lis,row):
    column = [0 for x in range(20)]
    for i in lis:
        i = list(i)
        for index,item in enumerate(row):
            i[2] = i[2].replace('元', '')
            i[3] = i[3].replace('+人看过', '')
            i[3] = i[3].replace('人看过', '')
            if int(i[3]) <= item:
                column[index] = column[index] + 1
                break
    return column

def get_pagination(dataAll,current_page,limit):
    total_page = math.ceil(len(dataAll) / 10)
    min = int(current_page - limit / 2)
    if min <= 0:
        min = 1
    max = min + 10
    if max >= total_page:
        max = total_page + 1

    return list(range(min,max))

def getAllProducts_filter(title,address):
    dataAll = getAllProducts()
    if title:
        dataAll = filter(filter_products_fn(title,address),dataAll)
    elif address:
        dataAll = filter(filter_products_fn(title,address),dataAll)
    else:
        dataAll = filter(filter_products_fn(title,address),dataAll)

    return list(dataAll)

def getAllUser_filter(name):
    dataAll = getAllUsers()
    if not name:return dataAll
    def filter_fn(item):
        if name in item:return True
    dataAll = filter(filter_fn,dataAll)

    return list(dataAll)

def filter_products_fn(title,address):
    if title:
        def filter_fn(item):
            if item[1].find(title) != -1:
                return True
    elif address:
        print(title,address)
        def filter_fn(item):
            if item[6].find(address) != -1:
                return True
    else:
        def filter_fn(item):
            if item[6].find(address) != -1 & item[1].find(title) != -1:
                return True

    return filter_fn

