from flask import Flask,render_template,url_for,redirect,request,json,jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
from bs4 import BeautifulSoup
import requests
import re
from urllib.request import urlopen
import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1346536639@127.0.0.1/password?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'aodong'
app.debug=True
db=SQLAlchemy(app)

class Allpasswords(db.Model):
    __tablename__='allpasswords'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20),nullable=False)
    userid=db.Column(db.String(30),nullable=False)
    password=db.Column(db.String(30),nullable=False)
    weburl=db.Column(db.String(300),nullable=False)
    iconurl=db.Column(db.String(100),nullable=False)
    createtime=db.Column(db.String(50),nullable=False)
    changetime=db.Column(db.String(50),nullable=False)

class Collections(db.Model):
    __tablename__='collections'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20),nullable=False)
    userid=db.Column(db.String(30),nullable=False)
    password=db.Column(db.String(30),nullable=False)
    weburl=db.Column(db.String(300),nullable=False)
    iconurl=db.Column(db.String(50),nullable=False)

@app.route('/mypassword',methods=['GET','POST'])
def indexpage():
    if request.method=="GET":
        return render_template('index.html')
@app.route('/getallpassword',methods=['POST'])
def getallpassword():
    if request.method=="POST":
        allinformation=Allpasswords.query.all()
        alllist=[]
        for i in range(len(allinformation)):
            alllist.append([allinformation[i].name,allinformation[i].userid,allinformation[i].iconurl])
        return jsonify(alllist)

@app.route('/getdetail',methods=['POST'])
def getdetail():
    if request.method=="POST":
        webname=json.loads(request.form.get('mywebname'))
        print(webname)
        detal=Allpasswords.query.filter_by(name=webname).first()
        detallist=[webname,detal.userid,detal.password,detal.weburl,detal.iconurl]
        detalincollect=Collections.query.filter_by(name=webname).first()
        if detalincollect==None:
            detallist.append(0)
        else:
            detallist.append(1)
        detallist.append(detal.createtime)
        detallist.append(detal.changetime)
        return jsonify(detallist)

@app.route('/getdelete',methods=['POST'])
def getdelete():
    if request.method=="POST":
        webname=json.loads(request.form.get('webname'))
        webobj=Allpasswords.query.filter_by(name=webname).first()
        db.session.delete(webobj)
        db.session.commit()
        print("删除成功")
        if Collections.query.filter_by(name=webname).first()!=None:
            db.session.delete(Collections.query.filter_by(name=webname).first())
            db.session.commit()
        return ''
#         newpassword=Allpasswords(name=webname,userid=username,password=password,weburl=weburl,iconurl=icourl)
@app.route('/getcollect',methods=['POST'])
def getcollect():
    if request.method=="POST":
        webname=json.loads(request.form.get('webname'))
        flag=json.loads(request.form.get('flag'))
        if flag=="1":
#             存入收藏夹
            passwordobj=Allpasswords.query.filter_by(name=webname).first()
            userid=passwordobj.userid
            password=passwordobj.password
            weburl=passwordobj.weburl
            iconurl=passwordobj.iconurl
            newcollect=Collections(name=webname,userid=userid,password=password,weburl=weburl,iconurl=iconurl)
            db.session.add(newcollect)
            db.session.commit()
        else:
            deleteobj=Collections.query.filter_by(name=webname).first()
            db.session.delete(deleteobj)
            db.session.commit()
        return ''

@app.route('/getitchange',methods=['POST'])
def getitchange():
    if request.method=='POST':
        name=json.loads(request.form.get('name'))
        webname=json.loads(request.form.get('newwebname'))
        username=json.loads(request.form.get('newusername'))
        password=json.loads(request.form.get('newpassword'))
        weburl=json.loads(request.form.get('newweburl'))
        changeitem=Allpasswords.query.filter_by(name=name).first()
        changeitem.name=webname
        changeitem.userid=username
        changeitem.password=password
        changeitem.weburl=weburl
        nowtime=str(datetime.datetime.now())[:16]
        changeitem.changetime=nowtime
        db.session.commit()
        if Collections.query.filter_by(name=name).first()!=None:
            changeincollect=Collections.query.filter_by(name=name).first()
            changeincollect.name=webname
            changeincollect.userid=username
            changeincollect.password=password
            changeincollect.weburl=weburl

            db.session.commit()
        return ''

@app.route('/getcollectlist',methods=['POST'])
def getcollectlist():
    if request.method=="POST":
        collectlist=[]
        allcollect=Collections.query.all()
        for i in range(len(allcollect)):
            collectlist.append([allcollect[i].name,allcollect[i].userid,allcollect[i].password,allcollect[i].weburl,allcollect[i].iconurl])
        return jsonify(collectlist)

@app.route('/getsearch',methods=['POST'])
def getsearch():
    if request.method=="POST":
        content=json.loads(request.form.get('content'))
        searchlist=[]
        alllist=Allpasswords.query.all()
        for i in range(len(alllist)):
            searchstr=str(alllist[i].name)+" "+str(alllist[i].userid)+" "+str(alllist[i].password)+" "+str(alllist[i].weburl)+" "+str(alllist[i].iconurl)
            if content in searchstr:
                searchlist.append([alllist[i].name,alllist[i].userid,alllist[i].iconurl])
        return jsonify(searchlist)

@app.route('/addpassword',methods=['POST'])
def addpassword():
    if request.method=="POST":
        webname=json.loads(request.form.get('webname'))
        username=json.loads(request.form.get('username'))
        password=json.loads(request.form.get('password'))
        weburl=json.loads(request.form.get('weburl'))
        icourl=""
        if weburl!="":

        #     爬取图标
            html=urlopen(weburl)
            bsobj=BeautifulSoup(html.read())
            ico=bsobj.find("link",{'href':re.compile('//.*ico')})
            if ico==None:
            #     换一个选择方式
                icoofref=bsobj.find("link",{'rel':'icon'})
                if icoofref==None:
                    icourl=""
                else:
                    icourl=icoofref['href']
            else:
                icourl=ico['href']
        if ('com' not in icourl) and ('cn' not in icourl):
            newweburl=""
            for i in range(len(weburl)):
                if i != len(weburl)-1:
                    newweburl+=weburl[i]
                else:
                    if weburl[i] !='/':
                        newweburl+=weburl[i]
            icourl=newweburl+icourl
        if icourl==None:
            icourl=""
        createtime=str(datetime.datetime.now())[:16]
        changetime=createtime
        newpassword=Allpasswords(name=webname,userid=username,password=password,weburl=weburl,iconurl=icourl,createtime=createtime,changetime=changetime)
        db.session.add(newpassword)
        db.session.commit()

        return ''
if __name__ == '__main__':
    db.create_all()
    app.run()