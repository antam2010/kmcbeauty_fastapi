docker compose exec api alembic revision --autogenerate -m "update user model: rename password, add age"

docker compose exec api alembic upgrade head


pip freeze > requirements.txt

source venv/bin/activate

deactivate