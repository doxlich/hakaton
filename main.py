from flask import Flask, render_template, request, redirect, session, jsonify, make_response
import csv
from data_classes import Product, Suppplier, User, UserRole
import pandas as pd
from datetime import datetime
from os import listdir

app = Flask(__name__)
app.secret_key = "big_nuts"


products: list[Product] = []
suppliers: list[Suppplier] = []
registered_users: list[User] = []

def get_users():
    global registered_users
    registered_users = []
    with open('data\\users.csv', mode='r', encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        next(csv_reader)  # Skip header row
        for row in csv_reader:
            if row == []:
                continue
            registered_users.append(User(row[0], row[1], row[3], row[4]))

def add_data_to_user(key: str, value: str):
    df = pd.read_csv('data\\users.csv', delimiter=';')

    user = session.get("user")
    row_index = df.index[df['name'] == user["name"]].tolist()[0]
    df.at[row_index, "cofee_shop"] = value

    df.to_csv('data\\users.csv', sep=';', index=False)


def save_user(name: str, email: str, password: str, role: int):
    data_to_save = [name, email, password, role]
    with open('data\\users.csv', mode='a', encoding="utf8", newline="") as csv_file:
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
        role = int(session.get("user")["role"])
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
        return render_template('add.html', data=data, suppliers=suppliers_names, products=products_dict, logged = session.get("logged"), user = session.get("user"))

@app.route('/register', methods=['POST'])
def register():
    if request.method == "POST":
        global registered_users
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        user_role = request.form["user-role"]
        coffe_shop_name = request.form["coffe_shop_name"]

        for user in registered_users:
            if user.name == username:
                return "Username already exists"
            if user.email == email:
                return "Email already exists"

        save_user(username, email, password, int(user_role))
        user = User(username, email, int(user_role), coffe_shop_name)
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
    if not session["logged"]:
        return "Log in!!!"
    return render_template('profile_for_supplier.html', user = session.get("user"), logged = session.get("logged"))

@app.route('/profile_for_manager')
def profile_for_manager():
    if not session["logged"]:
        return "Log in!!!"
    return render_template('profile_for_manager.html', user = session.get("user"), logged = session.get("logged"))

@app.route('/profile_for_buyer')
def profile_for_buyer():
    if not session["logged"]:
        return "Log in!!!"
    files = listdir('data/purchaser_lists')
    files_csv = [file for file in files if file.endswith('.csv')]
    files_data = []
    for file in files_csv:
        parts = file.split('-')[1:]
        shop_name = parts[0]
        date_str = ""
        for x in range(1, len(parts)):
            date_str = date_str + "-" + parts[x]
        date_str = date_str[1:]
        date_str = date_str[:-4]
        date = datetime.strptime(date_str, '%Y-%m-%d_%H-%M-%S').date()
        files_data.append((shop_name, date, file))
    return render_template('profile_for_buyer.html', user = session.get("user"), logged = session.get("logged"), files_data = files_data)

@app.route('/new_person')
def new_person():
    return render_template('new_person.html', user = session.get("user"))

@app.route('/start')
def start():
    return render_template('start.html', user = session.get("user"))

@app.route('/update_user_data', methods=['POST'])
def update_user_data():
    if not request.method == 'POST':
        return "GET isn't allowed"
    if not session["logged"]:
        return "Log in!!!"
    data = request.json # get the JSON data sent in the request
    cofee_shop = data['cofee-shop'] # get the value of the 'cofee_shop' field
    add_data_to_user("cofee_shop", cofee_shop)
    response = jsonify({'success': True}) # create a JSON response
    return make_response(response, 200) # return the response with a 200 status code

@app.route('/save-table-to-csv', methods=['POST'])
def save_table():
    if not request.method == 'POST':
        return "GET isn't allowed"
    if not session["logged"]:
        return "Log in!!!"
    user = session.get("user")
    csv_data = request.get_data().decode("utf8")
    with open(f"data/purchaser_lists/table_data-{user['cofee_shop']}-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        reader = csv.reader(csv_data.splitlines())
        for row in reader:
            writer.writerow(row)
    return "OK"

@app.route('/save-edited-table', methods=['POST'])
def save_edited_table():
    if not request.method == 'POST':
        return "GET isn't allowed"
    if not session["logged"]:
        return "Log in!!!"
    path, data = request.get_data().decode("utf8").split("+")
    with open(f"data/purchaser_lists/{path}-edited", "w", newline="") as f:
        writer = csv.writer(f)
        reader = csv.reader(data.splitlines())
        for row in reader:
            writer.writerow(row)
    return "OK"

@app.route('/buyer_edit')
def buyer_edit():
    file_path = request.args.get('file')
    if not session["logged"]:
        return "Log in!!!"
    user = session.get("user")
    csv_data = request.get_data().decode("utf8")
    suppliers_names = set()
    for supplier in suppliers:
        suppliers_names.add(supplier.supplier)
    products_dict = {}
    for product in products:
        products_dict[product.name] = product.consumption_week
    data = []
    with open(f"data/purchaser_lists/{file_path}", "r", newline="") as f:
        csv_reader = csv.reader(f, delimiter=';')
        for row in csv_reader:
            data.append((row[0], row[1], row[2], row[3]))
    return render_template('buyer_edit.html', user = session.get("user"), products_dict = products_dict, suppliers = suppliers_names, data = data, logged = session.get("logged"))

init()
if __name__ == '__main__':
    app.run(debug=True)
