import asyncio
from app.services import portfolio_service
from app.database import init_db

init_db()
targets = portfolio_service.list_targets("e5074d95-0e24-4ff6-be2f-b87d0dc440ba")
print("Targets for Group 2:")
print(targets)
