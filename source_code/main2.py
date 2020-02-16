
import random
from flask import Flask, request, render_template, flash, session, url_for, redirect
from sqlalchemy import Table, ForeignKey, Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

app = Flask(__name__, instance_relative_config=True, template_folder='docs',static_folder='docs/js')
app.config.from_pyfile('application.cfg', silent=False)

engine = create_engine(app.config['CONNECTION'], encoding='utf8')
Base = declarative_base()

sqlSession = sessionmaker(bind=engine)

nowstation = None
nowuser = 0

class User(Base):
    __tablename__ = 'USER'

    User_id = Column(Integer, primary_key=True)
    User_name = Column(String(20))
    User_type = Column(Integer)
    password = Column(String(30))
    real_name = Column(String(30))
    phone = Column(String(30))
    email = Column(String(30))
    birth = Column(String(30))
    sex = Column(String(30))

class Station(Base):
    __tablename__ = 'STATION'

    station_id = Column(Integer, primary_key=True)
    station_name = Column(String(20))
    station_type = Column(Integer)
    price = Column(Integer)
    route_id = Column(Integer)
    singletime = Column(String(20))

class Ticket(Base):
    __tablename__ = 'TICKET'

    ticket_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    depart = Column(String(20))
    to = Column(String(20))
    date = Column(String(20))
    time = Column(String(20))
    price = Column(Integer)
    seat = Column(String(20))



@app.route('/')
def indexpage():
    return render_template('page-login.html')

@app.route('/table')
def tablepage():
    users = sqlSession().query(User).all()

    return render_template('table-data-table.html', users=users)

@app.route('/stationtable')
def stationtablepage():
    stations = sqlSession().query(Station).filter_by(station_type=0).all()

    return render_template('table-station.html', stations=stations)

@app.route('/otherstation')
def otherstationpage():
    stations = sqlSession().query(Station).filter_by(station_type=1).all()

    return render_template('table-otherstation.html', stations=stations)

@app.route('/users')
def usertablepage():
    users = sqlSession().query(User).all()

    return render_template('table-user.html', users=users)

@app.route('/users2')
def usertablepage2():
    users = sqlSession().query(User).all()

    return render_template('table-user2.html', users=users)

@app.route('/tickets')
def tickettablepage():
    tickets = sqlSession().query(Ticket).all()

    return render_template('table-ticket.html', tickets=tickets)


@app.route('/tickets2')
def tickettablepage2():
    tickets = sqlSession().query(Ticket).all()

    return render_template('table-ticket2.html', tickets=tickets)

@app.route('/userorder', methods=['GET','POST'])
def userorder():
    order = request.form['order']
    engine.execute(order)
    return redirect(url_for('usertablepage'))


@app.route('/ticketorder', methods=['GET','POST'])
def ticketorder():
    order = request.form['order']
    engine.execute(order)
    return redirect(url_for('tickettablepage'))

@app.route('/history')
def historypage():
    tickets = sqlSession().query(Ticket).filter_by(user_id = nowuser).all()

    return render_template('table-history.html', tickets=tickets)


@app.route('/login', methods=['GET', 'POST'])
def loginpage():
    error = None
    if request.method == 'POST':
        name = request.form['username']
        pas = request.form['password']
        users = engine.execute("select * from user;")
        for i in users:
            if i[1] == name:
                if i[3] == pas:
                    session['logged_in'] = True
                    flash('You were logged in')
                    # return render_template('success.html')
                    global nowuser
                    nowuser = i[0]
                    return redirect(url_for('stationtablepage'))
                else:
                    error = 'wrong password'
                    return render_template('page-login.html', error=error)
        error = 'Not exist!'
        return render_template('page-login.html', error=error)
    return render_template('page-login.html', error=error)


@app.route('/requirement', methods=['GET', 'POST'])
def requirement():
    if request.method == 'POST':
        req = request.form['comment']
        x = engine.execute("select max(requirement_id) from requirement;")
        for i in x:
            max = i[0]
        engine.execute("Insert into requirement values({},{},'{}')".format(max+1, nowuser, req))
        return "已收到您的留言，我们很重视您的要求！"
    else:
        return render_template('page-requirement.html')






@app.route('/adminlogin', methods=['GET', 'POST'])
def adminloginpage():
    error = None
    if request.method == 'POST':
        name = request.form['username']
        pas = request.form['password']
        if name=='admin' and pas=='admin':
            return redirect(url_for('usertablepage'))
        if name == 'driver' and pas == 'driver':
            return redirect(url_for('usertablepage2'))
            #return "管理员登陆成功！"
        else:
            return render_template('page-adminlogin.html',error='输入错误')
    return render_template('page-adminlogin.html', error=error)


@app.route('/regist', methods=['GET', 'POST'])
def registpage():
    error = None
    if request.method == 'POST':
        uname = request.form['username']
        if uname==None:
            error = '名字不能为空'
            return render_template('page-regist.html', error=error)
        upass = request.form['password']
        users = sqlSession().query(User).all()
        for i in users:
            if uname==i.User_name:
                error = 'already exists'
                return render_template('page-regist.html', error=error)
        realname = request.form['realname']
        phone = request.form['phone']
        sex = request.form['sex']
        email = request.form['email']
        birth = request.form['birth']
        x = engine.execute("select max(User_id) from user;")
        for i in x:
            max = i[0]
        engine.execute("Insert into user values({},'{}',{},'{}','{}','{}','{}','{}','{}')".format(max+1,uname,1,upass,realname,phone,email,birth,sex))
        return render_template('page-login.html', error="注册成功，请登录")
    else:
        return render_template('page-regist.html', error=error)


