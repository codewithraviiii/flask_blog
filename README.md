# Flask Blogging Platform

Features: Blueprints, SQLAlchemy + Flask-Migrate, Flask-Login auth, Post/Tag CRUD (Flask-WTF),
Jinja2 templates with pagination, comments, search & tag filter, pytest tests, Gunicorn + Docker.

## Run
```
python -m venv venv
venv\Scripts\activate        # Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
flask --app run db init      # optional: migrations
python run.py
```
## Test
```
pytest
```
## Docker
```
docker build -t flask-blog .
docker run -p 8000:8000 flask-blog
```
