ls
rm dec0324fegi0e9
python manage.py flush --no-input -v 3
python manage.py makemigrations
python manage.py migrate -v 3
python manage.py migrate --run-syncdb -v 3
# email : password
# Johny.cache@gmail.com : sussPass
# Spoopy.skeleton@o2.pl : scaryPass
# Gary.theGrail@.com : holyPass
# elmohellmo@sesame-street.com : password1234
# john_cena@berkeley.edu.com : 123456789
python manage.py loaddata exemplaryData/users.json -v 3
python manage.py loaddata exemplaryData/boards.json
python manage.py loaddata exemplaryData/lists.json
python manage.py loaddata exemplaryData/cards.json