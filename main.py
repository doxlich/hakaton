from flask import Flask, render_template, request, redirect, session
import csv
from data_classes import Product, Suppplier, User, UserRole

app = Flask(__name__)
app.secret_key = "big_nuts"


products: list[Product] = []
suppliers: list[Suppplier] = []
registered_users: list[User] = []

def init():
    global products
    with open('data\\products.csv', mode='r', encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        next(csv_reader)  # Skip header row
        for row in csv_reader:
            products.append(Product(row[0], row[1], row[2], []))

    global suppliers
    with open('data\\suppliers.csv', mode='r', encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        next(csv_reader)  # Skip header row
        for row in csv_reader:
            suppliers.append(Suppplier(row[0], row[1], row[2]))

    for product in products:
        for supplier in suppliers:
            if product.name == supplier.product:
                product.suppliers.append(supplier.supplier)

    global registered_users
    with open('data\\users.csv', mode='r', encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        next(csv_reader)  # Skip header row
        for row in csv_reader:
            registered_users.append(User(row[0], row[1], row[3]))

#default login/register page
@app.route('/')
def index():
    return render_template('index.html', logged = session.get("logged"), user = session.get("user"))

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        pass
    elif request.method == 'GET':
        return render_template('add.html')

@app.route('/register', methods=['POST'])
def register():
    if request.method == "POST":
        global registered_users
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        user_role = request.form["user-role"]

        for user in registered_users:
            if user.name == username:
                return "Username already exists"

        registered_users.append(User(username, email, UserRole.SUPPLIER.value))
        return redirect("/")
    
@app.route('/login', methods=['POST'])
def login():
    if request.method == "POST":
        global registered_users
        name = request.form["name"]
        password = request.form["password"]

        for user in registered_users:
            if user.name == name or \
                user.email == name:
                session["user"] = user
                session["logged"] = True
                return redirect("/")
        return "Wrong username or password"

@app.route('/product')
def product():
    global products
    return render_template('xslx_test.html', data=products)

@app.route('/prod_sup')
def parsed():
    global products
    return render_template('pr_w_sup.html', products=products)

@app.route('/login_ex')
def login_ex():
    return render_template('login_ex.html')

init()
if __name__ == '__main__':
    app.run(debug=True)
