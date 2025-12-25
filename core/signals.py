from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from .models import WorkLabor, WorkOrder, WorkPart
from .utils import generate_order_no

@receiver(pre_save, sender=WorkOrder)
def wo_pre_save(sender, instance: WorkOrder, **kwargs):
    if not instance.order_no:
        instance.order_no = generate_order_no()

def _recalc(order: WorkOrder):
    order.recompute_totals(tax_rate=0.1)
    order.save(update_fields=["subtotal_parts","subtotal_labor","tax_amount","total_amount","updated_at"])

@receiver(post_save, sender=WorkPart)
def part_saved(sender, instance: WorkPart, **kwargs):
    _recalc(instance.work_order)

@receiver(post_delete, sender=WorkPart)
def part_deleted(sender, instance: WorkPart, **kwargs):
    _recalc(instance.work_order)

@receiver(post_save, sender=WorkLabor)
def labor_saved(sender, instance: WorkLabor, **kwargs):
    _recalc(instance.work_order)

@receiver(post_delete, sender=WorkLabor)
def labor_deleted(sender, instance: WorkLabor, **kwargs):
    _recalc(instance.work_order)
