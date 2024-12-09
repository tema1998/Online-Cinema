from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, constr, Field, EmailStr


class UserRegister(BaseModel):
    login: str
    password: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class SocialUserRegister(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class UserInfoOut(BaseModel):
    id: Optional[UUID] = None
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_superuser: Optional[bool] = None


class UserInDB(BaseModel):
    id: UUID
    login: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    login: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(RefreshTokenRequest):
    pass


class GetUserInfoRequest(BaseModel):
    user_id: UUID


class GetAccessToken(BaseModel):
    access_token: str


class SetUserPremiumRequest(BaseModel):
    user_id: str
    number_of_month: int


class UserUpdateRequest(BaseModel):
    login: Optional[str] = None
    old_password: Optional[str] = None
    new_password: Optional[str] = None


class UpdateUserCredentialsRequest(BaseModel):
    login: Optional[constr(min_length=3, max_length=50)] = Field(
        None, description="New login"
    )
    old_password: Optional[constr(min_length=6)] = Field(
        None, description="Old password"
    )
    new_password: Optional[constr(min_length=6)] = Field(
        None, description="New password"
    )


class UserResponse(BaseModel):
    id: UUID
    login: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    class Config:
        from_attributes = True


class RoleInDB(BaseModel):
    id: UUID
    name: str
    description: str
    permissions: list[str]

    class Config:
        from_attributes = True


class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: list[str]


class UpdateRoleRequest(BaseModel):
    name: Optional[constr(max_length=50)] = Field(None, description="New name")
    description: Optional[str] = Field(None, description="New description")
    permissions: Optional[list[str]] = Field(
        None, description="New permissions")


class RoleId(BaseModel):
    id: UUID


class RolesInDB(BaseModel):
    roles: list[RoleInDB]

    class Config:
        from_attributes = True


class UserLoginHistoryResponse(BaseModel):
    id: UUID
    user_id: UUID
    login_time: datetime
    user_agent: str
    ip_address: str

    class Config:
        from_attributes = True
        orm_mode = True


class UserRole(BaseModel):
    user_id: UUID
    role_id: UUID

    class Config:
        from_attributes = True


class UserPermissions(BaseModel):
    permissions: list[str]

    class Config:
        from_attributes = True


class AssignDeleteUserRoleRequest(BaseModel):
    role_name: Optional[constr(max_length=100)] = Field(
        None, description="Name of the role."
    )
