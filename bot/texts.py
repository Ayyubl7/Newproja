"""Botdagi barcha matnlar (o'zbekcha / ruscha)."""
from __future__ import annotations

LANGS = ("uz", "ru")
ADMIN_PANEL_BUTTON = "🛠 Admin panel"

TEXTS: dict[str, dict[str, str]] = {
    "uz": {
        "choose_lang": "🇺🇿 Tilni tanlang\n🇷🇺 Выберите язык",
        "welcome": (
            "Assalomu alaykum, {name}! 👋\n\n"
            "<b>{store}</b>ga xush kelibsiz 🍔\n"
            "{tagline}.\n\n"
            "Buyurtma berish uchun <b>«🍔 Menyuni ochish»</b> tugmasini bosing."
        ),
        "ask_phone": (
            "📱 Buyurtma bo'yicha siz bilan bog'lanishimiz uchun telefon raqamingizni yuboring.\n\n"
            "Pastdagi <b>«📱 Raqamni yuborish»</b> tugmasini bosing 👇"
        ),
        "btn_share_phone": "📱 Raqamni yuborish",
        "phone_saved": "✅ Raqamingiz saqlandi.",
        "phone_not_own": "Iltimos, o'zingizning raqamingizni pastdagi tugma orqali yuboring.",
        "btn_order": "🍔 Buyurtma berish",
        "btn_my_orders": "📦 Buyurtmalarim",
        "btn_about": "ℹ️ Biz haqimizda",
        "btn_contacts": "📞 Aloqa",
        "btn_settings": "⚙️ Sozlamalar",
        "open_menu": "Menyuni ochish uchun tugmani bosing 👇",
        "btn_open_menu": "🍔 Menyuni ochish",
        "menu_button": "Menyu",
        "closed_now": "😴 Hozir yopiqmiz. Ish vaqti: <b>{open}–{close}</b>.\nMenyuni ko'rishingiz mumkin, buyurtmalar ish vaqtida qabul qilinadi.",
        "paused_now": "⏸ Hozir buyurtmalar vaqtincha qabul qilinmayapti. Menyuni ko'rishingiz mumkin.",
        "no_orders": "Sizda hali buyurtmalar yo'q. Birinchisini hoziroq bering! 🍔",
        "my_orders_title": "📦 <b>Oxirgi buyurtmalaringiz</b>",
        "about": "🍔 <b>{store}</b>\n\n{about}\n\n🕒 Ish vaqti: <b>{open}–{close}</b>\n📍 Manzil: {address}",
        "contacts": "📞 <b>Biz bilan bog'lanish</b>\n\nTelefon: {phone}",
        "contacts_tg": "\nTelegram: @{username}",
        "contacts_ig": "\nInstagram: instagram.com/{instagram}",
        "settings": "⚙️ <b>Sozlamalar</b>\n\nTil: O'zbekcha\nTelefon: {phone}",
        "btn_change_lang": "🌐 Tilni o'zgartirish",
        "btn_change_phone": "📱 Raqamni o'zgartirish",
        "lang_saved": "✅ Til o'zgartirildi.",
        "unknown": "Quyidagi menyudan tanlang 👇",
        "not_set": "kiritilmagan",
        # buyurtma
        "order_created": (
            "✅ <b>Buyurtma #{id} qabul qilindi!</b>\n\n{items}\n\n"
            "{summary}\n"
            "💵 To'lov: {payment}\n{where}\n\n"
            "Operatorimiz tez orada buyurtmani tasdiqlaydi. Holati o'zgarsa, shu yerda xabar beramiz."
        ),
        "where_delivery": "🚚 Yetkazib berish: {address}",
        "where_pickup": "🛍 Olib ketish: {address}",
        "sum_items": "Mahsulotlar: {v}",
        "sum_delivery": "Yetkazib berish: {v}",
        "sum_free": "bepul",
        "sum_total": "<b>Jami: {v}</b>",
        "type_delivery": "Yetkazib berish",
        "type_pickup": "Olib ketish",
        "pay_cash": "Naqd pul",
        "pay_click": "Click",
        "pay_payme": "Payme",
        "st_new": "🆕 Yangi",
        "st_accepted": "👨‍🍳 Tayyorlanmoqda",
        "st_on_the_way": "🚗 Yo'lda",
        "st_ready": "🛍 Olib ketishga tayyor",
        "st_done": "✅ Yakunlandi",
        "st_cancelled": "❌ Bekor qilingan",
        "notify_accepted": "👨‍🍳 Buyurtma <b>#{id}</b> tasdiqlandi va tayyorlanmoqda!",
        "notify_on_the_way": "🚗 Buyurtma <b>#{id}</b> yo'lda! Kuryer tez orada yetib boradi.",
        "notify_ready": "🛍 Buyurtma <b>#{id}</b> tayyor! Uni olib ketishingiz mumkin:\n📍 {address}",
        "notify_done": "✅ Buyurtma <b>#{id}</b> yakunlandi. Yoqimli ishtaha! Bizni tanlaganingiz uchun rahmat 💛",
        "notify_cancelled": "❌ Buyurtma <b>#{id}</b> bekor qilindi. Savollaringiz bo'lsa, qo'ng'iroq qiling: {phone}",
        "pcs": "ta",
    },
    "ru": {
        "choose_lang": "🇺🇿 Tilni tanlang\n🇷🇺 Выберите язык",
        "welcome": (
            "Здравствуйте, {name}! 👋\n\n"
            "Добро пожаловать в <b>{store}</b> 🍔\n"
            "{tagline}.\n\n"
            "Чтобы сделать заказ, нажмите <b>«🍔 Открыть меню»</b>."
        ),
        "ask_phone": (
            "📱 Отправьте номер телефона, чтобы мы могли связаться с вами по заказу.\n\n"
            "Нажмите кнопку <b>«📱 Отправить номер»</b> ниже 👇"
        ),
        "btn_share_phone": "📱 Отправить номер",
        "phone_saved": "✅ Номер сохранён.",
        "phone_not_own": "Пожалуйста, отправьте свой номер кнопкой ниже.",
        "btn_order": "🍔 Заказать",
        "btn_my_orders": "📦 Мои заказы",
        "btn_about": "ℹ️ О нас",
        "btn_contacts": "📞 Контакты",
        "btn_settings": "⚙️ Настройки",
        "open_menu": "Нажмите кнопку, чтобы открыть меню 👇",
        "btn_open_menu": "🍔 Открыть меню",
        "menu_button": "Меню",
        "closed_now": "😴 Сейчас мы закрыты. Время работы: <b>{open}–{close}</b>.\nМеню можно посмотреть, заказы принимаем в рабочее время.",
        "paused_now": "⏸ Сейчас заказы временно не принимаются. Меню можно посмотреть.",
        "no_orders": "У вас пока нет заказов. Сделайте первый прямо сейчас! 🍔",
        "my_orders_title": "📦 <b>Ваши последние заказы</b>",
        "about": "🍔 <b>{store}</b>\n\n{about}\n\n🕒 Время работы: <b>{open}–{close}</b>\n📍 Адрес: {address}",
        "contacts": "📞 <b>Связаться с нами</b>\n\nТелефон: {phone}",
        "contacts_tg": "\nTelegram: @{username}",
        "contacts_ig": "\nInstagram: instagram.com/{instagram}",
        "settings": "⚙️ <b>Настройки</b>\n\nЯзык: Русский\nТелефон: {phone}",
        "btn_change_lang": "🌐 Сменить язык",
        "btn_change_phone": "📱 Сменить номер",
        "lang_saved": "✅ Язык изменён.",
        "unknown": "Выберите в меню ниже 👇",
        "not_set": "не указан",
        "order_created": (
            "✅ <b>Заказ #{id} принят!</b>\n\n{items}\n\n"
            "{summary}\n"
            "💵 Оплата: {payment}\n{where}\n\n"
            "Оператор скоро подтвердит заказ. Об изменениях статуса сообщим здесь."
        ),
        "where_delivery": "🚚 Доставка: {address}",
        "where_pickup": "🛍 Самовывоз: {address}",
        "sum_items": "Товары: {v}",
        "sum_delivery": "Доставка: {v}",
        "sum_free": "бесплатно",
        "sum_total": "<b>Итого: {v}</b>",
        "type_delivery": "Доставка",
        "type_pickup": "Самовывоз",
        "pay_cash": "Наличные",
        "pay_click": "Click",
        "pay_payme": "Payme",
        "st_new": "🆕 Новый",
        "st_accepted": "👨‍🍳 Готовится",
        "st_on_the_way": "🚗 В пути",
        "st_ready": "🛍 Готов к выдаче",
        "st_done": "✅ Завершён",
        "st_cancelled": "❌ Отменён",
        "notify_accepted": "👨‍🍳 Заказ <b>#{id}</b> подтверждён и уже готовится!",
        "notify_on_the_way": "🚗 Заказ <b>#{id}</b> в пути! Курьер скоро будет у вас.",
        "notify_ready": "🛍 Заказ <b>#{id}</b> готов! Забрать можно здесь:\n📍 {address}",
        "notify_done": "✅ Заказ <b>#{id}</b> завершён. Приятного аппетита! Спасибо, что выбрали нас 💛",
        "notify_cancelled": "❌ Заказ <b>#{id}</b> отменён. Если есть вопросы, позвоните: {phone}",
        "pcs": "шт",
    },
}

