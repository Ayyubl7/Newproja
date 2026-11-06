/* Ayva Burgers — Telegram Mini App (framework'siz, tez yuklanadi) */
(() => {
  'use strict';

  const tg = window.Telegram && window.Telegram.WebApp;
  const IN_TG = !!(tg && tg.initData);
  const params = new URLSearchParams(location.search);
  const CART_KEY = 'ayva_cart_v1';
  const LEAFLET = '/static/vendor/leaflet/';

  // ---------------------------------------------------------------- i18n
  const I18N = {
    uz: {
      cur: "so'm", pcs: 'ta', min: 'daqiqa',
      open: 'Ochiq', closed: 'Yopiq',
      closed_banner: "Hozir yopiqmiz. Ish vaqti: {hours}. Menyuni ko'rishingiz mumkin — buyurtmalar ish vaqtida qabul qilinadi.",
      paused_banner: "Hozir buyurtmalar vaqtincha qabul qilinmayapti. Menyuni ko'rishingiz mumkin — tez orada qaytamiz!", paused_chip: 'Pauza',
      promo_section: '🔥 Aksiyalar', err_paused: 'Buyurtmalar vaqtincha qabul qilinmayapti',
      hero_kicker: 'Bizning hit',
      pill_eta: '{eta} daq', pill_fee: 'Yetkazish {fee}', pill_free: '{amount} dan bepul',
      sold_out: 'Tugadi', badge_hit: '🔥 Hit', badge_new: '✨ Yangi', badge_spicy: '🌶 Achchiq',
      add: "Qo'shish", cart: 'Savat', view_cart: "Savatni ko'rish", clear: 'Tozalash',
      empty_title: "Savat hozircha bo'sh", empty_sub: "Menyudan o'zingizga yoqqan taomni tanlang", to_menu: 'Menyuga qaytish',
      upsell: "Yana nimadir qo'shamizmi?", free_left: "Bepul yetkazishgacha yana <b>{amount}</b>", free_ok: '🎉 Yetkazib berish bepul!',
      checkout: 'Rasmiylashtirish', subtotal: 'Mahsulotlar', delivery: 'Yetkazib berish', total: 'Jami', free: 'Bepul',
      pickup: 'Olib ketish', how: 'Qanday olasiz?', address: 'Manzil', address_ph: "Ko'cha, uy, xonadon, mo'ljal",
      loc_title: 'Lokatsiyani belgilang', loc_sub: 'Kuryer sizni tezroq topadi', loc_set: 'Lokatsiya belgilandi', loc_change: "O'zgartirish uchun bosing",
      map_hint: 'Xaritani suring — pinni aniq eshigingizga qo\'ying', map_done: 'Tayyor', locating: 'Joylashuv aniqlanmoqda…',
      pickup_from: 'Olib ketish manzili', pickup_eta: 'Taxminan {eta} daqiqada tayyor bo\'ladi',
      contact: 'Aloqa', name: 'Ismingiz', phone: 'Telefon raqam', comment: 'Izoh', comment_ph: "Masalan: domofon ishlamaydi, qo'ng'iroq qiling",
      payment: "To'lov usuli", pay_cash: 'Naqd pul', pay_cash_sub: 'Kuryerga yoki kassada', pay_click_sub: 'Onlayn to\'lov', pay_payme_sub: 'Onlayn to\'lov', soon: 'Tez orada',
      place: 'Buyurtma berish', min_order: 'Minimal buyurtma: {amount}',
      success_title: 'Buyurtma #{id} qabul qilindi!', success_sub: 'Operatorimiz tez orada tasdiqlaydi. Buyurtma holatini botdagi xabarlarda kuzatib boring.',
      order_no: 'Buyurtma', eta_delivery: 'Yetkazish vaqti', eta_pickup: 'Tayyor bo\'ladi', close: 'Yopish',
      open_in_tg: 'Menyuni Telegram bot orqali oching', open_in_tg_sub: 'Botdagi «🍔 Menyuni ochish» tugmasini bosing.', retry: 'Qayta urinish',
      err_generic: "Xatolik yuz berdi. Qayta urinib ko'ring.", err_network: "Internet bilan aloqa yo'q. Qayta urinib ko'ring.",
      err_closed: 'Hozir yopiqmiz — buyurtma ish vaqtida qabul qilinadi.', err_bad_phone: "Telefon raqamni to'g'ri kiriting",
      err_bad_address: "Manzilni to'liqroq yozing", err_unavailable: '«{name}» tugab qoldi — savatdan olib tashlandi',
      err_min_order: 'Minimal buyurtma: {amount}', err_too_fast: "Biroz kuting va qayta urinib ko'ring",
      err_unauthorized: 'Ilovani bot orqali qayta oching', err_payment_unavailable: "Bu to'lov usuli hozir mavjud emas",
      err_location: "Joylashuvni aniqlab bo'lmadi — xaritada qo'lda belgilang", err_empty_cart: "Savat bo'sh",
      err_type_disabled: 'Bu usul hozir ishlamayapti', err_bad_location: "Lokatsiya noto'g'ri",
    },
    ru: {
      cur: 'сум', pcs: 'шт', min: 'мин',
      open: 'Открыто', closed: 'Закрыто',
      closed_banner: 'Сейчас мы закрыты. Время работы: {hours}. Меню можно посмотреть — заказы принимаем в рабочее время.',
      paused_banner: 'Сейчас заказы временно не принимаются. Меню можно посмотреть — скоро вернёмся!', paused_chip: 'Пауза',
      promo_section: '🔥 Акции', err_paused: 'Заказы временно не принимаются',
      hero_kicker: 'Наш хит',
      pill_eta: '{eta} мин', pill_fee: 'Доставка {fee}', pill_free: 'Бесплатно от {amount}',
      sold_out: 'Закончился', badge_hit: '🔥 Хит', badge_new: '✨ Новинка', badge_spicy: '🌶 Острое',
      add: 'Добавить', cart: 'Корзина', view_cart: 'Корзина', clear: 'Очистить',
      empty_title: 'Корзина пока пуста', empty_sub: 'Выберите что-нибудь вкусное в меню', to_menu: 'Вернуться в меню',
      upsell: 'Добавим что-нибудь?', free_left: 'До бесплатной доставки ещё <b>{amount}</b>', free_ok: '🎉 Доставка бесплатно!',
      checkout: 'Оформить заказ', subtotal: 'Товары', delivery: 'Доставка', total: 'Итого', free: 'Бесплатно',
      pickup: 'Самовывоз', how: 'Как получить?', address: 'Адрес', address_ph: 'Улица, дом, квартира, ориентир',
      loc_title: 'Отметьте локацию', loc_sub: 'Курьер найдёт вас быстрее', loc_set: 'Локация отмечена', loc_change: 'Нажмите, чтобы изменить',
      map_hint: 'Двигайте карту — поставьте пин точно к двери', map_done: 'Готово', locating: 'Определяем местоположение…',
      pickup_from: 'Адрес самовывоза', pickup_eta: 'Будет готов примерно через {eta} мин',
      contact: 'Контакты', name: 'Ваше имя', phone: 'Номер телефона', comment: 'Комментарий', comment_ph: 'Например: домофон не работает, позвоните',
      payment: 'Способ оплаты', pay_cash: 'Наличные', pay_cash_sub: 'Курьеру или на кассе', pay_click_sub: 'Онлайн-оплата', pay_payme_sub: 'Онлайн-оплата', soon: 'Скоро',
      place: 'Заказать', min_order: 'Минимальный заказ: {amount}',
      success_title: 'Заказ #{id} принят!', success_sub: 'Оператор скоро подтвердит заказ. Следите за статусом в сообщениях бота.',
      order_no: 'Заказ', eta_delivery: 'Время доставки', eta_pickup: 'Будет готов', close: 'Закрыть',
      open_in_tg: 'Откройте меню через Telegram-бот', open_in_tg_sub: 'Нажмите кнопку «🍔 Открыть меню» в боте.', retry: 'Повторить',
      err_generic: 'Произошла ошибка. Попробуйте ещё раз.', err_network: 'Нет связи с интернетом. Попробуйте ещё раз.',
      err_closed: 'Сейчас мы закрыты — заказы принимаем в рабочее время.', err_bad_phone: 'Введите корректный номер телефона',
      err_bad_address: 'Укажите адрес подробнее', err_unavailable: '«{name}» закончился — убрали из корзины',
      err_min_order: 'Минимальный заказ: {amount}', err_too_fast: 'Подождите немного и попробуйте снова',
      err_unauthorized: 'Откройте приложение заново через бота', err_payment_unavailable: 'Этот способ оплаты сейчас недоступен',
      err_location: 'Не удалось определить местоположение — отметьте на карте вручную', err_empty_cart: 'Корзина пуста',
      err_type_disabled: 'Этот способ сейчас недоступен', err_bad_location: 'Неверная локация',
    },
  };

  const ICON = {
    plus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>',
    minus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="round"><path d="M5 12h14"/></svg>',
    close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    back: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5l-7 7 7 7"/></svg>',
    pin: '<svg class="map-pin" viewBox="0 0 38 50"><path d="M19 49C19 49 2 30.5 2 18.5a17 17 0 0 1 34 0C36 30.5 19 49 19 49z" fill="#F4AE16" stroke="#261703" stroke-width="2.5"/><circle cx="19" cy="18.5" r="6.5" fill="#261703"/></svg>',
  };

  // ---------------------------------------------------------------- state
  const state = {
    lang: params.get('lang') === 'ru' ? 'ru' : 'uz',
    store: null,
    categories: [],
    banners: [],
    products: new Map(),
    profile: {},
    cart: new Map(),
    view: 'loading',
    stack: [],
    menuScroll: 0,
    co: { type: 'delivery', address: '', lat: null, lon: null, name: '', phone: '', comment: '', payment: 'cash' },
    submitting: false,
    lastOrder: null,
    sheet: null,
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

  function tgAtLeast(v) { return !!(tg && tg.isVersionAtLeast && tg.isVersionAtLeast(v)); }
  function haptic(kind) {
    if (!tgAtLeast('6.1') || !tg.HapticFeedback) return;
    try {
      if (kind === 'success' || kind === 'error' || kind === 'warning') tg.HapticFeedback.notificationOccurred(kind);
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
    if (p.image) {
      const src = /^(https?:\/\/|\/)/.test(p.image) ? p.image : '/static/' + p.image;
      return { src, photo: true };
    }
    return { src: '/static/img/' + (categoryOf(p).icon || 'burger') + '.svg', photo: false };
  }
  const tint = (p) => `--tint: var(--tint-${esc(p.category)}, var(--tint-default))`;
  function img(p, lazy) {
    const im = imageOf(p);
    return `<img src="${esc(im.src)}" alt="" ${im.photo ? 'class="is-photo"' : ''} ${lazy ? 'loading="lazy"' : ''} decoding="async">`;
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

  // ---------------------------------------------------------------- cart
  function saveCart() {
    try { localStorage.setItem(CART_KEY, JSON.stringify(Object.fromEntries(state.cart))); } catch (_) { /* private mode */ }
  }
  function loadCart() {
    let raw = {};
    try { raw = JSON.parse(localStorage.getItem(CART_KEY) || '{}') || {}; } catch (_) { raw = {}; }
    state.cart.clear();
    for (const [id, qty] of Object.entries(raw)) {
      const p = state.products.get(id);
      if (p && p.available && Number.isInteger(qty) && qty > 0) state.cart.set(id, Math.min(qty, 50));
    }
  }
  const cartCount = () => { let n = 0; state.cart.forEach((q) => { n += q; }); return n; };
  const cartSubtotal = () => { let s = 0; state.cart.forEach((q, id) => { s += (state.products.get(id)?.price || 0) * q; }); return s; };

  function setQty(id, qty) {
    const p = state.products.get(id);
    if (!p) return;
    const prev = state.cart.get(id) || 0;
    qty = Math.max(0, Math.min(50, qty));
    if (qty === prev) return;
    if (qty === 0) state.cart.delete(id); else state.cart.set(id, qty);
    saveCart();
    haptic(qty > prev ? 'light' : 'soft');
    refreshControls(id);
    if (state.view === 'cart') renderCart();
    if (state.view === 'checkout') renderCheckoutSummary();
    renderBottom();
  }

  // ---------------------------------------------------------------- theme / telegram
  function applyTheme() {
    let dark = false;
    if (IN_TG) dark = tg.colorScheme === 'dark';
    else if (window.matchMedia) dark = matchMedia('(prefers-color-scheme: dark)').matches;
    document.documentElement.dataset.theme = dark ? 'dark' : 'light';
    const bg = dark ? '#15110C' : '#FFF8EE';
    const meta = $('meta[name="theme-color"]');
    if (meta) meta.content = bg;
    if (tgAtLeast('6.1')) {
      try { tg.setHeaderColor(bg); tg.setBackgroundColor(bg); } catch (_) { /* */ }
    }
    if (tgAtLeast('7.10')) { try { tg.setBottomBarColor(bg); } catch (_) { /* */ } }
  }

  function setupTelegram() {
    if (!tg) return;
    try { tg.ready(); tg.expand(); } catch (_) { /* */ }
    if (tgAtLeast('7.7')) { try { tg.disableVerticalSwipes(); } catch (_) { /* */ } }
    if (tgAtLeast('6.1')) tg.BackButton.onClick(goBack);
    tg.onEvent && tg.onEvent('themeChanged', applyTheme);
  }

  function updateBackButton() {
    if (!IN_TG || !tgAtLeast('6.1')) return;
    const show = !!state.sheet || ['cart', 'checkout'].includes(state.view);
    if (show) tg.BackButton.show(); else tg.BackButton.hide();
  }

  // ---------------------------------------------------------------- navigation
  function show(view) {
    $$('.view').forEach((el) => el.classList.toggle('is-active', el.id === 'view-' + view));
  }

  function go(view, push = true) {
    if (state.view === 'menu') state.menuScroll = window.scrollY;
    if (push && state.view !== view && ['menu', 'cart', 'checkout'].includes(state.view)) state.stack.push(state.view);
    state.view = view;
    if (view === 'cart') renderCart();
    if (view === 'checkout') renderCheckout();
    if (view === 'success') renderSuccess();
    if (view === 'menu') refreshAllControls();
    show(view);
    window.scrollTo(0, view === 'menu' ? state.menuScroll : 0);
    renderBottom();
    updateBackButton();
  }

  function goBack() {
    if (state.sheet) { closeSheet(); return; }
    if (state.view === 'success') { state.stack = []; go('menu', false); return; }
    const prev = state.stack.pop() || 'menu';
    go(prev, false);
  }

  // ---------------------------------------------------------------- menu view
  // variant: 'block' — karta ostidagi to'liq kenglikdagi tugma; 'sm' — savat qatoridagi ixcham stepper
  function control(p, variant) {
    const id = esc(p.id);
    const q = state.cart.get(p.id) || 0;
    if (variant === 'sm') {
      if (!p.available) return `<span class="out-label">${t('sold_out')}</span>`;
      return `<div class="stepper stepper--sm">
        <button data-action="dec" data-id="${id}" aria-label="-">${ICON.minus}</button>
        <span>${q}</span>
        <button data-action="inc" data-id="${id}" aria-label="+">${ICON.plus}</button>
      </div>`;
    }
    if (!p.available) return `<button class="buy" disabled>${t('sold_out')}</button>`;
    if (!q) return `<button class="buy" data-action="inc" data-id="${id}"><span class="buy__icon">${ICON.plus}</span>${t('add')}</button>`;
    return `<div class="stepper stepper--block">
      <button data-action="dec" data-id="${id}" aria-label="-">${ICON.minus}</button>
      <span>${q}</span>
      <button data-action="inc" data-id="${id}" aria-label="+">${ICON.plus}</button>
    </div>`;
  }

  function refreshControls(id) {
    const p = state.products.get(id);
    if (!p) return;
    $$(`[data-ctrl="${cssId(id)}"]`).forEach((el) => { el.innerHTML = control(p, el.dataset.variant || 'block'); });
  }
  function refreshAllControls() { state.products.forEach((_, id) => refreshControls(id)); }

  function badge(p) {
    let html = '';
    if (p.badge && I18N.uz['badge_' + p.badge]) html += `<span class="badge badge--${esc(p.badge)}">${t('badge_' + p.badge)}</span>`;
    if (p.discount) html += `<span class="badge badge--sale">−${p.discount}%</span>`;
    return html;
  }
  function priceHtml(p) {
    return p.old_price
      ? `<span class="price price--sale">${money(p.price)}</span> <s class="price-old">${money(p.old_price)}</s>`
      : `<span class="price">${money(p.price)}</span>`;
  }

  function card(p) {
    return `<article class="card ${p.available ? '' : 'is-out'}" data-action="open" data-id="${esc(p.id)}">
      <div class="card__media" style="${tint(p)}">${badge(p)}${img(p, true)}</div>
      <div class="card__body">
        <div class="card__name">${esc(L(p.name))}</div>
        ${L(p.description) ? `<div class="card__desc">${esc(L(p.description))}</div>` : ''}
        <div class="card__foot">
          <span class="card__price">${priceHtml(p)}</span>
          <div data-ctrl="${esc(p.id)}">${control(p, 'block')}</div>
        </div>
      </div>
    </article>`;
  }

  function renderMenu() {
    const s = state.store;
    const hours = !(s.hours && s.hours.open) ? '' : s.hours.open === s.hours.close ? '24/7' : `${s.hours.open}–${s.hours.close}`;
    const all = Array.from(state.products.values());
    const hero = all.find((p) => p.badge === 'hit' && p.available) || all.find((p) => p.available);
    const promo = all.filter((p) => p.old_price && p.available);
    const cats = (promo.length ? [{ id: '__promo', name: { uz: t('promo_section'), ru: t('promo_section') } }] : [])
      .concat(state.categories);
    const inCat = (c) => (c.id === '__promo' ? promo : all.filter((p) => p.category === c.id));

    const pills = [];
    if (hours) pills.push(`<span class="pill">🕒 <b>${esc(hours)}</b></span>`);
    if (s.delivery && s.delivery.enabled) {
      if (s.delivery.eta) pills.push(`<span class="pill">🚚 ${esc(t('pill_eta', { eta: s.delivery.eta }))}</span>`);
      if (s.delivery.fee) pills.push(`<span class="pill">💸 ${t('pill_fee', { fee: '<b>' + money(s.delivery.fee) + '</b>' })}</span>`);
      if (s.delivery.free_from) pills.push(`<span class="pill">🎁 ${t('pill_free', { amount: '<b>' + money(s.delivery.free_from) + '</b>' })}</span>`);
    }

    const sections = cats.map((c) => {
      const items = inCat(c);
      if (!items.length) return '';
      return `<section class="section" id="cat-${esc(c.id)}" data-cat="${esc(c.id)}">
        <h2 class="section__title">${esc(L(c.name))}</h2>
        <div class="grid">${items.map(card).join('')}</div>
      </section>`;
    }).join('');

    $('#view-menu').innerHTML = `
      <header class="header">
        <img class="header__logo" src="/static/img/logo.svg" alt="">
        <div class="header__title">
          <div class="header__name">${esc(s.name)}</div>
          <div class="header__tagline">${esc(L(s.tagline))}</div>
        </div>
        <span class="status-chip ${s.is_open ? '' : 'is-closed'}">${s.is_open ? t('open') : s.paused ? t('paused_chip') : t('closed')}</span>
      </header>
      ${s.paused ? `<div class="notice notice--danger">⏸ <span>${esc(t('paused_banner'))}</span></div>`
        : s.is_open ? '' : `<div class="notice notice--danger">😴 <span>${esc(t('closed_banner', { hours }))}</span></div>`}
      ${state.banners.length ? bannersHtml() : hero ? `<div class="hero" role="button" tabindex="0" data-action="open" data-id="${esc(hero.id)}">
        <div class="hero__text">
          <div class="hero__kicker">${t('hero_kicker')}</div>
          <div class="hero__title">${esc(L(hero.name))}</div>
          <div class="hero__sub">${esc(L(hero.description))}</div>
          <span class="hero__price">${money(hero.price)} ${ICON.plus.replace('<svg', '<svg width="16" height="16"')}</span>
        </div>
        <img class="hero__img" src="${esc(imageOf(hero).src)}" alt="">
      </div>` : ''}
      ${pills.length ? `<div class="pills">${pills.join('')}</div>` : ''}
      <nav class="tabs" id="tabs">${cats
        .filter((c) => inCat(c).length)
        .map((c, i) => `<button class="tab ${i === 0 ? 'is-active' : ''}" data-action="tab" data-cat="${esc(c.id)}">${esc(L(c.name))}</button>`)
        .join('')}</nav>
      ${sections}
      <div class="footer-note">${esc(s.name)} · ${esc(s.phone || '')}</div>`;
  }

  // ---------------------------------------------------------------- bannerlar (aksiya karuseli)
  function bannersHtml() {
    const slides = state.banners.map((b, i) => {
      const title = L(b.title);
      const text = L(b.text);
      const inner = b.image
        ? `<img class="slide__img" src="${esc(b.image)}" alt="" ${i ? 'loading="lazy"' : ''}>${title || text ? `<div class="slide__shade">
            ${title ? `<div class="slide__title">${esc(title)}</div>` : ''}${text ? `<div class="slide__text">${esc(text)}</div>` : ''}</div>` : ''}`
        : `<div class="slide__plain"><div class="slide__kicker">${t('promo_section')}</div>
            <div class="slide__title">${esc(title)}</div>${text ? `<div class="slide__text">${esc(text)}</div>` : ''}</div>
            <img class="slide__deco" src="/static/img/burger.svg" alt="">`;
      return `<div class="slide ${b.image ? '' : 'slide--plain'}" data-action="banner" data-type="${esc(b.link_type)}" data-target="${esc(b.link_id)}">${inner}</div>`;
    }).join('');
    const dots = state.banners.length > 1
      ? `<div class="dots">${state.banners.map((_, i) => `<span class="${i ? '' : 'is-active'}"></span>`).join('')}</div>` : '';
    return `<div class="carousel"><div class="carousel__track" id="carousel">${slides}</div>${dots}</div>`;
  }

  let carouselTimer = 0;
  function setupCarousel() {
    const track = $('#carousel');
    clearInterval(carouselTimer);
    if (!track || state.banners.length < 2) return;
    const dots = $$('.dots span');
    const step = () => track.firstElementChild.offsetWidth + 10; // slayd + oraliq
    const current = () => Math.round(track.scrollLeft / step());
    track.addEventListener('scroll', () => {
      const i = current();
      dots.forEach((d, j) => d.classList.toggle('is-active', i === j));
    }, { passive: true });
    let paused = false;
    track.addEventListener('touchstart', () => { paused = true; }, { passive: true });
    track.addEventListener('touchend', () => { setTimeout(() => { paused = false; }, 4000); }, { passive: true });
    carouselTimer = setInterval(() => {
      if (paused || state.view !== 'menu' || document.hidden) return;
      const next = (current() + 1) % state.banners.length;
      track.scrollTo({ left: next * step(), behavior: 'smooth' });
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
      for (const sec of $$('.section')) {
        if (sec.getBoundingClientRect().top - offset <= 0) current = sec.dataset.cat;
      }
      setActiveTab(current || ($$('.section')[0] || {}).dataset?.cat);
    });
  }
  function scrollToCat(cat) {
    const sec = document.getElementById('cat-' + cat);
    const tabs = $('#tabs');
    if (!sec) return;
    spyLock = Date.now() + 700;
    setActiveTab(cat);
    const top = sec.getBoundingClientRect().top + window.scrollY - (tabs ? tabs.offsetHeight : 60) + 4;
    window.scrollTo({ top, behavior: 'smooth' });
  }

  // ---------------------------------------------------------------- product sheet
  function openSheet(id) {
    const p = state.products.get(id);
    if (!p) return;
    state.sheet = { id, qty: 1 };
    const el = $('#sheet');
    el.classList.remove('is-closing');
    el.innerHTML = `
      <div class="sheet__backdrop" data-action="sheet-close"></div>
      <div class="sheet__panel" role="dialog" aria-modal="true">
        <div class="sheet__media" style="${tint(p)}">
          <span class="sheet__grab"></span>${badge(p)}${img(p)}
          <button class="sheet__close" data-action="sheet-close" aria-label="${t('close')}">${ICON.close}</button>
        </div>
        <div class="sheet__body">
          <h3 class="sheet__name">${esc(L(p.name))}</h3>
          ${p.old_price ? `<div class="sheet__price">${priceHtml(p)}</div>` : ''}
          ${L(p.description) ? `<p class="sheet__desc">${esc(L(p.description))}</p>` : '<div style="height:12px"></div>'}
        </div>
        <div class="sheet__foot" id="sheet-foot"></div>
      </div>`;
    el.hidden = false;
    renderSheetFoot();
    updateBackButton();
    haptic('light');
  }

  function renderSheetFoot() {
    const sh = state.sheet;
    const p = sh && state.products.get(sh.id);
    if (!p) return;
    $('#sheet-foot').innerHTML = p.available
      ? `<div class="stepper stepper--soft">
           <button data-action="sheet-dec" aria-label="-">${ICON.minus}</button><span>${sh.qty}</span>
           <button data-action="sheet-inc" aria-label="+">${ICON.plus}</button>
         </div>
         <button class="main-btn main-btn--center" data-action="sheet-add">
           <span class="main-btn__label">${t('add')} · ${money(p.price * sh.qty)}</span>
         </button>`
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

  // ---------------------------------------------------------------- cart view
  function pageHead(title, extra) {
    return `<div class="page-head">
      ${IN_TG ? '' : `<button class="back-btn" data-action="back" aria-label="back">${ICON.back}</button>`}
      <h1>${title}</h1>${extra || ''}
    </div>`;
  }

  function renderCart() {
    const view = $('#view-cart');
    if (!state.cart.size) {
      view.innerHTML = `${pageHead(t('cart'))}
        <div class="empty">
          <img class="empty__img" src="/static/img/burger.svg" alt="">
          <h2 class="empty__title">${t('empty_title')}</h2>
          <p class="empty__sub">${t('empty_sub')}</p>
          <button class="main-btn main-btn--center" data-action="to-menu"><span class="main-btn__label">${t('to_menu')}</span></button>
        </div>`;
      return;
    }
    const s = state.store;
    const subtotal = cartSubtotal();
    const rows = Array.from(state.cart.entries()).map(([id, q]) => {
      const p = state.products.get(id);
      return `<div class="row">
        <div class="thumb" style="${tint(p)}">${img(p)}</div>
        <div class="row__info">
          <div class="row__name">${esc(L(p.name))}</div>
          <div class="row__price">${money(p.price)}${p.old_price ? ` <s>${money(p.old_price)}</s>` : ''}</div>
          <div class="row__total">${money(p.price * q)}</div>
        </div>
        <span data-ctrl="${esc(id)}" data-variant="sm">${control(p, 'sm')}</span>
      </div>`;
    }).join('');

    let progress = '';
    const freeFrom = s.delivery && s.delivery.enabled ? Number(s.delivery.free_from || 0) : 0;
    if (freeFrom) {
      const pct = Math.min(100, Math.round((subtotal / freeFrom) * 100));
      progress = `<div class="progress">
        <div class="progress__text">${subtotal >= freeFrom ? t('free_ok') : t('free_left', { amount: money(freeFrom - subtotal) })}</div>
        <div class="progress__bar"><div class="progress__fill" style="width:${pct}%"></div></div>
      </div>`;
    }

    const upsellCats = ['sauces', 'drinks', 'snacks'];
    const upsell = upsellCats
      .flatMap((c) => Array.from(state.products.values()).filter((p) => p.category === c))
      .filter((p) => p.available && !state.cart.has(p.id))
      .slice(0, 10);

    view.innerHTML = `
      ${pageHead(t('cart'), `<button class="link-btn" data-action="clear">${t('clear')}</button>`)}
      <div class="list">${rows}</div>
      ${progress}
      ${upsell.length ? `<h3 class="upsell-title">${t('upsell')}</h3>
        <div class="upsell">${upsell.map((p) => `<div class="mini" data-action="open" data-id="${esc(p.id)}">
          <div class="mini__media" style="${tint(p)}">${img(p, true)}</div>
          <div class="mini__body">
            <div class="mini__name">${esc(L(p.name))}</div>
            <span class="price">${money(p.price)}</span>
            <div data-ctrl="${esc(p.id)}">${control(p, 'block')}</div>
          </div>
        </div>`).join('')}</div>` : ''}
      <div class="summary">
        <div class="summary__row summary__row--total"><span>${t('subtotal')}</span><span>${money(subtotal)}</span></div>
      </div>`;
  }

  // ---------------------------------------------------------------- checkout view
  function deliveryFee(subtotal) {
    const d = state.store.delivery || {};
    if (state.co.type !== 'delivery') return 0;
    if (d.free_from && subtotal >= d.free_from) return 0;
    return Number(d.fee || 0);
  }
  function minOrder() {
    const cfg = state.store[state.co.type] || {};
    return Number(cfg.min_order || 0);
  }

  function renderCheckout() {
    const s = state.store;
    const co = state.co;
    const canDelivery = !!(s.delivery && s.delivery.enabled);
    const canPickup = !!(s.pickup && s.pickup.enabled);
    const pays = s.payments || { cash: true };
    const payOpt = (key, icon, title, sub) => {
      const enabled = !!pays[key];
      return `<button class="pay-opt ${co.payment === key ? 'is-active' : ''}" data-action="pay" data-pay="${key}" ${enabled ? '' : 'disabled'}>
        <span class="pay-opt__icon pay-opt__icon--${key}">${icon}</span>
        <span class="pay-opt__text"><span class="pay-opt__title">${title}</span><br><span class="pay-opt__sub">${sub}</span></span>
        ${enabled ? '<span class="radio"></span>' : `<span class="soon">${t('soon')}</span>`}
      </button>`;
    };

    $('#view-checkout').innerHTML = `
      ${pageHead(t('checkout'))}
      ${s.is_open ? '' : `<div class="notice notice--danger">${s.paused ? '⏸' : '😴'} <span>${esc(t(s.paused ? 'err_paused' : 'err_closed'))}</span></div>`}

      ${canDelivery && canPickup ? `<div class="block">
        <h3 class="block__title">${t('how')}</h3>
        <div class="segment">
          <button data-action="type" data-type="delivery" class="${co.type === 'delivery' ? 'is-active' : ''}">🚚 ${t('delivery')}</button>
          <button data-action="type" data-type="pickup" class="${co.type === 'pickup' ? 'is-active' : ''}">🛍 ${t('pickup')}</button>
        </div>
      </div>` : ''}

      <div class="block" id="co-delivery" ${co.type === 'delivery' ? '' : 'hidden'}>
        <h3 class="block__title">${t('address')}</h3>
        <label class="field">
          <textarea class="input" id="f-address" data-field="address" rows="2" maxlength="300" placeholder="${esc(t('address_ph'))}">${esc(co.address)}</textarea>
        </label>
        <button class="loc-btn" id="loc-btn" data-action="loc"></button>
        <div id="map-slot"></div>
      </div>

      <div class="block" id="co-pickup" ${co.type === 'pickup' ? '' : 'hidden'}>
        <h3 class="block__title">${t('pickup_from')}</h3>
        <div class="pickup-card">
          <span class="pickup-card__icon">🍔</span>
          <div>
            <div class="pickup-card__title">${esc(L(s.address))}</div>
            ${s.pickup && s.pickup.eta ? `<div class="pickup-card__sub">${esc(t('pickup_eta', { eta: s.pickup.eta }))}</div>` : ''}
          </div>
        </div>
      </div>

      <div class="block">
        <h3 class="block__title">${t('contact')}</h3>
        <label class="field"><span class="field__label">${t('name')}</span>
          <input class="input" id="f-name" data-field="name" maxlength="64" autocomplete="given-name" value="${esc(co.name)}"></label>
        <label class="field"><span class="field__label">${t('phone')}</span>
          <input class="input" id="f-phone" data-field="phone" type="tel" inputmode="tel" maxlength="20" autocomplete="tel" placeholder="+998 90 123 45 67" value="${esc(co.phone)}"></label>
        <label class="field"><span class="field__label">${t('comment')}</span>
          <textarea class="input" data-field="comment" rows="2" maxlength="300" placeholder="${esc(t('comment_ph'))}">${esc(co.comment)}</textarea></label>
      </div>

      <div class="block">
        <h3 class="block__title">${t('payment')}</h3>
        <div class="pay">
          ${payOpt('cash', '💵', t('pay_cash'), t('pay_cash_sub'))}
          ${payOpt('click', 'click', 'Click', t('pay_click_sub'))}
          ${payOpt('payme', 'payme', 'Payme', t('pay_payme_sub'))}
        </div>
      </div>

      <div id="co-summary"></div>`;

    renderLocBtn();
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
      ${min && subtotal < min ? `<div class="summary__warn">${t('min_order', { amount: money(min) })}</div>` : ''}
    </div>`;
    renderBottom();
  }

  function renderLocBtn() {
    const b = $('#loc-btn');
    if (!b) return;
    const set = state.co.lat != null;
    b.classList.toggle('is-set', set);
    b.innerHTML = `<span class="loc-btn__icon">${set ? '✅' : '📍'}</span>
      <span class="loc-btn__text">
        <span class="loc-btn__title">${set ? t('loc_set') : t('loc_title')}</span><br>
        <span class="loc-btn__sub">${set ? t('loc_change') : t('loc_sub')}</span>
      </span>`;
  }

  // ---------------------------------------------------------------- map (Leaflet, faqat kerak bo'lganda yuklanadi)
  let map = null;
  let leafletPromise = null;
  function loadLeaflet() {
    if (window.L) return Promise.resolve();
    if (leafletPromise) return leafletPromise;
    leafletPromise = new Promise((resolve, reject) => {
      const css = document.createElement('link');
      css.rel = 'stylesheet';
      css.href = LEAFLET + 'leaflet.css';
      document.head.appendChild(css);
      const js = document.createElement('script');
      js.src = LEAFLET + 'leaflet.js';
      js.onload = resolve;
      js.onerror = () => { leafletPromise = null; reject(new Error('leaflet')); };
      document.head.appendChild(js);
    });
    return leafletPromise;
  }

  async function getPosition() {
    if (tgAtLeast('8.0') && tg.LocationManager) {
      const lm = tg.LocationManager;
      try {
        if (!lm.isInited) await new Promise((r) => lm.init(r));
        if (lm.isLocationAvailable) {
          const loc = await new Promise((r) => lm.getLocation(r));
          if (loc) return { lat: loc.latitude, lon: loc.longitude };
        }
      } catch (_) { /* brauzer usuliga o'tamiz */ }
    }
    if (!navigator.geolocation) throw new Error('unavailable');
    return new Promise((resolve, reject) => navigator.geolocation.getCurrentPosition(
      (p) => resolve({ lat: p.coords.latitude, lon: p.coords.longitude }),
      reject, { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 },
    ));
  }

  async function locate(centerMap) {
    toast(t('locating'));
    try {
      const pos = await getPosition();
      state.co.lat = +pos.lat.toFixed(6);
      state.co.lon = +pos.lon.toFixed(6);
      renderLocBtn();
      if (centerMap && map) map.setView([pos.lat, pos.lon], 17);
      $('#toast').classList.remove('is-shown');
      haptic('light');
    } catch (_) {
      toast(t('err_location'), true);
    }
  }

  async function openMap() {
    const slot = $('#map-slot');
    if (!slot || map) return;
    slot.innerHTML = `<div class="map-wrap" id="map-wrap">
      <div class="map" id="map"></div>${ICON.pin}
      <div class="map-hint">${t('map_hint')}</div>
      <div class="map-actions"><button class="map-fab" data-action="locate" aria-label="GPS">🎯</button></div>
      <button class="map-done" data-action="map-done">${t('map_done')}</button>
    </div>`;
    try { await loadLeaflet(); } catch (_) { slot.innerHTML = ''; toast(t('err_network'), true); return; }
    const store = state.store.location || { lat: 41.311081, lon: 69.240562 };
    const start = state.co.lat != null ? [state.co.lat, state.co.lon] : [store.lat, store.lon];
    map = window.L.map('map', { zoomControl: false, attributionControl: true }).setView(start, state.co.lat != null ? 17 : 13);
    map.attributionControl.setPrefix('Leaflet');
    window.L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19, attribution: '© OpenStreetMap',
    }).addTo(map);
    const wrap = $('#map-wrap');
    let userMoved = false;
    map.on('dragstart zoomstart', () => { userMoved = true; wrap.classList.add('is-moving'); });
    map.on('moveend', () => {
      wrap.classList.remove('is-moving');
      if (!userMoved && state.co.lat == null) return;
      const c = map.getCenter();
      state.co.lat = +c.lat.toFixed(6);
      state.co.lon = +c.lng.toFixed(6);
      renderLocBtn();
    });
    if (state.co.lat == null) locate(true);
  }

  function closeMap() {
    if (map) { map.remove(); map = null; }
    const slot = $('#map-slot');
    if (slot) slot.innerHTML = '';
  }

  // ---------------------------------------------------------------- submit
  const PHONE_RE = /^\+?[0-9][0-9 ()-]{6,20}$/;

  function markInvalid(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.add('is-invalid');
    el.focus({ preventScroll: true });
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    el.addEventListener('input', () => el.classList.remove('is-invalid'), { once: true });
  }

  async function submitOrder() {
    if (state.submitting) return;
    const co = state.co;
    const s = state.store;
    if (!s.is_open) { toast(t(s.paused ? 'err_paused' : 'err_closed'), true); return; }
    if (!state.cart.size) { toast(t('err_empty_cart'), true); return; }
    if (co.type === 'delivery' && co.address.trim().length < 5) { markInvalid('f-address'); toast(t('err_bad_address'), true); return; }
    const digits = (co.phone.match(/\d/g) || []).length;
    if (!PHONE_RE.test(co.phone.trim()) || digits < 9 || digits > 15) { markInvalid('f-phone'); toast(t('err_bad_phone'), true); return; }
    const subtotal = cartSubtotal();
    if (minOrder() && subtotal < minOrder()) { toast(t('err_min_order', { amount: money(minOrder()) }), true); return; }

    state.submitting = true;
    renderBottom();
    const body = {
      items: Array.from(state.cart.entries()).map(([id, qty]) => ({ id, qty })),
      type: co.type,
      address: co.type === 'delivery' ? co.address.trim() : '',
      lat: co.type === 'delivery' ? co.lat : null,
      lon: co.type === 'delivery' ? co.lon : null,
      name: co.name.trim(),
      phone: co.phone.trim(),
      comment: co.comment.trim(),
      payment: co.payment,
      lang: state.lang,
    };
    let res;
    try {
      res = await api('/api/order', body);
    } catch (_) {
      state.submitting = false;
      renderBottom();
      toast(t('err_network'), true);
      return;
    }
    state.submitting = false;

    if (res.data && res.data.ok) {
      state.lastOrder = { id: res.data.order.id, total: res.data.order.total, type: co.type };
      state.cart.clear();
      saveCart();
      closeMap();
      state.stack = [];
      haptic('success');
      go('success', false);
      return;
    }
    handleOrderError(res.data || {});
    renderBottom();
  }

  function handleOrderError(data) {
    const code = data.error || 'generic';
    if (code === 'unavailable' && data.product_id) {
      const p = state.products.get(data.product_id);
      if (p) {
        p.available = false;
        state.cart.delete(p.id);
        saveCart();
        refreshControls(p.id);
        renderCheckoutSummary();
        toast(t('err_unavailable', { name: L(p.name) }), true);
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
    const eta = o.type === 'pickup' ? (s.pickup && s.pickup.eta) : (s.delivery && s.delivery.eta);
    $('#view-success').innerHTML = `<div class="success">
      <svg class="check" viewBox="0 0 104 104"><circle cx="52" cy="52" r="52"/><path d="M31 53l14 14 28-29"/></svg>
      <h1>${esc(t('success_title', { id: o.id }))}</h1>
      <p>${t('success_sub')}</p>
      <div class="summary">
        <div class="summary__row"><span>${t('order_no')}</span><span><b>#${esc(o.id)}</b></span></div>
        ${eta ? `<div class="summary__row"><span>${o.type === 'pickup' ? t('eta_pickup') : t('eta_delivery')}</span><span>~${esc(eta)} ${t('min')}</span></div>` : ''}
        <div class="summary__row summary__row--total"><span>${t('total')}</span><span>${money(o.total || 0)}</span></div>
      </div>
      <button class="ghost-btn" data-action="to-menu">${t('to_menu')}</button>
    </div>`;
  }

  // ---------------------------------------------------------------- bottom bar
  function renderBottom() {
    const bar = $('#bottom-bar');
    const v = state.view;
    let html = '';
    const count = cartCount();
    const subtotal = cartSubtotal();
    if (v === 'menu' && count) {
      html = `<button class="main-btn" data-action="to-cart">
        <span class="main-btn__count">${count}</span>
        <span class="main-btn__label">${t('view_cart')}</span>
        <span class="main-btn__total">${money(subtotal)}</span>
      </button>`;
    } else if (v === 'cart' && count) {
      html = `<button class="main-btn" data-action="to-checkout">
        <span class="main-btn__label">${t('checkout')}</span>
        <span class="main-btn__total">${money(subtotal)}</span>
      </button>`;
    } else if (v === 'checkout' && count) {
      const total = subtotal + deliveryFee(subtotal);
      const blocked = !state.store.is_open || (minOrder() && subtotal < minOrder());
      html = `<button class="main-btn" data-action="submit" ${blocked || state.submitting ? 'disabled' : ''}>
        <span class="main-btn__label">${state.submitting ? '<span class="spinner"></span>' : t('place')}</span>
        <span class="main-btn__total">${money(total)}</span>
      </button>`;
    } else if (v === 'success' && IN_TG) {
      html = `<button class="main-btn main-btn--center" data-action="close"><span class="main-btn__label">${t('close')}</span></button>`;
    }
    bar.innerHTML = html;
    bar.hidden = !html;
  }

  // ---------------------------------------------------------------- error view
  function showError(titleKey, subKey, canRetry) {
    $('#view-error').innerHTML = `<div class="empty">
      <img class="empty__img" src="/static/img/logo.svg" alt="">
      <h2 class="empty__title">${t(titleKey)}</h2>
      ${subKey ? `<p class="empty__sub">${t(subKey)}</p>` : ''}
      ${canRetry ? `<button class="main-btn main-btn--center" data-action="retry"><span class="main-btn__label">${t('retry')}</span></button>` : ''}
    </div>`;
    state.view = 'error';
    show('error');
    renderBottom();
  }

  // ---------------------------------------------------------------- events
  document.addEventListener('click', (e) => {
    const el = e.target.closest('[data-action]');
    if (!el) return;
    const a = el.dataset.action;
    const id = el.dataset.id;
    switch (a) {
      case 'inc': e.stopPropagation(); setQty(id, (state.cart.get(id) || 0) + 1); break;
      case 'dec': e.stopPropagation(); setQty(id, (state.cart.get(id) || 0) - 1); break;
      case 'open': openSheet(id); break;
      case 'banner': openBanner(el.dataset.type, el.dataset.target); break;
      case 'tab': scrollToCat(el.dataset.cat); haptic('select'); break;
      case 'sheet-close': closeSheet(); break;
      case 'sheet-inc': state.sheet.qty = Math.min(50, state.sheet.qty + 1); renderSheetFoot(); haptic('select'); break;
      case 'sheet-dec': state.sheet.qty = Math.max(1, state.sheet.qty - 1); renderSheetFoot(); haptic('select'); break;
      case 'sheet-add': {
        const sid = state.sheet.id;
        const qty = state.sheet.qty;
        closeSheet();
        setQty(sid, (state.cart.get(sid) || 0) + qty);
        haptic('medium');
        break;
      }
      case 'to-cart': go('cart'); break;
      case 'to-checkout': go('checkout'); break;
      case 'to-menu': state.stack = []; go('menu', false); break;
      case 'back': goBack(); break;
      case 'clear': state.cart.clear(); saveCart(); refreshAllControls(); renderCart(); renderBottom(); haptic('warning'); break;
      case 'type': {
        state.co.type = el.dataset.type;
        $$('.segment button').forEach((b) => b.classList.toggle('is-active', b.dataset.type === state.co.type));
        $('#co-delivery').hidden = state.co.type !== 'delivery';
        $('#co-pickup').hidden = state.co.type !== 'pickup';
        if (map) map.invalidateSize();
        renderCheckoutSummary();
        haptic('select');
        break;
      }
      case 'pay':
        if (el.disabled) break;
        state.co.payment = el.dataset.pay;
        $$('.pay-opt').forEach((b) => b.classList.toggle('is-active', b.dataset.pay === state.co.payment));
        haptic('select');
        break;
      case 'loc': if (map) closeMap(); else openMap(); break;
      case 'locate': locate(true); break;
      case 'map-done': closeMap(); break;
      case 'submit': submitOrder(); break;
      case 'close': if (tg) tg.close(); break;
      case 'retry': init(); break;
      default: break;
    }
  });

  document.addEventListener('input', (e) => {
    const f = e.target.dataset && e.target.dataset.field;
    if (f) state.co[f] = e.target.value;
  });
  window.addEventListener('scroll', onScroll, { passive: true });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') goBack(); });

  // ---------------------------------------------------------------- init
  async function init() {
    document.documentElement.lang = state.lang;
    state.view = 'loading';
    show('loading');
    let res;
    try {
      res = await api('/api/bootstrap');
    } catch (_) {
      showError('err_network', null, true);
      return;
    }
    if (res.status === 401) { showError('open_in_tg', 'open_in_tg_sub', false); return; }
    if (!res.data || !res.data.ok) { showError('err_generic', null, true); return; }

    const d = res.data;
    state.store = d.store;
    state.categories = d.menu.categories;
    state.products = new Map(d.menu.products.map((p) => [p.id, p]));
    state.banners = d.banners || [];
    state.profile = d.profile || {};
    if (state.profile.lang === 'uz' || state.profile.lang === 'ru') state.lang = state.profile.lang;
    document.documentElement.lang = state.lang;

    const co = state.co;
    co.name = state.profile.name || '';
    co.phone = state.profile.phone || '+998 ';
    co.address = state.profile.address || '';
    if (!(state.store.delivery && state.store.delivery.enabled)) co.type = 'pickup';
    const pays = state.store.payments || {};
    co.payment = ['cash', 'click', 'payme'].find((k) => pays[k]) || 'cash';

    loadCart();
    renderMenu();
    setupCarousel();
    state.view = 'menu';
    go('menu', false);
    onScroll();
  }

  applyTheme();
  setupTelegram();
  init();
})();
