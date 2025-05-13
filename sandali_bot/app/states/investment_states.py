from aiogram.fsm.state import State, StatesGroup

class InvestmentStates(StatesGroup):
    selecting_category = State()
    selecting_asset    = State()
    entering_quantity  = State()
    entering_price     = State()

