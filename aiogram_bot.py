API_TOKEN = '5406422363:AAE77P3ZW-Jg3MRelYigygP_5LUfFNXVrQA'
#import logging
from aiogram import Bot, Dispatcher, executor, types

# Объект бота
bot = Bot(token=API_TOKEN)
# Диспетчер для бота
dp = Dispatcher(bot)
# Включаем логирование, чтобы не пропустить важные сообщения
#logging.basicConfig(level=logging.INFO)


# Хэндлер на команду /test1
@dp.message_handler(commands="add_player")
async def cmd_test1(message: types.Message):
    await message.answer("Test 1")

# Хэндлер на команду /test2 без dp
async def cmd_test2(message: types.Message):
    await message.reply("Test 2")


@dp.message_handler(lambda message: message.text == "Без пюрешки")
async def without_puree(message: types.Message):
    await message.reply("Так невкусно!")

#дп можно и отдельно сделать
dp.register_message_handler(cmd_test2, commands="test2")


if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)