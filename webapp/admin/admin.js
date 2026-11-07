/* Ayva Burgers — admin panel (framework'siz) */
(() => {
  'use strict';

  const tg = window.Telegram && window.Telegram.WebApp;
  const IN_TG = !!(tg && tg.initData);
  const LANG_KEY = 'ayva_admin_lang';

  // ================================================================ i18n
  const I18N = {
    uz: {
      cur: "so'm", pcs: 'ta', k: 'K', m: 'M',
      nav_orders: 'Buyurtmalar', nav_menu: 'Menyu', nav_promos: 'Aksiyalar', nav_stats: 'Statistika', nav_settings: 'Sozlamalar',
      admin: 'Admin panel', save: 'Saqlash', cancel: 'Bekor qilish', delete: "O'chirish", close: 'Yopish', add: "Qo'shish",
      saved: '✅ Saqlandi', deleted: "🗑 O'chirildi", replace: 'Almashtirish', remove: 'Olib tashlash',
      upload_hint: 'Rasm yuklash uchun bosing', uploading: 'Yuklanmoqda…', loading: 'Yuklanmoqda…', retry: 'Qayta urinish',
      search: 'Qidirish…', none: "Yo'q", yes: 'Ha', all: 'Hammasi', optional: 'ixtiyoriy',
      // kirish
      login_title: 'Admin panelga kirish', login_text: "Panelni botdagi /panel buyrug'i yoki «🛠 Admin panel» tugmasi orqali oching.",
      login_expired: "Kirish havolasi eskirgan yoki ishlatilgan. Botga /panel yozib, yangisini oling.",
      forbidden_title: "Ruxsat yo'q", forbidden_text: "Sizning Telegram ID: {id}. Egasi sizni Sozlamalar → Adminlar bo'limida qo'shishi kerak.",
      logout: 'Chiqish',
      // buyurtmalar
      tab_active: 'Faol', tab_history: 'Tarix', h_all: 'Hammasi', h_done: 'Yakunlangan', h_cancelled: 'Bekor qilingan',
      orders_search: 'Raqam, telefon yoki ism', no_active: "Hozir faol buyurtma yo'q", no_orders: 'Buyurtma topilmadi',
      load_more: "Ko'proq ko'rsatish", new_order_toast: '🆕 Yangi buyurtma #{id}',
      st_new: '🆕 Yangi', st_accepted: '👨‍🍳 Tayyorlanmoqda', st_on_the_way: "🚗 Yo'lda", st_ready: '🛍 Tayyor', st_done: '✅ Yakunlandi', st_cancelled: '❌ Bekor',
      act_accepted: '✅ Qabul qilish', act_on_the_way: "🚗 Yo'lga chiqdi", act_ready: '🛍 Tayyor', act_done: '🏁 Yakunlash', act_cancel: 'Bekor',
      confirm_cancel: 'Buyurtma #{id} bekor qilinsinmi? Mijozga xabar boradi.',
      type_delivery: 'Yetkazib berish', type_pickup: 'Olib ketish', pay_cash: 'Naqd', pay_click: 'Click', pay_payme: 'Payme',
      map: 'Xarita', delivery_fee: 'Yetkazish', total: 'Jami', stale: "Holat allaqachon o'zgargan — ro'yxat yangilandi",
      // menyu
      categories: 'Kategoriyalar', reorder: 'Tartiblash', reorder_done: 'Tayyor', new_product: 'Mahsulot',
      edit_product: 'Mahsulotni tahrirlash', add_product: 'Yangi mahsulot', no_products: "Bu yerda hali mahsulot yo'q",
      sold_out: 'Tugagan', hidden: 'Yashirin', on_sale: 'Sotuvda', products_n: '{n} ta mahsulot',
      f_image: 'Rasm', f_name_uz: "Nomi (o'zbekcha)", f_name_ru: 'Nomi (ruscha)', f_desc_uz: "Tarkibi / tavsif (o'zbekcha)", f_desc_ru: 'Tarkibi / tavsif (ruscha)',
      f_category_id: 'Kategoriya', f_price: "Narxi (so'm)", f_badge: 'Belgi', f_promo_price: "Aksiya narxi (so'm)",
      f_promo_from: 'Boshlanishi', f_promo_to: 'Tugashi', f_available: 'Sotuvda bor', f_available_sub: "O'chirilsa menyuda «Tugagan» bo'lib turadi",
      f_visible: "Menyuda ko'rsatish", f_visible_sub: "O'chirilsa mijozlar umuman ko'rmaydi",
      ru_hint: "Bo'sh qolsa o'zbekchasi ko'rsatiladi", photo_hint: 'Kvadrat yoki 4:3 surat yaxshi chiqadi. Avtomatik kichraytiriladi.',
      badge_: "Yo'q", badge_hit: '🔥 Hit', badge_new: '✨ Yangi', badge_spicy: '🌶 Achchiq',
      promo_toggle: 'Chegirma (aksiya) narxi', promo_toggle_sub: "Eski narx ustidan chizilib ko'rsatiladi",
      promo_dates_hint: "Sanalar bo'sh qolsa — aksiya darhol boshlanadi va o'zingiz o'chirguningizcha davom etadi.",
      confirm_delete_product: '«{name}» o\'chirilsinmi? Buni qaytarib bo\'lmaydi.',
      new_category: 'Yangi kategoriya', edit_category: 'Kategoriyani tahrirlash', f_icon: "Rasm (mahsulot surati bo'lmasa shu chiqadi)",
      cat_visible_sub: "O'chirilsa butun kategoriya menyudan yashiriladi", confirm_delete_category: '«{name}» kategoriyasi o\'chirilsinmi?',
      // aksiyalar
      banners: 'Bannerlar', banners_hint: 'Mijoz menyusining eng tepasida aylanib turadigan reklama kartalari.',
      new_banner: 'Yangi banner', edit_banner: 'Bannerni tahrirlash', no_banners: "Hali banner yo'q. Birinchisini qo'shing!",
      f_title_uz: "Sarlavha (o'zbekcha)", f_title_ru: 'Sarlavha (ruscha)', f_text_uz: "Qisqa matn (o'zbekcha)", f_text_ru: 'Qisqa matn (ruscha)',
      f_link: 'Bosilganda', link_: 'Hech narsa', link_product: 'Mahsulotni ochish', link_category: "Kategoriyaga o'tish",
      f_link_id: 'Qaysi biri', f_date_from: 'Boshlanishi', f_date_to: 'Tugashi', f_active: 'Faol',
      banner_img_hint: "Keng surat (2:1) yaxshi chiqadi. Surat bo'lmasa — sarlavha sariq fonda ko'rsatiladi.",
      confirm_delete_banner: "Banner o'chirilsinmi?",
      discounts: 'Chegirmalar', discounts_hint: "Narxi vaqtincha arzonlashtirilgan mahsulotlar. Mijoz menyusida «🔥 Aksiyalar» bo'limida ham chiqadi.",
      add_discount: 'Chegirma', no_discounts: "Hozir chegirmadagi mahsulot yo'q", pick_product: 'Mahsulotni tanlang',
      state_active: 'Faol', state_scheduled: 'Rejalashtirilgan', state_expired: "Muddati o'tgan", state_off: "O'chirilgan",
      until: '{d} gacha', from: '{d} dan',
      // statistika
      today: 'Bugun', d7: '7 kun', d30: '30 kun', revenue: 'Tushum', revenue_sub: 'yakunlangan buyurtmalar', orders: 'Buyurtmalar',
      avg_check: "O'rtacha chek", cancelled: 'Bekor qilingan', new_customers: 'Yangi mijozlar', customers_total: 'Jami {n} ta mijoz',
      delivery_pickup: 'Yetkazish / olib ketish', daily_revenue: 'Kunlik tushum', busy_hours: 'Soatlar bo\'yicha buyurtmalar',
      top_products: 'Eng ko\'p sotilganlar', no_data: "Bu davrda ma'lumot yo'q", show_table: 'Jadval', show_chart: 'Grafik',
      col_date: 'Sana', col_orders: 'Buyurtma', col_revenue: 'Tushum', hour: 'soat',
      // sozlamalar
      accepting_on: 'Buyurtmalar qabul qilinmoqda', accepting_off: "Buyurtmalar to'xtatilgan",
      accepting_sub_on: "Oshxona band bo'lsa yoki texnik sabab bilan vaqtincha o'chirib qo'yishingiz mumkin.",
      accepting_sub_off: "Mijozlar menyuni ko'radi, lekin buyurtma bera olmaydi.",
      confirm_pause: "Buyurtmalarni qabul qilish to'xtatilsinmi?",
      restaurant: "Restoran ma'lumotlari", f_name: 'Nomi', f_tagline_uz: "Shior (o'zbekcha)", f_tagline_ru: 'Shior (ruscha)',
      f_about_uz: "Biz haqimizda (o'zbekcha)", f_about_ru: 'Biz haqimizda (ruscha)', f_phone: 'Telefon', f_support_username: 'Telegram (admin username)',
      f_instagram: 'Instagram', f_address_uz: "Manzil (o'zbekcha)", f_address_ru: 'Manzil (ruscha)', f_location: 'Lokatsiya (xaritadagi nuqta)',
      f_lat: 'Kenglik (lat)', f_lon: 'Uzunlik (lon)', my_location: '📍 Hozirgi joylashuvim', check_map: "Xaritada ko'rish",
      hours: 'Ish vaqti', f_hours: 'Ish vaqti', f_open: 'Ochilish', f_close: 'Yopilish', hours_hint: "Yarim tundan o'tishi mumkin (masalan 10:00–02:00). 24 soat ishlasa, ikkalasiga bir xil vaqt qo'ying.",
      delivery: 'Yetkazib berish', f_delivery: 'Yetkazib berish', delivery_on: 'Yetkazib berish bor', f_fee: "Yetkazish narxi (so'm)", f_free_from: "Shu summadan bepul (so'm)", free_hint: "0 — har doim pullik",
      f_min_order: "Minimal buyurtma (so'm)", f_eta: 'Taxminiy vaqt (daqiqa)', pickup: 'Olib ketish', pickup_on: 'Olib ketish bor',
      payments: "To'lov usullari", f_payments: "To'lov", cash: 'Naqd pul', soon: 'Tez orada',
      unsaved: "Saqlanmagan o'zgarishlar bor", discard_confirm: "O'zgarishlar saqlanmasin?",
      admins: 'Adminlar', owner: 'Egasi', owners_hint: "Egalar .env faylidagi ADMIN_IDS orqali belgilanadi.",
      add_admin: "Admin qo'shish", f_user_id: 'Telegram ID', f_admin_name: 'Ismi (izoh uchun)',
      admin_id_hint: "Odam botga /id yozsa, bot uning ID'sini aytadi.", only_owner: "Adminlarni faqat egasi qo'sha oladi.",
      confirm_remove_admin: '{name} adminlikdan olinsinmi?', you: 'siz',
      broadcast: 'Mijozlarga xabar', broadcast_hint: "Aksiya yoki yangilik haqida botdagi barcha mijozlarga xabar yuboring.",
      f_text: 'Xabar matni', f_menu_button: '«Menyuni ochish» tugmasini qo\'shish', send: 'Yuborish',
      broadcast_confirm: '{n} ta mijozga yuborilsinmi?', broadcast_progress: 'Yuborilmoqda: {ok} / {total}', broadcast_done: '✅ Yuborildi: {ok}, yetib bormadi: {fail}',
      panel: 'Panel', panel_lang: 'Panel tili', desktop_hint: "Kompyuterdan ishlash uchun botga /panel yozing va «Kompyuterda ochish» havolasini bosing.",
      // xatolar
      err_network: "Internet bilan aloqa yo'q", e_generic: 'Xatolik yuz berdi', e_required: "to'ldirilishi shart", e_invalid: "noto'g'ri qiymat",
      e_too_long: 'juda uzun', e_out_of_range: "ruxsat etilgan oraliqdan tashqarida", e_promo_not_lower: "asosiy narxdan arzon bo'lishi kerak",
      e_bad_range: "tugash sanasi boshlanishidan oldin bo'lmasin", e_title_or_image: "sarlavha yoki rasm kerak",
      e_category_not_empty: "Kategoriyada mahsulotlar bor — avval ularni boshqa kategoriyaga o'tkazing yoki o'chiring",
      e_bad_image: "Rasmni o'qib bo'lmadi (JPG, PNG yoki WebP yuklang)", e_too_large: 'Rasm juda katta (12 MB gacha)',
      e_need_one_type: "yetkazib berish yoki olib ketishdan biri yoqilgan bo'lishi kerak", e_need_one_payment: "kamida bitta to'lov usuli kerak",
      e_owner_only: "Bu amal faqat egasi uchun", e_broadcast_running: 'Boshqa xabar yuborilmoqda', e_stale: "Holat allaqachon o'zgargan",
      e_unauthorized: 'Qaytadan kiring', e_forbidden: "Ruxsat yo'q", e_csrf: 'Sahifani yangilang',
      e_role_forbidden: "Bu amal uchun ruxsatingiz yo'q", e_already_owner: 'bu odam allaqachon egasi',
      role_owner: 'Egasi', role_admin: 'Administrator', role_cashier: 'Kassir', f_role: 'Roli',
      role_admin_sub: "Menyu, narxlar, aksiyalar, statistika va sozlamalar — hammasi",
      role_cashier_sub: "Faqat buyurtmalar, stop-list va buyurtmani vaqtincha to'xtatish",
      cashier_menu_note: "🔒 Kassir rejimi: faqat mahsulot sotuvda bor/yo'qligini o'zgartira olasiz.",
      cashier_settings_note: "🔒 Kassir rejimi: menyu, narx, aksiya va sozlamalarni administrator o'zgartiradi.",
      role_changed: '✅ Rol o\'zgartirildi',
    },
    ru: {
      cur: 'сум', pcs: 'шт', k: 'K', m: 'M',
      nav_orders: 'Заказы', nav_menu: 'Меню', nav_promos: 'Акции', nav_stats: 'Статистика', nav_settings: 'Настройки',
      admin: 'Админ-панель', save: 'Сохранить', cancel: 'Отмена', delete: 'Удалить', close: 'Закрыть', add: 'Добавить',
      saved: '✅ Сохранено', deleted: '🗑 Удалено', replace: 'Заменить', remove: 'Убрать',
      upload_hint: 'Нажмите, чтобы загрузить фото', uploading: 'Загрузка…', loading: 'Загрузка…', retry: 'Повторить',
      search: 'Поиск…', none: 'Нет', yes: 'Да', all: 'Все', optional: 'необязательно',
      login_title: 'Вход в админ-панель', login_text: 'Откройте панель командой /panel или кнопкой «🛠 Admin panel» в боте.',
      login_expired: 'Ссылка для входа устарела или уже использована. Напишите боту /panel и получите новую.',
      forbidden_title: 'Нет доступа', forbidden_text: 'Ваш Telegram ID: {id}. Владелец должен добавить вас в Настройки → Админы.',
      logout: 'Выйти',
      tab_active: 'Активные', tab_history: 'История', h_all: 'Все', h_done: 'Завершённые', h_cancelled: 'Отменённые',
      orders_search: 'Номер, телефон или имя', no_active: 'Сейчас нет активных заказов', no_orders: 'Заказы не найдены',
      load_more: 'Показать ещё', new_order_toast: '🆕 Новый заказ #{id}',
      st_new: '🆕 Новый', st_accepted: '👨‍🍳 Готовится', st_on_the_way: '🚗 В пути', st_ready: '🛍 Готов', st_done: '✅ Завершён', st_cancelled: '❌ Отменён',
      act_accepted: '✅ Принять', act_on_the_way: '🚗 Отправлен', act_ready: '🛍 Готов', act_done: '🏁 Завершить', act_cancel: 'Отменить',
      confirm_cancel: 'Отменить заказ #{id}? Клиент получит уведомление.',
      type_delivery: 'Доставка', type_pickup: 'Самовывоз', pay_cash: 'Наличные', pay_click: 'Click', pay_payme: 'Payme',
      map: 'Карта', delivery_fee: 'Доставка', total: 'Итого', stale: 'Статус уже изменился — список обновлён',
      categories: 'Категории', reorder: 'Порядок', reorder_done: 'Готово', new_product: 'Товар',
      edit_product: 'Редактирование товара', add_product: 'Новый товар', no_products: 'Здесь пока нет товаров',
      sold_out: 'Закончился', hidden: 'Скрыт', on_sale: 'В продаже', products_n: '{n} товаров',
      f_image: 'Фото', f_name_uz: 'Название (узбекский)', f_name_ru: 'Название (русский)', f_desc_uz: 'Состав / описание (узбекский)', f_desc_ru: 'Состав / описание (русский)',
      f_category_id: 'Категория', f_price: 'Цена (сум)', f_badge: 'Метка', f_promo_price: 'Акционная цена (сум)',
      f_promo_from: 'Начало', f_promo_to: 'Конец', f_available: 'В продаже', f_available_sub: 'Если выключить — в меню будет «Закончился»',
      f_visible: 'Показывать в меню', f_visible_sub: 'Если выключить — клиенты не увидят товар',
      ru_hint: 'Если пусто — покажем узбекское', photo_hint: 'Лучше квадратное фото или 4:3. Уменьшается автоматически.',
      badge_: 'Нет', badge_hit: '🔥 Хит', badge_new: '✨ Новинка', badge_spicy: '🌶 Острое',
      promo_toggle: 'Акционная цена (скидка)', promo_toggle_sub: 'Старая цена будет зачёркнута',
      promo_dates_hint: 'Если даты пустые — акция начнётся сразу и будет действовать, пока вы её не выключите.',
      confirm_delete_product: 'Удалить «{name}»? Это нельзя отменить.',
      new_category: 'Новая категория', edit_category: 'Редактирование категории', f_icon: 'Картинка (если у товара нет фото)',
      cat_visible_sub: 'Если выключить — вся категория скроется из меню', confirm_delete_category: 'Удалить категорию «{name}»?',
      banners: 'Баннеры', banners_hint: 'Рекламные карточки, которые листаются в самом верху меню.',
      new_banner: 'Новый баннер', edit_banner: 'Редактирование баннера', no_banners: 'Баннеров пока нет. Добавьте первый!',
      f_title_uz: 'Заголовок (узбекский)', f_title_ru: 'Заголовок (русский)', f_text_uz: 'Короткий текст (узбекский)', f_text_ru: 'Короткий текст (русский)',
      f_link: 'При нажатии', link_: 'Ничего', link_product: 'Открыть товар', link_category: 'Перейти в категорию',
      f_link_id: 'Что именно', f_date_from: 'Начало', f_date_to: 'Конец', f_active: 'Активен',
      banner_img_hint: 'Лучше широкое фото (2:1). Без фото заголовок будет на жёлтом фоне.',
      confirm_delete_banner: 'Удалить баннер?',
      discounts: 'Скидки', discounts_hint: 'Товары со временно сниженной ценой. В меню клиента они также в разделе «🔥 Акции».',
      add_discount: 'Скидка', no_discounts: 'Сейчас нет товаров со скидкой', pick_product: 'Выберите товар',
      state_active: 'Активна', state_scheduled: 'Запланирована', state_expired: 'Истекла', state_off: 'Выключен',
      until: 'до {d}', from: 'с {d}',
      today: 'Сегодня', d7: '7 дней', d30: '30 дней', revenue: 'Выручка', revenue_sub: 'завершённые заказы', orders: 'Заказы',
      avg_check: 'Средний чек', cancelled: 'Отменено', new_customers: 'Новые клиенты', customers_total: 'Всего {n} клиентов',
      delivery_pickup: 'Доставка / самовывоз', daily_revenue: 'Выручка по дням', busy_hours: 'Заказы по часам',
      top_products: 'Самые продаваемые', no_data: 'За этот период данных нет', show_table: 'Таблица', show_chart: 'График',
      col_date: 'Дата', col_orders: 'Заказы', col_revenue: 'Выручка', hour: 'час',
      accepting_on: 'Заказы принимаются', accepting_off: 'Приём заказов остановлен',
      accepting_sub_on: 'Можно временно выключить, если кухня перегружена или по техническим причинам.',
      accepting_sub_off: 'Клиенты видят меню, но не могут заказать.',
      confirm_pause: 'Остановить приём заказов?',
      restaurant: 'Данные ресторана', f_name: 'Название', f_tagline_uz: 'Слоган (узбекский)', f_tagline_ru: 'Слоган (русский)',
      f_about_uz: 'О нас (узбекский)', f_about_ru: 'О нас (русский)', f_phone: 'Телефон', f_support_username: 'Telegram (username админа)',
      f_instagram: 'Instagram', f_address_uz: 'Адрес (узбекский)', f_address_ru: 'Адрес (русский)', f_location: 'Локация (точка на карте)',
      f_lat: 'Широта (lat)', f_lon: 'Долгота (lon)', my_location: '📍 Моё местоположение', check_map: 'Посмотреть на карте',
      hours: 'Время работы', f_hours: 'Время работы', f_open: 'Открытие', f_close: 'Закрытие', hours_hint: 'Можно через полночь (например 10:00–02:00). Если круглосуточно — одинаковое время.',
      delivery: 'Доставка', f_delivery: 'Доставка', delivery_on: 'Есть доставка', f_fee: 'Стоимость доставки (сум)', f_free_from: 'Бесплатно от суммы (сум)', free_hint: '0 — всегда платно',
      f_min_order: 'Минимальный заказ (сум)', f_eta: 'Примерное время (мин)', pickup: 'Самовывоз', pickup_on: 'Есть самовывоз',
      payments: 'Способы оплаты', f_payments: 'Оплата', cash: 'Наличные', soon: 'Скоро',
      unsaved: 'Есть несохранённые изменения', discard_confirm: 'Не сохранять изменения?',
      admins: 'Админы', owner: 'Владелец', owners_hint: 'Владельцы задаются в ADMIN_IDS в файле .env.',
      add_admin: 'Добавить админа', f_user_id: 'Telegram ID', f_admin_name: 'Имя (для себя)',
      admin_id_hint: 'Пусть человек напишет боту /id — бот покажет его ID.', only_owner: 'Добавлять админов может только владелец.',
      confirm_remove_admin: 'Убрать {name} из админов?', you: 'вы',
      broadcast: 'Рассылка клиентам', broadcast_hint: 'Отправьте сообщение об акции или новинке всем клиентам бота.',
      f_text: 'Текст сообщения', f_menu_button: 'Добавить кнопку «Открыть меню»', send: 'Отправить',
      broadcast_confirm: 'Отправить {n} клиентам?', broadcast_progress: 'Отправка: {ok} / {total}', broadcast_done: '✅ Отправлено: {ok}, не доставлено: {fail}',
      panel: 'Панель', panel_lang: 'Язык панели', desktop_hint: 'Чтобы работать с компьютера, напишите боту /panel и нажмите «Открыть на компьютере».',
      err_network: 'Нет связи с интернетом', e_generic: 'Произошла ошибка', e_required: 'обязательно', e_invalid: 'неверное значение',
      e_too_long: 'слишком длинно', e_out_of_range: 'вне допустимого диапазона', e_promo_not_lower: 'должна быть ниже основной цены',
      e_bad_range: 'дата окончания раньше начала', e_title_or_image: 'нужен заголовок или фото',
      e_category_not_empty: 'В категории есть товары — сначала перенесите их или удалите',
      e_bad_image: 'Не удалось прочитать фото (загрузите JPG, PNG или WebP)', e_too_large: 'Фото слишком большое (до 12 МБ)',
      e_need_one_type: 'должна быть включена доставка или самовывоз', e_need_one_payment: 'нужен хотя бы один способ оплаты',
      e_owner_only: 'Только для владельца', e_broadcast_running: 'Уже идёт другая рассылка', e_stale: 'Статус уже изменился',
      e_unauthorized: 'Войдите заново', e_forbidden: 'Нет доступа', e_csrf: 'Обновите страницу',
      e_role_forbidden: 'Недостаточно прав для этого действия', e_already_owner: 'этот человек уже владелец',
      role_owner: 'Владелец', role_admin: 'Администратор', role_cashier: 'Кассир', f_role: 'Роль',
      role_admin_sub: 'Меню, цены, акции, статистика и настройки — всё',
      role_cashier_sub: 'Только заказы, стоп-лист и временная остановка приёма заказов',
      cashier_menu_note: '🔒 Режим кассира: можно только включать/выключать наличие товара.',
      cashier_settings_note: '🔒 Режим кассира: меню, цены, акции и настройки меняет администратор.',
      role_changed: '✅ Роль изменена',
    },
  };

  const SVG = (d, extra = '') => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" ${extra}>${d}</svg>`;
  const ICON = {
    orders: SVG('<path d="M6 3h12v18l-3-2-3 2-3-2-3 2z"/><path d="M9 8h6M9 12h6M9 16h3"/>'),
    menu: SVG('<path d="M4 11h16a8 8 0 0 0-16 0z"/><path d="M3 14h18M5 17h14a2 2 0 0 1-2 3H7a2 2 0 0 1-2-3z"/>'),
    promos: SVG('<path d="M20.6 13.4l-7.2 7.2a2 2 0 0 1-2.8 0L3 13V3h10l7.6 7.6a2 2 0 0 1 0 2.8z"/><circle cx="7.5" cy="7.5" r="1.5"/>'),
    stats: SVG('<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>'),
    settings: SVG('<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>'),
    plus: SVG('<path d="M12 5v14M5 12h14"/>', 'stroke-width="2.6"'),
    close: SVG('<path d="M6 6l12 12M18 6L6 18"/>', 'stroke-width="2.4"'),
    back: SVG('<path d="M15 5l-7 7 7 7"/>', 'stroke-width="2.4"'),
    up: SVG('<path d="M6 15l6-6 6 6"/>', 'stroke-width="2.4"'),
    down: SVG('<path d="M6 9l6 6 6-6"/>', 'stroke-width="2.4"'),
    search: SVG('<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/>'),
    edit: SVG('<path d="M4 20h4L19 9l-4-4L4 16z"/>'),
  };

  // ================================================================ state
  const S = {
    lang: 'uz', me: null, page: 'orders',
    menu: null, banners: null, store: null, admins: null, bc: null, customers: 0,
    orders: { tab: 'active', hist: 'history', list: [], q: '', hasMore: false },
    activeIds: null, activeCount: 0,
    stats: { days: 7, data: null, table: false },
    menuFilter: 'all', menuQuery: '', reorder: false,
    sheets: [], dirty: false,
  };

  // ================================================================ helpers
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  function t(key, vars) {
    let s = (I18N[S.lang] && I18N[S.lang][key]) ?? I18N.uz[key] ?? key;
    if (vars) for (const k in vars) s = s.split('{' + k + '}').join(vars[k]);
    return s;
  }
  const has = (key) => key in I18N.uz;
  const num = (n) => String(Math.round(n || 0)).replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
  const money = (n) => num(n) + ' ' + t('cur');
  function compact(n) {
    if (n >= 1e6) return (Math.round(n / 1e5) / 10).toString().replace('.', ',') + t('m');
    if (n >= 1e4) return Math.round(n / 1e3) + t('k');
    return num(n);
  }
  const fmtDate = (iso) => (iso ? iso.split('-').reverse().join('.') : '');
  const nameOf = (o, key = 'name') => (S.lang === 'ru' && o[key + '_ru']) || o[key + '_uz'] || '';
  function tgAtLeast(v) { return !!(tg && tg.isVersionAtLeast && tg.isVersionAtLeast(v)); }
  function haptic(kind) {
    if (!tgAtLeast('6.1') || !tg.HapticFeedback) return;
    try {
      if (['success', 'error', 'warning'].includes(kind)) tg.HapticFeedback.notificationOccurred(kind);
      else if (kind === 'select') tg.HapticFeedback.selectionChanged();
      else tg.HapticFeedback.impactOccurred(kind || 'light');
    } catch (_) { /* */ }
  }
  let toastTimer;
  function toast(msg, kind) {
    const el = $('#toast');
    el.textContent = msg;
    el.className = 'toast is-shown' + (kind ? ' toast--' + kind : '');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove('is-shown'), kind === 'error' ? 4200 : 2600);
    if (kind === 'error') haptic('error');
    if (kind === 'ok') haptic('success');
  }
  function confirmBox(msg) {
    return new Promise((resolve) => {
      if (IN_TG && tgAtLeast('6.2')) tg.showConfirm(msg, (ok) => resolve(!!ok));
      else resolve(window.confirm(msg));
    });
  }
  function errText(e) {
    if (!e || e.network) return t('err_network');
    const msg = has('e_' + e.error) ? t('e_' + e.error) : t('e_generic');
    const field = e.field && has('f_' + e.field) ? t('f_' + e.field) : '';
    return field ? `${field}: ${msg}` : msg;
  }
  const fail = (e) => toast(errText(e), 'error');

  function imgSrc(image, icon) {
    if (image && (image.startsWith('/') || /^https?:/.test(image))) return image;
    if (image) return '/static/' + image;
    return '/static/img/' + (icon || 'burger') + '.svg';
  }
  const catOf = (id) => (S.menu ? S.menu.categories.find((c) => c.id === id) : null);
  function thumb(p) {
    const cat = catOf(p.category_id) || {};
    const src = imgSrc(p.image, cat.icon);
    return `<div class="thumb" style="--tint: var(--tint-${esc(p.category_id)}, var(--tint-default))"><img src="${esc(src)}" alt="" loading="lazy" ${p.image ? '' : 'class="is-icon"'}></div>`;
  }

  // ================================================================ API
  async function api(method, path, body) {
    const headers = { 'X-Admin': '1' };
    if (IN_TG) headers.Authorization = 'tma ' + tg.initData;
    const opts = { method, headers, credentials: 'same-origin' };
    if (body instanceof FormData) opts.body = body;
    else if (body !== undefined) { headers['Content-Type'] = 'application/json'; opts.body = JSON.stringify(body); }
    let res;
    try { res = await fetch(path, opts); } catch (_) { throw { network: true }; }
    let data = {};
    try { data = await res.json(); } catch (_) { /* */ }
    if (!res.ok || data.ok === false) throw { status: res.status, ...data };
    return data;
  }

  // ================================================================ theme / telegram
  function applyTheme() {
    let dark = IN_TG ? tg.colorScheme === 'dark' : !!(window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches);
    document.documentElement.dataset.theme = dark ? 'dark' : 'light';
    const bg = dark ? '#15110C' : '#FFF8EE';
    $('meta[name="theme-color"]').content = bg;
    if (tgAtLeast('6.1')) { try { tg.setHeaderColor(bg); tg.setBackgroundColor(bg); } catch (_) { /* */ } }
    if (tgAtLeast('7.10')) { try { tg.setBottomBarColor(bg); } catch (_) { /* */ } }
  }
  function setupTelegram() {
    if (!tg) return;
    try { tg.ready(); tg.expand(); } catch (_) { /* */ }
    if (tgAtLeast('7.7')) { try { tg.disableVerticalSwipes(); } catch (_) { /* */ } }
    if (tgAtLeast('6.1')) tg.BackButton.onClick(() => closeSheet());
    tg.onEvent && tg.onEvent('themeChanged', applyTheme);
  }
  function updateBack() {
    if (!IN_TG || !tgAtLeast('6.1')) return;
    if (S.sheets.length) tg.BackButton.show(); else tg.BackButton.hide();
  }

  // ================================================================ shell / navigation
  const PAGES = ['orders', 'menu', 'promos', 'stats', 'settings'];
  const CASHIER_PAGES = ['orders', 'menu', 'settings'];
  const isFull = () => !!S.me && (S.me.role === 'owner' || S.me.role === 'admin');
  const pages = () => (isFull() ? PAGES : CASHIER_PAGES);
  function renderNav() {
    const nav = $('#nav');
    nav.hidden = false;
    nav.style.gridTemplateColumns = `repeat(${pages().length}, 1fr)`;
    nav.innerHTML = `<div class="nav__brand"><img src="/static/img/logo.svg" alt="">${esc(S.me.store_name || 'Ayva')}</div>` +
      pages().map((p) => `<button class="nav__item ${S.page === p ? 'is-active' : ''}" data-action="nav" data-page="${p}">
        ${ICON[p]}<span>${t('nav_' + p)}</span>${p === 'orders' && S.activeCount ? `<span class="nav__badge">${S.activeCount}</span>` : ''}
      </button>`).join('');
  }
  function renderTopbar() {
    $('#topbar').innerHTML = `<img class="topbar__logo" src="/static/img/logo.svg" alt="">
      <div class="topbar__title"><div class="topbar__kicker">${esc(S.me.store_name || '')} · ${t('role_' + (S.me.role || 'admin'))}</div>
      <div class="topbar__h">${t('nav_' + S.page)}</div></div>`;
  }

  async function go(page, { push = true } = {}) {
    if (!pages().includes(page)) page = 'orders';
    if (S.dirty && page !== S.page) {
      if (!(await confirmBox(t('discard_confirm')))) { renderNav(); return; }
      S.dirty = false;
    }
    S.page = page;
    if (push && location.hash !== '#' + page) history.replaceState(null, '', '#' + page);
    renderNav();
    renderTopbar();
    const el = $('#page');
    el.classList.add('is-loading');
    try {
      await LOADERS[page]();
      renderPage();
    } catch (e) {
      el.innerHTML = `<div class="empty"><div class="empty__icon">⚠️</div>${esc(errText(e))}<br><br>
        <button class="btn btn--primary" data-action="nav" data-page="${page}">${t('retry')}</button></div>`;
    }
    el.classList.remove('is-loading');
    window.scrollTo(0, 0);
  }
  function renderPage() {
    RENDERERS[S.page]();
    renderSavebar();
  }

  // ================================================================ ORDERS
  async function loadOrders(more = false) {
    const o = S.orders;
    const tab = o.tab === 'active' ? 'active' : o.hist;
    const qs = new URLSearchParams({ tab });
    if (o.q) qs.set('q', o.q);
    if (more && o.list.length) qs.set('before', o.list[o.list.length - 1].id);
    const d = await api('GET', '/api/admin/orders?' + qs);
    o.list = more ? o.list.concat(d.orders) : d.orders;
    o.hasMore = d.has_more;
    if (tab === 'active' && !o.q) trackActive(d.orders, false);
  }

  function trackActive(list, notify) {
    const ids = new Set(list.map((x) => x.id));
    if (notify && S.activeIds) {
      const fresh = list.filter((x) => !S.activeIds.has(x.id) && x.status === 'new');
      if (fresh.length) { toast(t('new_order_toast', { id: fresh.map((x) => x.id).join(', #') }), 'ok'); haptic('success'); }
    }
    S.activeIds = ids;
    S.activeCount = list.filter((x) => x.status === 'new').length;
    if (S.me) renderNav();
  }

  function orderCard(o) {
    const lines = [];
    const who = esc(o.name || '—') + (o.username ? ` (<a href="https://t.me/${esc(o.username)}" target="_blank" rel="noopener">@${esc(o.username)}</a>)` : '');
    lines.push(`<div>👤 ${who} · <a href="tel:${esc(o.phone.replace(/[^\d+]/g, ''))}">${esc(o.phone)}</a></div>`);
    if (o.type === 'delivery') {
      const map = o.lat != null ? ` · <a href="https://yandex.uz/maps/?pt=${o.lon},${o.lat}&z=17&l=map" target="_blank" rel="noopener">${t('map')}</a>` : '';
      lines.push(`<div>🚚 ${esc(o.address || '—')}${map}</div>`);
    } else {
      lines.push(`<div>🛍 ${t('type_pickup')}</div>`);
    }
    if (o.comment) lines.push(`<div>💬 ${esc(o.comment)}</div>`);

    const items = o.items.map((it) => `<div class="order__item"><span>${esc((it.name && (it.name[S.lang] || it.name.uz)) || it.id)} × ${it.qty}</span><span>${money(it.price * it.qty)}</span></div>`).join('');
    const fee = o.type === 'delivery' ? `<div class="order__item muted"><span>${t('delivery_fee')}</span><span>${o.delivery_fee ? money(o.delivery_fee) : '0'}</span></div>` : '';

    const act = (st, cls) => `<button class="btn ${cls}" data-action="ost" data-id="${o.id}" data-st="${st}">${t('act_' + st)}</button>`;
    let actions = '';
    if (o.status === 'new') actions = act('accepted', 'btn--primary') + act('cancel', 'btn--danger');
    else if (o.status === 'accepted') actions = act(o.type === 'delivery' ? 'on_the_way' : 'ready', 'btn--primary') + act('cancel', 'btn--danger');
    else if (o.status === 'on_the_way' || o.status === 'ready') actions = act('done', 'btn--dark');

    const tagCls = { new: 'tag--warn', accepted: 'tag--info', on_the_way: 'tag--info', ready: 'tag--info', done: 'tag--ok', cancelled: 'tag--danger' }[o.status];
    return `<article class="order ${o.status === 'new' ? 'is-new' : ''}">
      <div class="order__head"><span class="order__id">#${o.id}</span><span class="tag ${tagCls}">${t('st_' + o.status)}</span>
        <span class="order__time">${S.orders.tab === 'active' ? '' : esc(o.date) + ' · '}${esc(o.time)}</span></div>
      <div class="order__lines">${lines.join('')}</div>
      <div class="order__items">${items}${fee}</div>
      <div class="order__total"><span>${t('total')} · ${t('pay_' + o.payment)}</span><span>${money(o.total)}</span></div>
      ${actions ? `<div class="order__actions">${actions}</div>` : ''}
    </article>`;
  }

  function renderOrders() {
    const o = S.orders;
    const histChips = o.tab === 'history' ? `<div class="chips">${['history', 'done', 'cancelled'].map((h) =>
      `<button class="chip ${o.hist === h ? 'is-active' : ''}" data-action="hist" data-h="${h}">${t(h === 'history' ? 'h_all' : 'h_' + h)}</button>`).join('')}</div>` : '';
    const list = o.list.length ? o.list.map(orderCard).join('') :
      `<div class="empty"><div class="empty__icon">${o.tab === 'active' && !o.q ? '😌' : '🔎'}</div>${o.tab === 'active' && !o.q ? t('no_active') : t('no_orders')}</div>`;
    $('#page').innerHTML = `
      <div class="segment">
        <button class="${o.tab === 'active' ? 'is-active' : ''}" data-action="otab" data-tab="active">${t('tab_active')}${S.activeIds ? ` (${S.activeIds.size})` : ''}</button>
        <button class="${o.tab === 'history' ? 'is-active' : ''}" data-action="otab" data-tab="history">${t('tab_history')}</button>
      </div>
      <label class="search">${ICON.search}<input class="input" type="search" data-input="order-q" placeholder="${esc(t('orders_search'))}" value="${esc(o.q)}"></label>
      ${histChips}
      ${list}
      ${o.hasMore ? `<button class="btn btn--ghost load-more" data-action="more-orders">${t('load_more')}</button>` : ''}`;
  }

  async function setOrderStatus(id, st) {
    if (st === 'cancel') {
      if (!(await confirmBox(t('confirm_cancel', { id })))) return;
      st = 'cancelled';
    }
    try {
      await api('POST', `/api/admin/orders/${id}/status`, { status: st });
      haptic('success');
    } catch (e) {
      if (e.error === 'stale') toast(t('stale'), 'error'); else fail(e);
    }
    await loadOrders();
    if (S.page === 'orders') renderOrders();
  }

  // Har 15 soniyada faol buyurtmalarni tekshiramiz (yangi buyurtma kelsa — xabar)
  async function poll() {
    if (document.visibilityState !== 'visible' || !S.me) return;
    try {
      const d = await api('GET', '/api/admin/orders?tab=active');
      trackActive(d.orders, true);
      const o = S.orders;
      if (S.page === 'orders' && o.tab === 'active' && !o.q && !S.sheets.length) {
        const sig = (l) => l.map((x) => x.id + x.status).join();
        if (sig(d.orders) !== sig(o.list)) { o.list = d.orders; renderOrders(); }
      }
    } catch (_) { /* jim */ }
  }

  // ================================================================ MENU
  async function loadMenu() { S.menu = await api('GET', '/api/admin/menu'); }

  function priceHtml(p) {
    if (p.promo_price && p.promo_state === 'active') {
      const pct = Math.round((p.price - p.promo_price) * 100 / p.price);
      return `<span class="price">${money(p.promo_price)}</span><span class="price-old">${money(p.price)}</span><span class="tag tag--danger">−${pct}%</span>`;
    }
    let extra = '';
    if (p.promo_price && p.promo_state === 'scheduled') extra = `<span class="tag tag--info">${t('state_scheduled')}</span>`;
    return `<span class="price">${money(p.price)}</span>${extra}`;
  }

  function productRow(p, opts = {}) {
    const tags = [];
    if (!p.visible) tags.push(`<span class="tag">🙈 ${t('hidden')}</span>`);
    if (!p.available) tags.push(`<span class="tag tag--danger">${t('sold_out')}</span>`);
    if (p.badge) tags.push(`<span class="tag">${t('badge_' + p.badge)}</span>`);
    let side = '';
    if (opts.reorder) {
      side = `<button class="icon-btn" data-action="move-product" data-id="${esc(p.id)}" data-dir="-1" ${opts.first ? 'disabled' : ''} aria-label="up">${ICON.up}</button>
              <button class="icon-btn" data-action="move-product" data-id="${esc(p.id)}" data-dir="1" ${opts.last ? 'disabled' : ''} aria-label="down">${ICON.down}</button>`;
    } else if (opts.toggle !== false) {
      side = `<label class="switch" title="${esc(t('on_sale'))}"><input type="checkbox" data-toggle="available" data-id="${esc(p.id)}" ${p.available ? 'checked' : ''}><span></span></label>`;
    }
    return `<div class="prow ${p.available && p.visible ? '' : 'is-off'}" data-action="${opts.action || 'edit-product'}" data-id="${esc(p.id)}">
      ${thumb(p)}
      <div class="prow__info"><div class="prow__name">${esc(nameOf(p))}</div><div class="prow__meta">${priceHtml(p)}${tags.join('')}</div></div>
      <div class="prow__side">${side}</div>
    </div>`;
  }

  function renderMenu() {
    const m = S.menu;
    const q = S.menuQuery.trim().toLowerCase();
    const match = (p) => !q || [p.name_uz, p.name_ru, p.desc_uz].some((s) => (s || '').toLowerCase().includes(q));
    const cats = m.categories.filter((c) => S.menuFilter === 'all' || c.id === S.menuFilter);
    const chips = [`<button class="chip ${S.menuFilter === 'all' ? 'is-active' : ''}" data-action="mfilter" data-cat="all">${t('all')} · ${m.products.length}</button>`]
      .concat(m.categories.map((c) => `<button class="chip ${S.menuFilter === c.id ? 'is-active' : ''}" data-action="mfilter" data-cat="${esc(c.id)}">
        ${c.visible ? '' : '🙈 '}${esc(nameOf(c))} · ${m.products.filter((p) => p.category_id === c.id).length}</button>`));

    const sections = cats.map((c) => {
      const items = m.products.filter((p) => p.category_id === c.id && match(p));
      if (q && !items.length) return '';
      const rows = items.map((p, i) => productRow(p, { reorder: S.reorder && !q && isFull(), first: i === 0,
        last: i === items.length - 1, action: isFull() ? 'edit-product' : 'none' })).join('');
      return `<div class="cat-h"><h3>${esc(nameOf(c))}</h3>${c.visible ? '' : `<span class="tag">🙈 ${t('hidden')}</span>`}
          <span class="grow"></span>${isFull() ? `<button class="icon-btn" data-action="new-product" data-cat="${esc(c.id)}" aria-label="${t('add')}">${ICON.plus}</button>` : ''}</div>
        ${rows ? `<div class="plist">${rows}</div>` : `<div class="empty small">${t('no_products')}</div>`}`;
    }).join('');

    $('#page').innerHTML = `
      <label class="search">${ICON.search}<input class="input" type="search" data-input="menu-q" placeholder="${esc(t('search'))}" value="${esc(S.menuQuery)}"></label>
      ${isFull() ? `<div class="row-gap" style="margin-top:8px">
        <button class="btn btn--sm" data-action="categories">🗂 ${t('categories')}</button>
        <button class="btn btn--sm ${S.reorder ? 'btn--dark' : ''}" data-action="reorder-toggle">${S.reorder ? '✓ ' + t('reorder_done') : '↕ ' + t('reorder')}</button>
      </div>` : `<div class="notice">${t('cashier_menu_note')}</div>`}
      <div class="chips">${chips.join('')}</div>
      ${sections || `<div class="empty">${t('no_products')}</div>`}
      ${isFull() ? `<button class="fab" data-action="new-product">${ICON.plus}${t('new_product')}</button>` : ''}`;
  }

  async function toggleAvailable(id, value, input) {
    try {
      await api('PATCH', `/api/admin/products/${encodeURIComponent(id)}`, { available: value });
      const p = S.menu.products.find((x) => x.id === id);
      if (p) p.available = value;
      haptic('light');
      if (S.page === 'menu') renderMenu();
    } catch (e) { input.checked = !value; fail(e); }
  }

  async function moveProduct(id, dir) {
    const p = S.menu.products.find((x) => x.id === id);
    const list = S.menu.products.filter((x) => x.category_id === p.category_id);
    const i = list.indexOf(p);
    const j = i + dir;
    if (j < 0 || j >= list.length) return;
    [list[i], list[j]] = [list[j], list[i]];
    try {
      await api('POST', '/api/admin/products/reorder', { ids: list.map((x) => x.id) });
      await loadMenu();
      renderMenu();
      haptic('select');
    } catch (e) { fail(e); }
  }

  // ---------- uploader ----------
  function uploaderHtml(name, value, ratio, icon) {
    const src = value ? imgSrc(value) : (icon ? imgSrc('', icon) : '');
    const inner = value ? `<img src="${esc(src)}" alt="">`
      : `${icon ? `<img src="${esc(src)}" alt="" class="is-icon">` : ''}<div class="uploader__ph" ${icon ? 'style="position:absolute;bottom:14px"' : ''}><b>📷</b>${t('upload_hint')}</div>`;
    return `<div class="uploader" data-uploader="${name}" data-ratio="${ratio}" data-icon="${esc(icon || '')}" style="--ratio:${ratio}">
      <input type="hidden" name="${name}" value="${esc(value || '')}">
      <input type="file" accept="image/*" hidden data-file>
      <div class="uploader__box" data-action="upload-pick">${inner}</div>
      ${value ? `<div class="uploader__bar"><button type="button" class="btn btn--sm" data-action="upload-pick">${t('replace')}</button>
        <button type="button" class="btn btn--sm" data-action="upload-clear">${t('remove')}</button></div>` : ''}
    </div>`;
  }
  function setUploader(el, value) {
    el.outerHTML = uploaderHtml(el.dataset.uploader, value, el.dataset.ratio, el.dataset.icon);
  }
  async function doUpload(el, file) {
    el.classList.add('is-busy');
    const fd = new FormData();
    fd.append('file', file, file.name || 'photo.jpg');
    try {
      const d = await api('POST', '/api/admin/upload', fd);
      setUploader(el, d.url);
      haptic('light');
    } catch (e) {
      el.classList.remove('is-busy');
      fail(e);
    }
  }

  // ---------- forma qiymatlarini o'qish ----------
  function readForm(root) {
    const out = {};
    $$('[name]', root).forEach((el) => {
      if (el.type === 'file' || el.disabled) return;
      let v;
      if (el.type === 'checkbox') v = el.checked;
      else if (el.dataset.num !== undefined) v = el.value.trim() === '' ? null : Number(el.value);
      else v = el.value;
      const path = el.name.split('.');
      let cur = out;
      path.slice(0, -1).forEach((k) => { cur = cur[k] = cur[k] || {}; });
      cur[path[path.length - 1]] = v;
    });
    return out;
  }
  function markInvalid(root, field) {
    const el = root.querySelector(`[name="${field}"]`);
    if (!el) return;
    el.classList.add('is-invalid');
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    el.addEventListener('input', () => el.classList.remove('is-invalid'), { once: true });
  }
  const field = (label, input, hint) => `<label class="field"><span class="field__label">${label}</span>${input}${hint ? `<div class="field__hint">${hint}</div>` : ''}</label>`;
  const inp = (name, value, attrs = '') => `<input class="input" name="${name}" value="${esc(value ?? '')}" ${attrs}>`;
  const numInp = (name, value, attrs = '') => `<input class="input" name="${name}" type="number" inputmode="numeric" min="0" step="1" data-num value="${value ?? ''}" ${attrs}>`;
  const area = (name, value, attrs = '') => `<textarea class="input" name="${name}" rows="2" ${attrs}>${esc(value ?? '')}</textarea>`;
  const switchRow = (name, checked, title, sub, attrs = '') => `<div class="switch-row"><div class="switch-row__text"><div class="switch-row__title">${title}</div>
    ${sub ? `<div class="switch-row__sub">${sub}</div>` : ''}</div><label class="switch"><input type="checkbox" name="${name}" ${checked ? 'checked' : ''} ${attrs}><span></span></label></div>`;

  // ---------- mahsulot formasi ----------
  function openProductForm(id, opts = {}) {
    const isNew = !id;
    const firstCat = (S.menuFilter !== 'all' && S.menuFilter) || (S.menu.categories[0] || {}).id;
    const p = isNew ? { name_uz: '', name_ru: '', desc_uz: '', desc_ru: '', category_id: opts.cat || firstCat, price: '',
      promo_price: null, promo_from: null, promo_to: null, image: '', badge: '', available: true, visible: true }
      : S.menu.products.find((x) => x.id === id);
    if (!p) return;
    const promoOn = !!p.promo_price || !!opts.promo;
    const view = {
      title: isNew ? t('add_product') : t('edit_product'),
      body: () => `<form id="pform" onsubmit="return false">
        ${field(t('f_image'), uploaderHtml('image', p.image, '4 / 3', (catOf(p.category_id) || {}).icon), t('photo_hint'))}
        ${field(t('f_name_uz') + ' <b>*</b>', inp('name_uz', p.name_uz, 'maxlength="80" required'))}
        ${field(t('f_name_ru'), inp('name_ru', p.name_ru, 'maxlength="80"'), t('ru_hint'))}
        ${field(t('f_desc_uz'), area('desc_uz', p.desc_uz, 'maxlength="300"'))}
        ${field(t('f_desc_ru'), area('desc_ru', p.desc_ru, 'maxlength="300"'))}
        <div class="grid2">
          ${field(t('f_category_id') + ' <b>*</b>', `<select class="input" name="category_id">${S.menu.categories.map((c) =>
            `<option value="${esc(c.id)}" ${c.id === p.category_id ? 'selected' : ''}>${esc(nameOf(c))}</option>`).join('')}</select>`)}
          ${field(t('f_price') + ' <b>*</b>', numInp('price', p.price, 'min="100" data-live'))}
        </div>
        <div class="field"><span class="field__label">${t('f_badge')}</span>
          <input type="hidden" name="badge" value="${esc(p.badge)}">
          <div class="badge-pick">${['', 'hit', 'new', 'spicy'].map((b) => `<button type="button" class="${p.badge === b ? 'is-active' : ''}" data-action="pick-badge" data-badge="${b}">${t('badge_' + b)}</button>`).join('')}</div>
        </div>
        <div class="promo-box" id="promo-box">
          ${switchRow('_promo', promoOn, t('promo_toggle'), t('promo_toggle_sub'), 'data-promo-toggle')}
          <div id="promo-fields" ${promoOn ? '' : 'hidden'}>
            ${field(t('f_promo_price'), numInp('promo_price', p.promo_price, 'data-live'))}
            <div class="pct">${[10, 15, 20, 25, 30, 50].map((n) => `<button type="button" data-action="pct" data-pct="${n}">−${n}%</button>`).join('')}</div>
            <div class="preview-price" id="promo-preview"></div>
            <div class="grid2">
              ${field(t('f_promo_from'), `<input class="input" type="date" name="promo_from" value="${esc(p.promo_from || '')}">`)}
              ${field(t('f_promo_to'), `<input class="input" type="date" name="promo_to" value="${esc(p.promo_to || '')}">`)}
            </div>
            <div class="field__hint" style="margin-top:-4px">${t('promo_dates_hint')}</div>
          </div>
        </div>
        <div class="card" style="margin-top:0;padding:4px 16px">
          ${switchRow('available', p.available, t('f_available'), t('f_available_sub'))}
          ${switchRow('visible', p.visible, t('f_visible'), t('f_visible_sub'))}
        </div>
      </form>`,
      foot: () => `${isNew ? '' : `<button class="btn btn--danger" data-action="delete-product" data-id="${esc(p.id)}">${t('delete')}</button>`}
        <button class="btn btn--primary" data-action="save-product" data-id="${esc(p.id || '')}">${t('save')}</button>`,
      mount: (root) => {
        updatePromoPreview(root);
        if (opts.promo) setTimeout(() => $('#promo-box', root).scrollIntoView({ behavior: 'smooth', block: 'start' }), 250);
      },
    };
    openSheet(view);
  }

  function updatePromoPreview(root) {
    const box = $('#promo-preview', root);
    if (!box) return;
    const price = Number($('[name="price"]', root).value) || 0;
    const promo = Number($('[name="promo_price"]', root).value) || 0;
    if (!price || !promo) { box.innerHTML = ''; return; }
    if (promo >= price) { box.innerHTML = `<span class="tag tag--danger">${t('f_promo_price')}: ${t('e_promo_not_lower')}</span>`; return; }
    const pct = Math.round((price - promo) * 100 / price);
    box.innerHTML = `<span class="price-old">${money(price)}</span> → <span class="price">${money(promo)}</span><span class="tag tag--danger">−${pct}%</span>`;
  }

  async function saveProduct(id) {
    const root = $('#pform');
    const f = readForm(root);
    const promoOn = f._promo;
    const body = {
      name_uz: f.name_uz.trim(), name_ru: f.name_ru.trim(), desc_uz: f.desc_uz.trim(), desc_ru: f.desc_ru.trim(),
      category_id: f.category_id, price: f.price, badge: f.badge, image: f.image,
      available: f.available, visible: f.visible,
      promo_price: promoOn ? f.promo_price : null,
      promo_from: promoOn ? (f.promo_from || null) : null,
      promo_to: promoOn ? (f.promo_to || null) : null,
    };
    if (!body.name_uz) { markInvalid(root, 'name_uz'); return toast(`${t('f_name_uz')}: ${t('e_required')}`, 'error'); }
    if (!body.price || body.price < 100) { markInvalid(root, 'price'); return toast(`${t('f_price')}: ${t('e_required')}`, 'error'); }
    if (promoOn && (!body.promo_price || body.promo_price >= body.price)) {
      markInvalid(root, 'promo_price');
      return toast(`${t('f_promo_price')}: ${t('e_promo_not_lower')}`, 'error');
    }
    const btn = $('[data-action="save-product"]');
    btn.disabled = true;
    try {
      if (id) await api('PATCH', `/api/admin/products/${encodeURIComponent(id)}`, body);
      else await api('POST', '/api/admin/products', body);
      await loadMenu();
      closeSheet(true);
      toast(t('saved'), 'ok');
      renderPage();
    } catch (e) {
      btn.disabled = false;
      if (e.field) markInvalid(root, e.field);
      fail(e);
    }
  }

  async function deleteProduct(id) {
    const p = S.menu.products.find((x) => x.id === id);
    if (!p || !(await confirmBox(t('confirm_delete_product', { name: nameOf(p) })))) return;
    try {
      await api('DELETE', `/api/admin/products/${encodeURIComponent(id)}`);
      await loadMenu();
      closeSheet(true);
      toast(t('deleted'), 'ok');
      renderPage();
    } catch (e) { fail(e); }
  }

  // ---------- kategoriyalar ----------
  function openCategories() {
    openSheet({
      title: t('categories'),
      body: () => {
        const cats = S.menu.categories;
        return `<div class="plist" style="margin-top:0">${cats.map((c, i) => `<div class="prow" data-action="edit-category" data-id="${esc(c.id)}">
            <div class="thumb" style="--tint: var(--tint-${esc(c.id)}, var(--tint-default))"><img class="is-icon" src="${imgSrc('', c.icon)}" alt=""></div>
            <div class="prow__info"><div class="prow__name">${esc(nameOf(c))}</div>
              <div class="prow__meta muted">${t('products_n', { n: S.menu.products.filter((p) => p.category_id === c.id).length })}
              ${c.visible ? '' : `<span class="tag">🙈 ${t('hidden')}</span>`}</div></div>
            <div class="prow__side">
              <button class="icon-btn" data-action="move-category" data-id="${esc(c.id)}" data-dir="-1" ${i === 0 ? 'disabled' : ''}>${ICON.up}</button>
              <button class="icon-btn" data-action="move-category" data-id="${esc(c.id)}" data-dir="1" ${i === cats.length - 1 ? 'disabled' : ''}>${ICON.down}</button>
            </div></div>`).join('')}</div>`;
      },
      foot: () => `<button class="btn btn--primary" data-action="new-category">${ICON.plus.replace('<svg', '<svg width="18" height="18"')} ${t('new_category')}</button>`,
    });
  }

  function openCategoryForm(id) {
    const c = id ? S.menu.categories.find((x) => x.id === id) : { name_uz: '', name_ru: '', icon: 'burger', visible: true };
    openSheet({
      title: id ? t('edit_category') : t('new_category'),
      body: () => `<form id="cform" onsubmit="return false">
        ${field(t('f_name_uz') + ' <b>*</b>', inp('name_uz', c.name_uz, 'maxlength="40"'))}
        ${field(t('f_name_ru'), inp('name_ru', c.name_ru, 'maxlength="40"'), t('ru_hint'))}
        <div class="field"><span class="field__label">${t('f_icon')}</span><input type="hidden" name="icon" value="${esc(c.icon)}">
          <div class="icon-pick">${S.menu.icons.map((ic) => `<button type="button" class="${ic === c.icon ? 'is-active' : ''}" data-action="pick-icon" data-icon="${ic}"><img src="${imgSrc('', ic)}" alt="${ic}"></button>`).join('')}</div></div>
        <div class="card" style="padding:4px 16px">${switchRow('visible', c.visible, t('f_visible'), t('cat_visible_sub'))}</div>
      </form>`,
      foot: () => `${id ? `<button class="btn btn--danger" data-action="delete-category" data-id="${esc(id)}">${t('delete')}</button>` : ''}
        <button class="btn btn--primary" data-action="save-category" data-id="${esc(id || '')}">${t('save')}</button>`,
    });
  }

  async function saveCategory(id) {
    const root = $('#cform');
    const f = readForm(root);
    if (!f.name_uz.trim()) { markInvalid(root, 'name_uz'); return toast(`${t('f_name_uz')}: ${t('e_required')}`, 'error'); }
    try {
      const body = { name_uz: f.name_uz.trim(), name_ru: f.name_ru.trim(), icon: f.icon, visible: f.visible };
      if (id) await api('PATCH', `/api/admin/categories/${encodeURIComponent(id)}`, body);
      else await api('POST', '/api/admin/categories', body);
      await loadMenu();
      closeSheet();
      toast(t('saved'), 'ok');
      renderPage();
    } catch (e) { fail(e); }
  }

  async function deleteCategory(id) {
    const c = S.menu.categories.find((x) => x.id === id);
    if (!c || !(await confirmBox(t('confirm_delete_category', { name: nameOf(c) })))) return;
    try {
      await api('DELETE', `/api/admin/categories/${encodeURIComponent(id)}`);
      await loadMenu();
      if (S.menuFilter === id) S.menuFilter = 'all';
      closeSheet();
      toast(t('deleted'), 'ok');
      renderPage();
    } catch (e) { fail(e); }
  }

  async function moveCategory(id, dir) {
    const list = S.menu.categories.slice();
    const i = list.findIndex((c) => c.id === id);
    const j = i + dir;
    if (j < 0 || j >= list.length) return;
    [list[i], list[j]] = [list[j], list[i]];
    try {
      await api('POST', '/api/admin/categories/reorder', { ids: list.map((c) => c.id) });
      await loadMenu();
      renderSheet(true);
      renderPage();
    } catch (e) { fail(e); }
  }

  // ================================================================ PROMOS
  async function loadPromos() {
    const [, b] = await Promise.all([loadMenu(), api('GET', '/api/admin/banners')]);
    S.banners = b.banners;
  }

  const STATE_TAG = { active: 'tag--ok', scheduled: 'tag--info', expired: 'tag--danger', off: '' };
  function dateRange(from, to) {
    if (from && to) return `${fmtDate(from)} – ${fmtDate(to)}`;
    if (from) return t('from', { d: fmtDate(from) });
    if (to) return t('until', { d: fmtDate(to) });
    return '';
  }

  function renderPromos() {
    const banners = S.banners;
    const linkLabel = (b) => {
      if (b.link_type === 'product') { const p = S.menu.products.find((x) => x.id === b.link_id); return p ? '→ ' + nameOf(p) : ''; }
      if (b.link_type === 'category') { const c = catOf(b.link_id); return c ? '→ ' + nameOf(c) : ''; }
      return '';
    };
    const bcards = banners.map((b, i) => `<div class="banner-card" data-action="edit-banner" data-id="${b.id}">
        <div class="banner-card__visual">${b.image ? `<img src="${esc(imgSrc(b.image))}" alt="">` : `<span>${esc(nameOf(b, 'title'))}</span>`}</div>
        <div class="banner-card__body">
          <div class="row-gap"><span class="banner-card__title grow">${esc(nameOf(b, 'title') || '—')}</span><span class="tag ${STATE_TAG[b.state]}">${t('state_' + b.state)}</span></div>
          ${nameOf(b, 'text') ? `<div class="small muted">${esc(nameOf(b, 'text'))}</div>` : ''}
          <div class="banner-card__meta">${esc([linkLabel(b), dateRange(b.date_from, b.date_to)].filter(Boolean).join(' · '))}</div>
          <div class="banner-card__tools">
            <button class="icon-btn" data-action="move-banner" data-id="${b.id}" data-dir="-1" ${i === 0 ? 'disabled' : ''}>${ICON.up}</button>
            <button class="icon-btn" data-action="move-banner" data-id="${b.id}" data-dir="1" ${i === banners.length - 1 ? 'disabled' : ''}>${ICON.down}</button>
          </div>
        </div></div>`).join('');

    const promos = S.menu.products.filter((p) => p.promo_price);
    const rows = promos.map((p) => productRow(p, { toggle: false }).replace('<div class="prow__side"></div>',
      `<div class="prow__side"><span class="tag ${STATE_TAG[p.promo_state] || ''}">${t('state_' + (p.promo_state || 'off'))}</span></div>`)
      .replace('<div class="prow__meta">', `<div class="prow__meta">${p.promo_to || p.promo_from ? `<span class="small muted">${esc(dateRange(p.promo_from, p.promo_to))}</span>` : ''}`)).join('');

    $('#page').innerHTML = `
      <div class="section-h" style="margin-top:12px"><h2>${t('banners')}</h2><button class="btn btn--primary btn--sm" data-action="new-banner">${ICON.plus.replace('<svg', '<svg width="16" height="16"')} ${t('add')}</button></div>
      <div class="small muted">${t('banners_hint')}</div>
      ${bcards || `<div class="empty"><div class="empty__icon">🖼</div>${t('no_banners')}</div>`}
      <div class="section-h"><h2>${t('discounts')}</h2><button class="btn btn--primary btn--sm" data-action="new-discount">${ICON.plus.replace('<svg', '<svg width="16" height="16"')} ${t('add_discount')}</button></div>
      <div class="small muted">${t('discounts_hint')}</div>
      ${rows ? `<div class="plist">${rows}</div>` : `<div class="empty"><div class="empty__icon">🏷</div>${t('no_discounts')}</div>`}`;
  }

  function openBannerForm(id) {
    const b = id ? S.banners.find((x) => x.id === Number(id)) : { title_uz: '', title_ru: '', text_uz: '', text_ru: '', image: '',
      link_type: '', link_id: '', date_from: null, date_to: null, active: true };
    const targets = (type) => (type === 'product' ? S.menu.products.map((p) => [p.id, nameOf(p)]) : S.menu.categories.map((c) => [c.id, nameOf(c)]));
    const targetSelect = (type, sel) => `<select class="input" name="link_id">${targets(type).map(([v, l]) => `<option value="${esc(v)}" ${v === sel ? 'selected' : ''}>${esc(l)}</option>`).join('')}</select>`;
    openSheet({
      title: id ? t('edit_banner') : t('new_banner'),
      body: () => `<form id="bform" onsubmit="return false">
        ${field(t('f_image'), uploaderHtml('image', b.image, '2 / 1', ''), t('banner_img_hint'))}
        ${field(t('f_title_uz'), inp('title_uz', b.title_uz, 'maxlength="60"'))}
        ${field(t('f_title_ru'), inp('title_ru', b.title_ru, 'maxlength="60"'), t('ru_hint'))}
        ${field(t('f_text_uz'), inp('text_uz', b.text_uz, 'maxlength="140"'))}
        ${field(t('f_text_ru'), inp('text_ru', b.text_ru, 'maxlength="140"'))}
        ${field(t('f_link'), `<select class="input" name="link_type" data-link-type>${['', 'product', 'category'].map((v) => `<option value="${v}" ${v === b.link_type ? 'selected' : ''}>${t('link_' + v)}</option>`).join('')}</select>`)}
        <div id="link-target">${b.link_type ? field(t('f_link_id'), targetSelect(b.link_type, b.link_id)) : ''}</div>
        <div class="grid2">
          ${field(t('f_date_from'), `<input class="input" type="date" name="date_from" value="${esc(b.date_from || '')}">`)}
          ${field(t('f_date_to'), `<input class="input" type="date" name="date_to" value="${esc(b.date_to || '')}">`)}
        </div>
        <div class="card" style="padding:4px 16px">${switchRow('active', b.active, t('f_active'), '')}</div>
      </form>`,
      foot: () => `${id ? `<button class="btn btn--danger" data-action="delete-banner" data-id="${b.id}">${t('delete')}</button>` : ''}
        <button class="btn btn--primary" data-action="save-banner" data-id="${id || ''}">${t('save')}</button>`,
      mount: (root) => {
        $('[data-link-type]', root).addEventListener('change', (e) => {
          const type = e.target.value;
          $('#link-target', root).innerHTML = type ? field(t('f_link_id'), targetSelect(type, '')) : '';
        });
      },
    });
  }

  async function saveBanner(id) {
    const root = $('#bform');
    const f = readForm(root);
    const body = {
      title_uz: f.title_uz.trim(), title_ru: f.title_ru.trim(), text_uz: f.text_uz.trim(), text_ru: f.text_ru.trim(),
      image: f.image, link_type: f.link_type, link_id: f.link_type ? (f.link_id || '') : '',
      date_from: f.date_from || null, date_to: f.date_to || null, active: f.active,
    };
    if (!body.title_uz && !body.image) { markInvalid(root, 'title_uz'); return toast(t('e_title_or_image'), 'error'); }
    try {
      if (id) await api('PATCH', `/api/admin/banners/${id}`, body);
      else await api('POST', '/api/admin/banners', body);
      await loadPromos();
      closeSheet(true);
      toast(t('saved'), 'ok');
      renderPage();
    } catch (e) { if (e.field) markInvalid(root, e.field); fail(e); }
  }

  async function deleteBanner(id) {
    if (!(await confirmBox(t('confirm_delete_banner')))) return;
    try {
      await api('DELETE', `/api/admin/banners/${id}`);
      await loadPromos();
      closeSheet(true);
      toast(t('deleted'), 'ok');
      renderPage();
    } catch (e) { fail(e); }
  }

  async function moveBanner(id, dir) {
    const list = S.banners.slice();
    const i = list.findIndex((b) => b.id === Number(id));
    const j = i + dir;
    if (j < 0 || j >= list.length) return;
    [list[i], list[j]] = [list[j], list[i]];
    try {
      await api('POST', '/api/admin/banners/reorder', { ids: list.map((b) => b.id) });
      await loadPromos();
      renderPromos();
    } catch (e) { fail(e); }
  }

  function openDiscountPicker() {
    openSheet({
      title: t('pick_product'),
      body: () => `<label class="search" style="margin-top:0">${ICON.search}<input class="input" type="search" data-input="pick-q" placeholder="${esc(t('search'))}"></label>
        <div class="plist" id="pick-list">${S.menu.products.map((p) => productRow(p, { toggle: false, action: 'pick-discount' })).join('')}</div>`,
    });
  }

  // ================================================================ STATS
  async function loadStats() { S.stats.data = await api('GET', '/api/admin/stats?days=' + S.stats.days); }

  function niceMax(v) {
    if (v <= 0) return 1;
    const p = Math.pow(10, Math.floor(Math.log10(v)));
    const n = v / p;
    return (n <= 1 ? 1 : n <= 2 ? 2 : n <= 2.5 ? 2.5 : n <= 5 ? 5 : 10) * p;
  }

  // Bitta qatorli ustunli grafik: 4px yumaloq uch, 2px oraliq, ingichka to'r, har ustunda tooltip
  function barChart(items, fmtTick, labelEvery) {
    const max = niceMax(Math.max(...items.map((i) => i.value), 0));
    const ticks = [0, max / 2, max];
    return `<div class="chart" data-chart>
      <div class="chart__plot">
        ${ticks.map((v) => `<div class="chart__grid" style="bottom:${(v / max) * 100}%"></div><div class="chart__tick" style="bottom:calc(${(v / max) * 100}% - 0px);top:auto;transform:translateY(50%)">${fmtTick(v)}</div>`).join('')}
        ${items.map((it) => `<div class="chart__slot" tabindex="0" data-tip="${esc(it.tip)}">
          <div class="chart__bar" style="height:${it.value ? Math.max(1.5, (it.value / max) * 100) : 0}%"></div></div>`).join('')}
      </div>
      <div class="chart__x">${items.map((it, i) => `<span>${i % labelEvery === 0 ? esc(it.label) : ''}</span>`).join('')}</div>
    </div>`;
  }

  function renderStats() {
    const st = S.stats;
    const d = st.data;
    const T = d.totals;
    const seg = `<div class="segment">${[['1', 'today'], ['7', 'd7'], ['30', 'd30']].map(([v, k]) =>
      `<button class="${String(st.days) === v ? 'is-active' : ''}" data-action="sdays" data-days="${v}">${t(k)}</button>`).join('')}</div>`;
    const kpis = `<div class="kpis">
      <div class="kpi kpi--hero"><div class="kpi__label">${t('revenue')}</div><div class="kpi__value">${money(T.revenue)}</div><div class="kpi__sub">${t('revenue_sub')}: ${T.done}</div></div>
      <div class="kpi"><div class="kpi__label">${t('orders')}</div><div class="kpi__value">${num(T.orders)}</div><div class="kpi__sub">${t('cancelled')}: ${T.cancelled}</div></div>
      <div class="kpi"><div class="kpi__label">${t('avg_check')}</div><div class="kpi__value">${money(T.avg_check)}</div></div>
      <div class="kpi"><div class="kpi__label">${t('new_customers')}</div><div class="kpi__value">${num(T.new_customers)}</div><div class="kpi__sub">${t('customers_total', { n: num(T.customers_total) })}</div></div>
      <div class="kpi"><div class="kpi__label">${t('delivery_pickup')}</div><div class="kpi__value">${num(T.delivery)} / ${num(T.pickup)}</div></div>
    </div>`;

    let daily = '';
    if (d.days > 1) {
      const items = d.daily.map((r) => {
        const dd = r.date.slice(8, 10) + '.' + r.date.slice(5, 7);
        return { label: dd, value: r.revenue, tip: `<b>${dd}</b><br>${t('col_revenue')}: ${money(r.revenue)}<br>${t('col_orders')}: ${r.orders}` };
      });
      const hasData = d.daily.some((r) => r.revenue || r.orders);
      const table = `<table class="dtable"><thead><tr><th>${t('col_date')}</th><th>${t('col_orders')}</th><th>${t('col_revenue')}</th></tr></thead>
        <tbody>${d.daily.slice().reverse().map((r) => `<tr><td>${fmtDate(r.date)}</td><td>${r.orders}</td><td>${money(r.revenue)}</td></tr>`).join('')}</tbody></table>`;
      daily = `<div class="card"><div class="card__h"><h3 class="card__title">${t('daily_revenue')}</h3>
          <button class="btn btn--sm btn--ghost" data-action="stable">${st.table ? t('show_chart') : t('show_table')}</button></div>
        ${!hasData ? `<div class="empty small">${t('no_data')}</div>` : st.table ? table : barChart(items, compact, d.days > 7 ? 5 : 1)}</div>`;
    }

    const hoursMap = Object.fromEntries(d.busy_hours.map((h) => [h.hour, h.orders]));
    const hourItems = Array.from({ length: 24 }, (_, h) => ({ label: String(h), value: hoursMap[h] || 0,
      tip: `<b>${String(h).padStart(2, '0')}:00–${String((h + 1) % 24).padStart(2, '0')}:00</b><br>${t('col_orders')}: ${hoursMap[h] || 0}` }));
    const busy = `<div class="card"><div class="card__h"><h3 class="card__title">${t('busy_hours')}</h3></div>
      ${d.busy_hours.length ? barChart(hourItems, (v) => (Number.isInteger(v) ? String(v) : ''), 3) : `<div class="empty small">${t('no_data')}</div>`}</div>`;

    const topMax = Math.max(1, ...d.top.map((r) => r.qty));
    const top = `<div class="card"><div class="card__h"><h3 class="card__title">${t('top_products')}</h3></div>
      ${d.top.length ? `<div class="hbars">${d.top.map((r) => `<div class="hbar">
        <div class="hbar__top"><span class="hbar__name">${esc((r.name && (r.name[S.lang] || r.name.uz)) || r.id)}</span>
        <span class="hbar__val">${r.qty} ${t('pcs')} · ${money(r.revenue)}</span></div>
        <div class="hbar__track"><div class="hbar__fill" style="width:${(r.qty / topMax) * 100}%"></div></div></div>`).join('')}</div>`
        : `<div class="empty small">${t('no_data')}</div>`}</div>`;

    $('#page').innerHTML = seg + kpis + daily + busy + top;
  }

  // tooltip
  let tipEl = null;
  function showTip(slot) {
    const chart = slot.closest('[data-chart]');
    if (!chart) return;
    hideTip();
    tipEl = document.createElement('div');
    tipEl.className = 'tooltip';
    tipEl.innerHTML = slot.dataset.tip;
    chart.appendChild(tipEl);
    const cr = chart.getBoundingClientRect();
    const bar = slot.firstElementChild.getBoundingClientRect();
    let x = bar.left + bar.width / 2 - cr.left;
    const half = tipEl.offsetWidth / 2;
    x = Math.max(half, Math.min(cr.width - half, x));
    tipEl.style.left = x + 'px';
    tipEl.style.top = Math.max(tipEl.offsetHeight, bar.top - cr.top - 8) + 'px';
  }
  function hideTip() { if (tipEl) { tipEl.remove(); tipEl = null; } }

  // ================================================================ SETTINGS
  async function loadSettings() {
    if (!isFull()) {
      S.store = (await api('GET', '/api/admin/store')).store;
      return;
    }
    const [s, a, b] = await Promise.all([api('GET', '/api/admin/store'), api('GET', '/api/admin/admins'), api('GET', '/api/admin/broadcast')]);
    S.store = s.store;
    S.admins = a;
    S.bc = b.state;
    S.customers = b.customers;
  }

  function renderSettings() {
    const s = S.store;
    const a = S.admins;
    const on = s.accepting;
    const panel = `<div class="card"><h3 class="card__title">${t('panel')}</h3>
      <div class="field" style="margin-top:12px"><span class="field__label">${t('panel_lang')}</span>
      <div class="segment" style="margin-top:0">${['uz', 'ru'].map((l) => `<button class="${S.lang === l ? 'is-active' : ''}" data-action="lang" data-lang="${l}">${l === 'uz' ? "O'zbekcha" : 'Русский'}</button>`).join('')}</div></div>
      <div class="small muted">${t('desktop_hint')}</div>
      ${IN_TG ? '' : `<button class="btn btn--ghost btn--block" style="margin-top:12px" data-action="logout">${t('logout')}</button>`}</div>`;
    const loc = s.location || {};
    const pause = `<div class="card pause-card ${on ? '' : 'is-paused'}">
      <div class="pause-card__icon">${on ? '🟢' : '⏸'}</div>
      <div class="grow"><div class="card__title">${on ? t('accepting_on') : t('accepting_off')}</div>
        <div class="small muted">${on ? t('accepting_sub_on') : t('accepting_sub_off')}</div></div>
      <label class="switch"><input type="checkbox" data-toggle="accepting" ${on ? 'checked' : ''}><span></span></label></div>`;
    if (!isFull()) {
      $('#page').innerHTML = pause + `<div class="notice" style="margin-top:12px">${t('cashier_settings_note')}</div>` + panel;
      return;
    }

    const form = `<form id="sform" onsubmit="return false">
      <div class="card"><h3 class="card__title" style="margin-bottom:12px">${t('restaurant')}</h3>
        ${field(t('f_name'), inp('name', s.name, 'maxlength="60"'))}
        <div class="grid2">${field(t('f_tagline_uz'), inp('tagline.uz', s.tagline.uz, 'maxlength="120"'))}${field(t('f_tagline_ru'), inp('tagline.ru', s.tagline.ru, 'maxlength="120"'))}</div>
        ${field(t('f_about_uz'), area('about.uz', s.about.uz, 'maxlength="600" rows="3"'))}
        ${field(t('f_about_ru'), area('about.ru', s.about.ru, 'maxlength="600" rows="3"'))}
        <div class="grid2">${field(t('f_phone'), inp('phone', s.phone, 'type="tel" maxlength="30"'))}${field(t('f_support_username'), inp('support_username', s.support_username, 'maxlength="41" placeholder="@username"'))}</div>
        ${field(t('f_instagram'), inp('instagram', s.instagram, 'maxlength="60" placeholder="ayvaburgers"'))}
        ${field(t('f_address_uz'), inp('address.uz', s.address.uz, 'maxlength="200"'))}
        ${field(t('f_address_ru'), inp('address.ru', s.address.ru, 'maxlength="200"'))}
        <div class="field"><span class="field__label">${t('f_location')}</span>
          <div class="grid2"><input class="input" name="location.lat" type="number" step="any" data-num placeholder="${t('f_lat')}" value="${loc.lat ?? ''}">
          <input class="input" name="location.lon" type="number" step="any" data-num placeholder="${t('f_lon')}" value="${loc.lon ?? ''}"></div>
          <div class="row-gap" style="margin-top:8px"><button type="button" class="btn btn--sm" data-action="my-location">${t('my_location')}</button>
          ${loc.lat ? `<a class="btn btn--sm btn--ghost" target="_blank" rel="noopener" href="https://yandex.uz/maps/?pt=${loc.lon},${loc.lat}&z=17&l=map">${t('check_map')}</a>` : ''}</div>
        </div>
      </div>
      <div class="card"><h3 class="card__title" style="margin-bottom:12px">${t('hours')}</h3>
        <div class="grid2">${field(t('f_open'), `<input class="input" type="time" name="hours.open" value="${esc(s.hours.open)}">`)}${field(t('f_close'), `<input class="input" type="time" name="hours.close" value="${esc(s.hours.close)}">`)}</div>
        <div class="field__hint" style="margin-top:-4px">${t('hours_hint')}</div>
      </div>
      <div class="card"><h3 class="card__title">${t('delivery')}</h3>
        ${switchRow('delivery.enabled', s.delivery.enabled, t('delivery_on'), '')}
        <div class="grid2">${field(t('f_fee'), numInp('delivery.fee', s.delivery.fee))}${field(t('f_free_from'), numInp('delivery.free_from', s.delivery.free_from), t('free_hint'))}</div>
        <div class="grid2">${field(t('f_min_order'), numInp('delivery.min_order', s.delivery.min_order))}${field(t('f_eta'), inp('delivery.eta', s.delivery.eta, 'maxlength="20" placeholder="40–60"'))}</div>
      </div>
      <div class="card"><h3 class="card__title">${t('pickup')}</h3>
        ${switchRow('pickup.enabled', s.pickup.enabled, t('pickup_on'), '')}
        <div class="grid2">${field(t('f_min_order'), numInp('pickup.min_order', s.pickup.min_order))}${field(t('f_eta'), inp('pickup.eta', s.pickup.eta, 'maxlength="20" placeholder="15–20"'))}</div>
      </div>
      <div class="card" style="padding-bottom:4px"><h3 class="card__title">${t('payments')}</h3>
        ${switchRow('payments.cash', s.payments.cash, '💵 ' + t('cash'), '')}
        ${switchRow('payments.click', false, 'Click', `<span class="tag">${t('soon')}</span>`, 'disabled')}
        ${switchRow('payments.payme', false, 'Payme', `<span class="tag">${t('soon')}</span>`, 'disabled')}
      </div>
    </form>`;

    const ownerRows = a.owners.map((o) => `<div class="admin-row"><span class="avatar">👑</span><div class="grow"><b>${esc(o.name || 'ID ' + o.user_id)}</b>
      ${o.user_id === a.me ? `<span class="small muted">(${t('you')})</span>` : ''}<div class="small muted">${o.user_id} · ${t('role_owner')}</div></div></div>`).join('');
    const roleSelect = (x) => `<select class="input role-select" data-role-select data-id="${x.user_id}" data-name="${esc(x.name)}">
      ${['admin', 'cashier'].map((r) => `<option value="${r}" ${x.role === r ? 'selected' : ''}>${t('role_' + r)}</option>`).join('')}</select>`;
    const adminRows = a.admins.map((x) => `<div class="admin-row"><span class="avatar">${x.role === 'cashier' ? '🧾' : esc((x.name || '?').slice(0, 1).toUpperCase())}</span>
      <div class="grow"><b>${esc(x.name || 'ID ' + x.user_id)}</b>${x.user_id === a.me ? ` <span class="small muted">(${t('you')})</span>` : ''}
        <div class="small muted">${x.user_id}${a.can_manage ? '' : ' · ' + t('role_' + x.role)}</div></div>
      ${a.can_manage ? `${roleSelect(x)}<button class="icon-btn" data-action="remove-admin" data-id="${x.user_id}" data-name="${esc(x.name || x.user_id)}" aria-label="${t('delete')}">${ICON.close}</button>` : ''}</div>`).join('');
    const admins = `<div class="card"><h3 class="card__title">${t('admins')}</h3>
      ${ownerRows}${adminRows}
      ${a.can_manage ? `<form id="aform" onsubmit="return false" style="margin-top:12px">
        <div class="grid2">${field(t('f_user_id'), `<input class="input" name="user_id" type="number" inputmode="numeric" data-num>`)}${field(t('f_admin_name'), inp('name', '', 'maxlength="60"'))}</div>
        <div class="field__hint" style="margin:-4px 2px 10px">${t('admin_id_hint')}</div>
        <div class="field"><span class="field__label">${t('f_role')}</span><input type="hidden" name="role" value="admin">
          <div class="role-pick">${['admin', 'cashier'].map((r) => `<button type="button" class="${r === 'admin' ? 'is-active' : ''}" data-action="pick-role" data-role="${r}">
            <b>${t('role_' + r)}</b><span>${t('role_' + r + '_sub')}</span></button>`).join('')}</div></div>
        <button class="btn btn--block" data-action="add-admin">${ICON.plus.replace('<svg', '<svg width="16" height="16"')} ${t('add_admin')}</button></form>`
        : `<div class="small muted" style="margin-top:8px">${t('only_owner')}</div>`}
      <div class="small muted" style="margin-top:10px">${t('owners_hint')}</div></div>`;

    const bc = S.bc || {};
    const bcBody = bc.running
      ? `<div class="small">${t('broadcast_progress', { ok: bc.ok, total: bc.total })}</div><div class="progress"><div style="width:${bc.total ? (bc.ok + bc.fail) * 100 / bc.total : 0}%"></div></div>`
      : `<form id="bcform" onsubmit="return false">
          ${field(t('f_text'), area('text', '', 'rows="4" maxlength="4096"'))}
          ${field(t('f_image') + ` <span class="muted">(${t('optional')})</span>`, uploaderHtml('image', '', '16 / 9', ''))}
          ${switchRow('menu_button', true, t('f_menu_button'), '')}
          <button class="btn btn--primary btn--block" data-action="send-broadcast">${t('send')} · ${num(S.customers)}</button>
          ${bc.finished_at ? `<div class="small muted" style="margin-top:8px">${t('broadcast_done', { ok: bc.ok, fail: bc.fail })}</div>` : ''}
        </form>`;
    const broadcast = `<div class="card"><h3 class="card__title">${t('broadcast')}</h3><div class="card__sub" style="margin-top:4px">${t('broadcast_hint')}</div>${bcBody}</div>`;

    $('#page').innerHTML = pause + form + admins + broadcast + panel;
  }

  function renderSavebar() {
    let bar = $('#savebar');
    if (S.page === 'settings' && S.dirty) {
      if (!bar) {
        bar = document.createElement('div');
        bar.id = 'savebar';
        bar.className = 'savebar';
        document.body.appendChild(bar);
      }
      bar.innerHTML = `<button class="btn btn--ghost" data-action="discard">${t('cancel')}</button><button class="btn btn--primary" data-action="save-store">${t('save')}</button>`;
    } else if (bar) bar.remove();
  }

  async function saveStore() {
    const root = $('#sform');
    const f = readForm(root);
    const lat = f.location.lat, lon = f.location.lon;
    f.location = lat == null && lon == null ? null : { lat, lon };
    delete f.payments.click;
    delete f.payments.payme;
    ['fee', 'free_from', 'min_order'].forEach((k) => { if (f.delivery[k] == null) f.delivery[k] = 0; });
    if (f.pickup.min_order == null) f.pickup.min_order = 0;
    try {
      const d = await api('PATCH', '/api/admin/store', f);
      S.store = d.store;
      S.dirty = false;
      toast(t('saved'), 'ok');
      renderPage();
    } catch (e) {
      const fld = e.field && ({ hours: 'hours.open', location: 'location.lat', delivery: 'delivery.enabled' }[e.field] || e.field);
      if (fld) markInvalid(root, fld);
      fail(e);
    }
  }

  async function setAccepting(value, input) {
    if (!value && !(await confirmBox(t('confirm_pause')))) { input.checked = true; return; }
    try {
      const d = await api('PATCH', '/api/admin/store', { accepting: value });
      S.store.accepting = d.store.accepting;
      haptic(value ? 'success' : 'warning');
      const keepDirty = S.dirty;
      renderSettings();
      S.dirty = keepDirty;
      renderSavebar();
    } catch (e) { input.checked = !value; fail(e); }
  }

  let bcTimer = null;
  async function sendBroadcast() {
    const root = $('#bcform');
    const f = readForm(root);
    if (!f.text.trim() && !f.image) { markInvalid(root, 'text'); return toast(`${t('f_text')}: ${t('e_required')}`, 'error'); }
    if (!(await confirmBox(t('broadcast_confirm', { n: num(S.customers) })))) return;
    try {
      const d = await api('POST', '/api/admin/broadcast', { text: f.text.trim(), image: f.image, menu_button: f.menu_button });
      S.bc = d.state;
      renderSettings();
      clearInterval(bcTimer);
      bcTimer = setInterval(async () => {
        try {
          const b = await api('GET', '/api/admin/broadcast');
          S.bc = b.state;
          if (S.page === 'settings' && !S.dirty) renderSettings();
          if (!b.state.running) { clearInterval(bcTimer); toast(t('broadcast_done', { ok: b.state.ok, fail: b.state.fail }), 'ok'); }
        } catch (_) { clearInterval(bcTimer); }
      }, 1500);
    } catch (e) { fail(e); }
  }

  function myLocation() {
    if (!navigator.geolocation) return toast(t('e_generic'), 'error');
    navigator.geolocation.getCurrentPosition((p) => {
      $('[name="location.lat"]').value = p.coords.latitude.toFixed(6);
      $('[name="location.lon"]').value = p.coords.longitude.toFixed(6);
      S.dirty = true;
      renderSavebar();
    }, () => toast(t('e_generic'), 'error'), { enableHighAccuracy: true, timeout: 10000 });
  }

  async function addAdmin() {
    const root = $('#aform');
    const f = readForm(root);
    if (!f.user_id) { markInvalid(root, 'user_id'); return toast(`${t('f_user_id')}: ${t('e_required')}`, 'error'); }
    try {
      await api('POST', '/api/admin/admins', { user_id: f.user_id, name: f.name.trim(), role: f.role });
      S.admins = await api('GET', '/api/admin/admins');
      toast(t('saved'), 'ok');
      renderSettings();
    } catch (e) { fail(e); }
  }

  async function setRole(el) {
    try {
      await api('POST', '/api/admin/admins', { user_id: Number(el.dataset.id), name: el.dataset.name || '', role: el.value });
      S.admins = await api('GET', '/api/admin/admins');
      toast(t('role_changed'), 'ok');
      renderSettings();
    } catch (e) { fail(e); renderSettings(); }
  }

  async function removeAdmin(id, name) {
    if (!(await confirmBox(t('confirm_remove_admin', { name })))) return;
    try {
      await api('DELETE', `/api/admin/admins/${id}`);
      S.admins = await api('GET', '/api/admin/admins');
      renderSettings();
    } catch (e) { fail(e); }
  }

  const LOADERS = {
    orders: () => loadOrders(),
    menu: () => loadMenu(),
    promos: () => loadPromos(),
    stats: () => loadStats(),
    settings: () => loadSettings(),
  };
  const RENDERERS = { orders: renderOrders, menu: renderMenu, promos: renderPromos, stats: renderStats, settings: renderSettings };

  // ================================================================ sheet
  function openSheet(view) { S.sheets.push(view); renderSheet(); haptic('light'); }
  function renderSheet(isStatic) {
    const el = $('#sheet');
    const v = S.sheets[S.sheets.length - 1];
    if (!v) { el.hidden = true; el.innerHTML = ''; updateBack(); return; }
    const wasOpen = !el.hidden;
    el.innerHTML = `<div class="sheet__backdrop" data-action="sheet-close-all"></div>
      <div class="sheet__panel" role="dialog" aria-modal="true">
        <div class="sheet__head">${S.sheets.length > 1 ? `<button class="icon-btn" data-action="sheet-back" aria-label="back">${ICON.back}</button>` : ''}
          <h2>${v.title}</h2><button class="icon-btn" data-action="sheet-close-all" aria-label="${t('close')}">${ICON.close}</button></div>
        <div class="sheet__body">${v.body()}</div>
        ${v.foot ? `<div class="sheet__foot">${v.foot()}</div>` : ''}
      </div>`;
    if (wasOpen || isStatic) $$('.sheet__panel, .sheet__backdrop', el).forEach((n) => { n.style.animation = 'none'; });
    el.hidden = false;
    if (v.mount) v.mount(el);
    updateBack();
  }
  function closeSheet(all) {
    if (all) S.sheets = []; else S.sheets.pop();
    renderSheet(true);
  }

  // ================================================================ events
  document.addEventListener('click', async (e) => {
    if (e.target.closest('.switch')) return; // o'tkazgichlar "change" orqali
    const el = e.target.closest('[data-action]');
    if (!el) return;
    const a = el.dataset.action;
    const id = el.dataset.id;
    switch (a) {
      case 'nav': go(el.dataset.page); break;
      // orders
      case 'otab': S.orders.tab = el.dataset.tab; S.orders.q = ''; await loadOrders().catch(fail); renderOrders(); break;
      case 'hist': S.orders.hist = el.dataset.h; await loadOrders().catch(fail); renderOrders(); break;
      case 'more-orders': await loadOrders(true).catch(fail); renderOrders(); break;
      case 'ost': el.disabled = true; await setOrderStatus(Number(id), el.dataset.st); break;
      // menu
      case 'mfilter': S.menuFilter = el.dataset.cat; renderMenu(); haptic('select'); break;
      case 'reorder-toggle': S.reorder = !S.reorder; renderMenu(); break;
      case 'move-product': await moveProduct(id, Number(el.dataset.dir)); break;
      case 'edit-product': openProductForm(id); break;
      case 'new-product': openProductForm(null, { cat: el.dataset.cat }); break;
      case 'save-product': await saveProduct(id); break;
      case 'delete-product': await deleteProduct(id); break;
      case 'pick-badge':
        $$('.badge-pick button').forEach((b) => b.classList.toggle('is-active', b === el));
        $('#pform [name="badge"]').value = el.dataset.badge; haptic('select'); break;
      case 'pct': {
        const root = $('#pform');
        const price = Number($('[name="price"]', root).value) || 0;
        if (price) $('[name="promo_price"]', root).value = Math.round(price * (100 - Number(el.dataset.pct)) / 100 / 100) * 100;
        updatePromoPreview(root); haptic('select'); break;
      }
      case 'categories': openCategories(); break;
      case 'edit-category': if (!e.target.closest('.icon-btn')) openCategoryForm(id); break;
      case 'new-category': openCategoryForm(null); break;
      case 'save-category': await saveCategory(id); break;
      case 'delete-category': await deleteCategory(id); break;
      case 'move-category': await moveCategory(id, Number(el.dataset.dir)); break;
      case 'pick-role':
        $$('.role-pick button').forEach((b) => b.classList.toggle('is-active', b === el));
        $('#aform [name="role"]').value = el.dataset.role; haptic('select'); break;
      case 'pick-icon':
        $$('.icon-pick button').forEach((b) => b.classList.toggle('is-active', b === el));
        $('#cform [name="icon"]').value = el.dataset.icon; haptic('select'); break;
      // uploader
      case 'upload-pick': el.closest('[data-uploader]').querySelector('[data-file]').click(); break;
      case 'upload-clear': setUploader(el.closest('[data-uploader]'), ''); break;
      // promos
      case 'new-banner': openBannerForm(null); break;
      case 'edit-banner': if (!e.target.closest('.icon-btn')) openBannerForm(id); break;
      case 'save-banner': await saveBanner(id); break;
      case 'delete-banner': await deleteBanner(id); break;
      case 'move-banner': await moveBanner(id, Number(el.dataset.dir)); break;
      case 'new-discount': openDiscountPicker(); break;
      case 'pick-discount': S.sheets.pop(); openProductForm(id, { promo: true }); break;
      // stats
      case 'sdays': S.stats.days = Number(el.dataset.days); await loadStats().catch(fail); renderStats(); break;
      case 'stable': S.stats.table = !S.stats.table; renderStats(); break;
      // settings
      case 'save-store': await saveStore(); break;
      case 'discard': S.dirty = false; renderPage(); break;
      case 'my-location': myLocation(); break;
      case 'add-admin': await addAdmin(); break;
      case 'remove-admin': await removeAdmin(id, el.dataset.name); break;
      case 'send-broadcast': await sendBroadcast(); break;
      case 'lang':
        S.lang = el.dataset.lang;
        try { localStorage.setItem(LANG_KEY, S.lang); } catch (_) { /* */ }
        document.documentElement.lang = S.lang;
        renderNav(); renderTopbar(); renderPage(); break;
      case 'logout': await api('POST', '/api/admin/logout').catch(() => null); location.reload(); break;
      // sheet
      case 'sheet-back': closeSheet(); break;
      case 'sheet-close-all': closeSheet(true); break;
      default: break;
    }
  });

  document.addEventListener('change', (e) => {
    const el = e.target;
    if (el.dataset.toggle === 'available') toggleAvailable(el.dataset.id, el.checked, el);
    else if (el.dataset.toggle === 'accepting') setAccepting(el.checked, el);
    else if (el.dataset.roleSelect !== undefined) setRole(el);
    else if (el.dataset.promoToggle !== undefined) {
      const box = $('#promo-fields');
      box.hidden = !el.checked;
      if (el.checked) $('[name="promo_price"]', box).focus();
    } else if (el.matches('[data-file]') && el.files && el.files[0]) doUpload(el.closest('[data-uploader]'), el.files[0]);
    if (el.closest('#sform')) { S.dirty = true; renderSavebar(); }
  });

  let searchTimer;
  document.addEventListener('input', (e) => {
    const el = e.target;
    if (el.closest('#sform')) { if (!S.dirty) { S.dirty = true; renderSavebar(); } return; }
    if (el.dataset.live !== undefined) { updatePromoPreview($('#pform')); return; }
    const kind = el.dataset.input;
    if (kind === 'menu-q') {
      S.menuQuery = el.value;
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => {
        const pos = el.selectionStart;
        renderMenu();
        const again = $('[data-input="menu-q"]');
        again.focus();
        try { again.setSelectionRange(pos, pos); } catch (_) { /* */ }
      }, 200);
    } else if (kind === 'order-q') {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(async () => {
        S.orders.q = el.value.trim();
        await loadOrders().catch(fail);
        renderOrders();
        const again = $('[data-input="order-q"]');
        again.focus();
        try { again.setSelectionRange(again.value.length, again.value.length); } catch (_) { /* */ }
      }, 350);
    } else if (kind === 'pick-q') {
      const q = el.value.trim().toLowerCase();
      $$('#pick-list .prow').forEach((row) => { row.hidden = q && !row.textContent.toLowerCase().includes(q); });
    }
  });

  document.addEventListener('pointerover', (e) => { const s = e.target.closest('.chart__slot'); if (s) showTip(s); });
  document.addEventListener('pointerout', (e) => { if (e.target.closest('.chart__slot')) hideTip(); });
  document.addEventListener('focusin', (e) => { if (e.target.matches('.chart__slot')) showTip(e.target); });
  document.addEventListener('focusout', (e) => { if (e.target.matches('.chart__slot')) hideTip(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && S.sheets.length) closeSheet(); });
  window.addEventListener('hashchange', () => { const p = location.hash.slice(1); if (p && p !== S.page) go(p, { push: false }); });
  window.addEventListener('beforeunload', (e) => { if (S.dirty) { e.preventDefault(); e.returnValue = ''; } });

  // ================================================================ init
  function screen(title, text) {
    $('#nav').hidden = true;
    $('#topbar').innerHTML = '';
    $('#page').innerHTML = `<div class="center-screen"><div><img src="/static/img/logo.svg" alt=""><h1>${title}</h1><p>${text}</p></div></div>`;
  }

  async function init() {
    applyTheme();
    setupTelegram();
    try { S.lang = localStorage.getItem(LANG_KEY) || ''; } catch (_) { S.lang = ''; }
    try {
      S.me = await api('GET', '/api/admin/me');
    } catch (e) {
      S.lang = S.lang || 'uz';
      if (e.status === 403 && e.user_id) return screen(t('forbidden_title'), esc(t('forbidden_text', { id: e.user_id })));
      if (e.status === 401 || e.status === 403) {
        const expired = new URLSearchParams(location.search).get('login') === 'expired';
        return screen(t('login_title'), expired ? t('login_expired') : t('login_text'));
      }
      return screen('⚠️', esc(errText(e)));
    }
    if (!S.lang) S.lang = S.me.lang === 'ru' ? 'ru' : 'uz';
    document.documentElement.lang = S.lang;
    if (location.search) history.replaceState(null, '', location.pathname + location.hash);
    await go(location.hash.slice(1) || 'orders');
    if (S.page !== 'orders') api('GET', '/api/admin/orders?tab=active').then((d) => trackActive(d.orders, false)).catch(() => null);
    setInterval(poll, 15000);
  }

  init();
})();
