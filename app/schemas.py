from typing import Annotated, Optional
from pydantic import BaseModel, EmailStr, Field, StringConstraints, ConfigDict

from annotated_types import Ge, Le

NameStr = Annotated[str, StringConstraints(min_length=1, max_length=100)]
YearInt = Annotated[int, Ge(1900), Le(2100)]
PageInt = Annotated[int, Ge(1), Le(10000)]
TitleStr = Annotated[str, StringConstraints(min_length=1, max_length=255)]

NameStr = Annotated[str, StringConstraints()]

class AuthorRead(BaseModel):
    id: int
    name: NameStr
    email: EmailStr
    year_started: YearInt
    model_config = ConfigDict(from_attributes=True)


class AuthorCreate(BaseModel):
    name: NameStr
    email: EmailStr
    year_started: YearInt

class AuthorPatch(BaseModel):
    name: Optional [NameStr] = None
    email: Optional [EmailStr] = None
    year_started: Optional [YearInt] = None


class BookRead(BaseModel):
    id: int
    title: TitleStr
    pages: PageInt
    author_id: int
    model_config = ConfigDict(from_attributes=True)

class BookCreate(BaseModel):
    title: TitleStr
    pages: PageInt
    author_id: int
    
class BookPatch(BaseModel):
    title: Optional [TitleStr] = None
    pages: Optional [PageInt] = None

