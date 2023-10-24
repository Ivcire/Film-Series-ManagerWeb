from flask import Flask, render_template, request, redirect, url_for
import db
from models import Usuarios, Peliculas, Series, Generos, WatchedUsuarios
from sqlalchemy import and_
import ctypes #Libreria para crear alertas
import csv
import pandas as pd
import gc
import random

app = Flask(__name__) #Usamos flask para crear la app
actual_user = None
genre_list = []

#Creo la página Home
@app.route('/')
def home():
    return render_template("login.html")

@app.route('/login', methods=["POST"])
def login():
    user = request.form["id_user_login"]
    password = request.form["password_login"]
    user_login = db.session.query(Usuarios).filter(Usuarios.nombre_usuario==user).first()
    if user_login is not None:
        if user_login.clave_usuario == password:
            ctypes.windll.user32.MessageBoxW(0, "Log in succesful", "Login", 0x00001000)
            #Cargo la página Home al hacer login, para pasar una variable se le añade desde el URL_FOR
            global actual_user #hay que declarar la variable como global para que se pueda acceder a ella desde fuera de la funcion
            actual_user = user
            return redirect(url_for('main_page', username=actual_user))

        else:
            ctypes.windll.user32.MessageBoxW(0, "Incorrect password", "Error", 0x00001000)
    else:
        ctypes.windll.user32.MessageBoxW(0, "There is no user with that username", "Error", 0x00001000)
    return render_template("login.html")

@app.route('/register_page')
def sign_in_btn():
    return render_template("register.html")

@app.route('/register', methods = ["POST"])
def new_user():
    password = request.form["password_user"]
    confirm_password = request.form["confirm_password_user"]
    email = request.form["email_user"]
    username = request.form["username_user"]

    #Voy a comprobar que no haya ninguna cuenta ya creada con el email o username introducidos
    #Uso el query para hacer una consulta con el filter by que equivale al WHERE en SQL
    check_email = db.session.query(Usuarios).filter_by(email_usuario=email).first() #Importante FIRST para que devuelva el primer registro
    check_username = db.session.query(Usuarios).filter_by(nombre_usuario=username).first()

    if check_email is not None: #Si nos devuelven un valor es que se ha encontrado el email en la db
        ctypes.windll.user32.MessageBoxW(0, "Email already used!", "Error", 0x00001000)
    elif check_username is not None: #Lo mismo para un username
        ctypes.windll.user32.MessageBoxW(0, "Username already used!", "Error",0x00001000)
    else:
        if password == confirm_password and password != "" and 20 >= len(password) >= 8:
            user = Usuarios(email_usuario=email ,nombre_usuario=username,
                      clave_usuario=password) #Pido las variables con Flask mediante post
            db.session.add(user)
            db.session.commit()
            #Parametro 0x00001000 permite que la alerta se ponga por delante de la pagina
            ctypes.windll.user32.MessageBoxW(0, "User Created!", "Welcome to ARCANA", 0x00001000) #Alerta al crear usuario
        elif not 20 >= len(password) >= 8:
            ctypes.windll.user32.MessageBoxW(0, "Password must be 8-20 characters long.", "Error", 0x00001000) #Alerta al poner mal la contraseña
            return render_template("register.html")
        elif password != confirm_password:
            ctypes.windll.user32.MessageBoxW(0, "Passwords must be equal!", "Error",
                                             0x00001000)  # Alerta al poner mal la contraseña

    return render_template("register.html")

#Hay que poner en la app.route que necesitamos una variable con "/<nombrevariable>"
@app.route('/main_page/<username>')
def main_page(username): #Tambien hay que meter como parametro la variable que queremos que nos pasen desde el URL_FOR
    # Leo la base de datos y me creo un dataframe de pandas para manipularlo. IMPORTANTE sin el connect no nos va a funcionar
    film_selection = df_films.sort_values(by=["calificacion"]).tail() #Organizo las series por calificación y muestro las mejor valoradas
    film_selection = film_selection.values #Muy importante para poder mostrar las películas correctamente
    show_selection = df_series.sort_values(by=["calificacion"]).tail().values
    return render_template("home.html", top_films=film_selection, user=username,
                           top_series=show_selection)

