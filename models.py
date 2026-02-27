from pydantic import BaseModel

class NewsRequest(BaseModel):
    title: str
    text: str
    date: str
    categories: list[str]

class NewsResponse(BaseModel):
    title: str
    text: str
    date: str
    categories: list[str]


