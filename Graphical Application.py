# This python file is about Project 2
# Created by Li Ruizhi (Frankie) in 3/7/2021

from tkinter import *
from tkinter import ttk  
from tkinter import messagebox  
import sqlite3
import pathlib
import traceback

dbFile = None
conn = None
cur = None
ids=[]

def fnOpenDatabase():
    global dbFile,conn,cur
    dbFile=pathlib.Path("/Users/liruizhi/Downloads/BJTU/Developing Business Applications/GA_Database.db")
    if dbFile.exists():
        conn = sqlite3.connect(dbFile)
        cur = conn.cursor()
        return True
    else:
        messagebox.showerror('Error','Unable to locate database file.')
        return False

def fnUpdateOutputOrders():
    sql = "SELECT orderText from orders;"
    cur.execute(sql)
    records = cur.fetchall()
    # Clear / Reset the listbox
    lstPastOrders.delete(0, END)
    # Loop through the results/records and displacy them one at a time in the listbox
    for row in records:
        lstPastOrders.insert(END, str(row[0]))

def fnDisplay():
    sqlShowInventory = 'SELECT SUM(grounds),SUM(creamer),SUM(sugar),SUM(cups) FROM inventory;'
    sqlShowFinances = 'SELECT SUM(sales),SUM(expenses),SUM(sales) - SUM(expenses) FROM finances;'
    cur.execute(sqlShowInventory)
    recordsInventory = cur.fetchall()
    cur.execute(sqlShowFinances)
    recordsFinances = cur.fetchall()
    lblGrounds.config(text=int(recordsInventory[0][0]))
    lblCreamer.config(text=int(recordsInventory[0][1]))
    lblSugar.config(text=int(recordsInventory[0][2]))
    lblCups.config(text=int(recordsInventory[0][3]))
    lblSales.config(text='${:,.2f}'.format(recordsFinances[0][0]))
    lblExpenses.config(text='${:,.2f}'.format(recordsFinances[0][1]))
    lblProfit.config(text='${:,.2f}'.format(recordsFinances[0][2]))


# function for updating the inventory
def fnInventoryUpdate():
    # Determine if Add Grounds is checked
    Grounds = applyAddGrounds.get()
    Creamer = applyAddCreamer.get()
    Suger = applyAddSugar.get()
    Cups = applyAddCups.get()
    if Grounds+Creamer+Suger+Cups == 0:
        return 0
    else:
        addInventorySQL = 'INSERT INTO inventory (grounds,creamer,sugar,cups) VALUES (%d,%d,%d,%d);'%(Grounds*16,Creamer*16,Suger*16,Cups*10)
        addFinancesSQL= 'INSERT INTO finances (expenses) VALUES (%d);'%(Grounds*20+Creamer*2+Suger*1+Cups*4)
        cur.execute(addInventorySQL)
        cur.execute(addFinancesSQL)
        conn.commit()
        fnDisplay()

# function for updating the order
def fnOrderUpdate():
    sqlInventory = 'SELECT SUM(grounds), SUM(sugar), SUM(creamer), SUM(cups) FROM inventory;'
    cur.execute(sqlInventory)
    recordsInventory = cur.fetchall()
    try:
        quantity = float(entValue.get())
        if quantity<1:
            messagebox.showwarning('Invalid Quantity', 'Quantity must be greater than 0.')
        else:
            if recordsInventory[0][0] < quantity*2 or recordsInventory[0][3] < quantity*1 or applyCreamer.get() * (recordsInventory[0][2] - quantity*1) < 0 or applySugar.get() * (recordsInventory[0][1] - quantity*1) < 0:
                messagebox.showerror('Insufficent Inventory','There is not enough inventory to fulfill your order. Please add more.')
            else:
                
                reqCreamer = applyCreamer.get()*quantity
                reqSugar = applySugar.get()*quantity
                reqSQL = 'INSERT INTO inventory (grounds,creamer,sugar,cups) VALUES (%d,%d,%d,%d);'%(-quantity*2,-reqCreamer,-reqSugar,-quantity)
                cur.execute(reqSQL)
                conn.commit()
                if applyCreamer.get() == 1 and applySugar.get() == 1:
                    sql = 'INSERT INTO orders (orderText) VALUES ("' + str(int(quantity)) +' Creamer Sugar Cup(s) of Coffee");'
                    cur.execute(sql)
                    conn.commit()
                elif applyCreamer.get() == 1 and applySugar.get() == 0:
                    sql = 'INSERT INTO orders (orderText) VALUES ("' + str(int(quantity)) +' Creamer Cup(s) of Coffee");'
                    cur.execute(sql)
                    conn.commit()
                elif applyCreamer.get() == 0 and applySugar.get() == 1:
                    sql = 'INSERT INTO orders (orderText) VALUES ("' + str(int(quantity)) +' Sugar Cup(s) of Coffee");'
                    cur.execute(sql)
                    conn.commit()
                else:
                    sql = 'INSERT INTO orders (orderText) VALUES ("' + str(int(quantity)) +' Cup(s) of Coffee");'
                    cur.execute(sql)
                    conn.commit()
                # Update sales
                sql = 'INSERT INTO finances (sales) VALUES ('+ str(quantity*3.5) +'); '
                cur.execute(sql)
                conn.commit()
                fnDisplay()
                fnUpdateOutputOrders()
    except:
        messagebox.showerror('Invalid Quantity','Quantity must be a valid number.')


