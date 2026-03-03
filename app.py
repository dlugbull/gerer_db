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

@app.route('/databases/tables', methods=['GET', 'POST'])
def tables():
    database = request.form.get('database')
    mycursor = get_db().cursor()
    mycursor.execute(f"USE {database}")
    mycursor.execute("SHOW TABLES")
    list_tables = mycursor.fetchall()
    list_tables = [table[f"Tables_in_{database}"] for table in list_tables]
    return render_template("table.html", tables=list_tables, database=database)

@app.route('/database/table/show', methods=['GET', 'POST'])
def show_table():
    table = request.form.get('table')
    database = request.form.get('database')
    mycursor = get_db().cursor()
    mycursor.execute(f"USE {database}")
    mycursor.execute(f"SELECT * FROM {table}")
    content = mycursor.fetchall()
    keys = list(content[0].keys())
    values = [list(content[i].values()) for i in range(len(content))]
    len_content = len(content)
    return render_template("show_table.html", table=table, len_content=len_content, keys=keys, values=values, database=database)

@app.route('/database/table/delete', methods=['GET', 'POST'])
def delete_table():
    database = request.form.get('database')
    table = request.form.get('table')
    mycursor = get_db().cursor()
    mycursor.execute(f"USE {database}")
    try:
        mycursor.execute(f"DROP TABLE {table}")
        get_db().commit()
    except Exception as e:
        flash(f"La table {table} n'a pas pu être supprimée", "alert-warning")
    mycursor.execute("SHOW TABLES")
    list_tables = mycursor.fetchall()
    list_tables = [table[f"Tables_in_{database}"] for table in list_tables]
    return render_template("table.html", tables=list_tables, database=database)

@app.route('/database/table/delete_elt', methods=['GET', 'POST'])
def delete_elt():
    database = request.form.get('database')
    table = request.form.get('table')
    id = request.form.get('id')
    mycursor = get_db().cursor()
    mycursor.execute(f"USE {database}")
    try:
        mycursor.execute(f"DELETE FROM {table} WHERE id = {id}")
        get_db().commit()
    except Exception as e:
        flash(f"L'élément d'id {id} n'a pas pu être supprimé", "alert-warning")
    mycursor.execute(f"SELECT * FROM {table}")
    content = mycursor.fetchall()
    keys = list(content[0].keys())
    values = [list(content[i].values()) for i in range(len(content))]
    len_content = len(content)
    return render_template("show_table.html", table=table, len_content=len_content, keys=keys, values=values, database=database)

if __name__ == '__main__':
    app.run()