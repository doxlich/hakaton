from flask import Flask, render_template, request, redirect, session
import csv
from data_classes import Product, Suppplier, User, UserRole

app = Flask(__name__)
app.secret_key = "big_nuts"


products: list[Product] = []
suppliers: list[Suppplier] = []
registered_users: list[User] = []

def get_users():
    global registered_users
    registered_users = []
    with open('data\\users.csv', mode='r', encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';', lineterminator="\n")
        next(csv_reader)  # Skip header row
        for row in csv_reader:
            if row == []:
                continue
            registered_users.append(User(row[0], row[1], row[3]))

def save_user(name: str, email: str, password: str, role: int):
    data_to_save = [name, email, password, role]
    with open('data\\users.csv', mode='a', encoding="utf8") as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=';')
        csv_writer.writerow(data_to_save)

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

    get_users()

#default login/register page
@app.route('/')
def index():
    account_link = "/"
    if session.get("logged"):
        role = session.get("user")["role"]
        if role == UserRole.SUPPLIER.value:
            account_link = "profile_for_supplier"
        elif role == UserRole.MANAGER.value:
            account_link = "profile_for_manager"
        elif role == UserRole.DIRECTOR.value:
            account_link = "profile_for_buyer"
    return render_template('index.html', logged = session.get("logged"), user = session.get("user"), account_link = account_link)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        pass
    elif request.method == 'GET':
        data = []
        global products
        with open('data/ordered.csv', mode='r', encoding="utf8") as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                row['consumption_week'] = 0
                for product in products:
                    if product.name == row['name']:
                        row['consumption_week'] = float(product.consumption_week.replace(",", "."))
                        row['order_count'] = float(product.consumption_week.replace(",", "."))
                data.append(row)
            suppliers_names = set()
            for supplier in suppliers:
                suppliers_names.add(supplier.supplier)
            products_dict = {}
            for product in products:
                products_dict[product.name] = product.consumption_week
        return render_template('add.html', data=data, suppliers=suppliers_names, products=products_dict)

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
            if user.email == email:
                return "Email already exists"

        save_user(username, email, password, int(user_role))
        user = User(username, email, int(user_role))
        registered_users.append(user)
        set_logged(user)
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
                set_logged(user)
                return redirect("/")
        return "Wrong username or password"

def set_logged(user: User):
    session["user"] = user
    session["logged"] = True

@app.route('/products_edit')
def product():
    global products
    return render_template('products_edit.html', products=products)

@app.route('/suppliers_edit')
def parsed():
    global products
    return render_template('suppliers_edit.html', suppliers=suppliers)

@app.route('/login_ex')
def login_ex():
    return render_template('login_ex.html')

@app.route('/profile_for_supplier')
def profile_for_supplier():
    return render_template('profile_for_supplier.html')

@app.route('/profile_for_manager')
def profile_for_manager():
    return render_template('profile_for_manager.html')

@app.route('/profile_for_buyer')
def profile_for_buyer():
    return render_template('profile_for_buyer.html')

init()
if __name__ == '__main__':
    app.run(debug=True)
