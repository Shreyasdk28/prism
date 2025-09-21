from pydantic import BaseModel


class AddUserToSessionRequest(BaseModel):
    username : str

class AddProductToSessionRequest(BaseModel):
    product : str

class AddPrefsToSessionRequest(BaseModel):
    prefs : str


class Session(BaseModel):
    id : str
    username : str
    product : str
    prefs : str
