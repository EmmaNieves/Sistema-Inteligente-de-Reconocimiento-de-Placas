from fastapi import APIRouter
from database import get_all_alerts, resolve_alert

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/")
def list_alerts(unresolved_only: bool = False):
    return {"alerts": get_all_alerts(only_unresolved=unresolved_only)}


@router.patch("/{alert_id}/resolve")
def mark_resolved(alert_id: int):
    resolve_alert(alert_id)
    return {"ok": True, "alert_id": alert_id}


@router.get("/count")
def count_alerts():
    from database import get_all_alerts
    alerts = get_all_alerts(only_unresolved=True)
    return {"unresolved": len(alerts)}
