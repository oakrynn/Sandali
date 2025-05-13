from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta
from db.database import db
from keyboards.inline import get_stats_period_keyboard
from keyboards.reply import main_menu
from utils.charts import generate_bar_chart, generate_pie_chart
import os

router = Router()


@router.message(F.text == "📊 Statistics")
async def stats_cmd(message: Message):
    await message.answer(
        "📊 Select a period to view your spending stats:",
        reply_markup=get_stats_period_keyboard()
    )


@router.callback_query(F.data.startswith("stats_period:"))
async def show_stats(callback_query: CallbackQuery):
    period = callback_query.data.split(":")[1]
    user_id = callback_query.from_user.id
    end_date = datetime.now()

    if period == "day":
        start_date = end_date - timedelta(days=1)
        title = "Daily Spending"
    elif period == "week":
        start_date = end_date - timedelta(days=7)
        title = "Weekly Spending"
    elif period == "month":
        start_date = end_date - timedelta(days=30)
        title = "Monthly Spending"
    else:  # 3 months
        start_date = end_date - timedelta(days=90)
        title = "Last 3 Months Spending"

    # Fetch stats from database
    stats = db.get_spending_stats(user_id, start_date.isoformat(), end_date.isoformat())
    if not stats:
        await callback_query.message.answer(
            f"📭 No expenses found for {title.lower()}.",
            reply_markup=main_menu()
        )
        await callback_query.answer()
        return

    # Prepare response
    total_spend = sum(amount for _, amount in stats)
    response = f"📊 {title}\n\n"
    response += f"💰 Total Spend: ${total_spend:.2f}\n\n"
    response += "Top Categories:\n"
    for category, amount in stats[:5]:  # Top 5 categories
        emoji = db.category_emojis.get(category, "📌")
        response += f"• {emoji} {category}: ${amount:.2f}\n"

    # Generate and send charts
    try:
        bar_chart_path = generate_bar_chart(stats, title)
        pie_chart_path = generate_pie_chart(stats, title)

        await callback_query.message.answer(response, reply_markup=main_menu())
        await callback_query.message.answer_photo(
            FSInputFile(bar_chart_path),
        caption = f"{title} - Bar Chart"
        )
        await callback_query.message.answer_photo(
            FSInputFile(pie_chart_path),
            caption=f"{title} - Pie Chart"
        )

        # Clean up chart files
        if os.path.exists(bar_chart_path):
            os.remove(bar_chart_path)
        if os.path.exists(pie_chart_path):
            os.remove(pie_chart_path)
    except Exception as e:
        await callback_query.message.answer(
            f"❌ Error generating charts: {str(e)}",
            reply_markup=main_menu()
        )

    await callback_query.answer()