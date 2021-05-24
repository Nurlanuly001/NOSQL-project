from functools import reduce
from re import L
from flask import Flask, render_template, request, json,redirect,jsonify ,  session
from flask_mongoengine import MongoEngine
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from pymongo import MongoClient
from bson.json_util import dumps,loads

app = Flask(__name__,static_url_path='')
app.secret_key = "mongodb_agro"
app.config.from_object(__name__)


app.config['MONGODB_SETTINGS'] = {
    'db' : 'agrodb',
    'host' : 'localhost',
    'port' : 27017
}

db = MongoEngine()
db.init_app(app)

client=MongoClient() 
client = MongoClient("mongodb://localhost:27017/") 
mydatabase = client['agrodb'] 

############## CLASS #######################

class User(db.Document):
    name = db.StringField()
    email = db.StringField()
    password = db.StringField()
    reg_date = db.DateTimeField(datetime.now)
    is_admin = db.IntField()

class Seed(db.Document):
    seed_id = db.IntField()
    seed_name = db.StringField()
    hundredweight = db.IntField()
    seed_class = db.StringField()
    price = db.IntField()
    place = db.StringField()
    phone = db.IntField()
    total_weight = db.IntField()

class Request_seed(db.Document):
    seed_id = db.IntField()
    seed_name = db.StringField()
    hundredweight = db.IntField()
    seed_class = db.StringField()
    price = db.IntField()
    place = db.StringField()
    phone = db.IntField()
    total_weight = db.IntField()

################ BASIC HTML ######################

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register',methods=['POST','GET'])
def register():
    today = datetime.today()
    print(today)
    if request.method == 'POST':
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']
        _is_admin = 0
        if _name and _email and _password:
            _hashed_password = generate_password_hash(_password)
            users = User.objects(email=_email).first()
            if not users:
                usersave = User(name=_name,email=_email,password=_hashed_password,reg_date = today,is_admin=_is_admin)
                usersave.save()
                msg =  '{ "html":"ok"}'
                msghtml = json.loads(msg)
                return msghtml["html"]
            else:
                msg = '{"html":"<h4>Пользователь с такой почтой уже существует!</h4>"}'
                msghtml = json.loads(msg)
                return msghtml["html"]
        else:
            msg = "<h4>Введите все поля!</h4>"
            # msghtml = json.loads(msg)
            return jsonify(msg)
    else:    
        return render_template("register.html")

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']
        users = User.objects(email=_username).count()
        if users > 0:
            users_rs = User.objects(email=_username).first()
            password = users_rs['password']
            is_admin = users_rs['is_admin']
            if check_password_hash(password,_password) and is_admin == 0:
                session['sessionusername'] = _username
                return redirect('/catalog')
            elif check_password_hash(password,_password) and is_admin == 1:
                session['sessionusername'] = _username
                session['is_admin'] = 'yes'
                return redirect('/admin_panel')
            else:
                error = 'Неверный логин или пароль!'
                return render_template('login.html',error=error)
        else:
            error = 'Пользователь не найден!'
            return render_template('login.html',error=error)
    return render_template('login.html')


@app.route('/error')
def error():
    return render_template('404.html')

@app.route('/logout')
def logout():
    session.pop('sessionusername', None)
    session.pop('is_admin', None)
    return redirect('/')

############### CATALOG ########################

