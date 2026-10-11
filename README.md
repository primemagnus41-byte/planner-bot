# Shaxsiy Planner Bot (Arxitektura v2 + Obuna tizimi)

Ushbu bot shaxsiy rejalashtirish, mutolaa monitoringi, oraliqli takrorlash (SM-2 Spaced Repetition) va g'oyalarni saqlash uchun mo'ljallangan. Shuningdek, to'liq **Obuna (Subscription)** va **Admin boshqaruv tizimi** integratsiya qilingan.

---

## 🚀 Asosiy imkoniyatlar

1. **📋 Vazifalar va Reja:**
   - Kunlik reja ro'yxati, progress bar (`[████░░░░░░] 40%`).
   - Prioritetlar (Normal, Yuqori, Shoshilinch).
   - Vazifani bajarish (✅), o'tkazib yuborish (⚪️), o'chirish (🗑) va **Bekor qilish (Undo ↩️)**.
   - Kechagi bajarilmagan ishlarni avtomatik bugungi kunga ko'chirish.

2. **📚 Mutolaa (Reading):**
   - O'qilayotgan kitoblarning betlari va foizli progressi.
   - Har bir o'qish sessiyasini qayd etish.
   - Kitob tugagach taqriz va baho berish.

3. **🧠 Dars & SM-2 (Spaced Repetition):**
   - SuperMemo-2 ilmiy algoritmi bo'yicha oraliqli takrorlash.
   - Xotirani baholash (0, 3, 4, 5).
   - O'z vaqtida takrorlash eslatmalari.

4. **💡 G'oyalar va qaydlar:**
   - Tezkor fikrlarni toifalar va teglar bilan saqlash.
   - Pagination (sahifalash) va muhimlik (Star ⭐️).

5. **⏰ Eslatmalar (Outbox Pattern):**
   - Restartdan so'ng ham hech narsa yo'qolmaydi (`reminders` jadvali).
   - Ertalabki rejalashtirish va kechki sarhisob eslatmalari.
   - Obuna tugashiga 2 kun qolganda avtomatik ogohlantirish.
   - Har kecha ma'lumotlar bazasining backup nusxasini adminga yuborish.

6. **💎 Obuna (Subscription) Tizimi:**
   - Yangi foydalanuvchilar uchun avtomatik bepul sinov muddati (Trial — masalan 3 kun).
   - Obuna muddati tugaganda bot funksiyalari cheklanadi va to'lov uchun admin username'ga yo'naltiriladi (`@{admin_username}`).
   - Admin uchun qo'lda obuna berish/uzaytirish buyrug'i: `/grant <user_id> <kun>` (masalan: `/grant 123456789 30`).

---

## 📁 Arxitektura tuzilishi

Qatlamli (Clean Layered) arxitektura:
* **`app/config.py`**: Pydantic-settings orqali `.env` validatsiyasi.
* **`app/db/models/`**: SQLAlchemy 2.0 modellari (User, Subscription, Task, Book, Topic, SrsCard, Idea, Reminder).
* **`app/db/repositories/`**: Ma'lumotlar bazasi so'rovlari va IDOR himoyasi (`get_owned`).
* **`app/services/`**: Biznes mantiq (Aiogram import qilmaydi, 100% testlanuvchan).
* **`app/bot/middlewares/`**: Xatolar, DB sessiya, Obuna va kirish nazorati, Throttling.
* **`app/bot/handlers/`**: Taqdimot qatlami (Faqat interfeys va buyruqlar).
* **`app/scheduler/`**: APScheduler + Outbox pattern.

---

## 🛠 O'rnatish va ishga tushirish

### 1. Muhitni tayyorlash
```bash
# Virtual muhitni faollashtirish (Windows)
.\.venv\Scripts\activate

# Kutubxonalarni o'rnatish
pip install -r requirements.txt
```

### 2. `.env` faylini sozlash
`.env` faylida o'z ma'lumotlaringizni kiriting:
```env
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_ID=your_telegram_numeric_id
ADMIN_USERNAME=your_admin_username
DATABASE_URL=sqlite+aiosqlite:///data/planner.db
DEFAULT_TIMEZONE=Asia/Tashkent
LOG_LEVEL=INFO
TRIAL_DAYS=3
```

### 3. Ma'lumotlar bazasi migratsiyasi (Alembic)
```bash
alembic upgrade head
```

### 4. Botni ishga tushirish
```bash
python main.py
```

---

## 🧪 Testlarni ishga tushirish

Barcha biznes mantiq va SM-2 algoritmini tekshirish uchun:
```bash
python -m pytest -v
```

---

## 🐳 Docker orqali ishga tushirish

```bash
docker compose up -d --build
```
`./data` jildi Volume qilib ulangan, shuning uchun konteyner qayta o'chib yonsa ham baza saqlanib qoladi.