# Admin guruhidagi matnlar
ADMIN_TEXTS: dict[str, dict[str, str]] = {
    "uz": {
        "new_order": "🆕 <b>Yangi buyurtma #{id}</b>",
        "order_title": "🧾 <b>Buyurtma #{id}</b>",
        "customer": "👤 Mijoz: {name}",
        "phone": "📞 Telefon: {phone}",
        "type": "🚚 Turi: {type}",
        "address": "📍 Manzil: {address}",
        "map": "🗺 Xarita: {links}",
        "comment": "💬 Izoh: {comment}",
        "payment": "💵 To'lov: {payment}",
        "status": "Holat: <b>{status}</b>",
        "changed_by": "({by}, {time})",
        "btn_accept": "✅ Qabul qilish",
        "btn_cancel": "❌ Bekor qilish",
        "btn_on_the_way": "🚗 Yo'lga chiqdi",
        "btn_ready": "🛍 Tayyor",
        "btn_done": "🏁 Yakunlash",
        "btn_confirm_cancel": "Ha, bekor qilinsin",
        "btn_back": "« Orqaga",
        "confirm_cancel": "Buyurtma #{id} bekor qilinsinmi?",
        "status_changed": "Holat o'zgardi: {status}",
        "status_stale": "Bu buyurtma holati allaqachon o'zgargan.",
        "not_admin": "Bu amal faqat adminlar uchun.",
        "stoplist_title": "⛔ <b>Stop-list</b>\nKategoriyani tanlang. ⛔ belgili mahsulotlar menyuda «tugagan» bo'lib ko'rinadi.",
        "stoplist_cat": "<b>{cat}</b>\nMahsulotni bosib, sotuvda bor/yo'qligini almashtiring.",
        "stats": (
            "📊 <b>Statistika</b>\n\n"
            "<b>Bugun:</b> {t_total} ta buyurtma, {t_done} ta yakunlangan, {t_cancelled} ta bekor\n"
            "Tushum: <b>{t_revenue}</b>\n\n"
            "<b>Oxirgi 7 kun:</b> {w_total} ta buyurtma, {w_done} ta yakunlangan\n"
            "Tushum: <b>{w_revenue}</b>\n\n"
            "Hozir faol buyurtmalar: <b>{active}</b>\n"
            "Bot foydalanuvchilari: <b>{users}</b>"
        ),
        "active_none": "Faol buyurtmalar yo'q 👌",
        "active_title": "📋 <b>Faol buyurtmalar</b>",
        "panel_text": (
            "🛠 <b>Admin panel</b>\n\n"
            "Menyu, rasmlar, narxlar, aksiyalar, buyurtmalar, statistika va sozlamalar.\n\n"
            "📱 Telefonda — «Panelni ochish».\n"
            "💻 Kompyuterda — «Kompyuterda ochish» (havola 10 daqiqa amal qiladi va bir marta ishlaydi)."
        ),
        "panel_open": "🛠 Panelni ochish",
        "panel_desktop": "💻 Kompyuterda ochish",
        "panel_private_only": "Admin panel botning shaxsiy chatida ochiladi 👇",
        "panel_no_access": (
            "Sizda admin panelga ruxsat yo'q.\n\nSizning Telegram ID: <code>{user_id}</code>\n"
            "Egasi sizni panel → Sozlamalar → Adminlar bo'limida qo'shishi mumkin."
        ),
        "panel_no_https": "⚠️ PUBLIC_URL (https) sozlanmagan — panel ochilmaydi.",
        "broadcast_running": "📣 Hozir boshqa xabar yuborilmoqda, tugashini kuting.",
        "broadcast_help": "Reklama yuborish: kerakli xabarga (matn/rasm/video) <b>javob (reply)</b> qilib /broadcast yozing.",
        "broadcast_start": "📣 {count} ta foydalanuvchiga yuborilmoqda...",
        "broadcast_done": "📣 Tugadi: {ok} ta yuborildi, {fail} ta yetib bormadi (botni bloklagan).",
        "chat_id": "Bu chat ID: <code>{chat_id}</code>\nSizning ID: <code>{user_id}</code>",
        "admin_help": (
            "🛠 <b>Admin buyruqlari</b>\n\n"
            "/panel — admin panel (menyu, aksiyalar, sozlamalar)\n"
            "/active — faol buyurtmalar\n"
            "/stats — statistika\n"
            "/stoplist — mahsulotni vaqtincha o'chirish/yoqish\n"
            "/broadcast — reklama yuborish (xabarga reply qilib)\n"
            "/id — chat ID ni bilish"
        ),
    },
    "ru": {
        "new_order": "🆕 <b>Новый заказ #{id}</b>",
        "order_title": "🧾 <b>Заказ #{id}</b>",
        "customer": "👤 Клиент: {name}",
        "phone": "📞 Телефон: {phone}",
        "type": "🚚 Тип: {type}",
        "address": "📍 Адрес: {address}",
        "map": "🗺 Карта: {links}",
        "comment": "💬 Комментарий: {comment}",
        "payment": "💵 Оплата: {payment}",
        "status": "Статус: <b>{status}</b>",
        "changed_by": "({by}, {time})",
        "btn_accept": "✅ Принять",
        "btn_cancel": "❌ Отменить",
        "btn_on_the_way": "🚗 Отправлен",
        "btn_ready": "🛍 Готов",
        "btn_done": "🏁 Завершить",
        "btn_confirm_cancel": "Да, отменить",
        "btn_back": "« Назад",
        "confirm_cancel": "Отменить заказ #{id}?",
        "status_changed": "Статус изменён: {status}",
        "status_stale": "Статус этого заказа уже изменился.",
        "not_admin": "Это действие только для админов.",
        "stoplist_title": "⛔ <b>Стоп-лист</b>\nВыберите категорию. Товары с ⛔ показываются в меню как «закончились».",
        "stoplist_cat": "<b>{cat}</b>\nНажмите на товар, чтобы включить/выключить его продажу.",
        "stats": (
            "📊 <b>Статистика</b>\n\n"
            "<b>Сегодня:</b> {t_total} заказов, {t_done} завершено, {t_cancelled} отменено\n"
            "Выручка: <b>{t_revenue}</b>\n\n"
            "<b>Последние 7 дней:</b> {w_total} заказов, {w_done} завершено\n"
            "Выручка: <b>{w_revenue}</b>\n\n"
            "Активных заказов сейчас: <b>{active}</b>\n"
            "Пользователей бота: <b>{users}</b>"
        ),
        "active_none": "Активных заказов нет 👌",
        "active_title": "📋 <b>Активные заказы</b>",
        "panel_text": (
            "🛠 <b>Админ-панель</b>\n\n"
            "Меню, фото, цены, акции, заказы, статистика и настройки.\n\n"
            "📱 С телефона — «Открыть панель».\n"
            "💻 С компьютера — «Открыть на компьютере» (ссылка действует 10 минут и один раз)."
        ),
        "panel_open": "🛠 Открыть панель",
        "panel_desktop": "💻 Открыть на компьютере",
        "panel_private_only": "Админ-панель открывается в личном чате с ботом 👇",
        "panel_no_access": (
            "У вас нет доступа к админ-панели.\n\nВаш Telegram ID: <code>{user_id}</code>\n"
            "Владелец может добавить вас: панель → Настройки → Админы."
        ),
        "panel_no_https": "⚠️ PUBLIC_URL (https) не настроен — панель не откроется.",
        "broadcast_running": "📣 Сейчас идёт другая рассылка, дождитесь окончания.",
        "broadcast_help": "Рассылка: ответьте (reply) на нужное сообщение (текст/фото/видео) командой /broadcast.",
        "broadcast_start": "📣 Отправляю {count} пользователям...",
        "broadcast_done": "📣 Готово: отправлено {ok}, не доставлено {fail} (заблокировали бота).",
        "chat_id": "ID этого чата: <code>{chat_id}</code>\nВаш ID: <code>{user_id}</code>",
        "admin_help": (
            "🛠 <b>Команды админа</b>\n\n"
            "/panel — админ-панель (меню, акции, настройки)\n"
            "/active — активные заказы\n"
            "/stats — статистика\n"
            "/stoplist — временно выключить/включить товар\n"
            "/broadcast — рассылка (ответом на сообщение)\n"
            "/id — узнать ID чата"
        ),
    },
}


def norm_lang(lang: str | None) -> str:
    return lang if lang in LANGS else "uz"


def t(lang: str | None, key: str, **kwargs: object) -> str:
    text = TEXTS[norm_lang(lang)][key]
    return text.format(**kwargs) if kwargs else text


def at(lang: str, key: str, **kwargs: object) -> str:
    text = ADMIN_TEXTS[norm_lang(lang)][key]
    return text.format(**kwargs) if kwargs else text


def all_variants(key: str) -> set[str]:
    """Tugma matnini ikkala tilda tanish uchun."""
    return {TEXTS[lang][key] for lang in LANGS}
