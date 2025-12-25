
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.utils import timezone


class Branch(models.Model):
    name = models.CharField("센터명", max_length=120)
    phone = models.CharField("전화번호", max_length=40, blank=True)
    address = models.CharField("주소", max_length=255, blank=True)
    created_at = models.DateTimeField("생성일", auto_now_add=True)

    class Meta:
        verbose_name = "지점(센터)"
        verbose_name_plural = "지점(센터)"

    def __str__(self) -> str:
        return self.name


class Customer(models.Model):
    name = models.CharField("고객명", max_length=80)
    phone = models.CharField("전화번호", max_length=40, db_index=True)
    email = models.EmailField("이메일", blank=True)
    address = models.CharField("주소", max_length=255, blank=True)
    memo = models.TextField("메모", blank=True)
    created_at = models.DateTimeField("등록일", auto_now_add=True)
    updated_at = models.DateTimeField("수정일", auto_now=True)

    class Meta:
        verbose_name = "고객"
        verbose_name_plural = "고객"
        indexes = [models.Index(fields=["phone", "name"])]

    def __str__(self) -> str:
        return f"{self.name} ({self.phone})"


class Vehicle(models.Model):
    class DriveType(models.TextChoices):
        CHAIN = "CHAIN", "체인"
        BELT = "BELT", "벨트"
        SHAFT = "SHAFT", "샤프트"
        OTHER = "OTHER", "기타"

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="vehicles", verbose_name="고객")
    plate_no = models.CharField("번호판", max_length=32, blank=True, db_index=True)
    vin = models.CharField("차대번호(VIN)", max_length=64, blank=True, db_index=True)
    make = models.CharField("제조사", max_length=80, blank=True)
    model = models.CharField("차량 모델", max_length=120)
    year = models.PositiveIntegerField("연식", null=True, blank=True)
    displacement_cc = models.PositiveIntegerField("배기량(cc)", null=True, blank=True)
    color = models.CharField("색상", max_length=40, blank=True)
    drive_type = models.CharField("구동 방식", max_length=16, choices=DriveType.choices, default=DriveType.CHAIN)
    notes = models.TextField("비고", blank=True)
    created_at = models.DateTimeField("등록일", auto_now_add=True)

    class Meta:
        verbose_name = "차량"
        verbose_name_plural = "차량"
        indexes = [
            models.Index(fields=["plate_no"]),
            models.Index(fields=["vin"]),
            models.Index(fields=["model"]),
        ]

    def __str__(self) -> str:
        ident = self.plate_no or self.vin or "미등록"
        return f"{self.model} ({ident})"


class WorkOrder(models.Model):
    class Status(models.TextChoices):
        RECEIVED = "RECEIVED", "접수"
        IN_PROGRESS = "IN_PROGRESS", "작업중"
        WAITING_PARTS = "WAITING_PARTS", "부품대기"
        DONE = "DONE", "완료"
        RELEASED = "RELEASED", "출고"
        CANCELED = "CANCELED", "취소"

    order_no = models.CharField("접수번호", max_length=32, unique=True, db_index=True)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="work_orders", verbose_name="지점(센터)")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name="work_orders", verbose_name="차량")
    status = models.CharField("상태", max_length=20, choices=Status.choices, default=Status.RECEIVED)
    in_datetime = models.DateTimeField("입고일시", default=timezone.now)
    out_datetime = models.DateTimeField("출고일시", null=True, blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_work_orders",
        verbose_name="담당자",
    )
    odometer_in = models.PositiveIntegerField("입고 주행거리", null=True, blank=True)
    odometer_out = models.PositiveIntegerField("출고 주행거리", null=True, blank=True)
    customer_complaint = models.TextField("고객요청(증상)", blank=True)
    diagnosis = models.TextField("진단", blank=True)
    work_detail = models.TextField("작업내용", blank=True)
    recommendations = models.TextField("권장사항", blank=True)
    warranty_until = models.DateField("보증기한", null=True, blank=True)

    subtotal_parts = models.DecimalField("부품 소계", max_digits=12, decimal_places=0, default=0)
    subtotal_labor = models.DecimalField("공임 소계", max_digits=12, decimal_places=0, default=0)
    discount_amount = models.DecimalField("할인", max_digits=12, decimal_places=0, default=0)
    tax_amount = models.DecimalField("부가세", max_digits=12, decimal_places=0, default=0)
    total_amount = models.DecimalField("총액", max_digits=12, decimal_places=0, default=0)

    created_at = models.DateTimeField("생성일", auto_now_add=True)
    updated_at = models.DateTimeField("수정일", auto_now=True)

    class Meta:
        verbose_name = "작업오더(접수)"
        verbose_name_plural = "작업오더(접수)"
        ordering = ["-in_datetime", "-id"]

    def __str__(self) -> str:
        return self.order_no

    def recompute_totals(self, tax_rate: float = 0.1) -> None:
        parts_total = int(self.parts.aggregate(t=Sum("line_total"))["t"] or 0)
        labor_total = int(self.labor.aggregate(t=Sum("price"))["t"] or 0)
        discount = int(self.discount_amount or 0)
        taxable = max(0, parts_total + labor_total - discount)
        tax = int(round(taxable * tax_rate))
        self.subtotal_parts = parts_total
        self.subtotal_labor = labor_total
        self.tax_amount = tax
        self.total_amount = taxable + tax


class WorkPart(models.Model):
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name="parts", verbose_name="작업오더")
    part_name = models.CharField("부품/소모품명", max_length=160)
    qty = models.DecimalField("수량", max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField("단가", max_digits=12, decimal_places=0, default=0)
    line_total = models.DecimalField("금액", max_digits=12, decimal_places=0, default=0)

    class Meta:
        verbose_name = "작업 부품"
        verbose_name_plural = "작업 부품"

    def save(self, *args, **kwargs):
        self.line_total = int(round(float(self.qty) * float(self.unit_price)))
        super().save(*args, **kwargs)


class WorkLabor(models.Model):
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name="labor", verbose_name="작업오더")
    labor_name = models.CharField("공임 항목", max_length=160)
    minutes = models.PositiveIntegerField("시간(분)", null=True, blank=True)
    price = models.DecimalField("금액", max_digits=12, decimal_places=0, default=0)

    class Meta:
        verbose_name = "작업 공임"
        verbose_name_plural = "작업 공임"


class Payment(models.Model):
    class Method(models.TextChoices):
        CARD = "CARD", "카드"
        CASH = "CASH", "현금"
        TRANSFER = "TRANSFER", "계좌이체"
        OTHER = "OTHER", "기타"

    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name="payments", verbose_name="작업오더")
    method = models.CharField("결제수단", max_length=16, choices=Method.choices)
    amount = models.DecimalField("금액", max_digits=12, decimal_places=0, default=0)
    paid_at = models.DateTimeField("결제일시", default=timezone.now)
    note = models.CharField("비고", max_length=255, blank=True)

    class Meta:
        verbose_name = "결제"
        verbose_name_plural = "결제"
