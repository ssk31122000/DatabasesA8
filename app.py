from unicodedata import name
from urllib import response
from flask import Flask, redirect, render_template, request , url_for , Response
from flask_mysqldb import MySQL
import yaml

o_id=111

app = Flask(__name__)

# Configure db
db = yaml.safe_load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)

@app.route('/', methods=['POST','GET'])
def index():

    if request.method == 'POST':
        content=request.form
        cur = mysql.connection.cursor()
        resultValue = cur.execute("select * from accounts where username=%s",[(content['username'])])
        if resultValue >0 :
            result=cur.fetchall()
            print(result)
            return redirect(f"/products/{result[0][0]}")
        else:
            return redirect('/')
    else:
        return render_template('index.html')

@app.route('/register', methods=['POST','GET'])
def register():

    if request.method == 'POST':
        data=request.form
        cur = mysql.connection.cursor()
        cur.execute("select account_id from accounts order by account_id desc limit 1;")
        r=cur.fetchall()
        a=r[0][0]
        cur.execute("insert into accounts(account_id,username,first_name,last_name,password) values( %s , %s, %s,%s,%s)",(a+1,data['username'],data['firstname'],data['lastname'],data['password']))
        cur.execute("select account_id from accounts where username=%s;",[(data['username'])])
        r=cur.fetchall()
        a=r[0][0]
        cur.execute("insert into user(account_id,house_details,city,Country,pincode,phone_number) values( %s , %s, %s,%s,%s,%s)",(a,data['address'],data['city'],data['country'],data['pincode'],data['phone']))

        mysql.connection.commit()
        return redirect("/")
    else:
        return render_template('register.html')

@app.route('/products/<int:userid>')
def products(userid):
    
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT product.product_id,product_name,description,charges,vendor_id,list_id FROM product natural join list")
    if resultValue > 0:
        product = cur.fetchall()
        resultValue = cur.execute("SELECT * FROM category")
        category=cur.fetchall()
        return render_template('Products.html',products=product,category=category,userid=userid)


@app.route('/<int:userid>/<int:id>', methods=['POST','GET'])
def product(userid,id):

    if request.method == 'POST':
        pass
    else:
        cur = mysql.connection.cursor()
        resultValue = cur.execute("SELECT * FROM list where list_id= %s; ",[(id)])
        if resultValue > 0:
            product = cur.fetchall()
            # print(product)
            
            cur.execute("insert into order_details(user_id,total_price,create_time) values( %s , %s, NOW())",(userid,product[0][2]))
            cur.execute("select order_id from order_details where user_id=%s order by create_time desc limit 1;",[(userid)])
            r=cur.fetchall()
            orderid=r[0][0]
            cur.execute("insert into order_list(order_id,list_id,order_quantity) values(%s , %s, 1)",(orderid,id))
            mysql.connection.commit()
            return render_template('success.html',userid=userid)


@app.route('/search', methods=['POST','GET'])
def search():

    if request.method == 'POST':
        data=request.form
        cur = mysql.connection.cursor()
        resultValue = cur.execute("Select username from accounts where account_id in (select account_id from user where match(city) against(%s));",[(data['city'])])
        if resultValue>0:
            users=cur.fetchall()
            return render_template('list.html',list=users)
        else:
            return render_template('search.html')
    else:
        return render_template('search.html')


@app.route('/cart', methods=['POST','GET'])
def cart():

    if request.method == 'POST':
        pass
    else:
        return render_template('cart.html')


if __name__ == "__main__":
    app.run(debug=True)