import json
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from models import NewsRequest, NewsResponse
from database import session,engine
import database_models
import rag

app = FastAPI()
database_models.Base.metadata.create_all(bind=engine)

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

@app.post("/news")
def saveNews(news: NewsRequest, db = Depends(get_db)):
    db.add(database_models.News(title=news.title, text=news.text, date=news.date, categories=[database_models.Category(name=category) for category in news.categories]))
    db.commit()
    return {"message": "News saved successfully"}

@app.get("/news/{id}")
def updateNews(id:int, db = Depends(get_db)):
    db_news = db.query(database_models.News).filter(database_models.News.id == id).first()
    if not db_news:
        return {"message": "News not found"}
    return NewsResponse(title=db_news.title, text=db_news.text, date=db_news.date, categories=[category.name for category in db_news.categories])

@app.post("/news/all")
def saveNews(file: UploadFile = File(...), db = Depends(get_db)):
    try:
        content = file.file.read().decode("utf-8")
        data = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")

    for item in data:
        db.add(database_models.News(
            title=item['title'], 
            text=item['text'], 
            date=item['date'], 
            categories=[
                database_models.Category(name=category) for category in item['categories']]))
    db.commit()
    return {"message": "News saved successfully"}

# Rag ingestion End point
@app.post("/news/ingest")
def saveTOVector(string: str):
    try:
        mes = rag.saveTOVector(string)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error ingesting to vector store: " + str(e))
    return mes

@app.post("/news/ingest/file")
def saveToVectorFile(file: UploadFile = File(...)):
    try:
        mes = rag.saveToVectorFile(file)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error ingesting File to vector store: " + str(e))
    return mes

#Retriever
@app.post("/news/retrieve")
def getEmbeddings(question: str):
    try:
        answer = rag.getEmbeddings(question)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error retrieving from vector store: " + str(e))
    return answer

#Generation
@app.post("/news/generate")
def getResponse(question: str):
    try:
        response = rag.getResponse(question)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error generating response: " + str(e))
    return response

#Cache
@app.post("/news/cache")
def cacheResponse(question: str):
    try:
        mes = rag.getResposeWithChat(question)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error caching response: " + str(e))
    return mes