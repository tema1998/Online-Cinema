from pydantic import BaseModel, EmailStr, AnyUrl


class InstantMessageRequest(BaseModel):
    email: EmailStr
    message_data: dict


class NotificationAboutNewComment(BaseModel):
    user_first_name: str
    user_last_name: str


class WelcomeMessageRequest(BaseModel):
    message_data: dict


class WelcomeLinkMessageRequest(BaseModel):
    message_data: dict
    confirmation_link: AnyUrl


class PeriodicTaskParamsRequest(BaseModel):
    name: str
    interval_in_seconds: int


class PeriodicTaskIdRequest(BaseModel):
    task_id: str
