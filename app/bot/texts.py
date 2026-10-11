# Planner Bot — Barcha matnlar

WELCOME_START = (
    "👋 <b>Assalomu alaykum, {name}!</b>\n\n"
    "<b>Shaxsiy Planner Bot</b>ga xush kelibsiz.\n"
    "Bu bot orqali siz:\n"
    "• 📋 Kunlik va haftalik vazifalaringizni rejalashtirasiz\n"
    "• 📚 Kitob o'qish jarayoni va qaydlaringizni kuzatasiz\n"
    "• 🧠 Spaced repetition (SM-2) orqali o'rganganlaringizni esda saqlaysiz\n"
    "• 💡 Fikr va g'oyalaringizni tezda saqlab borasiz\n\n"
    "Pastdagi menyu tugmalaridan foydalanishingiz mumkin."
)

ACCESS_TRIAL_STARTED = (
    "🎉 <b>Xush kelibsiz!</b>\n\n"
    "Sizga <b>{days} kunlik bepul sinov muddati</b> faollashtirildi!\n"
    "Sinov muddati: <b>{expires_at}</b> gacha amal qiladi.\n\n"
    "Bot imkoniyatlaridan to'liq foydalanishingiz mumkin."
)

ACCESS_EXPIRED = (
    "⏳ <b>Obuna muddati tugagan!</b>\n\n"
    "Bot xizmatlaridan foydalanishni davom ettirish uchun obunani yangilashingiz kerak.\n\n"
    "💳 <b>Obuna bo'lish uchun adminga murojaat qiling:</b>\n"
    "👉 @{admin_username}\n\n"
    "To'lov qilingandan so'ng sizga darhol to'liq kirish huquqi beriladi."
)

ACCESS_BANNED = (
    "⛔️ <b>Kirish taqiqlangan!</b>\n\n"
    "Sizning hisobingiz bot ma'muri tomonidan bloklangan."
)

GENERIC_ERROR = "⚠️ Kutilmagan xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring."

CANCELLED = "❌ Amal bekor qilindi."

SUBSCRIPTION_INFO = (
    "💎 <b>Obuna ma'lumotlari:</b>\n\n"
    "• Holati: <b>{status}</b>\n"
    "• Tarif: <b>{plan}</b>\n"
    "• Amal qilish muddati: <b>{expires_at}</b>\n\n"
    "Obunani uzaytirish yoki to'lov qilish uchun adminga yozing: @{admin_username}"
)

PLANS_TEXT = (
    "💎 <b>Tariflar va obuna rejalari:</b>\n\n"
    "1️⃣ <b>1 oylik:</b> 30 000 so'm\n"
    "2️⃣ <b>3 oylik:</b> 75 000 so'm (tejamkor)\n"
    "3️⃣ <b>1 yillik:</b> 250 000 so'm (eng foydali)\n\n"
    "To'lov qilish va faollashtirish uchun adminga murojaat qiling:\n"
    "👉 @{admin_username}"
)
