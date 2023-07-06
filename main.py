# - - - | Telegram bot - Photo enhancer | - - -
# - - - | Developed for Charodey | - - -
import config
import json
from aiogram import Bot, Dispatcher, executor, types
import requests
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

url = "https://api.picsart.io/tools/1.0/upscale"

bot = Bot(token=config.token, parse_mode="Markdown")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

@dp.message_handler(commands=['start'])
async def handle_start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    channel_button = types.InlineKeyboardButton("💠 Подписаться на канал 💠", url='https://t.me/hugooo1')
    acceptCheck_button = types.InlineKeyboardButton("📄 Проверить", callback_data='checkJoinChannel')
    keyboard.add(channel_button, acceptCheck_button)
    await bot.send_message(chat_id=message.chat.id, text=f"*Привет, *`{message.from_user.first_name}`* !*\n\nДля начала обработки пожалуйста подпишись на наш канал. Это поможет нам поддерживать работу бота и нашего канала ☺️", reply_markup=keyboard)

@dp.message_handler(commands=['help'])
async def handle_help(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text='*❔ Возникли проблемы при работе с ботом? Cообщите об этом @xlxlxdb.*')
    
@dp.callback_query_handler(lambda c: c.data == 'checkJoinChannel')
async def handle_check_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    if (await bot.get_chat_member(-1001860539006, callback_query.message.chat.id)).is_chat_member():
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        await bot.send_message(chat_id=callback_query.message.chat.id, text='*Спасибо за поддержку!*\nТеперь тебе доступна обработка фото, чтобы начать обработку фото воспользуйся командой /enhance.')
    else:
        await bot.send_message(chat_id=callback_query.message.chat.id, text='😕 Ты еще не подписался на <a href="https://t.me/hugooo1">канал</a>', parse_mode="HTML")

class EnhanceState(StatesGroup):
    WAITING_FOR_PHOTO = State()

@dp.message_handler(commands=['enhance'])  
async def enhanceInputPhoto(message: types.Message):
    if (await bot.get_chat_member(-1001860539006, message.chat.id)).is_chat_member():
        await bot.send_message(chat_id=message.chat.id, text='*🖼 Пожалуйста, пришлите мне изображение.*')
        await EnhanceState.WAITING_FOR_PHOTO.set()
    else:
        await bot.send_message(chat_id=message.chat.id, text='😕 Ты еще не подписался на <a href="https://t.me/hugooo1">канал</a>', parse_mode="HTML")

    
@dp.message_handler(content_types=['photo', 'text'], state=EnhanceState.WAITING_FOR_PHOTO)
async def handle_received_photo(message: types.Message, state: FSMContext):
    if message.content_type == 'text':
        await bot.send_message(chat_id=message.chat.id, text='❗️ Не верная форматировка, отправьте фото формата png либо jpg.')
    else:
        photo = message.photo[-1]
        file_id = photo.file_id
        file_info = await bot.get_file(file_id)
        file_path = file_info.file_path

        file_url = f"https://api.telegram.org/file/bot{config.token}/{file_path}"
        print(file_url)
        response = requests.get(file_url)
        with open('photo.jpg', 'wb') as f:
            f.write(response.content)

        payload = {
            "upscale_factor": "x4",
            "image_url": file_url
        }
        for i in range(len(config.ai_tokens)+1):
            headers = {
                "accept": "application/json",
                "x-picsart-api-key": config.ai_tokens[i]
            }
            response = requests.post(url, data=payload, headers=headers)
            response_json = response.json()
            if response_json.get('fault') is not None:
                pass
                if i==len(config.ai_tokens):
                    await bot.send_message(chat_id=message.chat.id, text='🔴 При обработке запроса произошла ошибка, для оказания помощи свяжитесь с @xlxlxdb.')
            else:
                url_link = response_json['data']['url']
                await bot.send_photo(chat_id=message.chat.id, photo=url_link, caption="Ваш запрос обработан!:")
                break
            await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)