web: gunicorn -b 0.0.0.0:$PORT leela.wsgi
scheduler: python3 manage.py scheduler
sender: python3 manage.py send_emails
cleaner: python3 manage.py clean_entries
