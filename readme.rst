docker compose exec api alembic revision --autogenerate -m "update user model: rename password, add age"

docker compose exec api alembic upgrade head


pip install passlib[bcrypt]
echo "passlib[bcrypt]" >> requirements.txt


deactivate