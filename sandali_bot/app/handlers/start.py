from aiogram import Router, F
from aiogram.types import Message, Contact
from aiogram.filters import CommandStart, Command
from db.database import db
from keyboards.reply import get_phone_keyboard, main_menu

router = Router()

@router.message((CommandStart()))
async def start_cmd(message: Message):
    user = db.get_user(message.from_user.id)
    if user:
        await message.answer("Welcome back!", reply_markup=main_menu())
    else:
        await message.answer(
            "Welcome! Please share your phone number to register.",
            reply_markup=get_phone_keyboard()
        )

@router.message(F.contact)
async def process_contact(message: Message):
    contact: Contact = message.contact
    db.add_user(
        telegram_id=message.from_user.id,
        phone=contact.phone_number,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    await message.answer("Registration complete!", reply_markup=main_menu())