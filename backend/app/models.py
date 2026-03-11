import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    worklogs: list["WorkLog"] = Relationship(back_populates="user", cascade_delete=True)
    remittances: list["Remittance"] = Relationship(back_populates="user", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class TimeSegmentBase(SQLModel):
    amount: Decimal = Field(decimal_places=2)
    is_deleted: bool = False


class TimeSegmentCreate(TimeSegmentBase):
    worklog_id: uuid.UUID


class TimeSegment(TimeSegmentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    worklog_id: uuid.UUID = Field(
        foreign_key="worklog.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    worklog: "WorkLog" = Relationship(back_populates="time_segments")


class TimeSegmentPublic(TimeSegmentBase):
    id: uuid.UUID
    worklog_id: uuid.UUID
    created_at: datetime


class WorkLogBase(SQLModel):
    user_id: uuid.UUID
    task_id: str = Field(max_length=255)
    remittance_status: str = Field(default="UNREMITTED", max_length=50)


class WorkLogCreate(WorkLogBase):
    pass


class WorkLog(WorkLogBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    time_segments: list[TimeSegment] = Relationship(
        back_populates="worklog", cascade_delete=True
    )
    remittances: list["Remittance"] = Relationship(back_populates="worklog")
    adjustments: list["Adjustment"] = Relationship(back_populates="worklog")
    user: User | None = Relationship(back_populates="worklogs")


class WorkLogPublic(WorkLogBase):
    id: uuid.UUID
    amount: Decimal
    created_at: datetime


class WorkLogsPublic(SQLModel):
    data: list[WorkLogPublic]
    count: int


class RemittanceBase(SQLModel):
    user_id: uuid.UUID
    remittance_date: datetime
    amount: Decimal = Field(decimal_places=2)
    status: str = Field(default="PENDING", max_length=50)


class RemittanceCreate(RemittanceBase):
    pass


class Remittance(RemittanceBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    worklog_id: uuid.UUID | None = Field(
        foreign_key="worklog.id", nullable=True, ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    worklog: WorkLog | None = Relationship(back_populates="remittances")
    user: User | None = Relationship(back_populates="remittances")


class RemittancePublic(RemittanceBase):
    id: uuid.UUID
    created_at: datetime


class AdjustmentBase(SQLModel):
    worklog_id: uuid.UUID
    amount: Decimal = Field(decimal_places=2)
    reason: str | None = Field(default=None, max_length=500)


class AdjustmentCreate(AdjustmentBase):
    pass


class Adjustment(AdjustmentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    worklog_id: uuid.UUID = Field(
        foreign_key="worklog.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    worklog: WorkLog = Relationship(back_populates="adjustments")


class AdjustmentPublic(AdjustmentBase):
    id: uuid.UUID
    created_at: datetime
