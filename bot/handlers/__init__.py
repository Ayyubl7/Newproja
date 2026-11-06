from aiogram import Router

from . import admin, user


def build_router() -> Router:
    root = Router(name="root")
    # Admin birinchi: aks holda mijozning "fallback" handleri admin buyruqlarini ham ushlab qoladi
    root.include_router(admin.router)
    root.include_router(user.router)
    return root
