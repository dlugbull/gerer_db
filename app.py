from flask import Flask, request, render_template, redirect, url_for, flash, g, session
import pymysql.cursors

def get_db():
    if 'db' not in g:
        g.db =  pymysql.connect(
            host=session['host'],
            user=session['user_id'],
            password=session['password'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db

def activate_db_options(db):
    cursor = db.cursor()
    # Vérifier et activer l'option ONLY_FULL_GROUP_BY si nécessaire
    cursor.execute("SHOW VARIABLES LIKE 'sql_mode'")
    result = cursor.fetchone()
    if result:
        modes = result['Value'].split(',')
        if 'ONLY_FULL_GROUP_BY' not in modes:
            print('MYSQL : il manque le mode ONLY_FULL_GROUP_BY')   # mettre en commentaire
            cursor.execute("SET sql_mode=(SELECT CONCAT(@@sql_mode, ',ONLY_FULL_GROUP_BY'))")
            db.commit()
        else:
            print('MYSQL : mode ONLY_FULL_GROUP_BY  ok')   # mettre en commentaire
    # Vérifier et activer l'option lower_case_table_names si nécessaire
    cursor.execute("SHOW VARIABLES LIKE 'lower_case_table_names'")
    result = cursor.fetchone()
    if result:
        if result['Value'] != '0':
            print('MYSQL : valeur de la variable globale lower_case_table_names differente de 0')   # mettre en commentaire
            cursor.execute("SET GLOBAL lower_case_table_names = 0")
            db.commit()
        else :
            print('MYSQL : variable globale lower_case_table_names=0  ok')    # mettre en commentaire
    cursor.close()

app = Flask(__name__)
app.secret_key = 'une cle(token) : grain de sel(any random string)'

@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


@app.route('/')
def connect():
    session['user_id'] = ""
    session['password'] = ""
    session['host'] = ""

    return render_template('connection.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    session['user_id'] = request.form.get('login')
    session['password'] = request.form.get('password')
    session['host'] = request.form.get('host')
    try:
        mycursor = get_db().cursor()
        mycursor.close()
    except Exception as e:
        flash("Identifiants incorrects", "alert-warning")
        return redirect(url_for("connect"))
    return redirect('/databases/show')


@app.route('/databases/show')
def databases():
    if session['user_id']=="" or session['password']=="" or session['host']=="":
        flash("Veuillez vous connecter", "alert-warning")
        return redirect('/')
    mycursor = get_db().cursor()
    mycursor.execute("SHOW DATABASES")
    list_databases = mycursor.fetchall()
    databases=[]
    for database in list_databases:
        db = database["Database"]
        if db not in ["information_schema", "mysql", "performance_schema", "sys"]:
            mycursor.execute(f"USE {db}")
            mycursor.execute("SHOW TABLES")
            databases.append({"nom" : db, "nb_tables" : len(mycursor.fetchall())})

    mycursor.close()
    return render_template('database/show_databases.html', databases=databases)

@app.route('/databases/set', methods=['POST'])
def set_db():
    session['database'] = request.form.get('database')
    return redirect('/tables/show')

@app.route('/tables/show', methods=['GET', 'POST'])
def tables():
    mycursor = get_db().cursor()
    mycursor.execute(f"USE {session['database']}")
    mycursor.execute("SHOW TABLES")
    list_tables = mycursor.fetchall()
    list_tables = [table[f"Tables_in_{session['database']}"] for table in list_tables]
    mycursor.close()
    return render_template("table/show_tables.html", tables=list_tables)


@app.route('/tables/show_one', methods=['POST'])
def show_table():
    session['table'] = request.form.get('table')
    mycursor = get_db().cursor()
    mycursor.execute(f"USE {session['database']}")
    mycursor.execute(f"SELECT * FROM {session['table'] }")
    content = mycursor.fetchall()

    mycursor.execute(f"DESCRIBE {session['table'] };")
    description = mycursor.fetchall()

    mycursor.close()
    if content is not None and len(content) > 0:
        keys = list(content[0].keys())
        values = [list(content[i].values()) for i in range(len(content))]
        len_content = len(content)
        return render_template("table/show_one_table.html", table=session['table'] , len_content=len_content, keys=keys, values=values, description=description)
    return render_template("table/show_one_table.html", table=session['table'] , description=description)


@app.route('/tables/delete', methods=['POST'])
def delete_table():
    mycursor = get_db().cursor()
    mycursor.execute(f"USE {session['database'] }")
    try:
        mycursor.execute(f"DROP TABLE {session['table'] }")
        get_db().commit()
    except Exception as e:
        flash(f"La table {session['table'] } n'a pas pu être supprimée", "alert-warning")
    mycursor.close()
    return redirect('/tables/show')


@app.route('/tables/delete_elt', methods=['POST'])
def delete_elt():
    id = request.form.get('id')
    mycursor = get_db().cursor()
    mycursor.execute(f"USE {session['database'] }")
    try:
        mycursor.execute(f"DELETE FROM {session['table'] } WHERE id = {id}")
        get_db().commit()
    except Exception as e:
        flash(f"L'élément d'id {id} n'a pas pu être supprimé", "alert-warning")
    mycursor.close()
    return redirect('tables/show_one')


@app.route('/databases/delete', methods=['GET', 'POST'])
def delete():
    session['database']  = request.form.get('database')
    mycursor = get_db().cursor()
    mycursor.execute(f"SHOW TABLES IN {session['database']}")
    list_tables = mycursor.fetchall()
    if len(list_tables) == 0:
        mycursor.execute(f"DROP DATABASE {session['database']}")
        get_db().commit()
    else:
        flash(f"Impossible de supprimer la base de donnée {session['database']}", "alert-warning")
    mycursor.close()
    return redirect('/databases/show')


@app.route('/databases/add', methods=['GET'])
def add_database():
    return render_template('database/add_database.html')


@app.route('/databases/add', methods=['POST'])
def valid_add_database():
    name = request.form.get('nom')
    mycursor = get_db().cursor()
    try:
        mycursor.execute(f"CREATE DATABASE {name}")
    except Exception as e:
        flash("Vous n'avez pas la permission de créer cette base de donnée", "alert-warning")
    mycursor.close()
    return redirect('/databases/show')


@app.route('/tables/add', methods=['POST'])
def add_table():
    return render_template("table/add_table.html")


@app.route('/tables/valid_add', methods=['POST'])
def valid_add_table():
    nom = request.form.get('nom')
    nb_col = int(request.form.get('nb_colonnes'))
    colonnes=[]
    for i in range(1, nb_col+1):
        temp=[]
        temp.append(request.form.get('nom-colonne-' + str(i)))
        temp.append(request.form.get('type-colonne-' + str(i)))
        temp.append(request.form.get('primary-key-' + str(i))) #on ou None
        colonnes.append(temp)
    primary_key = [i[0] for i in colonnes if i[2]=="on"]
    if len(primary_key)==0:
        flash("Veuillez renseigner au moins une clé primaire", "alert-warning")
        return redirect('/tables/add')

    mycursor = get_db().cursor()
    mycursor.execute(f"USE {session['database']}")
    sql=f'''
    CREATE TABLE {nom}(
    '''
    for colonne in colonnes:
        sql+=f"{colonne[0]} {colonne[1]}, "
    sql+="PRIMARY KEY ("
    for primary in primary_key:
        sql+=f"{primary}, "
    sql=sql[:-2]
    sql+="));"
    mycursor.execute(sql)
    get_db().commit()
    mycursor.close()
    return redirect('/tables/show')


@app.route("/databases/vider", methods=['GET', 'POST'])
def vider():
    mycursor = get_db().cursor()
    mycursor.execute(f"USE {session['database']}")
    mycursor.execute(f"SHOW TABLES")
    content = mycursor.fetchall()
    while content is not None and content != [] and content != ():
        mycursor.execute(f"SHOW TABLES")
        content = mycursor.fetchall()
        for table in content:
            try:
                mycursor.execute(f"DROP TABLE {table[f"Tables_in_{session['database']}"]}")
                get_db().commit()
            except Exception as e:
                continue
    mycursor.close()
    return redirect('/databases/show')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)