@app.route('/catalog')
def catalog():
    print(session.get('sessionusername'))
    if session.get('sessionusername'):
        seed_all = Seed.objects.all()
        seed_col=mydatabase['seed']
        if request.args:
            if 'seed_name' in request.args:
                seed_all = loads(dumps(seed_col.find({'seed_name':request.args['seed_name']})))
            # else:
            #     if 'price1' in request.args and 'price2' not in request.args:
            #         # new_seed_all = []
            #         # for i in Seed.objects.all():
            #         #     if i.price >  request.args['price1']:
            #         #         new_seed_all.append(i)
            #         # print(new_seed_all)
            #         print('~~~')

            #     if 'price2' in request.args and 'price1' not in request.args :
            #         seed_all = loads(dumps(seed_col.find( { 'price': { "$lte": request.args['price2']} } )))
            #     if  'price1' in request.args and 'price2' in request.args:
            #         seed_all = loads(dumps(seed_col.find( { 'price': { "$gte": request.args['price1'],"$lte": request.args['price2']} } )))
                    
            #         new_seed_all = {'seed_id':'','seed_name':'','hundredweight':'','price':'','place':'','seed_class':'','phone':''}
                    
            #         for i in Seed.objects.all():
            #             if i.price >  int(request.args['price1']) and i.price > int(request.args['price2']):
            #                 print(i['seed_name'])
            #                 new_seed_all['seed_id'] += int(i['seed_id'])
            #                 new_seed_all['seed_name'] += i['seed_name']
            #                 new_seed_all['hundredweight'] += int(i['hundredweight'])
            #                 new_seed_all['price'] += int(i['price'])
            #                 new_seed_all['place'] += i['place']
            #                 new_seed_all['phone'] += int(i['phone'])
            #                 new_seed_all['seed_class'] += int(i['seed_class']
            #         seed_all = new_seed_all
                    

        # function to find name and count
        agg_result= seed_col.aggregate(
        [{
        "$group" : 
            {"_id" : "$seed_name", 
            "total" : {"$sum" : 1}
            }}
        ])
        print(seed_all)
        return render_template('catalog.html',seed=seed_all,list_seed=agg_result)
    else:
        return render_template('404.html',error = 'Ошибка авторизаций')

# @app.route('/filter_data',methods=['GET','POST'])
# def filter_data():
#     _seedclass = request.form['seed_class_num']
#     _price1 = request.form['price1']
#     _price2 = request.form['price2']
#     print(_price1)


@app.route('/add_request_seed', methods=['GET', 'POST'])
def add_request_seed():
    txtname = request.form['txtname']
    txthundredweight = request.form['txthundredweight']
    _seedclass = request.form['seed_class']
    _price = request.form['price']
    _place = request.form['place']
    _phone = request.form['phone']
    _total_weight = request.form['total_weight']
    seed_all = Request_seed.objects.all()
    seedsave = Request_seed(seed_id=seed_all.count()+1,seed_name=txtname, hundredweight=txthundredweight, seed_class=_seedclass,price=_price,place=_place,phone=_phone,total_weight=_total_weight)
    seedsave.save()
    return redirect('/catalog')

################ PRODUCT  ########################

@app.route('/product')
def show_product():
    seed_col=mydatabase['seed']
    # seed_all = loads(dumps(seed_col.find({'seed_id':seed_id})))
    seed_all = Seed.objects(seed_id=request.args.get('seed_id')).first()
    print(seed_all)
    return render_template('single_product.html',seed=seed_all)


################ ADMIN PANEL #####################

#read and admin panel
@app.route('/admin_panel')
def admin_panel():
    print("hello admin!")
    if session.get('sessionusername'):
        employee = User.objects.all()
        seed = Seed.objects.all()
        request_seed = Request_seed.objects().all()
        return render_template('useradmin.html',user = employee,seed=seed,request_product=request_seed)
    else:
        return render_template('404.html',error= 'Ошибка авторизаций')

#update user
@app.route('/update_user', methods=['POST'])
def update_user():
    pk = request.form['pk']
    namepost = request.form['name']
    value = request.form['value']
    user_rs = User.objects(email=pk).first()
    if not user_rs:
        return json.dumps({'error':'data not found'})
    else:
        if namepost == 'name':
            user_rs.update(name=value)
        elif namepost == 'email':
            user_rs.update(email=value)
        elif namepost == 'is_admin':
            user_rs.update(is_admin=value)
    return json.dumps({'status':'OK'})