@app.route('/films_page/<username>')
def film_page(username):
    users_info = read_users_db()
    #Saco los id de las últimas películas vistas
    watched_recently_id = users_info.loc[(users_info['usuario'] == actual_user) & (users_info['tipo_producto'] == "film"),
    ['id_producto']].tail().values

    watched_recently = []
    #Busco en la tabla de pelis el id y saco las últimas 5 vistas
    for x in watched_recently_id:
        #Me devuelve una lista de una lista, accedo a la posicion cero para sacar todos los elementos
        watched_recently_row = df_films[df_films['id_pelicula'] == x[0]].values
        watched_recently.append(watched_recently_row[0])
    #Selecciono elementos aleatorios de la lista para mostrarlos como recomendaciones

    genre_selection = random.sample(genres_films, 5)
    film_selection = {}
    #Creo un diccionario con mi selección de peliculas que voy a mostrar
    for genre in genre_selection:
        genre_films_selection = df_films[df_films['genero'].str.contains(genre)]
        count = len(genre_films_selection.index)

        if count >= 5: #Me aseguro de que solo se muestren 5 elementos por genero como máximo
            count = 5

        genre_films_selection = genre_films_selection.sample(n=count, replace=False)
        #SUPER IMPORTANTE PARA SACAR LOS VALORES A UNA LISTA
        film_selection[genre] = genre_films_selection.values

    return render_template("films_home.html", user=username, genres=genres_films,
                           gen_selection = genre_selection, film_selection=film_selection,
                           watched_recently=watched_recently)

@app.route('/show_page/<username>')
def show_page(username):
    users_info = read_users_db()
    # Saco los id de las últimas películas vistas
    watched_recently_id = users_info.loc[
        (users_info['usuario'] == actual_user) & (users_info['tipo_producto'] == "show"),
        ['id_producto']].tail().values

    watched_recently = []
    # Busco en la tabla de pelis el id y saco las últimas 5 vistas
    for x in watched_recently_id:
        # Me devuelve una lista de una lista, accedo a la posicion cero para sacar todos los elementos
        watched_recently_row = df_series[df_series['id_serie'] == x[0]].values
        watched_recently.append(watched_recently_row[0])
    #Selecciono elementos aleatorios de la lista para mostrarlos como recomendaciones
    genre_selection = random.sample(genres_series, 5)
    series_selection = {}
    #Creo un diccionario con mi selección de series que voy a mostrar
    for genre in genre_selection:
        genre_series_selection = df_series[df_series['genero'].str.contains(genre)]
        count = len(genre_series_selection.index)

        if count >= 5: #Me aseguro de que solo se muestren 5 elementos por genero como máximo
            count = 5

        genre_series_selection = genre_series_selection.sample(n=count, replace=False)
        #SUPER IMPORTANTE PARA SACAR LOS VALORES A UNA LISTA
        series_selection[genre] = genre_series_selection.values

    return render_template("shows_home.html", user=username, genres=genres_series,
                           gen_selection = genre_selection, series_selection=series_selection,
                           watched_recently=watched_recently)

@app.route('/film/<id>')
def fill_film(id):
    film = df_films[df_films['id_pelicula'] == int(id)].values
    users_info = read_users_db()
    #Saco la media de los ratings de los usuarios en la pelicula
    mean_rating = users_info['rating'][
        (users_info['id_producto'] == int(id)) & (users_info['tipo_producto'] == "film") & (users_info['rating'] != -1)].mean()
    #Saco las últimas 5 reviews de la película
    reviews = users_info.loc[
        (users_info['id_producto'] == int(id)) & (users_info['tipo_producto'] == "film") &
        ((users_info['review'].notnull())),
        ['review', 'usuario']].tail().values
    #Hay que tener en cuenta que nos devuelve una lista de listas, aunque en este caso solo hay una fila
    #Por lo que en HTML hay que acceder al valor film[0][x]
    return render_template('film.html', user=actual_user, film=film, rating_users=mean_rating, reviews=reviews)

@app.route('/show/<id>')
def fill_show(id):
    show = df_series[df_series['id_serie'] == int(id)].values
    #Hay que tener en cuenta que nos devuelve una lista de listas, aunque en este caso solo hay una fila
    #Por lo que en HTML hay que acceder al valor film[0][x]
    users_info = read_users_db()
    # Saco la media de los ratings de los usuarios en la serie
    mean_rating = users_info['rating'][
        (users_info['id_producto'] == int(id)) & (users_info['tipo_producto'] == "show") & (
                    users_info['rating'] != -1)].mean()
    # Saco las últimas 5 reviews de la película
    reviews = users_info.loc[
        (users_info['id_producto'] == int(id)) & (users_info['tipo_producto'] == "show") &
        ((users_info['review'].notnull())),
        ['review', 'usuario', 'rating']].tail().values
    return render_template('show.html', user=actual_user, show=show, rating=mean_rating, reviews=reviews)

