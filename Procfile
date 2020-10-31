release: python manage.py makemigrations
release: echo "makemigrations"
release: python manage.py migrate --run-syncdb
release: echo "migrate with --run-syncdb"
release: python manage.py migrate
release: echo "only migrate"
release: python manage.py loaddata exemplaryUserData
release: echo "loaddata"
web: gunicorn backend.wsgi --log-file