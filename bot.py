import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telethon import TelegramClient
from telethon.errors import FloodWaitError
import logging

API_ID = 22731419
API_HASH = '2e2a9ce500a5bd08bae56f6ac2cc4890'
BOT_TOKEN = '7936881674:AAFhO3rBeNLqCka4xDQ3UenJCF8PMpxf1cE'

GROUP_LINKS = [
    "https://t.me/buvayda_toshkentttt", "https://t.me/buvayda_bogdod_rishton_toshkend1",
    "https://t.me/BUVAYDA_YANGIQORGON_Toshkentt", "https://t.me/Toshkent_bogdod_buvayda_taksi",
    "https://t.me/buvayda_toshkent_bogdod_toshkent", "https://t.me/buvayda_toshkent_taksi2",
    "https://t.me/Buvayda_Bogdod_Toshkent", "https://t.me/Rishton_Toshkent2",
    "https://t.me/TOSHKENT_RISHTON_TAXI_745", "https://t.me/toshkentrishtonbagdod",
    "https://t.me/bagdod_rishton_toshkent_qoqon", "https://t.me/Toshkent_Rishton",
    "https://t.me/bagdod_rishton_qoqon_toshkent", "https://t.me/buvayda_toshkent_buvayda_taxi",
    "https://t.me/rishton_toshkent_24", "https://t.me/Rishton_Toshkent_Rishton",
    "https://t.me/pitagkr", "https://t.me/Bogdodtoshkenttaksi1",
    "https://t.me/Toshkent_Rishton24", "https://t.me/ToshkentRishtonTaxi",
    "https://t.me/Rishton_Toshkent", "https://t.me/rishton_toshkent_1",
    "https://t.me/taxichen", "https://t.me/toshkent_rishton_taxi",
    "https://t.me/Rishton_Toshkent_Bogdod_Taksi_01", "https://t.me/toshkent_rishtonn",
    "https://t.me/RishtonToshkenttaxiii", "https://t.me/Toshkent_Fargona_taxis",
    "https://t.me/RishtonGa", "https://t.me/toshkentlo",
    "https://t.me/rishton_toshkent_bogdod_n1", "https://t.me/toshkent_bogdod_rishton_buvayd",
    "https://t.me/toshkent_buvayda_bagdodd", "https://t.me/Bogdod_toshkent_yangiqorgonbuvay",
    "https://t.me/Toshkent_Bogdod_Toshken", "https://t.me/taxi_bogdod_toshken"
]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
client = TelegramClient("elon_session", API_ID, API_HASH)

user_data = {}

def start_menu():
    return InlineKeyboardMarkup().add(InlineKeyboardButton("📤 E'lon berish", callback_data="elon"))

def confirm_menu():
    return InlineKeyboardMarkup().add(InlineKeyboardButton("✅ Tasdiqlash", callback_data="tasdiqla"))

def cancel_reply_button():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("⛔ To‘xtatish"))
    return keyboard

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Assalomu alaykum!\nE'lon yuborish uchun quyidagini tanlang:", reply_markup=start_menu())

@dp.callback_query_handler(lambda call: True)
async def callbacks(call: types.CallbackQuery):
    user_id = call.from_user.id

    if call.data == "elon":
        user_data[user_id] = {"step": "waiting_for_elon", "stop": False}
        await call.message.edit_reply_markup()
        await call.message.answer("E'lon matnini yuboring:", reply_markup=ReplyKeyboardRemove())

    elif call.data == "tasdiqla":
        if user_id not in user_data or "text" not in user_data[user_id]:
            await call.message.answer("Avval e'lon yuboring.")
            return

        user_data[user_id]["stop"] = False
        await call.message.edit_reply_markup()
        await call.message.answer("E'lon yuborilmoqda...", reply_markup=cancel_reply_button())

        text = user_data[user_id]["text"]

        async def continuous_send():
            while not user_data.get(user_id, {}).get("stop"):
                for group_link in GROUP_LINKS:
                    if user_data.get(user_id, {}).get("stop"):
                        await bot.send_message(user_id, "❌ Yuborish to‘xtatildi.", reply_markup=ReplyKeyboardRemove())
                        return
                    try:
                        await client.send_message(group_link, text)
                        await bot.send_message(user_id, f"✅ Yuborildi: {group_link}")
                    except FloodWaitError as e:
                        await asyncio.sleep(e.seconds)
                        await bot.send_message(user_id, f"⏱ Kutish: {e.seconds} sekund ({group_link})")
                    except Exception as e:
                        await bot.send_message(user_id, f"❌ Xatolik: {group_link}\n{e}")
                    await asyncio.sleep(0.5)  # <== juda tez yuborish uchun 0.5 soniyaga tushirildi

                await asyncio.sleep(30)  # <== 10 daqiqa emas, endi 30 soniya kutadi

            await bot.send_message(user_id, "📨 Yuborish yakunlandi ✅", reply_markup=ReplyKeyboardRemove())
            user_data.pop(user_id, None)

        asyncio.create_task(continuous_send())

@dp.message_handler(lambda msg: msg.text == "⛔ To‘xtatish")
async def stop_handler(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_data:
        user_data[user_id]["stop"] = True
        await message.answer("🚫 Yuborish to‘xtatildi.", reply_markup=ReplyKeyboardRemove())

@dp.message_handler()
async def text_handler(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_data and user_data[user_id].get("step") == "waiting_for_elon":
        user_data[user_id]["text"] = message.text
        user_data[user_id]["step"] = "ready"
        await message.answer("E'lon qabul qilindi. Tasdiqlang:", reply_markup=confirm_menu())
    else:
        await message.answer("E'lon yuborish uchun /start buyrug‘idan foydalaning.")

async def main():
    logging.basicConfig(level=logging.INFO)
    await client.start()
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())
