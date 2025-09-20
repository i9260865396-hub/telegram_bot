from config.settings import settings
from database import db


def add():
    for admin_id in settings.admin_ids:
        db.add_admin(admin_id)
    print("✅ Админы добавлены из settings.admin_ids")
