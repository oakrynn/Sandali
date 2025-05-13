from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from keyboards.inline import get_investment_category_keyboard, get_investment_asset_keyboard
from keyboards.reply import main_menu
from states.investment_states import InvestmentStates
from db.database import db
from utils.api_clients import get_asset_price
from collections import defaultdict

router = Router()

# Pre-defined lists
STOCKS     = ["AAPL","MSFT","AMZN","GOOGL","META","TSLA","NVDA","JPM","WMT","V"]
CRYPTO     = ["BTC","ETH","BNB","XRP","ADA","SOL","DOGE","DOT","AVAX","SHIB"]
COMMODITY  = ["GOLD","SILVER","CRUDE_OIL","NAT_GAS","COPPER"]

@router.message(F.text == "💰 Investments")
async def invest_start(message: Message, state: FSMContext):
    await message.answer("Select asset category:", reply_markup=get_investment_category_keyboard())
    await state.set_state(InvestmentStates.selecting_category)

@router.callback_query(InvestmentStates.selecting_category, F.data.startswith("inv_cat:"))
async def choose_cat(cb: CallbackQuery, state: FSMContext):
    cat = cb.data.split(":")[1]
    mapping = {"stocks": STOCKS, "crypto": CRYPTO, "commodities": COMMODITY}
    items = mapping.get(cat, [])
    await cb.message.edit_text(f"Select {cat.capitalize()} asset:",
                               reply_markup=get_investment_asset_keyboard(cat, items))
    await state.set_state(InvestmentStates.selecting_asset)
    await cb.answer()

@router.callback_query(InvestmentStates.selecting_asset, F.data.startswith("inv_asset:"))
async def choose_asset(cb: CallbackQuery, state: FSMContext):
    asset = cb.data.split(":")[1]
    await state.update_data(asset=asset)
    await cb.message.answer(f"Enter quantity of <b>{asset}</b>:", parse_mode="HTML")
    await state.set_state(InvestmentStates.entering_quantity)
    await cb.answer()

@router.callback_query(F.data == "inv_back")
async def choose_asset(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text("Select an asset category:", reply_markup=get_investment_category_keyboard())
    await state.set_state(InvestmentStates.selecting_category)
    await cb.answer()


@router.message(InvestmentStates.entering_quantity)
async def enter_qty(msg: Message, state: FSMContext):
    try:
        qty = float(msg.text)
        await state.update_data(quantity=qty)
        await msg.answer("Enter purchase price per unit (in USD):")
        await state.set_state(InvestmentStates.entering_price)
    except ValueError:
        await msg.answer("❌ Invalid number. Please enter quantity again:")

@router.message(InvestmentStates.entering_price)
async def enter_price(msg: Message, state: FSMContext):
    try:
        price = float(msg.text)
        data = await state.get_data()
        asset, qty = data["asset"], data["quantity"]
        db.add_investment(msg.from_user.id, asset, qty, price, msg.date.isoformat())
        await msg.answer(
            f"✅ Recorded: <b>{qty}</b> of <b>{asset}</b> @ <b>${price:.2f}</b>\n",
            reply_markup=main_menu(),
            parse_mode="HTML"
        )
        await state.clear()
    except ValueError:
        await msg.answer("❌ Invalid price. Please enter price again:")

@router.message(F.text == "💼 View Portfolio")
async def view_portfolio(message: Message):
    user_id = message.from_user.id
    raw = db.get_investments(user_id)
    if not raw:
        await message.answer("Your portfolio is empty.", reply_markup=main_menu())
        return

    from collections import defaultdict

    portfolio = defaultdict(list)
    for asset, quantity, price in raw:
        portfolio[asset].append((quantity, price))

    response = "📈 <b>Your Portfolio</b>:\n\n"
    for asset, entries in portfolio.items():
        total_quantity = sum(q for q, _ in entries)
        total_cost = sum(q * p for q, p in entries)
        avg_price = total_cost / total_quantity if total_quantity else 0

        current_price = get_asset_price(asset)
        if current_price:
            current_value = total_quantity * current_price
            initial_value = total_cost
            gain = current_value - initial_value
            gain_percent = (gain / initial_value) * 100 if initial_value else 0

            gain_str = f"+${gain:.2f} (+{gain_percent:.1f}%)" if gain >= 0 else f"-${abs(gain):.2f} ({gain_percent:.1f}%)"

            response += (
                f"<b>{asset}</b> — {total_quantity:.4g} units\n"
                f"Avg Price: ${avg_price:.2f}\n"
                f"Current: ${current_price:.2f}\n"
                f"Gain: {gain_str}\n\n"
            )
        else:
            response += (
                f"<b>{asset}</b> — {total_quantity:.4g} units\n"
                f"Avg Price: ${avg_price:.2f}\n"
                f"Current: N/A\n\n"
            )

    await message.answer(response.strip(), reply_markup=main_menu(), parse_mode="HTML")
