from flask import Flask,request,render_template,session,redirect,jsonify
from utils.query import querys
import re
import time
from utils.getDate import *
import random
from datetime import datetime
import os
from model.index import predict
app = Flask(__name__)
app.secret_key = 'This is a app.secret_Key , You Know ?'
basedir = os.path.abspath(os.path.dirname(__file__))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        request.form = dict(request.form)

        def filter_fns(item):
            return request.form['uname'] in item and request.form['password'] in item

        users = querys('select * from user', [], 'select')
        login_success = list(filter(filter_fns, users))
        if not len(login_success):
            return '账号或密码错误'

        session['uname'] = request.form['uname']
        session['userId'] = login_success[0][0]
        if request.form['uname'] == 'admin':
            session['role'] = 'admin'
        else:
            session['role'] = 'user'
        return redirect('/home/1', 301)

    else:
        return render_template('./login.html')

@app.route('/registry',methods=['get','post'])
def registry():
    if request.method == 'POST':
        request.form = dict(request.form)
        if request.form['password'] != request.form['passwordCheked']:
            return '两次密码不符'
        else:
            def filter_fn(item):
                return request.form['uname'] in item

            users = querys('select * from user', [], 'select')
            filter_list = list(filter(filter_fn, users))
            if len(filter_list):
                return '该用户名已被注册'
            else:
                querys('insert into user(uname,password) values(%s,%s)',
                        [request.form['uname'], request.form['password']])

        return redirect('/login', 301)

    else:
        return render_template('./registry.html')

@app.route("/home/<int:page>")
def home(page):
    limit = 10
    uname = session['uname']
    nowTime = time.strftime("%Y %B %d %A", time.localtime())
    dataAll = getAllProducts()
    priceMean = getPriceMean()
    addressMaxCity = getMaxAddress()
    nowHistory = get_history()
    freeDelveryBi = int(get_free_delvery() * 100)
    row, column = get_priceData()
    paginations = get_pagination(dataAll,page, limit)
    return render_template(
        'home.html',
        uname=uname,
        nowTime=nowTime,
        productCount=len(dataAll),
        priceMean=int(priceMean),
        addressMaxCity=addressMaxCity,
        nowHistory=nowHistory,
        freeDelveryBi=freeDelveryBi,
        row=row,
        column=column,
        products=dataAll[(page - 1) * limit:page * limit],
        paginations=paginations,
        nowPage=page,
        totalpage=math.ceil(len(dataAll) / 10),
        role=session['role']
    )

@app.route('/addNotice',methods=['GET','POST'])
def addNotice():
    uname = session['uname']
    role = session['role']
    defaultStart = 0
    if request.args.get('start'): defaultStart = request.args.get('start')
    if request.method == 'GET':
        return render_template('addNotice.html', uname=uname, role=role, defaultStart=defaultStart)
    else:
        content = request.form['content']
        p_id = request.form['p_id']
        start = request.form['start']
        querys('insert into notices(role,message,username,p_id,start) values(%s,%s,%s,%s,%s)',
               [role, content, uname, p_id, start])
        return redirect('/home/1')


@app.route('/seeNotice/<int:dropId>')
def seeNotice(dropId):
    uname = session['uname']
    role = session['role']
    if dropId != '0':
        querys('DELETE FROM notices WHERE id = %s', [dropId])
    noticeList = querys('select * from notices',[],'select')
    return render_template('seeNotice.html',uname=uname,role=role,noticeList=noticeList,lenList=len(noticeList))

@app.route('/upload/',methods=['POST'])
def upload():
    f = request.files.get('file')
    random_num = random.randint(0, 100)
    filename = datetime.now().strftime("%Y%m%d%H%M%S") + "_" + str(random_num) + "." + f.filename.rsplit('.', 1)[1]
    file_path = basedir + "/static/file/" + filename
    f.save(file_path)
    data = {"msg": "success", "url": "/static/file/" + filename}
    payload = jsonify(data)
    return payload, 200

