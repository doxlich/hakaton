import openpyxl
wb = openpyxl.load_workbook('C:\\Users\\User\\Downloads\\hakaton\\hakaton\\data\\Model_zakupa_dlya_khakatona.xlsx', read_only=True)
# Select the worksheet you want to read from
ws = wb['список товаров']

#Print the title of the worksheet
print(ws.title)

data = [[cell.value for cell in row] for row in ws.iter_rows(min_row=2)]