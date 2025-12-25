
from django.contrib import admin
from .models import Branch, Customer, Vehicle, WorkOrder, WorkPart, WorkLabor, Payment

admin.site.site_header = "썬바이크 정비센터 관리자"
admin.site.site_title = "썬바이크 관리자"
admin.site.index_title = "관리 메뉴"

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name","phone","address","created_at")
    search_fields = ("name","phone","address")

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name","phone","email","created_at")
    search_fields = ("name","phone","email")

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("model","plate_no","vin","customer","created_at")
    search_fields = ("model","plate_no","vin","customer__name","customer__phone")

@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ("order_no","status","branch","vehicle","in_datetime","total_amount")
    search_fields = ("order_no","vehicle__model","vehicle__plate_no","vehicle__customer__name","vehicle__customer__phone")
    list_filter = ("status","branch")

admin.site.register(WorkPart)
admin.site.register(WorkLabor)
admin.site.register(Payment)
