release: python manage.py migrate --run-syncdb
echo "migrate with --run-syncdb"
release: python manage.py migrate
echo "only migrate"
release: python manage.py loaddata exemplaryUserData
echo "loaddata"
web: gunicorn backend.wsgi --log-file