@app.route('/buyticket/<station>')
def buypage(station):
    global nowstation
    nowstation = station
    #return "this is %s "%station
    return render_template('buy.html', station=station)



@app.route('/buyticket22/<f>/<t>/<d>/<time>/<seat>')
def buypage22(f,t,d,time,seat):
    x = engine.execute("select max(ticket_id) from Ticket;")
    result = engine.execute("select price from station where station_name = '{}'".format(nowstation))
    p = 0
    for r in result:
        p = int(r[0])  # 对应站点的票价

    for i in x:
        max = i[0]  # 当前票的最大id

    engine.execute("Insert into ticket values({},{},'{}','{}','{}','{}',{},'{}' )".format(max + 1, nowuser, f, t, d, time, p, seat))

    return "购买成功！出发地为{}, 目的地为{}, 发车时间为{}，座位为{} ".format(f, t, time, seat)









@app.route('/buyticket2/<station>')
def buypage2(station):
    global nowstation
    nowstation = station
    #return "this is %s "%station
    return render_template('buy21.html', station=station)


@app.route('/withdraw/<ticket_id>', methods=['GET','POST'])
def withdrawpage(ticket_id):
    if request.method == 'POST':
        if request.form['choice']=='0':
            return redirect(url_for('historypage'))
    #return "this is %s "%station
        else:
            engine.execute("delete from ticket where ticket_id = {}".format(ticket_id))
            return "退票成功"
    return render_template('withdraw.html', ticket_id=ticket_id)



@app.route('/buysuccess',methods = ['Get','Post'])
def buysuccesspage():
    direction = int(request.form['direction'])
    month = request.form['month']
    day = request.form['day']
    d = '2019-{}-{}'.format(month,day)
    x = engine.execute("select max(ticket_id) from Ticket;")
    result = engine.execute("select price from station where station_name = '{}'".format(nowstation))
    p = 0
    for r in result:
        p = int(r[0])

    for i in x:
        max = i[0]
    if direction == 0:
        engine.execute("Insert into ticket values({},{},'{}','{}','{}','{}',{},'{}' )".format(max + 1, nowuser, '机场', nowstation,d, '当日', p,'任意'))
    else:
        engine.execute("Insert into ticket values({},{},'{}','{}','{}','{}',{},'{}' )".format(max + 1, nowuser, nowstation,'机场', d, '当日', p,'任意'))

    return "购买成功！方向为{}, station为{} ".format(direction, nowstation)


@app.route('/buysuccess21',methods = ['Get','Post'])    #选择了站点，方向，日期后, 展示各时间票余量
def buysuccesspage21():
    direction = int(request.form['direction'])
    month = request.form['month']
    day = request.form['day']
    name = nowstation
    d='2019-{}-{}'.format(month,day)
    times = ['6:30', '8:00', '12:00', '3:00']
    timetable = {times[0]: {'A': 10, 'B': 10, 'C': 10, 'D': 10, 'E': 10},
                 times[1]: {'A': 10, 'B': 10, 'C': 10, 'D': 10, 'E': 10},
                 times[2]: {'A': 10, 'B': 10, 'C': 10, 'D': 10, 'E': 10},
                 times[3]: {'A': 10, 'B': 10, 'C': 10, 'D': 10, 'E': 10}}
    if direction==0:
        results = engine.execute("select `time`,seat,count(*) as n from ticket where `to`='机场' AND date = '{}' AND depart='{}'  group by `time`,seat;".format(d, name))
        for r in results:
            timetable[r[0]][r[1]] = 10-r[2]
        return render_template('table-left.html', f=name, t='机场', d=d, timetable=timetable)
    else:
        results = engine.execute("select `time`,seat,count(*) as n from ticket where `depart`='机场' AND date = '{}' AND depart='{}'  group by `time`,seat;".format(d, name))
        for r in results:
            timetable[r[0]][r[1]] = 10-r[2]
        return render_template('table-left.html', t=name, f='机场', d=d, timetable=timetable)



@app.route('/buysuccess2',methods = ['Get','Post'])
def buysuccesspage2():
    direction = int(request.form['direction'])
    month = request.form['month']
    day = request.form['day']
    stime = request.form['time']
    sseat = request.form['seat']
    d = '2019-{}-{}'.format(month,day)
    x = engine.execute("select max(ticket_id) from Ticket;")
    result = engine.execute("select price from station where station_name = '{}'".format(nowstation))
    p = 0
    for r in result:
        p = int(r[0])     #对应站点的票价

    for i in x:
        max = i[0]          #当前票的最大id
    if direction == 0:
        engine.execute("Insert into ticket values({},{},'{}','{}','{}','{}',{},'{}' )".format(max + 1, nowuser, '机场', nowstation,d, stime, p, sseat))
    else:
        engine.execute("Insert into ticket values({},{},'{}','{}','{}','{}',{},'{}' )".format(max + 1, nowuser, nowstation,'机场', d, stime, p,sseat))

    return "购买成功！方向为{}, station为{}, 发车时间为{}，座位为{} ".format(direction, nowstation, stime, sseat)







if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, threaded=True)












