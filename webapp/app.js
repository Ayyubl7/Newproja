/* Ayva Burgers — Telegram Mini App (framework'siz, tez yuklanadi) */
(() => {
  'use strict';

  const tg = window.Telegram && window.Telegram.WebApp;
  const IN_TG = !!(tg && tg.initData);
  const params = new URLSearchParams(location.search);
  const CART_KEY = 'ayva_cart_v2';
  const DRAFT_KEY = 'ayva_checkout_v1';

  // ---------------------------------------------------------------- i18n
  const I18N = {
    uz: {
      cur: "so'm", pcs: 'ta', min: 'daqiqa', from: 'dan',
      open: 'Ochiq', closed: 'Yopiq', paused_chip: 'Pauza',
      closed_banner: "Hozir yopiqmiz. Ish vaqti: {hours}. Menyuni ko'rishingiz mumkin — buyurtmalar ish vaqtida qabul qilinadi.",
      paused_banner: "Hozir buyurtmalar vaqtincha qabul qilinmayapti. Menyuni ko'rishingiz mumkin — tez orada qaytamiz!",
      promo_section: '🔥 Aksiyalar', hero_kicker: 'Bizning hit',
      pill_eta: '{eta} daq', pill_fee: 'Yetkazish {fee}', pill_free_delivery: 'Yetkazish bepul', pill_free_from: '{amount} dan bepul',
      sold_out: 'Tugadi', badge_hit: 'Hit', badge_new: 'Yangi', badge_spicy: 'Achchiq',
      add: "Qo'shish", choose: 'Tanlash', add_to_cart: 'Savatga',
      cart: 'Savat', view_cart: "Savatni ko'rish", clear: 'Tozalash',
      empty_title: "Savat hozircha bo'sh", empty_sub: "Menyudan o'zingizga yoqqan taomni tanlang", to_menu: 'Menyuga qaytish',
      upsell: "Yana nimadir qo'shamizmi?", free_left: 'Bepul yetkazishgacha yana <b>{amount}</b>', free_ok: '🎉 Yetkazib berish bepul!',
      checkout: 'Rasmiylashtirish', subtotal: 'Mahsulotlar', delivery: 'Yetkazib berish', total: 'Jami', free: 'Bepul',
      pickup: 'Olib ketish', how: 'Qanday olasiz?',
      where_delivery: 'Yetkazish manzili', where_pickup: "O'zim olib ketaman", where_none_label: 'Qayerga yetkazamiz?', where_none: 'Lokatsiyani yuboring',
      addr_title: 'Manzil', loc_from_tg: 'Telegram orqali yuborilgan lokatsiya', loc_change: 'Boshqa lokatsiya yuborish',
      loc_send: 'Lokatsiyani Telegram orqali yuborish', loc_empty_title: 'Lokatsiya hali yuborilmagan',
      loc_empty_sub: "Tugmani bosing — bot chatida «📍 Lokatsiyani yuborish» tugmasi chiqadi. Yuborganingizdan keyin buyurtma shu yerdan davom etadi.",
      loc_type_instead: "yoki manzilni qo'lda yozing", address_ph: "Ko'cha, uy, mo'ljal",
      details: 'Uy, podyezd, qavat, xonadon', details_ph: '12-uy, 2-podyezd, 3-qavat, 45-xonadon',
      loc_tg_only: 'Bu tugma faqat Telegram ichida ishlaydi', loc_going: 'Bot chatida lokatsiyangizni yuboring 👇',
      pickup_from: 'Olib ketish manzili', pickup_eta: "Taxminan {eta} daqiqada tayyor bo'ladi",
      you: "Ma'lumotlaringiz", name: 'Ism', phone: 'Telefon', phone_missing: 'Raqam kiritilmagan', phone_send: 'Yuborish',
      phone_ph: '+998 90 123 45 67', name_ph: 'Ismingiz', phone_denied: 'Raqam yuborilmadi',
      comment: 'Izoh', comment_ph: "Masalan: qo'ng'iroq qiling, ketchupsiz",
      payment: "To'lov usuli", pay_cash: 'Naqd pul', pay_cash_sub: 'Kuryerga yoki kassada', pay_click_sub: "Onlayn to'lov", pay_payme_sub: "Onlayn to'lov", soon: 'Tez orada',
      place: 'Buyurtma berish', min_order: 'Minimal buyurtma: {amount}',
      success_title: 'Buyurtma #{id} qabul qilindi!', success_sub: 'Operatorimiz tez orada tasdiqlaydi. Buyurtma holatini bot xabarlarida kuzatib boring.',
      order_no: 'Buyurtma', eta_delivery: 'Yetkazish vaqti', eta_pickup: "Tayyor bo'ladi", close: 'Yopish',
      open_in_tg: 'Menyuni Telegram bot orqali oching', open_in_tg_sub: 'Botdagi «🍔 Menyuni ochish» tugmasini bosing.', retry: 'Qayta urinish',
      err_generic: "Xatolik yuz berdi. Qayta urinib ko'ring.", err_network: "Internet bilan aloqa yo'q. Qayta urinib ko'ring.",
      err_closed: 'Hozir yopiqmiz — buyurtma ish vaqtida qabul qilinadi.', err_paused: 'Buyurtmalar vaqtincha qabul qilinmayapti',
      err_bad_phone: "Telefon raqamni kiriting", err_bad_address: 'Lokatsiyani yuboring yoki manzilni yozing',
      err_unavailable: '«{name}» tugab qoldi — savatdan olib tashlandi', err_min_order: 'Minimal buyurtma: {amount}',
      err_too_fast: "Biroz kuting va qayta urinib ko'ring", err_unauthorized: 'Ilovani bot orqali qayta oching',
      err_payment_unavailable: "Bu to'lov usuli hozir mavjud emas", err_empty_cart: "Savat bo'sh",
      err_type_disabled: 'Bu usul hozir ishlamayapti', err_bad_location: "Lokatsiya noto'g'ri",
      err_bad_variant: "Menyu yangilangan — mahsulotni qaytadan tanlang", err_cannot_message: "Botga /start yozing va qayta urinib ko'ring",
    },
    ru: {
      cur: 'сум', pcs: 'шт', min: 'мин', from: 'от',
      open: 'Открыто', closed: 'Закрыто', paused_chip: 'Пауза',
      closed_banner: 'Сейчас мы закрыты. Время работы: {hours}. Меню можно посмотреть — заказы принимаем в рабочее время.',
      paused_banner: 'Сейчас заказы временно не принимаются. Меню можно посмотреть — скоро вернёмся!',
      promo_section: '🔥 Акции', hero_kicker: 'Наш хит',
      pill_eta: '{eta} мин', pill_fee: 'Доставка {fee}', pill_free_delivery: 'Доставка бесплатно', pill_free_from: 'Бесплатно от {amount}',
      sold_out: 'Закончился', badge_hit: 'Хит', badge_new: 'Новинка', badge_spicy: 'Острое',
      add: 'Добавить', choose: 'Выбрать', add_to_cart: 'В корзину',
      cart: 'Корзина', view_cart: 'Корзина', clear: 'Очистить',
      empty_title: 'Корзина пока пуста', empty_sub: 'Выберите что-нибудь вкусное в меню', to_menu: 'Вернуться в меню',
      upsell: 'Добавим что-нибудь?', free_left: 'До бесплатной доставки ещё <b>{amount}</b>', free_ok: '🎉 Доставка бесплатно!',
      checkout: 'Оформление', subtotal: 'Товары', delivery: 'Доставка', total: 'Итого', free: 'Бесплатно',
      pickup: 'Самовывоз', how: 'Как получить?',
      where_delivery: 'Адрес доставки', where_pickup: 'Заберу сам', where_none_label: 'Куда доставить?', where_none: 'Отправьте локацию',
      addr_title: 'Адрес', loc_from_tg: 'Локация, отправленная через Telegram', loc_change: 'Отправить другую локацию',
      loc_send: 'Отправить локацию через Telegram', loc_empty_title: 'Локация ещё не отправлена',
      loc_empty_sub: 'Нажмите кнопку — в чате бота появится «📍 Отправить локацию». После отправки заказ продолжится отсюда.',
      loc_type_instead: 'или впишите адрес вручную', address_ph: 'Улица, дом, ориентир',
      details: 'Дом, подъезд, этаж, квартира', details_ph: 'дом 12, подъезд 2, этаж 3, кв. 45',
      loc_tg_only: 'Эта кнопка работает только в Telegram', loc_going: 'Отправьте локацию в чате бота 👇',
      pickup_from: 'Адрес самовывоза', pickup_eta: 'Будет готов примерно через {eta} мин',
      you: 'Ваши данные', name: 'Имя', phone: 'Телефон', phone_missing: 'Номер не указан', phone_send: 'Отправить',
      phone_ph: '+998 90 123 45 67', name_ph: 'Ваше имя', phone_denied: 'Номер не отправлен',
      comment: 'Комментарий', comment_ph: 'Например: позвоните, без кетчупа',
      payment: 'Способ оплаты', pay_cash: 'Наличные', pay_cash_sub: 'Курьеру или на кассе', pay_click_sub: 'Онлайн-оплата', pay_payme_sub: 'Онлайн-оплата', soon: 'Скоро',
      place: 'Заказать', min_order: 'Минимальный заказ: {amount}',
      success_title: 'Заказ #{id} принят!', success_sub: 'Оператор скоро подтвердит заказ. Следите за статусом в сообщениях бота.',
      order_no: 'Заказ', eta_delivery: 'Время доставки', eta_pickup: 'Будет готов', close: 'Закрыть',
      open_in_tg: 'Откройте меню через Telegram-бот', open_in_tg_sub: 'Нажмите кнопку «🍔 Открыть меню» в боте.', retry: 'Повторить',
      err_generic: 'Произошла ошибка. Попробуйте ещё раз.', err_network: 'Нет связи с интернетом. Попробуйте ещё раз.',
      err_closed: 'Сейчас мы закрыты — заказы принимаем в рабочее время.', err_paused: 'Заказы временно не принимаются',
      err_bad_phone: 'Укажите номер телефона', err_bad_address: 'Отправьте локацию или впишите адрес',
      err_unavailable: '«{name}» закончился — убрали из корзины', err_min_order: 'Минимальный заказ: {amount}',
      err_too_fast: 'Подождите немного и попробуйте снова', err_unauthorized: 'Откройте приложение заново через бота',
      err_payment_unavailable: 'Этот способ оплаты сейчас недоступен', err_empty_cart: 'Корзина пуста',
      err_type_disabled: 'Этот способ сейчас недоступен', err_bad_location: 'Неверная локация',
      err_bad_variant: 'Меню обновилось — выберите товар заново', err_cannot_message: 'Напишите боту /start и попробуйте снова',
    },
  };

  const ICON = {
    plus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>',
    minus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="round"><path d="M5 12h14"/></svg>',
    close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    back: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5l-7 7 7 7"/></svg>',
    edit: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20h4L19 9l-4-4L4 16z"/></svg>',
    tg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M21.5 4.3 2.9 11.5c-1.3.5-1.3 1.2-.2 1.6l4.8 1.5 1.8 5.6c.2.6.1.9.8.9.5 0 .7-.2 1-.5l2.3-2.2 4.8 3.5c.9.5 1.5.2 1.7-.8l3.1-14.6c.3-1.3-.5-1.9-1.5-1.4zM8.6 14.3l9.9-6.2c.5-.3.9-.1.5.2l-8.4 7.6-.3 3.6-1.7-5.2z"/></svg>',
    pin: '<svg class="loc-map__pin" viewBox="0 0 34 44"><path d="M17 43S2 26.5 2 16a15 15 0 0 1 30 0c0 10.5-15 27-15 27z" fill="#E2000D" stroke="#fff" stroke-width="2.5"/><circle cx="17" cy="16" r="5.5" fill="#fff"/></svg>',
  };

  // ---------------------------------------------------------------- state
  const state = {
    lang: params.get('lang') === 'ru' ? 'ru' : 'uz',
    store: null, categories: [], banners: [], products: new Map(), profile: {},
    cart: new Map(), // kalit: "id" yoki "id|variantIndex"
    view: 'loading', stack: [], menuScroll: 0,
    co: { type: 'delivery', name: '', phone: '', comment: '', details: '', address: '', payment: 'cash',
          editName: false, editPhone: false, typeAddress: false },
    submitting: false, lastOrder: null, sheet: null,
  };

  // ---------------------------------------------------------------- helpers
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const cssId = (s) => (window.CSS && CSS.escape ? CSS.escape(s) : s);
  function t(key, vars) {
    let s = (I18N[state.lang] && I18N[state.lang][key]) ?? I18N.uz[key] ?? key;
    if (vars) for (const k in vars) s = s.split('{' + k + '}').join(vars[k]);
    return s;
  }
  const L = (obj) => (obj && (obj[state.lang] || obj.uz || obj.ru)) || '';
  const num = (n) => String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
  const money = (n) => num(n) + ' ' + t('cur');
  const pill = (n, sale) => `<span class="price-pill ${sale ? 'price-pill--sale' : ''}">${num(n)} <small>${t('cur')}</small></span>`;

  const keyOf = (id, v) => (v === null || v === undefined ? id : `${id}|${v}`);
  function parseKey(key) {
    const i = key.lastIndexOf('|');
    return i < 0 ? { id: key, v: null } : { id: key.slice(0, i), v: Number(key.slice(i + 1)) };
  }
  function lineOf(key) {
    const { id, v } = parseKey(key);
    const p = state.products.get(id);
    if (!p) return null;
    const variant = v !== null ? p.variants[v] : null;
    return { p, v, variant, price: variant ? variant.price : p.price, old: variant ? variant.old_price : p.old_price };
  }

  function tgAtLeast(v) { return !!(tg && tg.isVersionAtLeast && tg.isVersionAtLeast(v)); }
  function haptic(kind) {
    if (!tgAtLeast('6.1') || !tg.HapticFeedback) return;
    try {
      if (['success', 'error', 'warning'].includes(kind)) tg.HapticFeedback.notificationOccurred(kind);
      else if (kind === 'select') tg.HapticFeedback.selectionChanged();
      else tg.HapticFeedback.impactOccurred(kind || 'light');
    } catch (_) { /* eski klientlar */ }
  }
  let toastTimer;
  function toast(msg, isError) {
    const el = $('#toast');
    el.textContent = msg;
    el.classList.toggle('toast--error', !!isError);
    el.classList.add('is-shown');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove('is-shown'), 3200);
    if (isError) haptic('error');
  }

  function categoryOf(p) { return state.categories.find((c) => c.id === p.category) || {}; }
  function imageOf(p) {
    if (p.image) return { src: /^(https?:\/\/|\/)/.test(p.image) ? p.image : '/static/' + p.image, photo: true };
    return { src: '/static/img/' + (categoryOf(p).icon || 'burger') + '.svg', photo: false };
  }
  function img(p, lazy) {
    const im = imageOf(p);
    return `<img src="${esc(im.src)}" alt="" ${im.photo ? '' : 'class="is-icon"'} ${lazy ? 'loading="lazy"' : ''} decoding="async">`;
  }

  // ---------------------------------------------------------------- API
  async function api(path, body) {
    const headers = {};
    if (tg && tg.initData) headers.Authorization = 'tma ' + tg.initData;
    const opts = { headers };
    if (body !== undefined) {
      opts.method = 'POST';
      headers['Content-Type'] = 'application/json';
      opts.body = JSON.stringify(body);
    }
    const res = await fetch(path, opts);
    let data = {};
    try { data = await res.json(); } catch (_) { /* bo'sh javob */ }
    return { status: res.status, data };
  }

  // ---------------------------------------------------------------- saqlash (savat va forma qoralamasi)
  function store(key, value) { try { localStorage.setItem(key, JSON.stringify(value)); } catch (_) { /* private */ } }
  function restore(key) { try { return JSON.parse(localStorage.getItem(key) || 'null'); } catch (_) { return null; } }
  function saveCart() { store(CART_KEY, Object.fromEntries(state.cart)); }
  function loadCart() {
    const raw = restore(CART_KEY) || {};
    state.cart.clear();
    for (const [key, qty] of Object.entries(raw)) {
      const line = lineOf(key);
      if (!line || !line.p.available || !Number.isInteger(qty) || qty < 1) continue;
      if (line.p.variants.length ? !line.variant : line.v !== null) continue;
      state.cart.set(key, Math.min(qty, 50));
    }
  }
  function saveDraft() {
    const c = state.co;
    store(DRAFT_KEY, { type: c.type, name: c.name, phone: c.phone, comment: c.comment, details: c.details, address: c.address, payment: c.payment });
  }

  const cartCount = () => { let n = 0; state.cart.forEach((q) => { n += q; }); return n; };
  const cartSubtotal = () => { let s = 0; state.cart.forEach((q, k) => { const l = lineOf(k); if (l) s += l.price * q; }); return s; };
  const qtyOfProduct = (id) => { let n = 0; state.cart.forEach((q, k) => { if (parseKey(k).id === id) n += q; }); return n; };

  function setQty(key, qty) {
    const line = lineOf(key);
    if (!line) return;
    const prev = state.cart.get(key) || 0;
    qty = Math.max(0, Math.min(50, qty));
    if (qty === prev) return;
    if (qty === 0) state.cart.delete(key); else state.cart.set(key, qty);
    saveCart();
    haptic(qty > prev ? 'light' : 'soft');
    refreshControls(line.p.id);
    if (state.view === 'cart') renderCart();
    if (state.view === 'checkout') renderCheckoutSummary();
    renderBottom();
  }

  // ---------------------------------------------------------------- theme / telegram
  function applyTheme() {
    const dark = IN_TG ? tg.colorScheme === 'dark' : !!(window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches);
    document.documentElement.dataset.theme = dark ? 'dark' : 'light';
    const bg = dark ? '#0B0B0B' : '#F3F1EE';
    if (tgAtLeast('6.1')) { try { tg.setHeaderColor('#0E0E0E'); tg.setBackgroundColor(bg); } catch (_) { /* */ } }
    if (tgAtLeast('7.10')) { try { tg.setBottomBarColor(bg); } catch (_) { /* */ } }
  }
  function setupTelegram() {
    if (!tg) return;
    try { tg.ready(); tg.expand(); } catch (_) { /* */ }
    if (tgAtLeast('7.7')) { try { tg.disableVerticalSwipes(); } catch (_) { /* */ } }
    if (tgAtLeast('6.1')) tg.BackButton.onClick(goBack);
    if (tg.onEvent) tg.onEvent('themeChanged', applyTheme);
  }
  function updateBackButton() {
    if (!IN_TG || !tgAtLeast('6.1')) return;
    if (state.sheet || ['cart', 'checkout'].includes(state.view)) tg.BackButton.show(); else tg.BackButton.hide();
  }

  // ---------------------------------------------------------------- navigation
  function show(view) { $$('.view').forEach((el) => el.classList.toggle('is-active', el.id === 'view-' + view)); }
  function go(view, push = true) {
    if (state.view === 'menu') state.menuScroll = window.scrollY;
    if (push && state.view !== view && ['menu', 'cart', 'checkout'].includes(state.view)) state.stack.push(state.view);
    state.view = view;
    if (view === 'cart') renderCart();
    if (view === 'checkout') renderCheckout();
    if (view === 'success') renderSuccess();
    if (view === 'menu') { refreshAllControls(); renderWhere(); }
    show(view);
    window.scrollTo(0, view === 'menu' ? state.menuScroll : 0);
    renderBottom();
    updateBackButton();
  }
  function goBack() {
    if (state.sheet) { closeSheet(); return; }
    if (state.view === 'success') { state.stack = []; go('menu', false); return; }
    go(state.stack.pop() || 'menu', false);
  }

  // ---------------------------------------------------------------- menu
  function priceLine(p) {
    const from = p.variants.length ? `<span class="from">${t('from')}</span>` : '';
    const old = p.old_price ? `<s class="price-old">${num(p.old_price)}</s>` : '';
    const main = pill(p.price, !!p.old_price);
    return state.lang === 'ru' ? from + main + old : main + from + old; // "20 000 so'm dan" / "от 20 000 сум"
  }

  function control(p, variant) {
    const id = esc(p.id);
    if (variant === 'sm') return ''; // savat qatorlari o'z stepperini chizadi
    if (!p.available) return `<button class="buy" disabled>${t('sold_out')}</button>`;
    if (p.variants.length) {
      const n = qtyOfProduct(p.id);
      return `<button class="buy ${n ? 'buy--chosen' : ''}" data-action="open" data-id="${id}"><span class="buy__icon">${ICON.plus}</span>${t('choose')}${n ? `<span class="buy__count">${n}</span>` : ''}</button>`;
    }
    const q = state.cart.get(p.id) || 0;
    if (!q) return `<button class="buy" data-action="inc" data-key="${id}"><span class="buy__icon">${ICON.plus}</span>${t('add')}</button>`;
    return `<div class="stepper stepper--block">
      <button data-action="dec" data-key="${id}" aria-label="-">${ICON.minus}</button><span>${q}</span>
      <button data-action="inc" data-key="${id}" aria-label="+">${ICON.plus}</button></div>`;
  }
  function refreshControls(id) {
    const p = state.products.get(id);
    if (p) $$(`[data-ctrl="${cssId(id)}"]`).forEach((el) => { el.innerHTML = control(p, 'block'); });
  }
  function refreshAllControls() { state.products.forEach((_, id) => refreshControls(id)); }

  function badges(p) {
    let html = '';
    if (p.badge && I18N.uz['badge_' + p.badge]) html += `<span class="badge badge--${esc(p.badge)}">${t('badge_' + p.badge)}</span>`;
    if (p.discount) html += `<span class="badge badge--sale">−${p.discount}%</span>`;
    return html;
  }

  function card(p) {
    return `<article class="card ${p.available ? '' : 'is-out'}" data-action="open" data-id="${esc(p.id)}">
      <div class="card__media">${badges(p)}${img(p, true)}</div>
      <div class="card__body">
        <div class="card__name">${esc(L(p.name))}</div>
        ${L(p.description) ? `<div class="card__desc">${esc(L(p.description))}</div>` : ''}
        <div class="card__foot">
          <div class="card__price">${priceLine(p)}</div>
          <div data-ctrl="${esc(p.id)}">${control(p, 'block')}</div>
        </div>
      </div>
    </article>`;
  }

  function whereHtml() {
    const s = state.store;
    const prof = state.profile;
    let icon = '📍', label = t('where_none_label'), value = t('where_none');
    if (state.co.type === 'pickup' && s.pickup.enabled) { icon = '🛍'; label = t('where_pickup'); value = L(s.address); }
    else if (prof.lat != null) { icon = '🚚'; label = t('where_delivery'); value = prof.address; }
    if (!s.delivery.enabled && !s.pickup.enabled) return '';
    return `<button class="where" data-action="where"><span class="where__icon">${icon}</span>
      <span class="where__text"><span class="where__label">${esc(label)}</span><br><span class="where__value">${esc(value)}</span></span>
      <span class="where__chev">›</span></button>`;
  }
  function renderWhere() { const el = $('#where-slot'); if (el && state.store) el.innerHTML = whereHtml(); }

  function heroHtml(all) {
    if (state.banners.length) return bannersHtml();
    const hero = all.find((p) => p.badge === 'hit' && p.available) || all.find((p) => p.available);
    if (!hero) return '';
    return `<div class="carousel"><div class="carousel__track"><div class="slide slide--plain" data-action="open" data-id="${esc(hero.id)}">
      <div class="slide__plain"><div class="slide__kicker">${t('hero_kicker')}</div><div class="slide__title">${esc(L(hero.name))}</div>
      <div class="slide__text">${t('from') === 'dan' ? `${money(hero.price)}${hero.variants.length ? 'dan' : ''}` : `${hero.variants.length ? 'от ' : ''}${money(hero.price)}`}</div></div>
      ${imageOf(hero).photo ? `<img class="slide__deco" src="${esc(imageOf(hero).src)}" alt="">` : ''}</div></div></div>`;
  }

  function renderMenu() {
    const s = state.store;
    const hours = !s.hours.open ? '' : s.hours.open === s.hours.close ? '24/7' : `${s.hours.open}–${s.hours.close}`;
    const all = Array.from(state.products.values());
    const promo = all.filter((p) => p.old_price && p.available);
    const cats = (promo.length ? [{ id: '__promo', name: { uz: t('promo_section'), ru: t('promo_section') } }] : []).concat(state.categories);
    const inCat = (c) => (c.id === '__promo' ? promo : all.filter((p) => p.category === c.id));

    const pills = [];
    if (hours) pills.push(`<span class="pill">🕒 <b>${esc(hours)}</b></span>`);
    if (s.delivery.enabled) {
      if (!s.delivery.fee) pills.push(`<span class="pill">🛵 <b>${t('pill_free_delivery')}</b></span>`);
      else pills.push(`<span class="pill">🛵 ${t('pill_fee', { fee: '<b>' + money(s.delivery.fee) + '</b>' })}</span>`);
      if (s.delivery.fee && s.delivery.free_from) pills.push(`<span class="pill">🎁 ${t('pill_free_from', { amount: '<b>' + money(s.delivery.free_from) + '</b>' })}</span>`);
      if (s.delivery.eta) pills.push(`<span class="pill">⏱ ${esc(t('pill_eta', { eta: s.delivery.eta }))}</span>`);
    }
    pills.push('<span class="pill">✅ <b>100% Halol</b></span>');

    const sections = cats.map((c) => {
      const items = inCat(c);
      if (!items.length) return '';
      return `<section class="section" id="cat-${esc(c.id)}" data-cat="${esc(c.id)}">
        <h2 class="section__title">${esc(L(c.name))}</h2><div class="grid">${items.map(card).join('')}</div></section>`;
    }).join('');

    $('#view-menu').innerHTML = `
      <header class="header">
        <div class="header__row">
          <img class="header__logo" src="/static/img/logo-light.png" alt="${esc(s.name)}">
          <span class="header__grow"></span>
          <span class="status-chip ${s.is_open ? '' : 'is-closed'}">${s.is_open ? t('open') : s.paused ? t('paused_chip') : t('closed')}</span>
        </div>
        <div class="header__tagline">${esc(L(s.tagline))}</div>
        <div id="where-slot">${whereHtml()}</div>
      </header>
      ${s.paused ? `<div class="notice">⏸ <span>${esc(t('paused_banner'))}</span></div>`
        : s.is_open ? '' : `<div class="notice">😴 <span>${esc(t('closed_banner', { hours }))}</span></div>`}
      ${heroHtml(all)}
      <div class="pills">${pills.join('')}</div>
      <nav class="tabs" id="tabs">${cats.filter((c) => inCat(c).length)
        .map((c, i) => `<button class="tab ${i === 0 ? 'is-active' : ''}" data-action="tab" data-cat="${esc(c.id)}">${esc(L(c.name))}</button>`).join('')}</nav>
      ${sections}
      <div class="footer-note">${esc(s.name)} · ${esc(s.phone || '')}</div>`;
  }

  // bannerlar (aksiya karuseli)
  function bannersHtml() {
    const slides = state.banners.map((b, i) => {
      const title = L(b.title), text = L(b.text);
      const inner = b.image
        ? `<img class="slide__img" src="${esc(b.image)}" alt="" ${i ? 'loading="lazy"' : ''}>${title || text ? `<div class="slide__shade">
            ${title ? `<div class="slide__title">${esc(title)}</div>` : ''}${text ? `<div class="slide__text">${esc(text)}</div>` : ''}</div>` : ''}`
        : `<div class="slide__plain"><div class="slide__kicker">${t('promo_section')}</div>
            <div class="slide__title">${esc(title)}</div>${text ? `<div class="slide__text">${esc(text)}</div>` : ''}</div>
            ${bannerDeco(b)}`;
      return `<div class="slide ${b.image ? '' : 'slide--plain'}" data-action="banner" data-type="${esc(b.link_type)}" data-target="${esc(b.link_id)}">${inner}</div>`;
    }).join('');
    const dots = state.banners.length > 1 ? `<div class="dots">${state.banners.map((_, i) => `<span class="${i ? '' : 'is-active'}"></span>`).join('')}</div>` : '';
    return `<div class="carousel"><div class="carousel__track" id="carousel">${slides}</div>${dots}</div>`;
  }
  function bannerDeco(b) {
    const p = b.link_type === 'product' ? state.products.get(b.link_id) : null;
    return p && imageOf(p).photo ? `<img class="slide__deco" src="${esc(imageOf(p).src)}" alt="">` : '';
  }
  let carouselTimer = 0;
  function setupCarousel() {
    const track = $('#carousel');
    clearInterval(carouselTimer);
    if (!track || state.banners.length < 2) return;
    const dots = $$('.dots span');
    const step = () => track.firstElementChild.offsetWidth + 10;
    const current = () => Math.round(track.scrollLeft / step());
    track.addEventListener('scroll', () => { const i = current(); dots.forEach((d, j) => d.classList.toggle('is-active', i === j)); }, { passive: true });
    let paused = false;
    track.addEventListener('touchstart', () => { paused = true; }, { passive: true });
    track.addEventListener('touchend', () => { setTimeout(() => { paused = false; }, 4000); }, { passive: true });
    carouselTimer = setInterval(() => {
      if (paused || state.view !== 'menu' || document.hidden) return;
      track.scrollTo({ left: ((current() + 1) % state.banners.length) * step(), behavior: 'smooth' });
    }, 5000);
  }
  function openBanner(type, target) {
    if (type === 'product' && state.products.has(target)) openSheet(target);
    else if (type === 'category' && document.getElementById('cat-' + target)) scrollToCat(target);
  }

  // scroll-spy
  let spyLock = 0, spyRaf = 0, activeCat = null;
  function setActiveTab(cat) {
    if (cat === activeCat) return;
    activeCat = cat;
    const tabs = $('#tabs');
    if (!tabs) return;
    $$('.tab', tabs).forEach((b) => {
      const on = b.dataset.cat === cat;
      b.classList.toggle('is-active', on);
      if (on) tabs.scrollTo({ left: b.offsetLeft - 16, behavior: 'smooth' });
    });
  }
  function onScroll() {
    if (state.view !== 'menu' || Date.now() < spyLock || spyRaf) return;
    spyRaf = requestAnimationFrame(() => {
      spyRaf = 0;
      const tabs = $('#tabs');
      const offset = (tabs ? tabs.offsetHeight : 60) + 12;
      let current = null;
      for (const sec of $$('.section')) if (sec.getBoundingClientRect().top - offset <= 0) current = sec.dataset.cat;
      setActiveTab(current || ($$('.section')[0] || {}).dataset?.cat);
    });
  }
  function scrollToCat(cat) {
    const sec = document.getElementById('cat-' + cat);
    const tabs = $('#tabs');
    if (!sec) return;
    spyLock = Date.now() + 700;
    setActiveTab(cat);
    window.scrollTo({ top: sec.getBoundingClientRect().top + window.scrollY - (tabs ? tabs.offsetHeight : 60) + 4, behavior: 'smooth' });
  }

  // ---------------------------------------------------------------- product sheet
  function openSheet(id) {
    const p = state.products.get(id);
    if (!p) return;
    state.sheet = { id, qty: 1, v: p.variants.length ? 0 : null };
    const el = $('#sheet');
    el.classList.remove('is-closing');
    el.innerHTML = `
      <div class="sheet__backdrop" data-action="sheet-close"></div>
      <div class="sheet__panel" role="dialog" aria-modal="true">
        <div class="sheet__media"><span class="sheet__grab"></span>${badges(p)}${img(p)}
          <button class="sheet__close" data-action="sheet-close" aria-label="${t('close')}">${ICON.close}</button></div>
        <div class="sheet__body">
          <h3 class="sheet__name">${esc(L(p.name))}</h3>
          <div class="sheet__price" id="sheet-price"></div>
          ${L(p.description) ? `<p class="sheet__desc">${esc(L(p.description))}</p>` : ''}
          <div id="sheet-variants"></div>
        </div>
        <div class="sheet__foot" id="sheet-foot"></div>
      </div>`;
    el.hidden = false;
    renderSheetDynamic();
    updateBackButton();
    haptic('light');
  }

  function renderSheetDynamic() {
    const sh = state.sheet;
    const p = sh && state.products.get(sh.id);
    if (!p) return;
    const line = lineOf(keyOf(p.id, sh.v));
    $('#sheet-price').innerHTML = `${pill(line.price, !!line.old)}${line.old ? `<s class="price-old">${num(line.old)} ${t('cur')}</s>` : ''}`;
    $('#sheet-variants').innerHTML = p.variants.length ? `<div class="variants">${p.variants.map((v, i) => `
      <button class="variant ${i === sh.v ? 'is-active' : ''}" data-action="sheet-v" data-v="${i}">
        <b>${esc(L(v.name))}</b><span>${num(v.price)}</span>${v.old_price ? `<s>${num(v.old_price)}</s>` : ''}</button>`).join('')}</div>` : '';
    $('#sheet-foot').innerHTML = p.available
      ? `<div class="stepper stepper--soft"><button data-action="sheet-dec" aria-label="-">${ICON.minus}</button><span>${sh.qty}</span>
           <button data-action="sheet-inc" aria-label="+">${ICON.plus}</button></div>
         <button class="main-btn main-btn--center" data-action="sheet-add"><span class="main-btn__label">${t('add_to_cart')} · ${money(line.price * sh.qty)}</span></button>`
      : `<button class="main-btn main-btn--center" disabled><span class="main-btn__label">${t('sold_out')}</span></button>`;
  }

  function closeSheet() {
    const el = $('#sheet');
    if (el.hidden) return;
    state.sheet = null;
    el.classList.add('is-closing');
    setTimeout(() => { el.hidden = true; el.innerHTML = ''; el.classList.remove('is-closing'); }, 200);
    updateBackButton();
  }

  // ---------------------------------------------------------------- cart
  function pageHead(title, extra) {
    return `<div class="page-head">${IN_TG ? '' : `<button class="back-btn" data-action="back" aria-label="back">${ICON.back}</button>`}
      <h1>${title}</h1>${extra || ''}</div>`;
  }

  function renderCart() {
    const view = $('#view-cart');
    if (!state.cart.size) {
      view.innerHTML = `${pageHead(t('cart'))}<div class="empty">
        <img class="empty__img" src="/static/img/burger.svg" alt=""><h2 class="empty__title">${t('empty_title')}</h2>
        <p class="empty__sub">${t('empty_sub')}</p>
        <button class="main-btn main-btn--center" data-action="to-menu"><span class="main-btn__label">${t('to_menu')}</span></button></div>`;
      return;
    }
    const s = state.store;
    const subtotal = cartSubtotal();
    const rows = Array.from(state.cart.entries()).map(([key, q]) => {
      const l = lineOf(key);
      return `<div class="row">
        <div class="thumb">${img(l.p)}</div>
        <div class="row__info"><div class="row__name">${esc(L(l.p.name))}</div>
          ${l.variant ? `<div class="row__variant">${esc(L(l.variant.name))}</div>` : ''}
          <div class="row__price">${money(l.price * q)}</div></div>
        <div class="stepper stepper--sm"><button data-action="dec" data-key="${esc(key)}" aria-label="-">${ICON.minus}</button>
          <span>${q}</span><button data-action="inc" data-key="${esc(key)}" aria-label="+">${ICON.plus}</button></div>
      </div>`;
    }).join('');

    let progress = '';
    const freeFrom = s.delivery.enabled && s.delivery.fee ? Number(s.delivery.free_from || 0) : 0;
    if (freeFrom) {
      const pct = Math.min(100, Math.round((subtotal / freeFrom) * 100));
      progress = `<div class="summary"><div class="small" style="font-weight:700;margin-bottom:8px">${subtotal >= freeFrom ? t('free_ok') : t('free_left', { amount: money(freeFrom - subtotal) })}</div>
        <div style="height:8px;border-radius:99px;background:var(--surface-2);overflow:hidden"><div style="height:100%;width:${pct}%;background:var(--brand)"></div></div></div>`;
    }
    const upsell = ['drinks', 'snacks', 'sauces']
      .flatMap((c) => Array.from(state.products.values()).filter((p) => p.category === c))
      .filter((p) => p.available && !p.variants.length && !state.cart.has(p.id)).slice(0, 10);

    view.innerHTML = `
      ${pageHead(t('cart'), `<button class="link-btn" data-action="clear">${t('clear')}</button>`)}
      <div class="list">${rows}</div>
      ${progress}
      ${upsell.length ? `<h3 class="upsell-title">${t('upsell')}</h3><div class="upsell">${upsell.map((p) => `
        <div class="mini" data-action="open" data-id="${esc(p.id)}"><div class="mini__media">${img(p, true)}</div>
          <div class="mini__body"><div class="mini__name">${esc(L(p.name))}</div>${pill(p.price, !!p.old_price)}
            <div data-ctrl="${esc(p.id)}">${control(p, 'block')}</div></div></div>`).join('')}</div>` : ''}
      <div class="summary"><div class="summary__row summary__row--total"><span>${t('subtotal')}</span><span>${money(subtotal)}</span></div></div>`;
  }

  // ---------------------------------------------------------------- checkout
  const hasLocation = () => state.profile.lat != null && state.profile.lon != null;
  function deliveryFee(subtotal) {
    const d = state.store.delivery;
    if (state.co.type !== 'delivery') return 0;
    if (d.free_from && subtotal >= d.free_from) return 0;
    return Number(d.fee || 0);
  }
  const minOrder = () => Number((state.store[state.co.type] || {}).min_order || 0);

  function mapTiles(lat, lon) {
    const z = 16, n = 2 ** z;
    const x = (lon + 180) / 360 * n;
    const r = lat * Math.PI / 180;
    const y = (1 - Math.log(Math.tan(r) + 1 / Math.cos(r)) / Math.PI) / 2 * n;
    const tx = Math.floor(x), ty = Math.floor(y);
    let html = '';
    for (let dx = -2; dx <= 2; dx += 1) {
      for (let dy = -1; dy <= 1; dy += 1) {
        const left = Math.round((tx + dx - x) * 256), top = Math.round((ty + dy - y) * 256);
        html += `<img src="https://tile.openstreetmap.org/${z}/${tx + dx}/${ty + dy}.png" alt="" loading="lazy" onerror="this.style.visibility='hidden'" style="left:calc(50% + ${left}px);top:calc(50% + ${top}px)">`;
      }
    }
    return html + ICON.pin + '<span class="loc-map__attr">© OpenStreetMap</span>';
  }

  function deliveryPanel() {
    const co = state.co;
    if (hasLocation()) {
      const prof = state.profile;
      return `<div class="panel">
        <div class="loc-map" data-action="open-map">${mapTiles(prof.lat, prof.lon)}</div>
        <div class="loc-info"><span class="loc-info__icon">📍</span><div class="loc-info__text">
          <div class="loc-info__title">${esc(prof.address || '')}</div><div class="loc-info__sub">${t('loc_from_tg')}</div></div></div>
        <div class="panel__pad">
          <button class="tg-btn tg-btn--ghost" data-action="req-loc">${ICON.tg}${t('loc_change')}</button>
          <label class="field"><span class="field__label">${t('details')}</span>
            <input class="input" data-field="details" maxlength="120" placeholder="${esc(t('details_ph'))}" value="${esc(co.details)}"></label>
        </div></div>`;
    }
    return `<div class="panel"><div class="loc-empty">
        <div class="loc-empty__icon">📍</div><div class="loc-empty__title">${t('loc_empty_title')}</div>
        <p class="loc-empty__sub">${t('loc_empty_sub')}</p>
        <button class="tg-btn" data-action="req-loc">${ICON.tg}${t('loc_send')}</button>
        ${co.typeAddress
          ? `<label class="field" style="text-align:left"><textarea class="input" id="f-address" data-field="address" rows="2" maxlength="250" placeholder="${esc(t('address_ph'))}">${esc(co.address)}</textarea></label>
             <label class="field" style="text-align:left"><span class="field__label">${t('details')}</span>
             <input class="input" data-field="details" maxlength="120" placeholder="${esc(t('details_ph'))}" value="${esc(co.details)}"></label>`
          : `<button class="text-link" data-action="type-address">${t('loc_type_instead')}</button>`}
      </div></div>`;
  }

  function contactRows() {
    const co = state.co;
    const canAsk = IN_TG && tgAtLeast('6.9') && typeof tg.requestContact === 'function';
    const nameRow = `<div class="info-row"><span class="info-row__icon">👤</span><div class="info-row__text">
        <div class="info-row__label">${t('name')}</div>
        ${co.editName ? `<input class="input" id="f-name" data-field="name" maxlength="64" placeholder="${esc(t('name_ph'))}" value="${esc(co.name)}">`
          : `<div class="info-row__value ${co.name ? '' : 'is-empty'}">${esc(co.name || '—')}</div>`}</div>
        ${co.editName ? '' : `<button class="edit-btn" data-action="edit-name" aria-label="edit">${ICON.edit}</button>`}</div>`;
    let phoneSide = '';
    if (!co.editPhone) {
      phoneSide = !co.phone && canAsk
        ? `<button class="tg-chip" data-action="req-phone">${ICON.tg}${t('phone_send')}</button>`
        : `<button class="edit-btn" data-action="edit-phone" aria-label="edit">${ICON.edit}</button>`;
    }
    const phoneRow = `<div class="info-row"><span class="info-row__icon">📱</span><div class="info-row__text">
        <div class="info-row__label">${t('phone')}</div>
        ${co.editPhone ? `<input class="input" id="f-phone" data-field="phone" type="tel" inputmode="tel" maxlength="20" placeholder="${esc(t('phone_ph'))}" value="${esc(co.phone)}">`
          : `<div class="info-row__value ${co.phone ? '' : 'is-empty'}">${esc(co.phone || t('phone_missing'))}</div>`}</div>${phoneSide}</div>`;
    return nameRow + phoneRow;
  }
  function renderContact() { const el = $('#co-contact'); if (el) el.innerHTML = contactRows(); }

  function renderCheckout() {
    const s = state.store;
    const co = state.co;
    const pays = s.payments || { cash: true };
    const payOpt = (key, icon, title, sub) => {
      const on = !!pays[key];
      return `<button class="pay-opt ${co.payment === key ? 'is-active' : ''}" data-action="pay" data-pay="${key}" ${on ? '' : 'disabled'}>
        <span class="pay-opt__icon pay-opt__icon--${key}">${icon}</span>
        <span class="pay-opt__text"><span class="pay-opt__title">${title}</span><br><span class="pay-opt__sub">${sub}</span></span>
        ${on ? '<span class="radio"></span>' : `<span class="soon">${t('soon')}</span>`}</button>`;
    };
    $('#view-checkout').innerHTML = `
      ${pageHead(t('checkout'))}
      ${s.is_open ? '' : `<div class="notice">${s.paused ? '⏸' : '😴'} <span>${esc(t(s.paused ? 'err_paused' : 'err_closed'))}</span></div>`}
      ${s.delivery.enabled && s.pickup.enabled ? `<div class="block"><h3 class="block__title">${t('how')}</h3><div class="segment">
          <button data-action="type" data-type="delivery" class="${co.type === 'delivery' ? 'is-active' : ''}">🛵 ${t('delivery')}</button>
          <button data-action="type" data-type="pickup" class="${co.type === 'pickup' ? 'is-active' : ''}">🛍 ${t('pickup')}</button>
        </div></div>` : ''}
      <div class="block" id="co-delivery" ${co.type === 'delivery' ? '' : 'hidden'}><h3 class="block__title">${t('addr_title')}</h3>${deliveryPanel()}</div>
      <div class="block" id="co-pickup" ${co.type === 'pickup' ? '' : 'hidden'}><h3 class="block__title">${t('pickup_from')}</h3>
        <div class="panel"><div class="pickup-card"><span class="pickup-card__icon">🍔</span><div>
          <div class="pickup-card__title">${esc(L(s.address))}</div>
          ${s.pickup.eta ? `<div class="pickup-card__sub">${esc(t('pickup_eta', { eta: s.pickup.eta }))}</div>` : ''}</div></div></div></div>
      <div class="block"><h3 class="block__title">${t('you')}</h3><div class="panel" id="co-contact">${contactRows()}</div></div>
      <div class="block"><h3 class="block__title">${t('comment')}</h3>
        <textarea class="input" data-field="comment" rows="2" maxlength="300" placeholder="${esc(t('comment_ph'))}">${esc(co.comment)}</textarea></div>
      <div class="block"><h3 class="block__title">${t('payment')}</h3><div class="pay">
        ${payOpt('cash', '💵', t('pay_cash'), t('pay_cash_sub'))}${payOpt('click', 'click', 'Click', t('pay_click_sub'))}${payOpt('payme', 'payme', 'Payme', t('pay_payme_sub'))}
      </div></div>
      <div id="co-summary"></div>`;
    renderCheckoutSummary();
  }

  function renderCheckoutSummary() {
    const box = $('#co-summary');
    if (!box) return;
    const subtotal = cartSubtotal();
    const fee = deliveryFee(subtotal);
    const min = minOrder();
    box.innerHTML = `<div class="summary">
      <div class="summary__row"><span>${t('subtotal')} · ${cartCount()} ${t('pcs')}</span><span>${money(subtotal)}</span></div>
      ${state.co.type === 'delivery' ? `<div class="summary__row"><span>${t('delivery')}</span><span>${fee ? money(fee) : `<span class="free">${t('free')}</span>`}</span></div>` : ''}
      <div class="summary__row summary__row--total"><span>${t('total')}</span><span>${money(subtotal + fee)}</span></div>
      ${min && subtotal < min ? `<div class="summary__warn">${t('min_order', { amount: money(min) })}</div>` : ''}</div>`;
    renderBottom();
  }

  // Telegram orqali lokatsiya: bot chatga tugma yuboradi, Mini App yopiladi
  async function requestLocation() {
    if (!IN_TG) { toast(t('loc_tg_only'), true); return; }
    saveDraft();
    let res;
    try { res = await api('/api/request-location', {}); } catch (_) { toast(t('err_network'), true); return; }
    if (!res.data || !res.data.ok) { showError(res.data || {}); return; }
    haptic('success');
    toast(t('loc_going'));
    setTimeout(() => { try { tg.close(); } catch (_) { /* */ } }, 700);
  }

  function setPhone(raw) {
    const digits = String(raw || '').replace(/[^\d+]/g, '');
    state.co.phone = digits.startsWith('+') ? digits : '+' + digits;
    state.co.editPhone = false;
    saveDraft();
    renderContact();
    haptic('success');
  }
  function requestPhone() {
    if (!(IN_TG && tgAtLeast('6.9') && typeof tg.requestContact === 'function')) { state.co.editPhone = true; renderContact(); return; }
    tg.requestContact((ok, res) => {
      if (!ok) { toast(t('phone_denied'), true); return; }
      const c = res && res.responseUnsafe && res.responseUnsafe.contact;
      if (c && c.phone_number) { setPhone(c.phone_number); return; }
      // eski klientlar: raqam botga keladi — profildan qayta o'qiymiz
      setTimeout(async () => {
        try { const r = await api('/api/bootstrap'); if (r.data && r.data.profile && r.data.profile.phone) setPhone(r.data.profile.phone); } catch (_) { /* */ }
      }, 1500);
    });
  }

  // ---------------------------------------------------------------- submit
  const PHONE_RE = /^\+?[0-9][0-9 ()-]{6,20}$/;
  function scrollTo(sel) { const el = $(sel); if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' }); }

  async function submitOrder() {
    if (state.submitting) return;
    const co = state.co;
    const s = state.store;
    if (!s.is_open) { toast(t(s.paused ? 'err_paused' : 'err_closed'), true); return; }
    if (!state.cart.size) { toast(t('err_empty_cart'), true); return; }
    const delivery = co.type === 'delivery';
    if (delivery && !hasLocation() && co.address.trim().length < 5) { scrollTo('#co-delivery'); toast(t('err_bad_address'), true); return; }
    const digits = (co.phone.match(/\d/g) || []).length;
    if (!PHONE_RE.test(co.phone.trim()) || digits < 9 || digits > 15) {
      if (!co.editPhone && !co.phone) requestPhone(); else { co.editPhone = true; renderContact(); }
      scrollTo('#co-contact'); toast(t('err_bad_phone'), true); return;
    }
    const subtotal = cartSubtotal();
    if (minOrder() && subtotal < minOrder()) { toast(t('err_min_order', { amount: money(minOrder()) }), true); return; }

    let address = '';
    if (delivery) {
      const base = hasLocation() ? state.profile.address : co.address.trim();
      address = [base, co.details.trim()].filter(Boolean).join(' — ');
    }
    state.submitting = true;
    renderBottom();
    const body = {
      items: Array.from(state.cart.entries()).map(([key, qty]) => {
        const { id, v } = parseKey(key);
        return v === null ? { id, qty } : { id, qty, v };
      }),
      type: co.type, address,
      lat: delivery && hasLocation() ? state.profile.lat : null,
      lon: delivery && hasLocation() ? state.profile.lon : null,
      name: co.name.trim(), phone: co.phone.trim(), comment: co.comment.trim(), payment: co.payment, lang: state.lang,
    };
    let res;
    try { res = await api('/api/order', body); } catch (_) {
      state.submitting = false; renderBottom(); toast(t('err_network'), true); return;
    }
    state.submitting = false;
    if (res.data && res.data.ok) {
      state.lastOrder = { id: res.data.order.id, total: res.data.order.total, type: co.type };
      state.cart.clear();
      saveCart();
      co.comment = ''; co.details = '';
      saveDraft();
      state.stack = [];
      haptic('success');
      go('success', false);
      return;
    }
    showError(res.data || {});
    renderBottom();
  }

  function showError(data) {
    const code = data.error || 'generic';
    if ((code === 'unavailable' || code === 'bad_variant') && data.product_id) {
      const p = state.products.get(data.product_id);
      if (p) {
        if (code === 'unavailable') p.available = false;
        Array.from(state.cart.keys()).filter((k) => parseKey(k).id === p.id).forEach((k) => state.cart.delete(k));
        saveCart();
        refreshControls(p.id);
        if (state.view === 'checkout') renderCheckoutSummary();
        toast(code === 'unavailable' ? t('err_unavailable', { name: L(p.name) }) : t('err_bad_variant'), true);
        return;
      }
    }
    if (code === 'closed' || code === 'paused') state.store.is_open = false;
    if (code === 'paused') state.store.paused = true;
    if (code === 'min_order') { toast(t('err_min_order', { amount: money(data.min_order || 0) }), true); return; }
    toast(I18N.uz['err_' + code] ? t('err_' + code) : t('err_generic'), true);
  }

  // ---------------------------------------------------------------- success
  function renderSuccess() {
    const o = state.lastOrder || {};
    const s = state.store;
    const eta = o.type === 'pickup' ? s.pickup.eta : s.delivery.eta;
    $('#view-success').innerHTML = `<div class="success">
      <svg class="check" viewBox="0 0 104 104"><circle cx="52" cy="52" r="52"/><path d="M31 53l14 14 28-29"/></svg>
      <h1>${esc(t('success_title', { id: o.id }))}</h1><p>${t('success_sub')}</p>
      <div class="summary">
        <div class="summary__row"><span>${t('order_no')}</span><span><b>#${esc(o.id)}</b></span></div>
        ${eta ? `<div class="summary__row"><span>${o.type === 'pickup' ? t('eta_pickup') : t('eta_delivery')}</span><span>~${esc(eta)} ${t('min')}</span></div>` : ''}
        <div class="summary__row summary__row--total"><span>${t('total')}</span><span>${money(o.total || 0)}</span></div>
      </div>
      <button class="ghost-btn" data-action="to-menu">${t('to_menu')}</button></div>`;
  }

  // ---------------------------------------------------------------- bottom bar
  function renderBottom() {
    const bar = $('#bottom-bar');
    const v = state.view;
    const count = cartCount();
    const subtotal = cartSubtotal();
    let html = '';
    if (v === 'menu' && count) {
      html = `<button class="main-btn" data-action="to-cart"><span class="main-btn__count">${count}</span>
        <span class="main-btn__label">${t('view_cart')}</span><span class="main-btn__total">${money(subtotal)}</span></button>`;
    } else if (v === 'cart' && count) {
      html = `<button class="main-btn" data-action="to-checkout"><span class="main-btn__label">${t('checkout')}</span>
        <span class="main-btn__total">${money(subtotal)}</span></button>`;
    } else if (v === 'checkout' && count) {
      const blocked = !state.store.is_open || (minOrder() && subtotal < minOrder());
      html = `<button class="main-btn" data-action="submit" ${blocked || state.submitting ? 'disabled' : ''}>
        <span class="main-btn__label">${state.submitting ? '<span class="spinner"></span>' : t('place')}</span>
        <span class="main-btn__total">${money(subtotal + deliveryFee(subtotal))}</span></button>`;
    } else if (v === 'success' && IN_TG) {
      html = `<button class="main-btn main-btn--center" data-action="close"><span class="main-btn__label">${t('close')}</span></button>`;
    }
    bar.innerHTML = html;
    bar.hidden = !html;
  }

  function showErrorView(titleKey, subKey, canRetry) {
    $('#view-error').innerHTML = `<div class="empty"><img class="empty__img" src="/static/img/logo-badge.png" alt="" style="border-radius:24px">
      <h2 class="empty__title">${t(titleKey)}</h2>${subKey ? `<p class="empty__sub">${t(subKey)}</p>` : ''}
      ${canRetry ? `<button class="main-btn main-btn--center" data-action="retry"><span class="main-btn__label">${t('retry')}</span></button>` : ''}</div>`;
    state.view = 'error';
    show('error');
    renderBottom();
  }

  // ---------------------------------------------------------------- events
  document.addEventListener('click', (e) => {
    const el = e.target.closest('[data-action]');
    if (!el) return;
    const a = el.dataset.action;
    const key = el.dataset.key;
    switch (a) {
      case 'inc': e.stopPropagation(); setQty(key, (state.cart.get(key) || 0) + 1); break;
      case 'dec': e.stopPropagation(); setQty(key, (state.cart.get(key) || 0) - 1); break;
      case 'open': openSheet(el.dataset.id); break;
      case 'banner': openBanner(el.dataset.type, el.dataset.target); break;
      case 'tab': scrollToCat(el.dataset.cat); haptic('select'); break;
      case 'where': requestLocation(); break; // bot chatida: lokatsiya / oldingi manzil / olib ketish
      case 'sheet-close': closeSheet(); break;
      case 'sheet-v': state.sheet.v = Number(el.dataset.v); renderSheetDynamic(); haptic('select'); break;
      case 'sheet-inc': state.sheet.qty = Math.min(50, state.sheet.qty + 1); renderSheetDynamic(); haptic('select'); break;
      case 'sheet-dec': state.sheet.qty = Math.max(1, state.sheet.qty - 1); renderSheetDynamic(); haptic('select'); break;
      case 'sheet-add': {
        const k = keyOf(state.sheet.id, state.sheet.v);
        const qty = state.sheet.qty;
        closeSheet();
        setQty(k, (state.cart.get(k) || 0) + qty);
        haptic('medium');
        break;
      }
      case 'to-cart': go('cart'); break;
      case 'to-checkout': go('checkout'); break;
      case 'to-menu': state.stack = []; go('menu', false); break;
      case 'back': goBack(); break;
      case 'clear': state.cart.clear(); saveCart(); refreshAllControls(); renderCart(); renderBottom(); haptic('warning'); break;
      case 'type':
        state.co.type = el.dataset.type;
        $$('.segment button').forEach((b) => b.classList.toggle('is-active', b.dataset.type === state.co.type));
        $('#co-delivery').hidden = state.co.type !== 'delivery';
        $('#co-pickup').hidden = state.co.type !== 'pickup';
        saveDraft();
        renderCheckoutSummary();
        haptic('select');
        break;
      case 'req-loc': requestLocation(); break;
      case 'open-map': {
        const url = `https://yandex.uz/maps/?pt=${state.profile.lon},${state.profile.lat}&z=17&l=map`;
        if (tg && tg.openLink) tg.openLink(url); else window.open(url, '_blank');
        break;
      }
      case 'type-address':
        state.co.typeAddress = true;
        $('#co-delivery').innerHTML = `<h3 class="block__title">${t('addr_title')}</h3>${deliveryPanel()}`;
        $('#f-address').focus();
        break;
      case 'edit-name': state.co.editName = true; renderContact(); $('#f-name').focus(); break;
      case 'edit-phone': state.co.editPhone = true; renderContact(); $('#f-phone').focus(); break;
      case 'req-phone': requestPhone(); break;
      case 'pay':
        if (el.disabled) break;
        state.co.payment = el.dataset.pay;
        $$('.pay-opt').forEach((b) => b.classList.toggle('is-active', b.dataset.pay === state.co.payment));
        haptic('select');
        break;
      case 'submit': submitOrder(); break;
      case 'close': if (tg) tg.close(); break;
      case 'retry': init(); break;
      default: break;
    }
  });
  document.addEventListener('input', (e) => {
    const f = e.target.dataset && e.target.dataset.field;
    if (f) { state.co[f] = e.target.value; saveDraft(); }
  });
  window.addEventListener('scroll', onScroll, { passive: true });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') goBack(); });

  // ---------------------------------------------------------------- init
  async function init() {
    document.documentElement.lang = state.lang;
    state.view = 'loading';
    show('loading');
    let res;
    try { res = await api('/api/bootstrap'); } catch (_) { showErrorView('err_network', null, true); return; }
    if (res.status === 401) { showErrorView('open_in_tg', 'open_in_tg_sub', false); return; }
    if (!res.data || !res.data.ok) { showErrorView('err_generic', null, true); return; }

    const d = res.data;
    state.store = d.store;
    state.categories = d.menu.categories;
    state.products = new Map(d.menu.products.map((p) => [p.id, { ...p, variants: p.variants || [] }]));
    state.banners = d.banners || [];
    state.profile = d.profile || {};
    if (state.profile.lang === 'uz' || state.profile.lang === 'ru') state.lang = state.profile.lang;
    document.documentElement.lang = state.lang;

    const co = state.co;
    const draft = restore(DRAFT_KEY) || {};
    co.name = state.profile.name || draft.name || '';
    co.phone = state.profile.phone || draft.phone || '';
    co.comment = draft.comment || '';
    co.details = draft.details || '';
    co.address = draft.address || '';
    co.type = params.get('type') || state.profile.type || draft.type || 'delivery';
    if (co.type === 'delivery' && !state.store.delivery.enabled) co.type = 'pickup';
    if (co.type === 'pickup' && !state.store.pickup.enabled) co.type = 'delivery';
    const pays = state.store.payments || {};
    co.payment = ['cash', 'click', 'payme'].find((k) => pays[k]) || 'cash';

    loadCart();
    renderMenu();
    setupCarousel();
    state.view = 'menu';
    if (params.get('to') === 'checkout' && state.cart.size) {
      state.stack = ['menu', 'cart'];
      go('checkout', false);
    } else {
      go('menu', false);
    }
    onScroll();
  }

  applyTheme();
  setupTelegram();
  init();
})();
