from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states.expense_states import AddExpense
from keyboards.inline import get_category_keyboard, get_amount_keyboard
from keyboards.reply import main_menu, cancel_keyboard, delete_keyboard
from db.database import db

router = Router()

@router.message(F.text == "➕ Add Expense")
async def add_expense_cmd(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_categories = db.get_categories(user_id)
    await state.update_data(user_id=user_id)
    await message.answer("Please select a category for your expense:", reply_markup=get_category_keyboard(user_categories))
    await state.set_state(AddExpense.selecting_category)

@router.callback_query(F.data == "add_category")
async def prompt_custom_category(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Please enter the name of your custom category:", reply_markup=cancel_keyboard())
    await state.set_state(AddExpense.adding_custom_category)
    await callback_query.answer()

@router.message(AddExpense.adding_custom_category)
async def add_custom_category(message: Message, state: FSMContext):
    user_id = message.from_user.id
    category_name = message.text.strip()
    if category_name != "❌ Cancel":
        if db.add_category(user_id, category_name):
            await message.answer(f"✅ Category '{category_name}' added!", reply_markup=main_menu())
            await state.update_data(category=category_name)
            await message.answer("💵 Please select an amount:", reply_markup=get_amount_keyboard())
            await state.set_state(AddExpense.selecting_amount)
        else:
            await message.answer("❌ Category already exists. Please choose another name:", reply_markup=cancel_keyboard())
    else:
        await state.set_state(AddExpense.selecting_category)



@router.callback_query(F.data.startswith("category:"))
async def select_category(callback_query: CallbackQuery, state: FSMContext):
    category = callback_query.data.split(":")[1]
    await state.update_data(category=category)
    await callback_query.message.edit_text("💵 Please select an amount:", reply_markup=get_amount_keyboard())
    await state.set_state(AddExpense.selecting_amount)
    await callback_query.answer()

@router.callback_query(F.data.startswith("amount:"))
async def select_amount(callback_query: CallbackQuery, state: FSMContext):
    amount = float(callback_query.data.split(":")[1])
    await state.update_data(amount=amount)
    await callback_query.message.answer("📝 Please enter a description (or type 'skip' to skip):", reply_markup=cancel_keyboard())
    await state.set_state(AddExpense.entering_description)
    await callback_query.answer()

@router.callback_query(F.data == "custom_amount")
async def prompt_custom_amount(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("💵 Please enter the amount:", reply_markup=cancel_keyboard())
    await state.set_state(AddExpense.entering_amount)
    await callback_query.answer()

@router.callback_query(F.data == "back_to_category")
async def back_to_main(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    user_categories = db.get_categories(user_id)
    await callback_query.message.edit_text("Please select a category for your expense:", reply_markup=get_category_keyboard(user_categories))
    await state.set_state(AddExpense.selecting_category)

@router.message(F.text == "❌ Cancel")
async def cancel_action(message: Message, state: FSMContext):
    await message.answer("Action cancelled.", reply_markup=main_menu())
    await state.clear()

@router.message(AddExpense.entering_amount)
async def enter_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        await state.update_data(amount=amount)
        await message.answer("📝 Please enter a description (or type 'skip' to skip):", reply_markup=cancel_keyboard())
        await state.set_state(AddExpense.entering_description)
    except ValueError:
        await message.answer("❌ Invalid amount. Please enter a number:", reply_markup=cancel_keyboard())

@router.message(AddExpense.entering_description)
async def enter_description(message: Message, state: FSMContext):
    data = await state.get_data()
    category = data['category']
    amount = data['amount']
    description = message.text if message.text.lower() != 'skip' else None
    user_id = message.from_user.id
    date = message.date.isoformat()
    db.add_expense(user_id, category, amount, description, date)
    await message.answer("✅ Expense added successfully!", reply_markup=main_menu())
    await state.clear()

@router.message(F.text == "📋 View Expenses")
async def view_expenses(message: Message):
    user_id = message.from_user.id
    expenses = db.get_expenses(user_id, limit=10)
    if not expenses:
        await message.answer("📭 No expenses found.", reply_markup=main_menu())
        return
    response = "📋 Recent Expenses:\n\n"
    for expense in expenses:
        expense_id = expense[0]
        category = expense[1]
        amount = f"${expense[2]:.2f}"
        description = f" - {expense[3]}" if expense[3] else ""
        date = expense[4].split("T")[0]
        time = expense[4].split("T")[1].split(".")[0]
        emoji = db.category_emojis.get(category, "📌")
        response += f"•ID: {expense_id}\n {emoji} {amount} ({category}){description}\n  {date} {time}\n\n"
    await message.answer(response, reply_markup=delete_keyboard())


@router.message(F.text == "🗑️ Delete Expense")
async def delete_expense_prompt(message: Message, state: FSMContext):
    await message.answer("Enter the expense ID to delete:", reply_markup=cancel_keyboard())
    await state.set_state(AddExpense.deleting_expense)

@router.message(AddExpense.deleting_expense)
async def delete_expenses(message: Message, state: FSMContext):
    try:
        expense_id = int(message.text)
        user_id = message.from_user.id
        if db.delete_expense(user_id, expense_id):
            await message.answer(f"✅ Expense ID {expense_id} deleted.", reply_markup=main_menu())
        else:
            await message.answer(f"❌ No expense found with ID {expense_id}.", reply_markup=main_menu())
    except ValueError:
        await message.answer("❌ Please enter a valid expense ID.", reply_markup=main_menu())
    await state.clear()