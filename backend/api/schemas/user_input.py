from pydantic import BaseModel

class UserInput(BaseModel):
    user_input: str

class FilePathInput(BaseModel):
    file_path: str