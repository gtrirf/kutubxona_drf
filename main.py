import os
import django
import random
import uuid
from datetime import timedelta
from django.utils import timezone
from asgiref.sync import sync_to_async
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BotCommand, Message
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.executor import start_polling
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import CustomUser, VerificationCode

API_TOKEN = os.getenv('BOT_API')

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())
user_contact_status = {}


async def startup_answer(dp):
    await bot.send_message(5160960485, "Bot ishlashni boshladi!")
    await bot.set_my_commands([
        BotCommand(command='/start', description='Botni ishga tushirish'),
        BotCommand(command='/help', description='Yordam so\'rash'),
        BotCommand(command='/login', description='Tastiqlash kodi olish')
    ])


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    if user_contact_status.get(user_id, False):
        await message.reply("Siz allaqachon kontakt yuborgansiz, agar login qilmoqchi bo'lsangiz, /login bosing")
    else:
        button = KeyboardButton('Send Contact', request_contact=True)
        markup = ReplyKeyboardMarkup(resize_keyboard=True).add(button)
        text = f"Hello, {message.from_user.first_name}, please send your contact."
        await message.reply(text, reply_markup=markup, parse_mode=types.ParseMode.HTML)


@dp.message_handler(commands=['help'])
async def help_answer(message: Message):
    text = """
    <b>Bot Commands</b>:
    /start - Botni ishga tushirish
    /help - Yordam so'rash
    /login - Tastiqlash kodini olish
    """
    await bot.send_message(message.from_user.id, text, parse_mode='HTML')


@dp.message_handler(commands=['login'])
async def login(message: types.Message):
    user_queryset = await sync_to_async(CustomUser.objects.filter)(telegram_username=message.from_user.username)
    user = user_queryset.first() if user_queryset.exists() else None
    if user:
        verification_code = await get_or_create_verification_code(user)
        await message.reply(f"Sizning tastiqlash kodingiz: {verification_code.code}.Bu minut ichida amal qiladi!")
    else:
        await message.reply("Siz xali kontakt yubormadingiz")


@dp.message_handler(content_types=[types.ContentType.CONTACT])
async def contact(message: types.Message):
    user_id = message.from_user.id

    if message.contact:
        phone_number = message.contact.phone_number
        telegram_id = message.from_user.id

        user, created = await sync_to_async(CustomUser.objects.get_or_create)(
            phone_number=phone_number,
            telegram_id=telegram_id,
            defaults={
                'telegram_username': message.from_user.username,
                'telegram_profile_photo': None
            }
        )

        if created or not user.has_usable_password():
            user.set_password(str(uuid.uuid4()))
            await sync_to_async(user.save)()

        photos = await bot.get_user_profile_photos(message.from_user.id)

        if photos.total_count > 0:
            photo_file_id = photos.photos[0][0].file_id
            file_info = await bot.get_file(photo_file_id)
            file_path = file_info.file_path
            file_url = f'https://api.telegram.org/file/bot{API_TOKEN}/{file_path}'

            user.telegram_profile_photo = file_url
            await sync_to_async(user.save)()

        verification_code = await get_or_create_verification_code(user)
        await message.reply(f"Sizning: {verification_code.code} tastiqlash kodingiz xali aktiv!")

        user_contact_status[user_id] = True

        no_contact_markup = ReplyKeyboardMarkup(resize_keyboard=False)
        await message.reply("Sizning kontakt malumotlaringiz jo'natildi", reply_markup=no_contact_markup)


async def get_or_create_verification_code(user):
    """
    Get an active verification code or create a new one if none exists or the existing one is expired.
    """
    verification_code_queryset = await sync_to_async(VerificationCode.objects.filter)(
        user=user,
        is_active=True
    )

    if verification_code_queryset.exists():
        verification_code = verification_code_queryset.first()
        if not verification_code.is_valid():
            await sync_to_async(verification_code_queryset.update)(is_active=False)
            verification_code = await create_verification_code(user)
    else:
        verification_code = await create_verification_code(user)

    return verification_code


async def create_verification_code(user):
    """
    Create a new verification code for the user.
    """
    code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    verification_code = await sync_to_async(VerificationCode.objects.create)(
        user=user, code=code, is_active=True
    )
    return verification_code


async def shutdown_answer(dp):
    await bot.send_message(5160960485, "Bot stopped working!")


async def delete_expired_codes():
    """
    Function to deactivate and delete expired verification codes.
    """
    expired_codes = VerificationCode.objects.filter(
        is_active=True,
        created_at__lte=timezone.now() - timedelta(minutes=1)
    )
    for code in expired_codes:
        code.is_active = False
        code.save()
    VerificationCode.objects.filter(is_active=False).delete()


if __name__ == '__main__':
    scheduler = AsyncIOScheduler()
    scheduler.add_job(delete_expired_codes, 'interval', minutes=1)
    scheduler.start()
    start_polling(dp, skip_updates=True, on_startup=startup_answer, on_shutdown=shutdown_answer)
