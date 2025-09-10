from pydantic import BaseModel


class ProjectResponse(BaseModel):
    id: int
    title: str
    thumbnail: str
    image: str
    description: str
    link: str
    date: str
    popularity: int