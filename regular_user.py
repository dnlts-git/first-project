import requests
from aiogram import Router, types, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, KeyboardButton, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import KeyboardBuilder, InlineKeyboardBuilder

user = Router()


def get_crypto_prices(crypto_id, vs_currency):
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": crypto_id,
        "vs_currencies": vs_currency
    }
    response = requests.get(url, params=params)
    return response.json()


class BankOfData(StatesGroup):
    crypto = State()
    currency = State()


@user.message(CommandStart())
async def start_cmd(message: Message, state: FSMContext):
    crypto = InlineKeyboardBuilder()

    crypto.add(InlineKeyboardButton(text='BTC', callback_data='bitcoin'))
    crypto.add(InlineKeyboardButton(text='ETH', callback_data='ethereum'))

    await message.answer('Выберите криптовалюту:', reply_markup=crypto.adjust(2).as_markup())
    await state.set_state(BankOfData.crypto)


@user.callback_query(F.data == 'again')
async def start_again(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    crypto = InlineKeyboardBuilder()

    crypto.add(InlineKeyboardButton(text='BTC', callback_data='bitcoin'))
    crypto.add(InlineKeyboardButton(text='ETH', callback_data='ethereum'))

    await callback.message.answer('Выберите криптовалюту:', reply_markup=crypto.adjust(2).as_markup())
    await state.set_state(BankOfData.crypto)

@user.callback_query(F.data.in_(['bitcoin', 'ethereum']), StateFilter(BankOfData.crypto))
async def send_currency(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    crypto_name = callback.data

    await state.update_data(crypto=crypto_name)

    curr = InlineKeyboardBuilder()

    curr.add(InlineKeyboardButton(text='USD', callback_data='usd'))
    curr.add(InlineKeyboardButton(text='UAH', callback_data='uah'))

    await callback.message.answer('Выберите валюту для вывода', reply_markup=curr.adjust(2).as_markup())
    await state.set_state(BankOfData.currency)


@user.callback_query(F.data.in_(['usd', 'uah']), StateFilter(BankOfData.currency))
async def get_calculated_and_send(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    curr_name = callback.data

    data = await state.get_data()
    crypto_name = data.get('crypto')

    price_of_crypto = get_crypto_prices(crypto_id=crypto_name, vs_currency=curr_name)

    actual_price = price_of_crypto.get(f'{crypto_name}').get(f'{curr_name}')

    again = InlineKeyboardBuilder()

    again.add(InlineKeyboardButton(text='Попробовать снова', callback_data='again'))

    await callback.message.answer(f'Цена <b>1 {'BTC' if crypto_name == 'bitcoin' else 'ETH'}</b> '
                                  f'= <b>{actual_price} {'$' if curr_name == 'usd' else '₴'}</b>',
                                  reply_markup=again.as_markup())
