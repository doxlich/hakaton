from flask import Flask, render_template, request
import csv
from dataclasses import dataclass

app = Flask(__name__)

@dataclass
class Product:
    category: str
    name: str
    consumption_month: str
    suppliers: list[str]

@dataclass
class Suppplier:
    product: str
    nomenclature: str
    supplier: str

products: list[Product] = []
suppliers: list[Suppplier] = []

def init():
    #wb = openpyxl.load_workbook('data\\Model_zakupa_dlya_khakatona.xlsx', read_only=True)
    #products_sheet = wb["список товаров"]
    #suppliers_sheet = wb["Наименования поставщика"]
    #ws = wb['Область работы']
    global products
    with open('data\\products.csv', mode='r', encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        next(csv_reader)  # Skip header row
        for row in csv_reader:
            print(row)
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

#default login/reister page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        pass
    elif request.method == 'GET':
        return render_template('add.html')

@app.route('/aa')
def aa():
    return render_template('aaadd.html')

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
    global products_with_supplier
    return render_template('login_ex.html', products=products_with_supplier)

init()
if __name__ == '__main__':
    app.run(debug=True)
