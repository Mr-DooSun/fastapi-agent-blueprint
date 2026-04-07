from nicegui import app, ui

from src._core.config import settings


class AdminAuthProvider:
    """Simple env-var based authentication.

    Swap to JWT by implementing the same interface.
    """

    @staticmethod
    def authenticate(username: str, password: str) -> bool:
        return username == settings.admin_id and password == settings.admin_password

    @staticmethod
    def is_authenticated() -> bool:
        return app.storage.user.get("authenticated", False)

    @staticmethod
    def login(username: str) -> None:
        app.storage.user["authenticated"] = True
        app.storage.user["username"] = username

    @staticmethod
    def logout() -> None:
        app.storage.user["authenticated"] = False
        app.storage.user.pop("username", None)


def require_auth() -> bool:
    """Guard function. Call at the top of every admin page.

    Returns False and redirects to login if not authenticated.
    """
    if not AdminAuthProvider.is_authenticated():
        ui.navigate.to("/admin/login")
        return False
    return True
