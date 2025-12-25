from io import BytesIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum
from django.http import FileResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from .forms import CustomerForm, VehicleForm, WorkOrderForm, WorkPartForm, WorkLaborForm, PaymentForm
from .models import Customer, Vehicle, WorkOrder, WorkPart, WorkLabor, Payment


class DashboardView(LoginRequiredMixin, ListView):
    template_name = "core/dashboard.html"
    model = WorkOrder
    context_object_name = "orders"

    def get_queryset(self):
        qs = WorkOrder.objects.select_related("vehicle","vehicle__customer","branch")
        q = self.request.GET.get("q","").strip()
        if q:
            qs = qs.filter(
                Q(order_no__icontains=q)|
                Q(vehicle__plate_no__icontains=q)|
                Q(vehicle__model__icontains=q)|
                Q(vehicle__customer__phone__icontains=q)|
                Q(vehicle__customer__name__icontains=q)
            )
        return qs.order_by("-in_datetime","-id")


class CustomerCreateView(LoginRequiredMixin, CreateView):
    template_name = "core/form.html"
    model = Customer
    form_class = CustomerForm
    def get_success_url(self):
        return reverse("dashboard")


class VehicleCreateView(LoginRequiredMixin, CreateView):
    template_name = "core/form.html"
    model = Vehicle
    form_class = VehicleForm
    def get_success_url(self):
        return reverse("dashboard")


class WorkOrderCreateView(LoginRequiredMixin, CreateView):
    template_name = "core/form.html"
    model = WorkOrder
    form_class = WorkOrderForm
    def get_initial(self):
        initial = super().get_initial()
        initial.setdefault("in_datetime", timezone.now())
        return initial
    def get_success_url(self):
        return reverse("workorder_detail", kwargs={"pk": self.object.pk})


class WorkOrderDetailView(LoginRequiredMixin, DetailView):
    template_name = "core/workorder_detail.html"
    model = WorkOrder
    context_object_name = "order"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["part_form"] = WorkPartForm()
        ctx["labor_form"] = WorkLaborForm()
        ctx["payment_form"] = PaymentForm(initial={"paid_at": timezone.now()})
        ctx["payments_total"] = self.object.payments.aggregate(t=Sum("amount"))["t"] or 0
        return ctx


@login_required
def add_part(request: HttpRequest, pk: int) -> HttpResponse:
    order = get_object_or_404(WorkOrder, pk=pk)
    form = WorkPartForm(request.POST)
    if form.is_valid():
        p = form.save(commit=False); p.work_order = order; p.save()
        messages.success(request, "부품이 추가되었습니다.")
    else:
        messages.error(request, "부품 입력을 확인해주세요.")
    return redirect("workorder_detail", pk=pk)


@login_required
def add_labor(request: HttpRequest, pk: int) -> HttpResponse:
    order = get_object_or_404(WorkOrder, pk=pk)
    form = WorkLaborForm(request.POST)
    if form.is_valid():
        l = form.save(commit=False); l.work_order = order; l.save()
        messages.success(request, "공임이 추가되었습니다.")
    else:
        messages.error(request, "공임 입력을 확인해주세요.")
    return redirect("workorder_detail", pk=pk)


@login_required
def add_payment(request: HttpRequest, pk: int) -> HttpResponse:
    order = get_object_or_404(WorkOrder, pk=pk)
    form = PaymentForm(request.POST)
    if form.is_valid():
        pay = form.save(commit=False); pay.work_order = order; pay.save()
        messages.success(request, "결제가 추가되었습니다.")
    else:
        messages.error(request, "결제 입력을 확인해주세요.")
    return redirect("workorder_detail", pk=pk)