# add user
@app.route('/add_user', methods=['GET', 'POST'])
def create_user():
    today = datetime.today()
    txtname = request.form['txtname']
    txtemail = request.form['txtemail']
    txtpassword = request.form['txtpassword']
    hashed_password = generate_password_hash(txtpassword)
    _is_admin = 0
    users = User.objects(email=txtemail).first()
    if not users:
        usersave = User(name=txtname, email=txtemail, password=hashed_password,reg_date=today,is_admin=_is_admin)
        usersave.save()
    return redirect('/admin_panel')

# delete user
@app.route('/delete_user/<string:email>', methods = ['POST','GET'])
def delete_user(email):
    print(email)
    user = User.objects(email=email).first()
    if not user:
        return jsonify({'error': 'data not found'})
    else:
        user.delete() 
    return redirect('/admin_panel')

# add seed
@app.route('/add_seed', methods=['GET', 'POST'])
def create_seed():
    txtname = request.form['txtname']
    txthundredweight = request.form['txthundredweight']
    _seedclass = request.form['seed_class']
    _price = request.form['price']
    _place = request.form['place']
    _phone = request.form['phone']
    _total_weight = request.form['total_weight']
    seed_all = Seed.objects.all()
    seedsave = Seed(seed_id=seed_all.count()+1,seed_name=txtname, hundredweight=txthundredweight, seed_class=_seedclass,price=_price,place=_place,phone=_phone,total_weight=_total_weight)
    seedsave.save()
    return redirect('/admin_panel')

# delete seed
@app.route('/delete_seed/<string:seed_id>', methods = ['POST','GET'])
def delete_seed(seed_id):
    print(seed_id)
    seed = Seed.objects(seed_id=seed_id).first()
    if not seed:
        return jsonify({'error': 'data not found'})
    else:
        seed.delete()
    return redirect('/admin_panel')

#update seed
@app.route('/update_seed', methods=['POST'])
def update_seed():
    pk = request.form['pk']
    namepost = request.form['name']
    value = request.form['value']
    seed_rs = Seed.objects(seed_id=pk).first()
    if not seed_rs:
        return json.dumps({'error':'data not found'})
    else:
        if namepost == 'seed_name':
            seed_rs.update(seed_name=value)
        elif namepost == 'hundredweight':
            seed_rs.update(hundredweight=value)
        elif namepost == 'seed_class':
            seed_rs.update(seed_class=value)
        elif namepost == 'price':
            seed_rs.update(price=value)
        elif namepost == 'place':
            seed_rs.update(place=value)
        elif namepost == 'phone':
            seed_rs.update(phone=value)
        elif namepost == 'total_weight':
            seed_rs.update(total_weight=value)
    return json.dumps({'status':'OK'})

# confirm request product
@app.route('/confirm_seed',methods=['GET'])
def confirm_seed():
    _seed_id = request.args.get('seed_id')
    _seed_name = request.args.get('seed_name')
    _hundredweight = request.args.get('hundredweight')
    _seed_class = request.args.get('seed_class')
    _price = request.args.get('price')
    _place = request.args.get('place')
    _phone = request.args.get('phone')
    _total_weight = request.args.get('total_weight')
    print(_phone,_total_weight)
    
    seed_all = Seed.objects.all()
    seedsave = Seed(seed_id=seed_all.count()+1,seed_name=_seed_name, hundredweight=_hundredweight, seed_class=_seed_class,price=_price,place=_place,phone=_phone,total_weight=_total_weight)
    seedsave.save()

    r_seed_check = Request_seed.objects(seed_id=_seed_id).first()
    if not r_seed_check:
        return jsonify({'error': 'data not found'})
    else:
        r_seed_check.delete()
    return redirect('/admin_panel')


################ END ADMIN PANEL #####################

if __name__ == "__main__":
    app.run(debug=True)