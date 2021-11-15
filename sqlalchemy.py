#in database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker



SQLALCHEMY_DATABASE_URL = 'sqlite:///./blog.db' # sqlite database
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# models.py
from database import Base
from sqlalchemy import Column, Integer, String



class Blog(Base):
    __tablename__ = "blog"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    desc = Column(String)




# schemas.py

from pydantic import BaseModel

class Blog(BaseModel):
    title: str
    desc: str



#main.py
from fastapi import FastAPI, Response, status, HTTPException
import models
from database import engine, SessionLocal
models.Base.metadata.create_all(engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/newblogpost")
def index(request: schemas.Blog, db: Session = Depends(get_db)):
    new_blog = models.Blog(title=request.title, desc=request.desc) # it should match from schemas.Blog
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

@app.get("/getsingleblog/{id}", satus_code=200)
def getSingleBlog(id, response: Response db: Session = Depends(get_db)):
    query = db.query(models.Blog).filter(models.Blog.id == id).first()

    if not query:
        raise HTTPException(status_code=404, details: "Blog not Found!")
        # response.status_code = 404
        # return {"details": "Blog not found"}

    return query

@app.delete("/deleteblog/{id}")
def deleteItem(id, db: Session = Depends(get_db)):
    query = db.query(models.Blog).filter(models.Blog.id == id).delete()
    db.commit()

    if not query:
        raise HTTPException(status_code=501, message="Could not Delete the file")
    return {"message": "file deleted successfully"}
