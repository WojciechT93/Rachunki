Clone project from Github and setup instructions:

git clone git@github.com:WojciechT93/Rachunki.git

In the "Rachunki" folder run:

python3 -m venv env

source env/bin/activate

pip install -r requirements.txt

python manage.py makemigrations

python manage.py migrate

python manage.py createsuperuser --email example@example.example --username admin