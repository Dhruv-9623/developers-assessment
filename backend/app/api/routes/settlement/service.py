from decimal import Decimal
from datetime import datetime
from sqlmodel import Session

from app import crud
from app.models import Remittance, WorkLog, RemittanceCreate


class SettlementService:
    @staticmethod
    def generate_remittances_for_all_users(session: Session) -> list[Remittance]:
        remittances = []
        users = crud.get_all_users(session=session)
        
        for user in users:
            unremitted_worklogs = crud.list_worklogs(
                session=session, remittance_status="UNREMITTED"
            )
            unremitted_for_user = [wl for wl in unremitted_worklogs if wl.user_id == user.id]
            
            if unremitted_for_user:
                total_amount: Decimal = Decimal("0.00")
                for worklog in unremitted_for_user:
                    amount = crud.get_worklog_amount(session=session, worklog_id=worklog.id)
                    total_amount += amount
                
                if total_amount > 0:
                    remittance_in = RemittanceCreate(
                        user_id=user.id,
                        remittance_date=datetime.utcnow(),
                        amount=total_amount,
                        status="COMPLETED",
                    )
                    remittance = crud.create_remittance(
                        session=session, remittance_in=remittance_in
                    )
                    remittances.append(remittance)
                    
                    for worklog in unremitted_for_user:
                        crud.update_worklog_status(
                            session=session, worklog_id=worklog.id, status="REMITTED"
                        )
        
        return remittances

    @staticmethod
    def list_worklogs_with_amounts(
        session: Session, remittance_status: str | None = None
    ) -> list[dict]:
        worklogs = crud.list_worklogs(
            session=session, remittance_status=remittance_status
        )
        
        result = []
        for worklog in worklogs:
            amount = crud.get_worklog_amount(session=session, worklog_id=worklog.id)
            result.append(
                {
                    "id": worklog.id,
                    "user_id": worklog.user_id,
                    "task_id": worklog.task_id,
                    "remittance_status": worklog.remittance_status,
                    "amount": amount,
                    "created_at": worklog.created_at,
                }
            )
        
        return result
