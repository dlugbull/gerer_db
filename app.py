from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g
from flask import Blueprint
import pymysql.cursors

from connect_db import *




app = Flask(__name__)
app.secret_key = 'une cle(token) : grain de sel(any random string)'


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def layout():
    return render_template('_layout.html')

@app.route('/databases')
def databases():
    mycursor = get_db().cursor()
    mycursor.execute("SHOW DATABASES")
    list_databases = mycursor.fetchall()
    databases=[]
    for database in list_databases:
        db = database["Database"]
        mycursor.execute(f"USE {db}")
        mycursor.execute("SHOW TABLES")
        databases.append({"nom" : db, "nb_tables" : len(mycursor.fetchall())})
    
    return render_template('databases.html', databases=databases)

if __name__ == '__main__':
    app.run()