@app.route('/film_genre/<genre>')
def show_genre_films(genre):
    all_genre_films = df_films[df_films['genero'].str.contains(genre)].values

    return render_template('film_genre.html', user=actual_user, films=all_genre_films, genre=genre)

@app.route('/show_genre/<genre>')
def show_genre_series(genre):
    all_genre_series = df_series[df_series['genero'].str.contains(genre)].values

    return render_template('show_genre.html', user=actual_user, series=all_genre_series, genre=genre)

@app.route('/add_watched/<id>', methods = ["POST"])
def add_to_watched_db(id):
    product_type = request.form["product_type"]
    check_watched_results = check_watched(id, product_type)
    is_film, is_show, is_watched = check_watched_results[0],  check_watched_results[1],  check_watched_results[2]
    print(is_watched)
    if not is_watched:
        if is_film:
            watched = WatchedUsuarios(id_producto=id, tipo_producto="film", usuario=actual_user)
        elif is_show:
            watched = WatchedUsuarios(id_producto=id, tipo_producto="show", usuario=actual_user)
        db.session.add(watched)
        db.session.commit()
        ctypes.windll.user32.MessageBoxW(0, "Product Added to Watched", "Product Added!", 0x00001000)
    else:
        ctypes.windll.user32.MessageBoxW(0, "Product Already Added to Watched", "Product NOT Added!", 0x00001000)

    #Al redirigir hay que comprobar si estábamos añadiendo una peli o una serie
    if is_film:
        return redirect(url_for('fill_film', id=id))
    elif is_show:
        return redirect(url_for('fill_show', id=id))

@app.route('/delete_watched/<id>', methods = ["POST"])
def delete_watched_db(id):
    product_type = request.form["product_type"]
    check_watched_results = check_watched(id, product_type)
    is_film, is_show, is_watched = check_watched_results[0], check_watched_results[1], check_watched_results[2]

    if is_watched:
        delete = db.session.query(WatchedUsuarios).filter(and_(WatchedUsuarios.id_producto == id,
                                                                      WatchedUsuarios.tipo_producto == product_type,
                                                                      WatchedUsuarios.usuario == actual_user)).delete()
        db.session.commit()
        ctypes.windll.user32.MessageBoxW(0, "Product deleted from watched", "Product Deleted!", 0x00001000)
    else:
        ctypes.windll.user32.MessageBoxW(0, "Product not Watched, please first add as watched", "Product NOT Watched!",
                                         0x00001000)

    #Al redirigir hay que comprobar si estábamos añadiendo una peli o una serie
    if is_film:
        return redirect(url_for('fill_film', id=id))
    elif is_show:
        return redirect(url_for('fill_show', id=id))

@app.route('/edit_watched/<id>', methods=["POST"])
def  edit_watched(id):
    product_type = request.form["product_type"]
    rating = request.form["rating"]
    if not isfloat(rating):
        rating = -1
    review = request.form["review"]
    check_watched_results = check_watched(id, product_type)
    is_film, is_show, is_watched, product = check_watched_results[0], check_watched_results[1], check_watched_results[2],check_watched_results[3]

    if is_watched:
        product.rating = rating
        product.review = review
        db.session.commit()

        ctypes.windll.user32.MessageBoxW(0, "Review Edited!", "Review", 0x00001000)
    else:
        ctypes.windll.user32.MessageBoxW(0, "Product not Watched, please first add as watched", "Product NOT Watched!", 0x00001000)

    if is_film:
        return redirect(url_for('fill_film', id=id))
    elif is_show:
        return redirect(url_for('fill_show', id=id))

@app.route('/search' , methods=["POST"])
def search():
    search_item = request.form["search"]
    searched_films = df_films[df_films['titulo'].str.contains(search_item)].values
    searched_shows = df_series[df_series['titulo'].str.contains(search_item)].values
    return render_template('search_page.html', user=actual_user, searched_films=searched_films,
                            searched_shows=searched_shows)

@app.route('/profile')
def display_profile():
    users_info = read_users_db()
    #Saco las peliculas que ha visto el usuario
    films_watched = users_info[(users_info['usuario'] == actual_user) & (users_info['tipo_producto'] == "film")]
    #Las cuento para mostrarlo como estadistica
    number_films = len(films_watched.index)
    shows_watched = users_info[(users_info['usuario'] == actual_user) & (users_info['tipo_producto'] == "show")]
    number_shows = len(shows_watched.index)
    #Saco la lista de ids de series vistas
    shows_id = shows_watched['id_producto'].values.tolist()
    # Ahora lo que busco es sacar un dataframe de la tabla de series con los id que ha visto el usuario
    user_watchlist = df_series[df_series['id_serie'].isin(shows_id)]
    # El objetivo es sacar la media de duracion de los capitulos de las series vistas
    user_watchlist_duration = round(user_watchlist['duracion'].mean())
    return render_template('profile.html', user=actual_user, number_films=number_films, number_shows=number_shows,
                          mean_chapter=user_watchlist_duration)


