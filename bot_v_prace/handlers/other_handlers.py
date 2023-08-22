from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
router: Router = Router()
# Этот хэндлер будет срабатывать на любые сообщения, кроме тех
# для которых есть отдельные хэндлеры, вне состояний
@router.message(StateFilter(default_state))
async def send_echo(message: Message, state: FSMContext):
    await message.answer(text='Извините, не понятное сообщение \n'
                             'Чтобы приступить к рассчету - отправьте '
                             'команду /fillform \n'
                            'Чтобы записаться на замер _ отправте'
                              'команду /filldata')