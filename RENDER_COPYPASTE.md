# Render 설정값 (복붙용) - 썬바이크

## 1) Web Service (Django) 생성
- Environment: **Python**
- Build Command:
```
pip install -r requirements.txt && python manage.py collectstatic --noinput
```
- Start Command:
```
python manage.py migrate && python manage.py bootstrap_admin && gunicorn motosvc.wsgi:application --bind 0.0.0.0:$PORT
```

## 2) Environment Variables (Web Service)
아래를 Render → Web Service → Environment Variables에 추가하세요.

- `DJANGO_SECRET_KEY` : (긴 랜덤 문자열)
- `DJANGO_DEBUG` : `0`
- `DJANGO_ALLOWED_HOSTS` : `sunbike-service.onrender.com,sunbike.shop,www.sunbike.shop`
- `DATABASE_URL` : (Render Postgres의 Internal Database URL 그대로 붙여넣기)
- `STATIC_URL` : `https://sunbike-static.onrender.com/`

## 3) Static Site (정적파일) 생성
Static Site의 Publish Directory는 Web Service 빌드 결과인 `staticfiles`를 사용합니다.
- Publish Directory: `staticfiles`

> Static Site는 GitHub 저장소를 같이 쓰도록 만들고,
> Build Command는 비워두거나 아래처럼 설정하세요:
```
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

## 4) 관리자 계정 자동 생성
Start Command에 포함된 `python manage.py bootstrap_admin`가
최초 1회 아래 계정을 자동 생성합니다 (없으면 생성, 있으면 스킵).
- 아이디: `admin`
- 비번: `admin1234`
배포 후 꼭 바꾸세요.
