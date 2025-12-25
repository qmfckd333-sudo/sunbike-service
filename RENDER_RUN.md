# 로컬 실행 (회사 PC에서 바로 실행)

## 1) 가상환경 생성/활성화
CMD 기준:
```
python -m venv .venv
.venv\Scripts\activate.bat
```

## 2) 패키지 설치
```
pip install -r requirements.txt
```

## 3) DB 생성
```
python manage.py migrate
python manage.py bootstrap_admin
```

## 4) 서버 실행
```
python manage.py runserver 0.0.0.0:8000
```

접속:
- 직원 화면: http://127.0.0.1:8000/
- 관리자: http://127.0.0.1:8000/admin/
