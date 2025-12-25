# Moto Service Center Prototype (Django)

- 고객/차량/작업오더 기반 정비 기록
- 부품/공임/결제 입력
- 견적서/정비명세서 PDF 출력(ReportLab)

## 실행
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

- 접속: http://127.0.0.1:8000
- Admin: http://127.0.0.1:8000/admin


## 썬바이크 커스텀
- 로고: static/core/logo.jpg
- 테마: 흑백(black & white)
- PDF: 로고 포함 견적/명세서
