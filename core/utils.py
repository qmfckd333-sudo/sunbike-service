from datetime import date
from django.db import transaction

def generate_order_no(prefix_date: date | None = None) -> str:
    from .models import WorkOrder
    d = prefix_date or date.today()
    prefix = d.strftime("%Y%m%d")
    with transaction.atomic():
        last = (WorkOrder.objects.select_for_update()
                .filter(order_no__startswith=prefix)
                .order_by("-order_no")
                .first())
        if not last:
            return f"{prefix}-001"
        try:
            n = int(last.order_no.split("-")[-1])
        except Exception:
            n = 0
        return f"{prefix}-{n+1:03d}"
