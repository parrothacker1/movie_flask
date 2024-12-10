from sqlalchemy import create_engine,Column,String,Integer,Float,ForeignKey,insert,delete,select,func,update
from sqlalchemy.orm import declarative_base,sessionmaker,relationship  
from sqlalchemy.dialects.postgresql import ARRAY
import os
import uuid

Base = declarative_base()
engine = create_engine(os.environ['DATABASE_URL'])
engine.connect()

Session = sessionmaker(bind=engine)
session = Session()

class Movies(Base):
    __tablename__ = "movies"
    id = Column(String(255),primary_key=True)
    name = Column(String(255),nullable=False)
    year = Column(Integer)
    genres_ids = Column(ARRAY(Integer))
    actors_ids = Column(ARRAY(Integer))
    technicians_ids = Column(ARRAY(Integer))

class Genre(Base):
    __tablename__ = 'genre'
    id = Column(Integer,primary_key=True)
    name = Column(String(255),nullable=False)

class Actor(Base):
    __tablename__ = 'actor'
    id = Column(Integer,primary_key=True)
    name = Column(String(255),nullable=False)

class Technician(Base):
    __tablename__ = 'technician'
    id = Column(Integer,primary_key=True)
    name = Column(String(255),nullable=False)

class UserRating(Base):
    __tablename__ = "userratings"
    id = Column(Integer,primary_key=True)
    rating = Column(Float,nullable=False)
    movie_id = Column(String,ForeignKey('movies.id'))
    movies = relationship("Movies")


Base.metadata.create_all(engine)

def movies_list(filters=None):
    try:
        results_list = []
        if filters is None:
            # Optimized for N+1 Querying 
            movies_list = session.query(Movies).all()
            user_ratings = {x[1]:x[0] for x in session.execute(select(func.avg(UserRating.rating),UserRating.movie_id).group_by(UserRating.movie_id)).all()}
            for movie in movies_list:
                result = {}
                result["id"] = movie.id
                result["name"] = movie.name
                result["year"] = movie.year
                result["genres_ids"] = movie.genres_ids
                result["actors_ids"] = movie.actors_ids
                result["technicians_ids"] = movie.technicians_ids
                result["user_ratings"] = user_ratings.get(movie.id,None)
                results_list.append(result)
        else:
            movies_list = session.query(Movies).all()
            res_movies = set([])
            for i in movies_list:
                actors_ids = filters.get('actors_ids',[])
                genres_ids = filters.get("genres_ids",[])
                technicians_ids = filters.get("technicians_ids",[])
                for j in actors_ids:
                    if j in (i.actors_ids if i.actors_ids is not None else []):
                        res_movies.add(i)
                for j in genres_ids:
                    if j in (i.genres_ids if i.genres_ids  is not None else []):
                        res_movies.add(i)
                for j in technicians_ids:
                    if j in (i.technicians_ids if i.technicians_ids is not None else []):
                        res_movies.add(i)
            movies_ids = [x.id for x in res_movies]
            user_ratings = {x[1]:x[0] for x in session.execute(select(func.avg(UserRating.rating),UserRating.movie_id).group_by(UserRating.movie_id).where(UserRating.movie_id.in_(movies_ids))).all()}
            for movie in res_movies:
                result = {}
                result["id"] = movie.id
                result["name"] = movie.name
                result["year"] = movie.year
                result["genres_ids"] = movie.genres_ids
                result["actors_ids"] = movie.actors_ids
                result["technicians_ids"] = movie.technicians_ids
                result["user_ratings"] = user_ratings.get(movie.id,None)
                results_list.append(result)

        return results_list
    except ValueError:
        session.rollback()
        return -1

def delete_actor(id):
    try:
        all_movie_actors = set([x[0] for x in session.execute(select(func.unnest(Movies.actors_ids))).all()])
        if id in all_movie_actors:
            return 0
        else:
            session.execute(delete(Actor).where(Actor.id == id))
            session.commit()
            return 1
    except:
        session.rollback()
        return -1

def add_update(data):
    try:
        if 'id' in data.keys():
            movie_id = data.pop('id')
            session.execute(update(Movies).where(Movies.id==movie_id).values(**data))
            session.commit()
            return 1
        else:
            data['id']=str(uuid.uuid4())
            new_movie=Movies(**data)
            session.add(new_movie)
            session.commit()
            return 1
    except ValueError:
        session.rollback()
        return -1
