from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal

# Enums
PriorityType = Literal['LOW', 'MEDIUM', 'HIGH']
StatusType = Literal['OPEN', 'IN_PROGRESS', 'CLOSED']

# Ticket Schemas
class TicketCreateSchema(BaseModel):
    title: str = Field(min_length=4, max_length=100)
    description: str = Field(min_length=10)
    priority: PriorityType
    reporter: str = Field(min_length=2)
    projectId: Optional[str] = None
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if len(v) < 4:
            raise ValueError('Title must be at least 4 characters')
        if len(v) > 100:
            raise ValueError('Title must be at most 100 characters')
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if len(v) < 10:
            raise ValueError('Description must be at least 10 characters')
        return v
    
    @field_validator('reporter')
    @classmethod
    def validate_reporter(cls, v):
        if len(v) < 2:
            raise ValueError('Reporter name must be at least 2 characters')
        return v

class TicketUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, min_length=4, max_length=100)
    description: Optional[str] = Field(None, min_length=10)
    priority: Optional[PriorityType] = None
    status: Optional[StatusType] = None
    reporter: Optional[str] = Field(None, min_length=2)

# Comment Schema
class CommentCreateSchema(BaseModel):
    author: str = Field(min_length=2)
    body: str = Field(min_length=2, max_length=500)
    
    @field_validator('author')
    @classmethod
    def validate_author(cls, v):
        if len(v) < 2:
            raise ValueError('Author name must be at least 2 characters')
        return v
    
    @field_validator('body')
    @classmethod
    def validate_body(cls, v):
        if len(v) < 2:
            raise ValueError('Comment must be at least 2 characters')
        if len(v) > 500:
            raise ValueError('Comment must be at most 500 characters')
        return v

# Auth Schemas
class SignupSchema(BaseModel):
    name: str = Field(min_length=1)
    email: str
    password: str = Field(min_length=6)
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if len(v) < 1:
            raise ValueError('Name is required')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v

class LoginSchema(BaseModel):
    email: str
    password: str = Field(min_length=1)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 1:
            raise ValueError('Password is required')
        return v

# Project Schema
class ProjectCreateSchema(BaseModel):
    name: str
    parentProject: str