import uuid
from typing import Any
from decimal import Decimal

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import (
    Item,
    ItemCreate,
    User,
    UserCreate,
    UserUpdate,
    WorkLog,
    WorkLogCreate,
    TimeSegment,
    TimeSegmentCreate,
    Remittance,
    RemittanceCreate,
    Adjustment,
    AdjustmentCreate,
)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def create_worklog(
    *, session: Session, worklog_in: WorkLogCreate
) -> WorkLog:
    db_worklog = WorkLog.model_validate(worklog_in)
    session.add(db_worklog)
    session.commit()
    session.refresh(db_worklog)
    return db_worklog


def get_worklog(*, session: Session, worklog_id: uuid.UUID) -> WorkLog | None:
    statement = select(WorkLog).where(WorkLog.id == worklog_id)
    return session.exec(statement).first()


def list_worklogs(
    *, session: Session, remittance_status: str | None = None
) -> list[WorkLog]:
    statement = select(WorkLog)
    if remittance_status:
        statement = statement.where(WorkLog.remittance_status == remittance_status)
    return session.exec(statement).all()


def update_worklog_status(
    *, session: Session, worklog_id: uuid.UUID, status: str
) -> WorkLog | None:
    worklog = get_worklog(session=session, worklog_id=worklog_id)
    if not worklog:
        return None
    worklog.remittance_status = status
    session.add(worklog)
    session.commit()
    session.refresh(worklog)
    return worklog


def create_time_segment(
    *, session: Session, segment_in: TimeSegmentCreate
) -> TimeSegment:
    db_segment = TimeSegment.model_validate(segment_in)
    session.add(db_segment)
    session.commit()
    session.refresh(db_segment)
    return db_segment


def get_time_segments_for_worklog(
    *, session: Session, worklog_id: uuid.UUID
) -> list[TimeSegment]:
    statement = select(TimeSegment).where(
        (TimeSegment.worklog_id == worklog_id) & (TimeSegment.is_deleted == False)
    )
    return session.exec(statement).all()


def get_worklog_amount(*, session: Session, worklog_id: uuid.UUID) -> Decimal:
    segments = get_time_segments_for_worklog(session=session, worklog_id=worklog_id)
    total: Decimal = Decimal("0.00")
    for segment in segments:
        total += segment.amount
    
    adjustments = session.exec(
        select(Adjustment).where(Adjustment.worklog_id == worklog_id)
    ).all()
    for adjustment in adjustments:
        total += adjustment.amount
    
    return total


def create_remittance(
    *, session: Session, remittance_in: RemittanceCreate
) -> Remittance:
    db_remittance = Remittance.model_validate(remittance_in)
    session.add(db_remittance)
    session.commit()
    session.refresh(db_remittance)
    return db_remittance


def create_adjustment(
    *, session: Session, adjustment_in: AdjustmentCreate
) -> Adjustment:
    db_adjustment = Adjustment.model_validate(adjustment_in)
    session.add(db_adjustment)
    session.commit()
    session.refresh(db_adjustment)
    return db_adjustment


def get_all_users(*, session: Session) -> list[User]:
    statement = select(User)
    return session.exec(statement).all()
