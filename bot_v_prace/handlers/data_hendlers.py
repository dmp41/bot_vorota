from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from bot_v_prace.database import database
from copy import deepcopy
from aiogram import Bot, Dispatcher, F
from bot_v_prace.keyboard.keyboard import keyboard
from bot_v_prace.services.calculate import pr_or,prace
from aiogram.filters import Command, CommandStart, StateFilter, Text
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message, PhotoSize,InputMediaPhoto)

#Получаем ID текущего модератора
router: Router = Router()

#Создаем временную базу данных
data_dict: dict = {}

# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMDataForm(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодейтсвия с пользователем
    fill_name = State()        # Состояние ожидания ввода имени
    fill_place = State()       # Состояние ожидания ввода адреса
    fill_phone = State()        # Состояние ожидания ввода телефона
    fill_time = State()       # Состояние ожидания выбора времени



# Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='Чтобы приступить к рассчету - отправьте '
                'команду /filldata')

    # Сбрасываем состояние
    await state.clear()


# Этот хэндлер будет срабатывать на команду "/cancel" в состоянии
# по умолчанию и сообщать, что эта команда доступна в машине состояний
@router.message(Command(commands='cancel2'), StateFilter(default_state))
async def process_cancel_command(message: Message):

    await message.answer(text='Отменять нечего.\n\n'
                              'Чтобы перейти к заполнению анкеты - '
                              'отправьте команду /filldata')


# Этот хэндлер будет срабатывать на команду /filldata
# и переводить бота в состояние ожидания ввода имени
@router.message(Command(commands='filldata'), StateFilter(default_state))
async def process_filldata_command(message: Message, state: FSMContext):

    await message.answer(text='Пожалуйста, напишите свое имя')
    #Устанавливаем состояние ожидания ввода имени
    await state.set_state(FSMDataForm.fill_name)


# Этот хэндлер будет срабатывать, если введено корректное имя
# и переводить в состояние ожидания ввода ширины
@router.message(StateFilter(FSMDataForm.fill_name),
                lambda x: x.text.isalpha())
async def process_name_sent(message: Message, state: FSMContext):
    # Cохраняем введенное имя в хранилище по ключу "name"
    await state.update_data(name=message.text)

    await message.answer(text='Спасибо!\n\nА теперь введите адрес установки ворот.')
    # Устанавливаем состояние ожидания ввода высот
    await state.set_state(FSMDataForm.fill_place)




#Этот хэндлер будет срабатывать, если введен адрес
 #и переводить в состояние ожидания ввода телефона
@router.message(StateFilter(FSMDataForm.fill_place))

async def process_name_sent(message: Message, state: FSMContext):
    # Cохраняем введенный адрес в хранилище по ключу "place"
    await state.update_data(place=message.text)
    await message.answer(text='Спасибо!\n\nА теперь введите номер телефона в формате(8***********)')
    # Устанавливаем состояние ожидания ввода выбора привода
    await state.set_state(FSMDataForm.fill_phone)





# Этот хэндлер будет срабатывать, если введен корректный номер телефона
# и переводить в состояние выбора управления
@router.message(StateFilter(FSMDataForm.fill_phone),
            lambda x: x.text.isdigit() and len(x.text) == 11)
async def process_age_sent(message: Message, state: FSMContext):
    # Cохраняем телефон в хранилище по ключу "phone"
    await state.update_data(phone=message.text)
    # Создаем объекты инлайн-кнопок
    motor_button = InlineKeyboardButton(text='10.00 - 12.00',
                                       callback_data='10.00 - 12.00')
    arm_button = InlineKeyboardButton(text='14.00 - 17.00',
                                         callback_data='14.00 - 17.00')
    no_m_button = InlineKeyboardButton(text='19.00 - 21.00',
                                        callback_data='19.00 - 21.00')
    # Добавляем кнопки в клавиатуру (две в одном ряду и одну в другом)
    keyboard: list[list[InlineKeyboardButton]] = [
        [motor_button,
         no_m_button],[arm_button]]
    # Создаем объект инлайн-клавиатуры
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    # Отправляем пользователю сообщение с клавиатурой
    await message.answer(text='Спасибо!\n\nВыберите удобное для Вас время',
                         reply_markup=markup)
    # Устанавливаем состояние ожидания выбора управления
    await state.set_state(FSMDataForm.fill_time)


# Этот хэндлер будет срабатывать, если во время ввода телефона
# будет введено что-то некорректное
@router.message(StateFilter(FSMDataForm.fill_phone))
async def warning_not_age(message: Message):
    await message.answer(
        text='Формат в котором нужно написать номер телефона - 89111111111\n\n'
             'Попробуйте еще раз\n\nЕсли вы хотите прервать '
             'заполнение анкеты - отправьте команду /cancel')






# Этот хэндлер будет срабатывать на выбор времени
# и выводить из машины состояний
@router.callback_query(StateFilter(FSMDataForm.fill_time),
                   Text(text=['10.00 - 12.00', '14.00 - 17.00', '19.00 - 21.00']))
async def process_wish_news_press(callback: CallbackQuery, state: FSMContext):
    # C помощью менеджера контекста сохраняем данные о
    # времени по ключу "time"
    await state.update_data(time=callback.data)
    # Добавляем в "временную базу данных" анкету пользователя
    # по ключу id пользователя
    data_dict[callback.from_user.id] = await state.get_data()
    # Добавляем анкеты в базу данных
    await database.sql_add_command(data_dict[callback.from_user.id])
    # Завершаем машину состояний
    await state.clear()

    # Отправляем в чат сообщение о выходе из машины состояний
    #await callback.message.edit_text(text='Спасибо! Ваши данные сохранены!\n\n'
                                          #'Вы вышли из машины состояний')
    # Отправляем в чат сообщение с предложением посмотреть свою анкету
    await callback.message.answer(text='Спасибо, наш сотрудник свяжется с Вами в ближайшее время')


# Этот хэндлер будет срабатывать, если во время выбора времени
# будет введено/отправлено что-то некорректное
@router.message(StateFilter(FSMDataForm.fill_time))
async def warning_not_wish_news(message: Message):
    await message.answer(text='Пожалуйста, воспользуйтесь кнопками!\n\n'
                              'Если вы хотите прервать заполнение анкеты - '
                              'отправьте команду /cancel')



# Этот хэндлер будет срабатывать на отправку команды /showbase
# и отправлять в чат данные анкеты, либо сообщение об отсутствии данных
@router.message(Command(commands='showbase'), StateFilter(default_state))
async def process_showdata_command(message: Message):
        # Показывает базу данных
        await database.sql_read(message)


# Этот хэндлер будет срабатывать на любые сообщения, кроме тех
# для которых есть отдельные хэндлеры, вне состояний
#@router.message(StateFilter(default_state))
#async def send_echo(message: Message, state: FSMContext):
 #   await message.answer(text='Извините, не понятное сообщение'
                             #'Чтобы приступить к рассчету - отправьте '
                             #'команду /filldata')

