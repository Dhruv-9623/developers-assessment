from typing import Any

from fastapi import APIRouter, Query
from sqlmodel import Session

from app.api.deps import SessionDep
from app.api.routes.settlement.service import SettlementService
from app.models import WorkLogPublic, RemittancePublic, WorkLogsPublic
from pydantic import BaseModel

router = APIRouter(tags=["settlement"], prefix="/settlement")


class RemittanceResponse(BaseModel):
    data: list[RemittancePublic]
    count: int


@router.post("/generate-remittances-for-all-users")
def generate_remittances_for_all_users(session: SessionDep) -> RemittanceResponse:
    remittances = SettlementService.generate_remittances_for_all_users(session)
    return RemittanceResponse(data=remittances, count=len(remittances))


@router.get("/list-all-worklogs")
def list_all_worklogs(
    session: SessionDep,
    remittanceStatus: str | None = Query(None),
) -> Any:
    worklogs_data = SettlementService.list_worklogs_with_amounts(
        session, remittance_status=remittanceStatus
    )
    
    result = {
        "data": worklogs_data,
        "count": len(worklogs_data)
    }
    return result
