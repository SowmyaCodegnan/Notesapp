#pip install mysql-connector-python

import mysql.connector

db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Codegnan@25',
    database='notes_app'
)
cursor = db.cursor()