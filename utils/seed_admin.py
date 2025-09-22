from config.settings import settings
from database.sqlite_utils import add_admin


def add():
    for admin_id in settings.admin_ids:
        add_admin(admin_id)
    print("✅ Админы добавлены из settings.admin_ids")
