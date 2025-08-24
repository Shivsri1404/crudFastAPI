from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    user_image_path: str | None = None   # return image path
    model_config = ConfigDict(from_attributes=True)
