"""Botdagi barcha matnlar (o'zbekcha / ruscha)."""
from __future__ import annotations

LANGS = ("uz", "ru")
ADMIN_PANEL_BUTTON = "🛠 Admin panel"

TEXTS: dict[str, dict[str, str]] = {
    "uz": {
        "choose_lang": "🇺🇿 Tilni tanlang\n🇷🇺 Выберите язык",
        "greet": (
            "👋 Assalomu alaykum!\n<b>{store}</b> botiga xush kelibsiz.\n\n"
            "3 ta qisqa savol — va buyurtma berishingiz mumkin. Keyingi safar hammasi eslab qolinadi."
        ),
        # ro'yxatdan o'tish: raqam → ism → manzil
        "ask_phone": (
            "📱 <b>1/3 · Telefon raqamingiz</b>\n\n"
            "Buyurtma bo'yicha siz bilan bog'lanishimiz uchun pastdagi <b>«📱 Raqamni yuborish»</b> tugmasini bosing 👇"
        ),
        "ask_phone_edit": "📱 Yangi raqamni pastdagi tugma orqali yuboring yoki yozing (masalan, +998 90 123 45 67) 👇",
        "btn_share_phone": "📱 Raqamni yuborish",
        "phone_saved": "✅ Raqamingiz saqlandi.",
        "phone_not_own": "Iltimos, o'zingizning raqamingizni pastdagi tugma orqali yuboring.",
        "bad_phone": "Raqam noto'g'ri. Masalan: +998 90 123 45 67",
        "ask_name": "👤 <b>2/3 · Ismingiz</b>\n\nSizga qanday murojaat qilaylik? Ismingizni yozing yoki pastdagi tugmani bosing 👇",
        "ask_name_edit": "👤 Yangi ismingizni yozing 👇",
        "bad_name": "Iltimos, ismingizni harflar bilan yozing (2–40 belgi).",
        "name_saved": "✅ Ismingiz saqlandi: <b>{name}</b>",
        "ask_location": (
            "📍 <b>3/3 · Manzilingiz</b>\n\n"
            "Pastdagi <b>«📍 Lokatsiyani yuborish»</b> tugmasini bosing yoki manzilni yozib yuboring "
            "(ko'cha, uy, mo'ljal)."
        ),
        "ask_location_edit": (
            "📍 <b>Yetkazib berish manzili</b>\n\n"
            "Pastdagi <b>«📍 Lokatsiyani yuborish»</b> tugmasini bosing yoki manzilni yozib yuboring "
            "(ko'cha, uy, mo'ljal)."
        ),
        "ask_location_other": "\nBoshqa joy kerak bo'lsa: 📎 → <b>Lokatsiya</b> → xaritadan tanlang.",
        "ask_location_pickup": "\n\nO'zingiz olib ketsangiz — <b>«🛍 Olib ketaman»</b>.",
        "bad_address": "Manzil juda qisqa. Ko'cha, uy va mo'ljalni yozing yoki lokatsiya yuboring 📍",
        "btn_send_location": "📍 Lokatsiyani yuborish",
        "btn_prev_address": "🏠 Oldingi manzil",
        "btn_pickup_self": "🛍 Olib ketaman",
        "btn_back": "⬅️ Orqaga",
        "location_saved": "✅ <b>Manzil saqlandi</b>\n📍 {address}",
        "location_point": "Xaritadagi nuqta",
        "choose_branch": "🏪 <b>Qaysi filialdan olib ketasiz?</b>",
        "pickup_chosen": "✅ <b>Olib ketish</b> — {branch}\n📍 {address}",
        "welcome": "🎉 <b>Tayyor, {name}!</b>\n\n<b>{store}</b>ga xush kelibsiz 🍔\n{tagline}",
        "welcome_back": "👋 Xush kelibsiz, {name}!\n\n<b>{store}</b> — {tagline}",
        # buyurtma paneli
        "panel_delivery": "🚚 <b>Yetkazib berish</b>\n📍 {address}",
        "panel_pickup": "🛍 <b>Olib ketish</b> — {branch}\n📍 {address}",
        "panel_hint": "\n\nMenyudan taom tanlang 👇",
        "continue_order": "\n\nBuyurtmani davom ettirish uchun tugmani bosing 👇",
        "btn_open_menu": "🍔 Menyuni ochish",
        "btn_continue_order": "🛒 Buyurtmani davom ettirish",
        "btn_change_address": "📍 Manzilni o'zgartirish",
        "btn_to_pickup": "🛍 Olib ketaman",
        "btn_to_delivery": "🚚 Yetkazib berish",
        "btn_change_branch": "🏪 Boshqa filial",
        "open_menu": "Menyuni ochish uchun tugmani bosing 👇",
        "menu_button": "Menyu",
        "closed_now": "😴 Hozir barcha filiallarimiz yopiq. Menyuni ko'rishingiz mumkin, buyurtmalar ish vaqtida qabul qilinadi.",
        "paused_now": "⏸ Hozir buyurtmalar vaqtincha qabul qilinmayapti. Menyuni ko'rishingiz mumkin.",
        # asosiy menyu
        "btn_order": "🍔 Buyurtma berish",
        "btn_my_orders": "📦 Buyurtmalarim",
        "btn_branches": "🏪 Filiallar",
        "btn_contacts": "📞 Aloqa",
        "btn_settings": "⚙️ Sozlamalar",
        "btn_about": "ℹ️ Biz haqimizda",
        "home_menu": "Asosiy menyu 👇",
        "unknown": "Quyidagi menyudan tanlang 👇",
        "not_set": "kiritilmagan",
        # filiallar va aloqa
        "about": "🍔 <b>{store}</b>\n{about}",
        "branches_title": "🏪 <b>Filiallarimiz</b>",
        "branch_item": "<b>{name}</b> · {state}\n📍 {address}\n🕒 {hours}",
        "branch_phone": " · 📞 {phone}",
        "branch_map": "\n🗺 <a href=\"{url}\">Xaritada ko'rish</a>",
        "hours_24": "24/7",
        "state_open": "🟢 ochiq",
        "state_closed": "🔴 yopiq",
        "contacts": "📞 <b>Aloqa</b>\n\n{phones}",
        "contacts_line": "{name}: {phone}",
        "contacts_tg": "\n\n💬 Telegram: @{username}",
        "contacts_ig": "\n📸 Instagram: <a href=\"https://instagram.com/{instagram}\">@{instagram}</a>",
        # sozlamalar
        "settings": (
            "⚙️ <b>Sozlamalar</b>\n\n"
            "👤 Ism: {name}\n📱 Telefon: {phone}\n📍 Manzil: {address}\n🌐 Til: O'zbekcha"
        ),
        "settings_pickup": "olib ketish — {branch}",
        "btn_set_name": "👤 Ism",
        "btn_set_phone": "📱 Raqam",
        "btn_set_address": "📍 Manzil",
        "btn_set_lang": "🌐 Til",
        "lang_saved": "✅ Til o'zgartirildi.",
        # buyurtmalarim
        "no_orders": "Sizda hali buyurtmalar yo'q. Birinchisini hoziroq bering! 🍔",
        "my_orders_title": "📦 <b>Oxirgi buyurtmalaringiz</b>",
        "btn_repeat": "🔁 #{id} takrorlash",
        "btn_cancel_order": "❌ #{id} bekor qilish",
        "cancel_confirm": "Buyurtma <b>#{id}</b> bekor qilinsinmi?",
        "btn_yes_cancel": "Ha, bekor qilinsin",
        "btn_no": "Yo'q",
        "cancelled_by_you": "❌ Buyurtma <b>#{id}</b> bekor qilindi.",
        "cannot_cancel": "Buyurtma #{id} allaqachon qabul qilingan. Bekor qilish uchun qo'ng'iroq qiling: {phone}",
        "kept": "👌 Buyurtma o'z kuchida.",
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
        "branch_line": "🏪 Filial: {name}",
        # baho
        "rate_ask": "\n\nBuyurtma sizga yoqdimi? Baholang 👇",
        "rate_thanks": "Rahmat! Bahoyingiz: {stars}",
        "rate_thanks_full": "💛 Rahmat! Sizni yana kutib qolamiz.",
        "rate_already": "Bu buyurtma allaqachon baholangan",
        "ask_feedback": "😔 Uzr so'raymiz! Nima yoqmadi? Yozib qoldiring — albatta e'tibor beramiz.",
        "btn_skip": "⏭ O'tkazib yuborish",
        "feedback_thanks": "🙏 Rahmat! Fikringiz jamoamizga yetkazildi.",
    },
    "ru": {
        "choose_lang": "🇺🇿 Tilni tanlang\n🇷🇺 Выберите язык",
        "greet": (
            "👋 Здравствуйте!\nДобро пожаловать в бот <b>{store}</b>.\n\n"
            "3 коротких вопроса — и можно заказывать. В следующий раз всё будет сохранено."
        ),
        "ask_phone": (
            "📱 <b>1/3 · Ваш номер телефона</b>\n\n"
            "Чтобы мы могли связаться с вами по заказу, нажмите кнопку <b>«📱 Отправить номер»</b> ниже 👇"
        ),
        "ask_phone_edit": "📱 Отправьте новый номер кнопкой ниже или напишите его (например, +998 90 123 45 67) 👇",
        "btn_share_phone": "📱 Отправить номер",
        "phone_saved": "✅ Номер сохранён.",
        "phone_not_own": "Пожалуйста, отправьте свой номер кнопкой ниже.",
        "bad_phone": "Неверный номер. Например: +998 90 123 45 67",
        "ask_name": "👤 <b>2/3 · Ваше имя</b>\n\nКак к вам обращаться? Напишите имя или нажмите кнопку ниже 👇",
        "ask_name_edit": "👤 Напишите новое имя 👇",
        "bad_name": "Пожалуйста, напишите имя буквами (2–40 символов).",
        "name_saved": "✅ Имя сохранено: <b>{name}</b>",
        "ask_location": (
            "📍 <b>3/3 · Ваш адрес</b>\n\n"
            "Нажмите кнопку <b>«📍 Отправить локацию»</b> ниже или напишите адрес (улица, дом, ориентир)."
        ),
        "ask_location_edit": (
            "📍 <b>Адрес доставки</b>\n\n"
            "Нажмите кнопку <b>«📍 Отправить локацию»</b> ниже или напишите адрес (улица, дом, ориентир)."
        ),
        "ask_location_other": "\nНужен другой адрес: 📎 → <b>Геопозиция</b> → выберите на карте.",
        "ask_location_pickup": "\n\nЗаберёте сами — <b>«🛍 Заберу сам»</b>.",
        "bad_address": "Слишком короткий адрес. Напишите улицу, дом и ориентир или отправьте локацию 📍",
        "btn_send_location": "📍 Отправить локацию",
        "btn_prev_address": "🏠 Предыдущий адрес",
        "btn_pickup_self": "🛍 Заберу сам",
        "btn_back": "⬅️ Назад",
        "location_saved": "✅ <b>Адрес сохранён</b>\n📍 {address}",
        "location_point": "Точка на карте",
        "choose_branch": "🏪 <b>Из какого филиала заберёте?</b>",
        "pickup_chosen": "✅ <b>Самовывоз</b> — {branch}\n📍 {address}",
        "welcome": "🎉 <b>Готово, {name}!</b>\n\nДобро пожаловать в <b>{store}</b> 🍔\n{tagline}",
        "welcome_back": "👋 С возвращением, {name}!\n\n<b>{store}</b> — {tagline}",
        "panel_delivery": "🚚 <b>Доставка</b>\n📍 {address}",
        "panel_pickup": "🛍 <b>Самовывоз</b> — {branch}\n📍 {address}",
        "panel_hint": "\n\nВыберите блюда в меню 👇",
        "continue_order": "\n\nНажмите кнопку, чтобы продолжить заказ 👇",
        "btn_open_menu": "🍔 Открыть меню",
        "btn_continue_order": "🛒 Продолжить заказ",
        "btn_change_address": "📍 Изменить адрес",
        "btn_to_pickup": "🛍 Заберу сам",
        "btn_to_delivery": "🚚 Доставка",
        "btn_change_branch": "🏪 Другой филиал",
        "open_menu": "Нажмите кнопку, чтобы открыть меню 👇",
        "menu_button": "Меню",
        "closed_now": "😴 Сейчас все филиалы закрыты. Меню можно посмотреть, заказы принимаем в рабочее время.",
        "paused_now": "⏸ Сейчас заказы временно не принимаются. Меню можно посмотреть.",
        "btn_order": "🍔 Заказать",
        "btn_my_orders": "📦 Мои заказы",
        "btn_branches": "🏪 Филиалы",
        "btn_contacts": "📞 Контакты",
        "btn_settings": "⚙️ Настройки",
        "btn_about": "ℹ️ О нас",
        "home_menu": "Главное меню 👇",
        "unknown": "Выберите в меню ниже 👇",
        "not_set": "не указан",
        "about": "🍔 <b>{store}</b>\n{about}",
        "branches_title": "🏪 <b>Наши филиалы</b>",
        "branch_item": "<b>{name}</b> · {state}\n📍 {address}\n🕒 {hours}",
        "branch_phone": " · 📞 {phone}",
        "branch_map": "\n🗺 <a href=\"{url}\">Показать на карте</a>",
        "hours_24": "24/7",
        "state_open": "🟢 открыто",
        "state_closed": "🔴 закрыто",
        "contacts": "📞 <b>Контакты</b>\n\n{phones}",
        "contacts_line": "{name}: {phone}",
        "contacts_tg": "\n\n💬 Telegram: @{username}",
        "contacts_ig": "\n📸 Instagram: <a href=\"https://instagram.com/{instagram}\">@{instagram}</a>",
        "settings": (
            "⚙️ <b>Настройки</b>\n\n"
            "👤 Имя: {name}\n📱 Телефон: {phone}\n📍 Адрес: {address}\n🌐 Язык: Русский"
        ),
        "settings_pickup": "самовывоз — {branch}",
        "btn_set_name": "👤 Имя",
        "btn_set_phone": "📱 Номер",
        "btn_set_address": "📍 Адрес",
        "btn_set_lang": "🌐 Язык",
        "lang_saved": "✅ Язык изменён.",
        "no_orders": "У вас пока нет заказов. Сделайте первый прямо сейчас! 🍔",
        "my_orders_title": "📦 <b>Ваши последние заказы</b>",
        "btn_repeat": "🔁 Повторить #{id}",
        "btn_cancel_order": "❌ Отменить #{id}",
        "cancel_confirm": "Отменить заказ <b>#{id}</b>?",
        "btn_yes_cancel": "Да, отменить",
        "btn_no": "Нет",
        "cancelled_by_you": "❌ Заказ <b>#{id}</b> отменён.",
        "cannot_cancel": "Заказ #{id} уже принят. Чтобы отменить, позвоните: {phone}",
        "kept": "👌 Заказ остаётся в силе.",
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
        "branch_line": "🏪 Филиал: {name}",
        "rate_ask": "\n\nВам понравился заказ? Оцените 👇",
        "rate_thanks": "Спасибо! Ваша оценка: {stars}",
        "rate_thanks_full": "💛 Спасибо! Ждём вас снова.",
        "rate_already": "Этот заказ уже оценён",
        "ask_feedback": "😔 Простите! Что не понравилось? Напишите — мы обязательно разберёмся.",
        "btn_skip": "⏭ Пропустить",
        "feedback_thanks": "🙏 Спасибо! Ваш отзыв передан команде.",
    },
}

# Admin guruhidagi matnlar
ADMIN_TEXTS: dict[str, dict[str, str]] = {
    "uz": {
        "new_order": "🆕 <b>Yangi buyurtma #{id}</b>",
        "branch": "🏪 Filial: <b>{name}</b>",
        "rating_line": "Mijoz bahosi: {stars}",
        "rating_note": "{stars} — buyurtma #{id} ({name})",
        "by_customer": "mijoz",
        "customer_cancelled": "❌ Mijoz #{id} buyurtmani bekor qildi",
        "feedback_note": "💬 #{id} bo'yicha mijoz fikri ({name}):\n{text}",
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
        "branch": "🏪 Филиал: <b>{name}</b>",
        "rating_line": "Оценка клиента: {stars}",
        "rating_note": "{stars} — заказ #{id} ({name})",
        "by_customer": "клиент",
        "customer_cancelled": "❌ Клиент отменил заказ #{id}",
        "feedback_note": "💬 Отзыв клиента по заказу #{id} ({name}):\n{text}",
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
