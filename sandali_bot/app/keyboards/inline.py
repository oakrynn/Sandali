from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

default_categories = [
    ("🍔 Food", "Food"),
    ("🚗 Transport", "Transport"),
    ("🎉 Entertainment", "Entertainment"),
    ("💡 Utilities", "Utilities"),
    ("🛒 Other", "Other")
]

quick_amounts = [1, 5, 10, 15, 20, 50, 100]

def get_category_keyboard(user_categories):
    builder = InlineKeyboardBuilder()
    # Default categories
    for display, category in default_categories:
        builder.button(text=display, callback_data=f"category:{category}")
    # User-defined categories
    for category in user_categories:
        builder.button(text=f"📌 {category}", callback_data=f"category:{category}")
    # Custom category option
    builder.button(text="➕ Add Custom Category", callback_data="add_category")
    builder.adjust(2)  # 2 buttons per row
    return builder.as_markup()

def get_amount_keyboard():
    builder = InlineKeyboardBuilder()
    for amount in quick_amounts:
        builder.button(text=f"${amount}", callback_data=f"amount:{amount}")
    builder.button(text="✍️ Custom Amount", callback_data="custom_amount")
    builder.button(text="🔙 Back to Categories", callback_data="back_to_category")
    builder.adjust(2)  # 3 buttons per row for amounts
    return builder.as_markup()

def get_stats_period_keyboard():
    builder = InlineKeyboardBuilder()
    periods = [
        ("📅 Day", "day"),
        ("📅 Week", "week"),
        ("📅 Month", "month"),
        ("📅 3 Months", "3months")
    ]
    for display, period in periods:
        builder.button(text=display, callback_data=f"stats_period:{period}")
    builder.adjust(1)  # 2 buttons per row
    return builder.as_markup()

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_investment_category_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📈 Stocks",        callback_data="inv_cat:stocks")
    builder.button(text="💱 Crypto",        callback_data="inv_cat:crypto")
    builder.button(text="⛏️ Commodities",   callback_data="inv_cat:commodities")
    return builder.as_markup()

def get_investment_asset_keyboard(category: str, items: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for asset in items:
        builder.button(text=asset, callback_data=f"inv_asset:{asset}")
    builder.button(text="🔙 Back", callback_data="inv_back")
    builder.adjust(2)
    return builder.as_markup()
