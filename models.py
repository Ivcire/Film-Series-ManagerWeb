from sqlalchemy import Column, Integer, String, Float
import db

class Usuarios(db.Base): #Esta tabla será la de las usuarios
    __tablename__ = "usuarios"
    __table_args__ = {'sqlite_autoincrement': True} #Quiero tener la primary key autoincremental
    id_usuario = Column(Integer, primary_key=True) #Id para cada uno de los usuarios, debe ser diferente para todos
    nombre_usuario = Column(String(16), nullable=False) #Se guarda el nombre del usuario, el mail y la contraseña para hacer login
    email_usuario = Column(String(50), nullable=False)
    clave_usuario = Column(String(50), nullable=False)

    def __init__(self, email_usuario, nombre_usuario, clave_usuario):
        self.email_usuario = email_usuario
        self.nombre_usuario = nombre_usuario
        self.clave_usuario = clave_usuario

    def __str__(self):
        return "ID Usuario: {} -> Nombre Usuario: {} -> Contraseña: {}".format(self.id_usuario, self.nombre_usuario,
                                                                               self.clave_usuario)

class Peliculas(db.Base):
    __tablename__ = "peliculas"
    __table_args__ = {'sqlite_autoincrement': True}  # Quiero tener la primary key autoincremental
    id_pelicula = Column(Integer, primary_key=True)  # Id para cada uno de las pelis
    imdb_link = Column(String, nullable=False)
    titulo = Column(String, nullable=False)
    calificacion = Column(Float, nullable=False)
    genero = Column(String, nullable=False)
    poster = Column(String, nullable=False)

    def __init__(self, imdb_link, titulo, calificacion, genero, poster):
        self.imdb_link = imdb_link
        self.titulo = titulo
        self.genero = genero
        self.calificacion = calificacion
        self.poster = poster

class Generos(db.Base):
    __tablename__ = "generos"
    __table_args__ = {'sqlite_autoincrement': True}  # Quiero tener la primary key autoincremental
    id_genero = Column(Integer, primary_key=True)
    genero = Column(String, nullable=False)

    def __init__(self, genero):
        self.genero = genero

class Series(db.Base):
    __tablename__ = "series"
    __table_args__ = {'sqlite_autoincrement': True}  # Quiero tener la primary key autoincremental
    id_serie = Column(Integer, primary_key=True)  # Id para cada uno de las series
    titulo = Column(String, nullable=False)
    anio_salida = Column(Integer, nullable=False)
    anio_final = Column(Integer)
    duracion = Column(Integer, nullable=False)
    genero = Column(String, nullable=False)
    calificacion = Column(Float, nullable=False)
    cast = Column(String, nullable=False)
    sinopsis = Column(String, nullable=False)

    def __init__(self, titulo, anio_salida, duracion, genero, calificacion, cast, sinopsis):
        self.titulo = titulo
        self.anio_salida = anio_salida
        self.duracion = duracion
        self.genero = genero
        self.calificacion = calificacion
        self.cast = cast
        self.sinopsis = sinopsis

class WatchedUsuarios(db.Base):
    __tablename__ = "watched_usuarios"
    __table_args__ = {'sqlite_autoincrement': True}  # Quiero tener la primary key autoincremental
    id_rating = Column(Integer, primary_key=True)
    id_producto = Column(Integer, nullable=False)
    tipo_producto = Column(String, nullable=False)
    usuario = Column(String, nullable=False)
    rating = Column(Float)
    review = Column(String)

    def __int__(self, id_producto, tipo_producto, usuario, rating = None, review = None):
        self.id_producto = id_producto
        self.tipo_producto = tipo_producto
        self.usuario = usuario
        self.rating = rating
        self.review = review



