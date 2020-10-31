release: python manage.py makemigrations
release: python manage.py migrate --run-syncdb
release: python manage.py migrate
release: python manage.py loaddata exemplaryUserData
web: gunicorn backend.wsgi --log-file