def check_watched(id, product_type):
    is_film, is_show, is_watched = False, False, False
    # Compruebo si es una pelicula o una serie
    if product_type == "film":
        is_film = True
    elif product_type == "show":
        is_show = True
    # Hago una busqueda para que no se repitan las películas en la DB
    # El and_ solo me funciona con filter, por eso no uso filter_by
    # En este caso hay que usar un == para hacer la comparación
    check_product = db.session.query(WatchedUsuarios).filter(and_(WatchedUsuarios.id_producto == id,
                                                                  WatchedUsuarios.tipo_producto == product_type,
                                                                  WatchedUsuarios.usuario == actual_user)).first()

    if check_product is not None:
        is_watched = True

    return is_film, is_show, is_watched, check_product

def fill_movie_DB():
    with open("database/MovieGenre.csv", "r", encoding="ISO-8859-1") as my_csv_file:
        reader = csv.reader(my_csv_file, delimiter=",") #Elijo el delimitador para mi CSV
        next(reader) #Me salto la cabecera
        global genre_list
        for row in reader:
            #Las películas con información incompleta las ignoro
            if isfloat(row[3]):
                genres = row[4].split("|")
                for x in genres:
                    if x not in genre_list and len(x) != 0 :
                        genre_list.append(x)
                        genre = Generos(x)
                        db.session.add(genre)
                #Quito películas que no tienen año de lanzamiento en el CSV
                film = Peliculas(row[1], row[2], float(row[3]), row[4], row[5])
                db.session.add(film)
        db.session.commit()

def fill_series_DB():
    with open("database/TV Series.csv", "r", encoding="utf-8") as my_csv_file:
        reader = csv.reader(my_csv_file, delimiter=",") #Elijo el delimitador para mi CSV
        next(reader) #Me salto la cabecera
        indb_list = []
        for row in reader:
            #Este if comprueba que no hay duplicados.
            #Si el elemento no está lo añade a la lista para la proxima iteración comprobar el siguiente
            if row[0] not in indb_list:
                indb_list.append(row[0])
                #Viene el año de lanzamiento y de finalizacion juntos, lo he hecho así porque el split no me funcionaba bien
                year = row[1][1:-1]
                release_year = year[:4]
                end_year = year[5:]
                #Para esto quiero separar los minutos del número y poder usarlo para analisis, uso strip para que no
                #de problemas el isnumeric porque los espacios no los traga
                runtime = row[2].replace("min", "").strip()
                genres = row[3].split(",")
                for x in genres:
                    x = x.strip()
                    if x not in genre_list and len(x) != 0 and x != "****":
                        genre_list.append(x)
                        genre = Generos(x)
                        db.session.add(genre)
                if isfloat(row[4]) and release_year.isnumeric() and runtime.isnumeric():
                    show = Series(row[0], int(release_year), int(runtime), row[3], float(row[4]), row[5], row[6])
                    if len(end_year) == 4:
                        show.anio_final = int(end_year)
                    db.session.add(show)

        db.session.commit()
        #Ya no necesito esta lista así que la borro con el garbage collector
        del indb_list
        gc.collect()

def genreFilmsSeriesList():
    df = pd.read_sql_table("generos", db.engine.connect())
    #me guardo una lista de los generos de las peliculas y series para trabajar más cómodo
    genres_films = df["genero"].values.tolist()
    genres_series = df["genero"][df["genero"] != "Film-Noir"].values.tolist()
    return genres_films, genres_series

def read_users_db():
    df = pd.read_sql_table("watched_usuarios", db.engine.connect())
    return df

def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    #Lo uso para testear la creación de databases
    #db.Base.metadata.drop_all(db.engine)
    db.Base.metadata.create_all(db.engine)
    if db.session.query(Peliculas).first() is None:
        fill_movie_DB()

    if db.session.query(Series).first() is None:
        fill_series_DB()

    genres_films,genres_series = genreFilmsSeriesList()[0], genreFilmsSeriesList()[1]
    df_films = pd.read_sql_table('peliculas', db.engine.connect())
    df_series = pd.read_sql_table('series', db.engine.connect())
    # El debug=True hace que cada vez que reiniciemos el servidor o modifiquemos codigo, el servidor de Flask se reinicie solo
    app.run(host="localhost", port=8000, debug=True)
