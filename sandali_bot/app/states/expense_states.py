from aiogram.fsm.state import State, StatesGroup

class AddExpense(StatesGroup):
    selecting_category = State()
    adding_custom_category = State()
    selecting_amount = State()
    entering_amount = State()
    entering_description = State()
    deleting_expense = State()