@login_required
def invoice_pdf(request: HttpRequest, pk: int) -> HttpResponse:
    """견적서/정비명세서 PDF (썬바이크 흑백 + 로고)"""
    order = get_object_or_404(WorkOrder.objects.select_related("vehicle","vehicle__customer","branch"), pk=pk)

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    W, H = A4

    # --- Font: try Korean (Windows: Malgun Gothic), fallback to Helvetica ---
    font_name = "Helvetica"
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        # common Windows font path
        candidates = [
            r"C:\\Windows\\Fonts\\malgun.ttf",
            r"C:\\Windows\\Fonts\\malgunsl.ttf",
        ]
        for fp in candidates:
            import os
            if os.path.exists(fp):
                pdfmetrics.registerFont(TTFont("MalgunGothic", fp))
                font_name = "MalgunGothic"
                break
    except Exception:
        font_name = "Helvetica"

    # --- Header (logo + title) ---
    from django.conf import settings
    logo_paths = [
        settings.BASE_DIR / "static" / "core" / "logo.jpg",
        settings.BASE_DIR / "static" / "core" / "logo.png",
    ]
    logo_path = next((p for p in logo_paths if p.exists()), None)

    top_y = H - 18*mm
    if logo_path:
        try:
            # draw logo (fit height 14mm)
            c.drawImage(str(logo_path), 20*mm, H-28*mm, height=14*mm, width=14*mm, mask='auto')
        except Exception:
            pass

    c.setFillColorRGB(0, 0, 0)
    c.setFont(font_name, 16)
    c.drawString(36*mm, top_y, "썬바이크 정비 견적/명세서")

    c.setFont(font_name, 10)
    c.drawRightString(190*mm, H-22*mm, f"발행일: {timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M')}")

    # --- Basic info box ---
    cust = order.vehicle.customer
    ident = order.vehicle.plate_no or order.vehicle.vin or "-"
    y = H - 36*mm
    c.setLineWidth(0.8)
    c.rect(20*mm, y-26*mm, 170*mm, 26*mm)  # box

    c.setFont(font_name, 10)
    c.drawString(24*mm, y-8*mm, f"접수번호: {order.order_no}")
    c.drawString(24*mm, y-14*mm, f"센터: {order.branch.name}")
    c.drawString(24*mm, y-20*mm, f"고객: {cust.name}  /  {cust.phone}")
    c.drawString(110*mm, y-8*mm, f"차량: {order.vehicle.model}")
    c.drawString(110*mm, y-14*mm, f"식별: {ident}")
    c.drawString(110*mm, y-20*mm, f"입고 주행거리: {order.odometer_in or '-'}")

    # --- Sections ---
    y = y - 36*mm

    def section_title(txt):
        nonlocal y
        c.setFont(font_name, 11)
        c.drawString(20*mm, y, txt)
        y -= 4*mm
        c.setLineWidth(0.6)
        c.line(20*mm, y, 190*mm, y)
        y -= 8*mm

    def table_header(cols):
        nonlocal y
        c.setFont(font_name, 9)
        for (x, label, align) in cols:
            if align == "R":
                c.drawRightString(x, y, label)
            else:
                c.drawString(x, y, label)
        y -= 3*mm
        c.line(20*mm, y, 190*mm, y)
        y -= 6*mm

    # Parts
    section_title("부품/소모품")
    table_header([
        (20*mm, "품목", "L"),
        (120*mm, "수량", "R"),
        (155*mm, "단가", "R"),
        (190*mm, "금액", "R"),
    ])
    c.setFont(font_name, 9)
    for p in order.parts.all():
        if y < 35*mm:
            c.showPage()
            y = H - 20*mm
        c.drawString(20*mm, y, str(p.part_name)[:34])
        c.drawRightString(120*mm, y, str(p.qty))
        c.drawRightString(155*mm, y, f"{int(p.unit_price):,}")
        c.drawRightString(190*mm, y, f"{int(p.line_total):,}")
        y -= 6*mm

    # Labor
    y -= 4*mm
    section_title("공임")
    table_header([
        (20*mm, "항목", "L"),
        (190*mm, "금액", "R"),
    ])
    c.setFont(font_name, 9)
    for l in order.labor.all():
        if y < 35*mm:
            c.showPage()
            y = H - 20*mm
        c.drawString(20*mm, y, str(l.labor_name)[:40])
        c.drawRightString(190*mm, y, f"{int(l.price):,}")
        y -= 6*mm

    # Totals (black/white)
    y -= 8*mm
    c.setLineWidth(0.8)
    c.rect(110*mm, y-28*mm, 80*mm, 28*mm)
    c.setFont(font_name, 10)
    c.drawString(114*mm, y-8*mm, "부품 소계")
    c.drawRightString(188*mm, y-8*mm, f"{int(order.subtotal_parts):,} 원")
    c.drawString(114*mm, y-14*mm, "공임 소계")
    c.drawRightString(188*mm, y-14*mm, f"{int(order.subtotal_labor):,} 원")
    c.drawString(114*mm, y-20*mm, "부가세")
    c.drawRightString(188*mm, y-20*mm, f"{int(order.tax_amount):,} 원")
    c.setFont(font_name, 12)
    c.drawString(114*mm, y-26*mm, "총액")
    c.drawRightString(188*mm, y-26*mm, f"{int(order.total_amount):,} 원")

    # Notes
    y = min(y-38*mm, 60*mm)
    c.setFont(font_name, 9)
    c.drawString(20*mm, y, "비고:")
    c.setFont(font_name, 9)
    note = (order.recommendations or "").strip() or "—"
    c.drawString(30*mm, y, note[:90])

    c.showPage()
    c.save()
    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename=f"sunbike_{order.order_no}.pdf")

