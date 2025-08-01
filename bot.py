import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telethon import TelegramClient
from telethon.errors import FloodWaitError

API_ID = 22731419
API_HASH = '2e2a9ce500a5bd08bae56f6ac2cc4890'
BOT_TOKEN = '7936881674:AAFhO3rBeNLqCka4xDQ3UenJCF8PMpxf1cE'

GROUPS = [
    "https://t.me/buvayda_toshkent_bogdod_toshkent",
    # ... (boshqa barcha guruhlaringiz)
    1373629932
]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
client = TelegramClient("elon_session", API_ID, API_HASH)
user_data = {}

# Klaviaturalar
def start_menu():
    return InlineKeyboardMarkup().add(InlineKeyboardButton("📤 E'lon berish", callback_data="elon"))

def confirm_menu():
    return InlineKeyboardMarkup().add(InlineKeyboardButton("✅ Tasdiqlash", callback_data="tasdiqla"))

def cancel_reply_button():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("⛔ To‘xtatish"))
    return kb

def new_ad_button():
    return InlineKeyboardMarkup().add(InlineKeyboardButton("📤 Yangi e'lon", callback_data="elon"))

# Start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Assalomu alaykum!\nE'lon yuborish uchun quyidagini tanlang:", reply_markup=start_menu())

# Tugmalar ishlovchi
@dp.callback_query_handler(lambda call: True)
async def callbacks(call: types.CallbackQuery):
    user_id = call.from_user.id

    if call.data == "elon":
        user_data[user_id] = {"step": "waiting_for_elon", "stop": False}
        await call.message.edit_reply_markup()
        await call.message.answer("✍️ E'lon matnini yuboring:", reply_markup=ReplyKeyboardRemove())

    elif call.data == "tasdiqla":
        if user_id not in user_data or "text" not in user_data[user_id]:
            await call.message.answer("Avval e'lon yuboring.")
            return

        user_data[user_id]["stop"] = False
        await call.message.edit_reply_markup()
        await call.message.answer("📤 E'lon yuborilmoqda...", reply_markup=cancel_reply_button())

        text = user_data[user_id]["text"]

        async def continuous_send():
            while not user_data.get(user_id, {}).get("stop"):
                for group in GROUPS:
                    if user_data.get(user_id, {}).get("stop"):
                        await bot.send_message(user_id, "❌ Yuborish to‘xtatildi.", reply_markup=new_ad_button())
                        return
                    try:
                        await client.send_message(group, text)
                        await bot.send_message(user_id, f"✅ Yuborildi: {group}")
                    except FloodWaitError as e:
                        await asyncio.sleep(e.seconds)
                        await bot.send_message(user_id, f"⏱ Kutish: {e.seconds} sekund ({group})")
                    except Exception as e:
                        await bot.send_message(user_id, f"❌ Xatolik: {group}\n{e}")
                    await asyncio.sleep(0.5)  # Har bir guruh orasida 0.5 sek

                await asyncio.sleep(60)  # 1 daqiqa kutish (har doira uchun)

        asyncio.create_task(continuous_send())

# To‘xtatish tugmasi
@dp.message_handler(lambda msg: msg.text == "⛔ To‘xtatish")
async def stop_handler(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_data:
        user_data[user_id]["stop"] = True
        await message.answer("🚫 Yuborish to‘xtatildi.", reply_markup=ReplyKeyboardRemove())
        await message.answer("Yuborishni qaytadan boshlash uchun pastdagi tugmani bosing:", reply_markup=new_ad_button())

# Matn qabul qilish
@dp.message_handler()
async def text_handler(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_data and user_data[user_id].get("step") == "waiting_for_elon":
        user_data[user_id]["text"] = message.text
        user_data[user_id]["step"] = "ready"
        await message.answer("✅ E'lon qabul qilindi. Tasdiqlash uchun tugmani bosing:", reply_markup=confirm_menu())
    else:
        await message.answer("E'lon yuborish uchun /start buyrug‘idan foydalaning.")

# Ishga tushirish
async def main():
    logging.basicConfig(level=logging.INFO)
    await client.start()
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())
