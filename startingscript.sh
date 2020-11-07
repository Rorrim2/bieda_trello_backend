python manage.py migrate
python manage.py migrate --run-syncdb
# email : password
# Johny.cache@gmail.com : sussPass
# Spoopy.skeleton@o2.pl : scaryPass
# Gary.theGrail@.com : holyPass
python manage.py loaddata exemplaryData/users.json
python manage.py loaddata exemplaryData/boards.json
python manage.py loaddata exemplaryData/lists.json