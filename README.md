# 🍔 Ayva Burgers — Telegram yetkazib berish boti

Telegram bot, Mini App (bot ichida ochiladigan menyu) va admin panel. Mijoz rasmli menyudan taom tanlaydi,
savatga soladi, manzil yoki olib ketish filialini belgilaydi, buyurtma beradi. Buyurtma darhol tegishli
filialning xodimlar guruhiga va admin panelga tushadi. Restoran egasi menyu, narx, rasm, aksiya va sozlamalarni panelning o'zidan boshqaradi —
dasturchi kerak emas.

![Ayva Burgers Mini App va admin panel](docs/preview.png)

## Imkoniyatlar

**Mijoz uchun (o'zbekcha / ruscha)**
- Birinchi kirishda 3 qadam: **telefon → ism → manzil** (lokatsiya, yozilgan manzil yoki «🛍 Olib ketaman» + filial),
  keyin menyu. Hammasi eslab qolinadi — keyingi safar «🍔 Buyurtma berish» saqlangan manzil bilan darhol menyuni
  ochadi («📍 Manzilni o'zgartirish», «🛍 Olib ketaman» tugmalari bilan)
- Mini App — minimalistik dizayn (Inter shrifti, oq/qora, bitta qizil aksent), yorug' va qorong'i rejim
- Mini App: aksiya bannerlari, «🔥 Aksiyalar» bo'limi, kategoriyalar, rasmli kartalar, chegirma narxlari
  (eski narx chizilgan), «Hit / Yangi / Achchiq» belgilari, savat
- Bepul yetkazishgacha qolgan summa ko'rsatkichi, sous/ichimlik takliflari
- Lokatsiya Telegram'ning o'z tugmasi bilan yuboriladi va OpenStreetMap orqali matnga aylantiriladi
- Mini App'da ism, telefon va manzil kartochka ko'rinishida (xarita bilan); olib ketishda filial tanlanadi
  (ish vaqti va «hozir yopiq» belgisi bilan); yetkazib berishda eng yaqin ochiq filial avtomatik tanlanadi
- **Filiallar**: CHPK, Charxiy (24/7), Navoiy — har birining ish vaqti, manzili, telefoni va o'z xodimlar guruhi
- **📦 Buyurtmalarim**: holati, 🔁 bir tugmada takrorlash (savatga tushadi), hali qabul qilinmagan buyurtmani
  ❌ bekor qilish (guruhga xabar boradi)
- **⭐ Baho**: buyurtma yakunlangach mijoz 1–5 baho qo'yadi; 3 va undan pastida «nima yoqmadi?» deb so'raladi —
  baho va izoh filial guruhiga keladi, panelda statistikasi ko'rinadi
- Variantli mahsulotlar: pitsa (kichik/o'rta/katta), lavash (mini/oddiy/extra), hot-dog (klassik/cheese/…)
- To'lov: faqat naqd pul (kuryerga yoki kassada)
- Ish vaqtidan tashqari yoki admin to'xtatganda buyurtma qabul qilinmaydi (menyuni ko'rish mumkin)
- Bosh menyu: «🍔 Buyurtma berish», «📦 Buyurtmalarim», «🏪 Filiallar», «📞 Aloqa»,
  «⚙️ Sozlamalar» (ism, raqam, manzil, tilni o'zgartirish)

**Admin panel** (botda `/panel` yoki «🛠 Admin panel» tugmasi)
- 📋 **Buyurtmalar** — faol buyurtmalar, bir tugma bilan holat o'zgartirish, tarix, raqam/telefon bo'yicha qidiruv,
  filial bo'yicha filtr, mijoz bahosi va izohi. Yangi buyurtma kelsa panel o'zi xabar beradi
- 🍔 **Menyu** — mahsulot qo'shish/tahrirlash/o'chirish: rasm (telefondan yuklanadi, avtomatik kichraytiriladi),
  nomi va tarkibi (uz/ru), narx, kategoriya, belgi. «Sotuvda bor» (stop-list) va «Menyuda ko'rsatish» o'tkazgichlari,
  tartibni o'zgartirish. Kategoriyalarni qo'shish, nomlash, rasmini tanlash, yashirish
- 🔥 **Aksiyalar** — chegirma narxi (sana bilan yoki muddatsiz, −10/−20/−30% tugmalari),
  menyu tepasida aylanadigan bannerlar (rasm yoki sarlavha, bosilganda mahsulot yoki kategoriyani ochadi)
- 📊 **Statistika** — bugun / 7 / 30 kun: tushum, buyurtmalar, o'rtacha chek, yangi mijozlar, o'rtacha baho
  (1–5 taqsimoti va so'nggi izohlar), filiallar kesimida, kunlik tushum grafigi, soatlar bo'yicha yuklama,
  eng ko'p sotilgan mahsulotlar
- ⚙️ **Sozlamalar** — buyurtmalarni vaqtincha to'xtatish, **filiallar** (nomi, manzili, telefoni, ish vaqti,
  xaritadagi nuqtasi — Google/Yandex havolasini qo'yish kifoya, buyurtmalar guruhi), restoran ma'lumotlari,
  yetkazish narxi, bepul yetkazish chegarasi, minimal buyurtma, adminlar ro'yxati,
  mijozlarga xabar (rasm + matn + «Menyuni ochish» tugmasi)
- Telefonda Telegram ichida ochiladi; kompyuterda — bot beradigan bir martalik havola orqali (parolsiz)

**Rollar**

| Rol | Kim belgilaydi | Nima qila oladi |
|---|---|---|
| 👑 Egasi | `.env` dagi `ADMIN_IDS` | Hammasi + adminlarni qo'shish, rolini o'zgartirish, o'chirish |
| Administrator | Egasi panelda qo'shadi | Menyu, narx, rasm, aksiyalar, statistika, sozlamalar, mijozlarga xabar |
| 🧾 Kassir | Egasi panelda qo'shadi | Faqat buyurtmalar, stop-list (mahsulot tugadi/bor) va buyurtmani vaqtincha to'xtatish |

Cheklovlar serverda tekshiriladi — kassir narxni yoki menyuni hatto to'g'ridan-to'g'ri so'rov bilan ham o'zgartira olmaydi.

**Xodimlar guruhi**
- Buyurtma filialning o'z guruhiga keladi (panel → Sozlamalar → Filiallar → «Buyurtmalar guruhi»).
  Guruh belgilanmagan filial buyurtmalari umumiy `ADMIN_CHAT_ID` guruhiga tushadi
- Har bir buyurtma: filial, mijoz, telefon, manzil, xarita havolasi, mahsulotlar, summa
- Tugmalar: ✅ Qabul qilish → 🚗 Yo'lga chiqdi / 🛍 Tayyor → 🏁 Yakunlash, ❌ Bekor qilish
  (panel bilan sinxron — qayerda bosilsa ham ikkalasida yangilanadi)
- `/active` (filial guruhida — faqat o'sha filial buyurtmalari), `/stats`, `/stoplist`, `/broadcast`, `/panel`, `/id`
- Guruh — ishonchli xodimlar xonasi: guruhdagi hamma buyurtma tugmalarini, `/active`, `/stats` va `/stoplist` ni
  ishlata oladi. `/broadcast` (mijozlarga reklama) faqat ega va administratorga; botning shaxsiy chatida
  kassirga `/stats` ham yopiq

**Xavfsizlik va tezlik**
- Narxlar faqat serverda hisoblanadi (aksiya narxi ham) — mijoz narxni o'zgartira olmaydi
- Mini App va panel so'rovlari Telegram imzosi (`initData`) bilan tekshiriladi; kompyuterdagi kirish —
  imzolangan cookie (7 kun), bir martalik havola 10 daqiqa amal qiladi
- Panelga faqat egalar (`ADMIN_IDS`) va ular qo'shgan adminlar kira oladi
- Asinxron server (aiohttp + aiogram 3, webhook): 200–300 ta bir vaqtdagi mijoz uchun bemalol yetadi

## Tuzilishi

```
bot/              Python server
  handlers/       bot: mijoz (user.py) va admin (admin.py)
  admin_api.py    admin panel API (/api/admin/*), rasm yuklash, kirish
  web.py          Mini App API (/api/bootstrap, /api/order)
  catalog.py      menyu, aksiya narxlari, ish vaqti, narx hisoblash
  db.py           SQLite: buyurtmalar, mijozlar, menyu, bannerlar, sozlamalar, adminlar
  orders.py       buyurtma xabarlari va holatlari
  seed.py         birinchi ishga tushishda data/*.json → baza
webapp/           Mini App (index.html, app.js, styles.css, rasmlar)
webapp/admin/     admin panel (index.html, admin.js, admin.css)
data/             menu.json, store.json — faqat birinchi ishga tushish uchun namuna
tests/            avtomatik testlar
```

## 1. Telegram'da tayyorgarlik (5 daqiqa)

1. [@BotFather](https://t.me/BotFather) → `/newbot` → nom: `Ayva Burgers`, username masalan `ayvaburgers_bot`.
   Berilgan **tokenni** saqlang.
2. BotFather'da: `/setuserpic` (logo), `/setdescription`, `/setabouttext`.
3. Xodimlar uchun Telegram **guruh** oching (masalan «Ayva — Buyurtmalar»), botni qo'shing va
   **admin** qiling.
4. Bot ishga tushgach:
   - guruhda `/id` yozing → chiqqan raqam `ADMIN_CHAT_ID` bo'ladi;
   - botga shaxsiy `/id` yozing → sizning ID'ingiz `ADMIN_IDS` bo'ladi (panel egasi).
   Ikkalasini server sozlamalariga qo'yib, qayta ishga tushiring.
5. Botga `/panel` yozing — admin panel ochiladi. Boshqa xodimlarni panel → Sozlamalar → Adminlar orqali
   qo'shasiz: Telegram ID (xodim botga `/id` yozib biladi) va rol — Administrator yoki Kassir.
6. Har bir filial uchun alohida guruh kerak bo'lsa (CHPK, Charxiy, Navoiy): har biriga botni qo'shing,
   guruhda `/id` yozing va panel → Sozlamalar → Filiallar → filial → «Buyurtmalar guruhi»ga qo'ying.
   Server sozlamalarini o'zgartirish yoki qayta ishga tushirish shart emas.

## 2. Serverga joylash

### A variant — Railway (tavsiya: eng tez va oson, ~5$/oy)

1. Bu repozitoriyni GitHub'ga yuklang.
2. [railway.com](https://railway.com) → **New Project → Deploy from GitHub repo** → shu repo.
3. Servis **Settings → Networking → Generate Domain** (https manzil beriladi, `PUBLIC_URL` avtomatik olinadi).
4. **Variables**: `BOT_TOKEN`, `ADMIN_CHAT_ID`, `ADMIN_IDS` (xohlasangiz `ADMIN_LANG=ru`).
5. **Volume** qo'shing, mount path: `/data` — **majburiy**: buyurtmalar, menyu va yuklangan rasmlar shu yerda
   saqlanadi. Volume bo'lmasa, har deployda hammasi o'chib ketadi.
6. Deploy tugagach botga `/start` yozing.

### B variant — o'z VPS'ingiz (Docker + avtomatik HTTPS)

Kerak: VPS (Ubuntu, 1 GB RAM yetadi), domen (masalan `menu.ayvaburgers.uz`) — uning A-yozuvi VPS IP'siga.

```bash
git clone <repo> ayva && cd ayva
cp .env.example .env      # BOT_TOKEN, ADMIN_CHAT_ID, ADMIN_IDS, DOMAIN ni to'ldiring
docker compose up -d --build
docker compose logs -f bot
```

Baza va rasmlar `ayva-data` docker volume'ida saqlanadi.

### Tez sinov — GitHub Actions'da (bepul, 6 soatgacha)

Server olmasdan botni ko'rib chiqish uchun. **Doimiy ishlash uchun emas**: vaqt tugagach bot to'xtaydi,
paneldagi o'zgarishlar va buyurtmalar o'chadi (har safar namuna menyu bilan boshlanadi).

1. Repozitoriya → **Settings → Secrets and variables → Actions → New repository secret** →
   Name: `BOT_TOKEN`, Secret: @BotFather bergan token. Tokenni hech qachon kodga yoki ochiq joyga yozmang.
2. **Actions → «Botni sinash (6 soatgacha)» → Run workflow**. Admin panel uchun `admin_ids` ga Telegram
   ID'ingizni yozing (bilmasangiz, avval bo'sh qoldirib ishga tushiring va botga `/id` yozing).
3. 1–2 daqiqadan keyin botga `/start` yozing.

### Kompyuterda sinash

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env      # BOT_TOKEN ni yozing

# Faqat dizaynni ko'rish (Telegram'siz): http://localhost:8080 va http://localhost:8080/admin/
BOT_MODE=web DEV_MODE=1 python -m bot

# Botni to'liq sinash uchun https tunnel kerak (Mini App faqat https'da ochiladi):
#   cloudflared tunnel --url http://localhost:8080   → berilgan https manzilni PUBLIC_URL ga yozing
python -m bot

pytest -q                 # testlar
```

`DEV_MODE=1` da panel parolsiz ochiladi — serverda **hech qachon** yoqmang.

## 3. Menyu va ma'lumotlar

Hammasi admin paneldan o'zgartiriladi, serverni qayta ishga tushirish kerak emas — o'zgarish mijozlarda darhol ko'rinadi.

- `data/menu.json` va `data/store.json` faqat **birinchi** ishga tushishda bazaga yuklanadi. Menyu
  t.me/ayva_burgers kanalidagi menyu jadvallari asosida tuzilgan — **narxlar 2023-yil yanvardagi**, ularni
  paneldan yangilang.
- Mahsulot suratlari `webapp/img/products/` da — kanal postlaridan kesib olingan; paneldan istalganini almashtirish mumkin.
  Keyin ular o'qilmaydi, menyu bazada saqlanadi.
- Mahsulot rasmlari: telefondan yoki kompyuterdan yuklang (JPG/PNG/WebP, 12 MB gacha). Server ularni
  1200 px gacha kichraytirib, WebP'ga o'giradi. Rasm bo'lmasa kategoriyaning chizilgan rasmi chiqadi.
- **Filiallar** `data/store.json` dagi `branches` ro'yxatidan birinchi ishga tushishda yuklanadi; keyin paneldan
  boshqariladi. Navoiy filialining aniq manzili va uchala filialning xaritadagi nuqtasini panelda kiriting —
  nuqta bo'lsa, yetkazib berish buyurtmasi mijozga eng yaqin ochiq filialga tushadi.
- **Logo va ranglar**: logolar — `webapp/img/logo-dark.png` (oq fon uchun), `logo-light.png` (qora fon uchun),
  `logo-badge.png`; brend rangi — `webapp/styles.css` boshidagi `--brand` (qizil).
