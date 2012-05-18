teammaia_fbhack
===============

pip install django
django-admin.py startproject --template https://digitalinc@github.com/digitalinc/django_project_template/zipball/master supertrunfo
cd supertrunfo
pip install -r requirements.txt
pip install -e git+git@github.com:digitalinc/django-fukinbook.git#egg=django_fukinbook
python manage.py syncdb
python manage.py runserver