@app.route('/addProduct',methods=['get','post'])
def addProduct():
    uname = session['uname']
    role = session['role']
    if request.method == 'GET':
        return render_template('addProduct.html',uname=uname,role=role)
    else:
        querys('''insert into products(title,price,buy_len,img_src,name,address,isFreeDelivery,href,nameHref) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
               [
                   request.form['title'],
                   request.form['price'],
                   request.form['buy_len'],
                   request.form['img_src'],
                   request.form['name'],
                   request.form['address'],
                   '1' if request.form['isFreeDelivery'] == '是' else '0',
                   '#',
                   '#'
               ])
        return redirect('/table/1/0')

@app.route('/editProduct/<int:p_id>',methods=['get','post'])
def editProduct(p_id):
    uname = session['uname']
    role = session['role']
    if request.method == 'GET':
        p_info = querys('select * from products where id = %s',[p_id],'select')
        return render_template('editProduct.html',uname=uname,role=role,p_info=p_info[0],p_id=p_id)
    else:
        querys('''
            Update products set title=%s,price=%s,buy_len=%s,img_src=%s,name=%s,address=%s where id = %s
        ''',[
            request.form['title'],
            request.form['price'],
            request.form['buy_len'],
            request.form['img_src'],
            request.form['name'],
            request.form['address'],
            p_id
        ])
        return redirect('/table/1/0')

@app.route("/address_t")
def address_t():
    uname = session['uname']
    address_all = querys('select * from products',[],'select')
    data_all = [

    ]
    data_allTwo = [

    ]
    china = [
        {
            "ProID": 1,
            "name": "北京",
            "ProSort": 1,
            "ProRemark": "直辖市"
        },
        {
            "ProID": 2,
            "name": "天津",
            "ProSort": 2,
            "ProRemark": "直辖市"
        },
        {
            "ProID": 3,
            "name": "河北",
            "ProSort": 5,
            "ProRemark": "省份"
        },
        {
            "ProID": 4,
            "name": "山西",
            "ProSort": 6,
            "ProRemark": "省份"
        },
        {
            "ProID": 5,
            "name": "内蒙古自治区",
            "ProSort": 32,
            "ProRemark": "自治区"
        },
        {
            "ProID": 6,
            "name": "辽宁",
            "ProSort": 8,
            "ProRemark": "省份"
        },
        {
            "ProID": 7,
            "name": "吉林",
            "ProSort": 9,
            "ProRemark": "省份"
        },
        {
            "ProID": 8,
            "name": "黑龙江",
            "ProSort": 10,
            "ProRemark": "省份"
        },
        {
            "ProID": 9,
            "name": "上海",
            "ProSort": 3,
            "ProRemark": "直辖市"
        },
        {
            "ProID": 10,
            "name": "江苏",
            "ProSort": 11,
            "ProRemark": "省份"
        },
        {
            "ProID": 11,
            "name": "浙江",
            "ProSort": 12,
            "ProRemark": "省份"
        },
        {
            "ProID": 12,
            "name": "安徽",
            "ProSort": 13,
            "ProRemark": "省份"
        },
        {
            "ProID": 13,
            "name": "福建",
            "ProSort": 14,
            "ProRemark": "省份"
        },
        {
            "ProID": 14,
            "name": "江西",
            "ProSort": 15,
            "ProRemark": "省份"
        },
        {
            "ProID": 15,
            "name": "山东",
            "ProSort": 16,
            "ProRemark": "省份"
        },
        {
            "ProID": 16,
            "name": "河南",
            "ProSort": 17,
            "ProRemark": "省份"
        },
        {
            "ProID": 17,
            "name": "湖北",
            "ProSort": 18,
            "ProRemark": "省份"
        },
        {
            "ProID": 18,
            "name": "湖南",
            "ProSort": 19,
            "ProRemark": "省份"
        },
        {
            "ProID": 19,
            "name": "广东",
            "ProSort": 20,
            "ProRemark": "省份"
        },
        {
            "ProID": 20,
            "name": "海南",
            "ProSort": 24,
            "ProRemark": "省份"
        },
        {
            "ProID": 21,
            "name": "广西壮族自治区",
            "ProSort": 28,
            "ProRemark": "自治区"
        },
        {
            "ProID": 22,
            "name": "甘肃",
            "ProSort": 21,
            "ProRemark": "省份"
        },
        {
            "ProID": 23,
            "name": "陕西",
            "ProSort": 27,
            "ProRemark": "省份"
        },
        {
            "ProID": 24,
            "name": "新疆维吾尔自治区",
            "ProSort": 31,
            "ProRemark": "自治区"
        },
        {
            "ProID": 25,
            "name": "青海",
            "ProSort": 26,
            "ProRemark": "省份"
        },
        {
            "ProID": 26,
            "name": "宁夏回族自治区",
            "ProSort": 30,
            "ProRemark": "自治区"
        },
        {
            "ProID": 27,
            "name": "重庆",
            "ProSort": 4,
            "ProRemark": "直辖市"
        },
        {
            "ProID": 28,
            "name": "四川",
            "ProSort": 22,
            "ProRemark": "省份"
        },
        {
            "ProID": 29,
            "name": "贵州",
            "ProSort": 23,
            "ProRemark": "省份"
        },
        {
            "ProID": 30,
            "name": "云南",
            "ProSort": 25,
            "ProRemark": "省份"
        },
        {
            "ProID": 31,
            "name": "西藏自治区",
            "ProSort": 29,
            "ProRemark": "自治区"
        },
        {
            "ProID": 32,
            "name": "台湾",
            "ProSort": 7,
            "ProRemark": "省份"
        },
        {
            "ProID": 33,
            "name": "澳门特别行政区",
            "ProSort": 33,
            "ProRemark": "特别行政区"
        },
        {
            "ProID": 34,
            "name": "香港特别行政区",
            "ProSort": 34,
            "ProRemark": "特别行政区"
        }
    ]
    for i in china:
        data_all.append({
            'name':i['name'],
            'value':0
        })
        data_allTwo.append({
            'name':i['name'],
            'value':0
        })
    for i in address_all:
        i = list(i)
        for index,j in enumerate(data_all):
            if i[6] == j['name']:
                i[3] = i[3].replace('+人看过','')
                i[3] = i[3].replace('人看过','')
                j['value'] += 1
                data_allTwo[index]['value'] += int(i[3])
                break

    return render_template('address_t.html',uname=uname,data_all=data_all,
                           role=session['role'],
                           data_allTwo=data_allTwo
                           )

@app.route("/price_t")
def price_t():
    uname = session['uname']
    row, column = get_priceData()
    X,Y=get_priceDataTwo()
    return render_template('price_t.html',uname=uname,row=row,column=column,
                           role=session['role'],
                           X=X,
                           Y=Y
                           )

@app.route("/free_deliVer_t")
def free_deliVer_t():
    uname = session['uname']
    delivery_all = querys('select address,isFreeDelivery from products', [], 'select')
    cityDic = {}
    for i in delivery_all:
        if cityDic.get(i[0],-1) == -1:
            cityDic[i[0]] = 1
        else:
            cityDic[i[0]] += 1
    citySorted = list(sorted(cityDic.items(),key=lambda x:x[1],reverse=True))
    listCity = [x[0] for x in citySorted][:6]
    res1 = [{
        'name':'包邮',
        'value':0
    },{
        'name':'需邮费',
        'value':0
    }]
    res2 = [{
        'name':'包邮',
        'value':0
    },{
        'name':'需邮费',
        'value':0
    }]
    res3 = [{
        'name':'包邮',
        'value':0
    },{
        'name':'需邮费',
        'value':0
    }]
    res4 = [{
        'name':'包邮',
        'value':0
    },{
        'name':'需邮费',
        'value':0
    }]
    res5 = [{
        'name':'包邮',
        'value':0
    },{
        'name':'需邮费',
        'value':0
    }]
    res6 = [{
        'name':'包邮',
        'value':0
    },{
        'name':'需邮费',
        'value':0
    }]
    for i in delivery_all:
        if i[0] == listCity[0]:
            if i[1] == '1':
                res1[0]['value'] += 1
            else:
                res1[1]['value'] += 1
        elif i[0] == listCity[1]:
            if i[1] == '1':
                res2[0]['value'] += 1
            else:
                res2[1]['value'] += 1
        elif i[0] == listCity[2]:
            if i[1] == '1':
                res3[0]['value'] += 1
            else:
                res3[1]['value'] += 1
        elif i[0] == listCity[3]:
            if i[1] == '1':
                res4[0]['value'] += 1
            else:
                res4[1]['value'] += 1
        elif i[0] == listCity[4]:
            if i[1] == '1':
                res5[0]['value'] += 1
            else:
                res5[1]['value'] += 1
        elif i[0] == listCity[5]:
            if i[1] == '1':
                res6[0]['value'] += 1
            else:
                res6[1]['value'] += 1
    # for i in delivery_all:
    #     for j in randomCityList:
    #         if i[0] == j:
    #             for i in delivery_all:
    #                 dataRes.append({})
    return render_template('free_deliVer_t.html', uname=uname,
                           role=session['role'],
                           res1=res1,
                           res2=res2,
                           res3=res3,
                           res4=res4,
                           res5=res5,
                           res6=res6,
                           listCity=listCity
                           )

@app.route("/buy_len_t")
def buy_len_t():
    uname = session['uname']
    row, column = get_buy_lenData()
    return render_template('buy_len_t.html', uname=uname, row=row, column=column,        role=session['role']
)

@app.route("/product_p")
def product_p():
    uname = session['uname']
    return render_template('product_p.html', uname=uname,        role=session['role']
)

@app.route("/name_p")
def name_p():
    uname = session['uname']
    return render_template('name_p.html', uname=uname,role=session['role']
)

@app.route("/address_p")
def address_p():
    uname = session['uname']
    return render_template('address_p.html', uname=uname,role=session['role']
)

@app.route("/userList/<int:page>/<int:dropId>",methods=['GET','POST'])
def userList(page,dropId):
    if request.method == 'GET':
        if dropId != 0:
            sqlSelect = 'select * from user where id = %s'
            obj = querys(sqlSelect,[dropId],'select')
            if len(obj) == 1:
                sqlDrop = 'delete from user where id = %s'
                querys(sqlDrop, [dropId])

        limit = 10
        uname = session['uname']
        dataAll = getAllUsers()
        paginations = get_pagination(dataAll, page, limit)
        totalpage = math.ceil(len(dataAll) / limit)
        return render_template(
            'userList.html',
            uname=uname,
            products=dataAll[(page - 1) * limit:page * limit],
            paginations=paginations,
            nowPage=page,
            totalpage=totalpage,
            role=session['role']
        )
    elif request.method == 'POST':
        if dropId != 0:
            sqlSelect = 'select * from user where id = %s'
            obj = querys(sqlSelect,[dropId],'select')
            if len(obj) == 1:
                sqlDrop = 'delete from user where id = %s'
                querys(sqlDrop, [dropId])

        limit = 10
        uname = session['uname']
        searchForm = dict(request.form)
        dataAll = getAllUser_filter(searchForm['name'])
        paginations = get_pagination(dataAll,page, limit)
        totalpage = math.ceil(len(dataAll) / limit)
        return render_template(
            'userList.html',
            uname=uname,
            products=dataAll[(page - 1) * limit:page * limit],
            paginations=paginations,
            nowPage=page,
            totalpage=totalpage
        )

@app.route("/table/<int:page>/<int:dropId>",methods=['GET','POST'])
def table(page,dropId):
    if request.method == 'GET':
        if dropId != 0:
            sqlSelect = 'select * from products where id = %s'
            obj = querys(sqlSelect,[dropId],'select')
            if len(obj) == 1:
                sqlDrop = 'delete from products where id = %s'
                querys(sqlDrop, [dropId])

        limit = 10
        uname = session['uname']
        dataAll = getAllProducts()
        paginations = get_pagination(dataAll, page, limit)
        totalpage = math.ceil(len(dataAll) / limit)
        return render_template(
            'table.html',
            uname=uname,
            products=dataAll[(page - 1) * limit:page * limit],
            paginations=paginations,
            nowPage=page,
            totalpage=totalpage,
            role=session['role']
        )
    elif request.method == 'POST':
        if dropId != 0:
            sqlSelect = 'select * from products where id = %s'
            obj = querys(sqlSelect,[dropId],'select')
            if len(obj) == 1:
                sqlDrop = 'delete from products where id = %s'
                querys(sqlDrop, [dropId])

        limit = 10
        uname = session['uname']
        searchForm = dict(request.form)
        dataAll = getAllProducts_filter(**searchForm)
        paginations = get_pagination(dataAll,page, limit)
        totalpage = math.ceil(len(dataAll) / limit)
        return render_template(
            'table.html',
            uname=uname,
            products=dataAll[(page - 1) * limit:page * limit],
            paginations=paginations,
            nowPage=page,
            totalpage=totalpage
        )

@app.route("/changeUserInfo",methods=['GET','POST'])
def changeUserInfo():
    uname = session['uname']
    if request.method == 'GET':
        return render_template('changeUserInfo.html',uname=uname)
    else:
        olduserPasswor = querys('select password from user where uname=%s',[uname],'select')[0][0]
        if olduserPasswor != request.form.get('oldPassword'):return '输入的原始密码不符合'
        querys('''
                    Update user set password=%s where uname = %s
                ''', [
            request.form.get('newPassword'),
            uname
        ])
        return redirect('/login')

@app.route('/')
def redirect_to_home():
    return redirect('/login')

@app.before_request
def before_requre():
    pat = re.compile(r'^/static')
    if re.search(pat,request.path):
        return
    if request.path == "/login" :
        return
    if request.path == '/registry':
        return
    uname = session.get('uname')
    if uname:
        return None

    return redirect("/login")


@app.route("/model",methods=['GET','POST'])
def model():
    uname = session['uname']
    result = predict(session['userId'])
    return render_template('model.html', uname=uname, role=session['role'], result=result)


if __name__ == '__main__':
    app.run(port=5001)
