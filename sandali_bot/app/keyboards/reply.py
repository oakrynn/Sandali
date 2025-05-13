from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Add Expense"), KeyboardButton(text="📋 View Expenses")],
            [KeyboardButton(text="📊 Statistics"), KeyboardButton(text="💰 Investments"), KeyboardButton(text="💼 View Portfolio")]
        ],
        resize_keyboard=True
    )

def get_phone_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📞 Share Phone Number", request_contact=True)]
        ],
        resize_keyboard=True
    )

def cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Cancel")]
        ],
        resize_keyboard=True
    )

def delete_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🗑️ Delete Expense")],
            [KeyboardButton(text="❌ Cancel")]
        ],
        resize_keyboard=True
    )