from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine('sqlite:///database/pelis.db',
connect_args={'check_same_thread': False}) #La base de datos se ejecutará en segundo plano

Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()