# Create a graphic
root = Tk()
root.title("Project 2")
root.geometry("800x300")

# Initialize variables
sales = 0
expenses = 0
profit = 0
numGrounds = 0
numCreamer = 0
numSugar = 0
numCups = 0
quantity = 0

# Declare title of each part
Label(root, text='INVENTORY').grid(row=0, column=0, sticky=W)
Label(root, text='ADD TO INVENTORY').grid(row=0, column=3, sticky=W)
Label(root, text='ORDER FORM').grid(row=0, column=5, sticky=W)
Label(root, text='FINANCIAL DATA').grid(row=0, column=7, sticky=W)

# Column 0 & 1  Content: INVENTORY
Label(root, text='Grounds:').grid(row=1, column=0, sticky=W)
lblGrounds = Label(root, text="0")
lblGrounds.grid(row=1, column=1)

Label(root, text='Creamer:').grid(row=2, column=0, sticky=W)
lblCreamer = Label(root, text="0")
lblCreamer.grid(row=2, column=1)

Label(root, text='Sugar:').grid(row=3, column=0, sticky=W)
lblSugar = Label(root, text="0")
lblSugar.grid(row=3, column=1)

Label(root, text='Cups:').grid(row=4, column=0, sticky=W)
lblCups = Label(root, text="0")
lblCups.grid(row=4, column=1)

# Blank column
Label(root, text='      ').grid(row=0, column=2)

# Column 2 & 3  Content: ADD TO INVENTORY
applyAddGrounds = IntVar()
chkGrounds = Checkbutton(root, text="Add 16 oz of Grounds", variable=applyAddGrounds)
chkGrounds.grid(row=1, column=3, sticky=W)

applyAddCreamer = IntVar()
chkCreamer = Checkbutton(root, text="Add 16 oz of Creamer", variable=applyAddCreamer)
chkCreamer.grid(row=2, column=3, sticky=W)

applyAddSugar = IntVar()
chkSugar = Checkbutton(root, text="Add 16 oz of Sugar", variable=applyAddSugar)
chkSugar.grid(row=3, column=3, sticky=W)

applyAddCups = IntVar()
chkCups = Checkbutton(root, text='Add 10 Cups', variable=applyAddCups)
chkCups.grid(row=4, column=3, sticky=W)

Button(root, text='Add To Inventory', command=fnInventoryUpdate).grid(row=5, column=3, sticky=W)

# Blank column
Label(root, text='      ').grid(row=0, column=4)

# Column 3.1 Content: ORDER FORM
Label(root, text='Quantity').grid(row=1, column=5, sticky=W, columnspan=2)
entValue = Entry(root, width=4)
entValue.grid(row=1, column=5, sticky=E)

applyCreamer = IntVar()
chkCreamer2 = Checkbutton(root, text="Creamer", variable=applyCreamer)
chkCreamer2.grid(row=2, column=5, sticky=W)

applySugar = IntVar()
chkSugar2 = Checkbutton(root, text="Sugar", variable=applySugar)
chkSugar2.grid(row=3, column=5, sticky=W)

Button(root, text='Place Order', command=fnOrderUpdate).grid(row=4, column=5, sticky=W)

# Column 3.2 Content: PAST ORDERS
Label(root, text='PAST ORDERS').grid(row=7, column=5, sticky=W)
frmPastOrders = Frame(root)
frmPastOrders.grid(row=8, column=5, sticky=W, columnspan=30)
scrPastOrders = Scrollbar(frmPastOrders)
scrPastOrders.pack(side=RIGHT, fill=Y)
lstPastOrders = Listbox(frmPastOrders, height=5, width=30, yscrollcommand=scrPastOrders.set )
lstPastOrders.pack()
scrPastOrders.config(command=lstPastOrders.yview)


# Blank column
Label(root, text='      ').grid(row=0, column=6)

# Column 4  Content: FINANCIAL DATA
Label(root, text='Sales:').grid(row=1, column=7, sticky=W)
lblSales = Label(root, text='$0.00')
lblSales.grid(row=1, column=8,sticky=W)

Label(root, text='Expenses:').grid(row=2, column=7, sticky=W)
lblExpenses = Label(root, text='$0.00')
lblExpenses.grid(row=2, column=8,sticky=W)

Label(root, text='Profit:').grid(row=3, column=7, sticky=W)
lblProfit = Label(root, text='$0.00')
lblProfit.grid(row=3, column=8,sticky=W)

if fnOpenDatabase()==True:
    fnOpenDatabase()
    fnUpdateOutputOrders()
    fnDisplay()
    root.mainloop()