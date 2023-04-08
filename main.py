from flask import Flask, render_template
import openpyxl

app = Flask(__name__)

@app.route('/')
def index():
    wb = openpyxl.load_workbook('data\\Model_zakupa_dlya_khakatona.xlsx', read_only=True)
    products_sheet = wb["список товаров"]
    suppliers_sheet = wb["Наименования поставщика"]
    ws = wb['Область работы']

    #data = [[cell.value for cell in row] for row in ws.iter_rows(min_row=2)]
    products = []
    for row in products_sheet.iter_rows(min_row=2, values_only=True):
        category_3, category_nom, element_nom, total, *_ = row
        if element_nom == None:
            continue
        products.append((category_3, category_nom, element_nom, total))

    suppliers = []
    for row in suppliers_sheet.iter_rows(min_row=2, values_only=True):
        name, availability, supplier, *_ = row
        suppliers.append((name, availability, supplier))

    #print(suppliers)
    products_with_supplier = {}
    for product in products:
        product_name = product[2]
        print(product_name)
        for supplier in suppliers:
            if product_name in supplier:
                products_with_supplier[product_name] = supplier

    print(products_with_supplier)

    # Render the template with the data
    return render_template('xslx_test.html', data=products)

if __name__ == '__main__':
    app.run(debug=True)
