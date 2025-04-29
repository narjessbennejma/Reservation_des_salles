from pydantic import BaseModel

class SalleBase(BaseModel):
    nom: str
    capacite: int
    localisation: str

class SalleCreate(SalleBase):
    pass

class SalleResponse(SalleBase):
    id: int

    class Config:
        from_attributes = True
