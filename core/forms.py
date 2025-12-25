from django import forms
from .models import Customer, Vehicle, WorkOrder, WorkPart, WorkLabor, Payment

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["name","phone","email","address","memo"]
        widgets = {"memo": forms.Textarea(attrs={"rows":3})}

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ["customer","plate_no","vin","make","model","year","displacement_cc","color","drive_type","notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows":3})}

class WorkOrderForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = ["branch","vehicle","status","assigned_to","in_datetime","out_datetime","odometer_in","odometer_out",
                  "customer_complaint","diagnosis","work_detail","recommendations","warranty_until","discount_amount"]
        widgets = {
            "in_datetime": forms.DateTimeInput(attrs={"type":"datetime-local"}),
            "out_datetime": forms.DateTimeInput(attrs={"type":"datetime-local"}),
            "customer_complaint": forms.Textarea(attrs={"rows":2}),
            "diagnosis": forms.Textarea(attrs={"rows":2}),
            "work_detail": forms.Textarea(attrs={"rows":3}),
            "recommendations": forms.Textarea(attrs={"rows":2}),
        }

class WorkPartForm(forms.ModelForm):
    class Meta:
        model = WorkPart
        fields = ["part_name","qty","unit_price"]

class WorkLaborForm(forms.ModelForm):
    class Meta:
        model = WorkLabor
        fields = ["labor_name","minutes","price"]

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["method","amount","paid_at","note"]
        widgets = {"paid_at": forms.DateTimeInput(attrs={"type":"datetime-local"})}
