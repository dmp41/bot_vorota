from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from bot_v_prace.database.database import user_dict_template,users_db
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
user_dict: dict = {}

# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMFillForm(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодейтсвия с пользователем
    fill_long = State()        # Состояние ожидания ввода ширины
    fill_hight = State()       # Состояние ожидания ввода высоты
    fill_prit = State()        # Состояние ожидания ввода притолоки
    fill_motor = State()       # Состояние ожидания выбора наличия электропривода
    fill_door = State()        # Состояние ожидания выбора наличия калитки



# Этот хэндлер будет срабатывать на команду /start вне состояний
# и предлагать перейти к заполнению анкеты, отправив команду /fillform
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(text='Чтобы перейти к заполнению анкеты - '
                              'отправьте команду /fillform',reply_markup=keyboard)


# Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(text='Чтобы снова перейти к заполнению анкеты - '
                              'отправьте команду /fillform')
    # Сбрасываем состояние
    await state.clear()


# Этот хэндлер будет срабатывать на команду "/cancel" в состоянии
# по умолчанию и сообщать, что эта команда доступна в машине состояний
@router.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(text='Отменять нечего.\n\n'
                              'Чтобы перейти к заполнению анкеты - '
                              'отправьте команду /fillform')


# Этот хэндлер будет срабатывать на команду /fillform
# и переводить бота в состояние ожидания ввода ширины
@router.message(Command(commands='fillform'), StateFilter(default_state))
async def process_fillform_command(message: Message, state: FSMContext):
    await message.answer_photo(
        photo='AgACAgIAAxkBAAMSZJEyGcTZQY0ICJlFl7sptYdGUycAAvrOMRsZNIlIjbH-uZ4STSIBAAMCAANzAAMvBA',
        caption='Пожалуйста, введите ширину проема в мм от 2000 до 4500')
    #await message.answer(text='Пожалуйста, введите ширину проема в мм от 2000 до 4500')
    # Устанавливаем состояние ожидания ввода ширины
    await state.set_state(FSMFillForm.fill_long)


# Этот хэндлер будет срабатывать, если введена корректная ширина
# и переводить в состояние ожидания ввода ширины
@router.message(StateFilter(FSMFillForm.fill_long),
                lambda x: x.text.isdigit() and 2000 <= int(x.text) <= 4500)
async def process_name_sent(message: Message, state: FSMContext):
    # Cохраняем введенную ширину в хранилище по ключу "long"
    await state.update_data(long=message.text)
    await message.answer_photo(
        photo='AgACAgIAAxkBAAMUZJEyIYtGx6E2E_T4q5Tirql7S7QAAv3OMRsZNIlIff9gZjJ1dhsBAAMCAANzAAMvBA',
        caption='Спасибо!\n\nА теперь введите высоту проема в мм от 1800 до 3000')
    #await message.answer(text='Спасибо!\n\nА теперь введите высоту проема в мм от 1800 до 3000')
    # Устанавливаем состояние ожидания ввода высот
    await state.set_state(FSMFillForm.fill_hight)


# Этот хэндлер будет срабатывать, если во время ввода ширины
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_long))
async def warning_not_name(message: Message):
    await message.answer(text='Ширина проема должна быть числом от 2000 до 4500\n\n'
             'Попробуйте еще раз\n\nЕсли вы хотите прервать '
             'заполнение анкеты - отправьте команду /cancel')

# Этот хэндлер будет срабатывать, если введена корректная высота
# и переводить в состояние ожидания ввода притолоки
#@router.message(StateFilter(FSMFillForm.fill_hight),
                #lambda x: x.text.isdigit() and 1800 <= int(x.text) <= 3000)
#async def process_name_sent(message: Message, state: FSMContext):
    # Cохраняем введеннную высоту в хранилище по ключу "hight"
    #await state.update_data(hight=message.text)
    #await message.answer(text='Спасибо!\n\nА теперь введите размер притолоки(размер от верха проема до потолка) в мм от 230 до 1000')
    # Устанавливаем состояние ожидания ввода выбора привода
    #await state.set_state(FSMFillForm.fill_prit)


# Этот хэндлер будет срабатывать, если во время ввода высоты
# будет введено что-то некорректное
#@router.message(StateFilter(FSMFillForm.fill_hight))
#async def warning_not_name(message: Message):
    #await message.answer(text='Высота проема должна быть числом от 1800 до 3500\n\n'
                              #'Попробуйте еще раз\n\nЕсли вы хотите прервать '
                              #'заполнение анкеты - отправьте команду /cancel')


# Этот хэндлер будет срабатывать, если введен корректный размер высоты проема
# и переводить в состояние выбора управления
@router.message(StateFilter(FSMFillForm.fill_hight),
            lambda x: x.text.isdigit() and 1800 <= int(x.text) <= 3000)
async def process_age_sent(message: Message, state: FSMContext):
    # Cохраняем притолоку в хранилище по ключу "hight"
    await state.update_data(hight=message.text)
    # Создаем объекты инлайн-кнопок
    motor_button = InlineKeyboardButton(text='Электропривод',
                                       callback_data='Электропривод')
    arm_button = InlineKeyboardButton(text='Ручной цепной привод',
                                         callback_data='Ручной цепной привод')
    no_m_button = InlineKeyboardButton(text='Без привода',
                                        callback_data='Без привода')
    # Добавляем кнопки в клавиатуру (две в одном ряду и одну в другом)
    keyboard: list[list[InlineKeyboardButton]] = [
        [motor_button,
         no_m_button],[arm_button]]
    # Создаем объект инлайн-клавиатуры
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    # Отправляем пользователю сообщение с клавиатурой
    await message.answer(text='Спасибо!\n\nВыберите тип управления воротами',
                         reply_markup=markup)
    # Устанавливаем состояние ожидания выбора управления
    await state.set_state(FSMFillForm.fill_motor)


# Этот хэндлер будет срабатывать, если во время ввода высоты
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_hight))
async def warning_not_age(message: Message):
    await message.answer(
        text='Высота проема должна быть числом от 1800 до 3000\n\n'
             'Попробуйте еще раз\n\nЕсли вы хотите прервать '
             'заполнение анкеты - отправьте команду /cancel')


# Этот хэндлер будет срабатывать, если выбрано управление
# и переводить в состояние согласия получать новости
@router.callback_query(StateFilter(FSMFillForm.fill_motor),
                   Text(text=['Электропривод', 'Ручной цепной привод', 'Без привода']))
async def process_education_press(callback: CallbackQuery, state: FSMContext):
    # Cохраняем данные об электроприводе по ключу "motor"
    await state.update_data(motor=callback.data)

    # Создаем объекты инлайн-кнопок
    yes_door_button = InlineKeyboardButton(text='Да',
                                           callback_data='Да')
    no_door_button = InlineKeyboardButton(text='Нет',
                                          callback_data='Нет')
    # Добавляем кнопки в клавиатуру в один ряд
    keyboard: list[list[InlineKeyboardButton]] = [
                                    [yes_door_button,
                                     no_door_button]]
    # Создаем объект инлайн-клавиатуры
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    # Редактируем предыдущее сообщение с кнопками, отправляя
    # новый текст и новую клавиатуру
    await callback.message.edit_text(text='Спасибо!\n\n'
                                          'Остался последний шаг.\n'
                                          'Нужна ли встроенная калитка?',
                                     reply_markup=markup)
    # Устанавливаем состояние ожидания выбора получать новости или нет
    await state.set_state(FSMFillForm.fill_door)


# Этот хэндлер будет срабатывать, если во время выбора управления
# будет введено/отправлено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_motor))
async def warning_not_education(message: Message):
    await message.answer(text='Пожалуйста, пользуйтесь кнопками '
                              'при выборе управления воротами\n\nЕсли вы хотите '
                              'прервать заполнение анкеты - отправьте '
                              'команду /cancel')


# Этот хэндлер будет срабатывать на выбор нужна или
# не нужна калитка и выводить из машины состояний
@router.callback_query(StateFilter(FSMFillForm.fill_door),
                   Text(text=['Да', 'Нет']))
async def process_wish_news_press(callback: CallbackQuery, state: FSMContext):
    # C помощью менеджера контекста сохраняем данные о
    # получении новостей по ключу "wish_news"
    await state.update_data(door=callback.data)
    # Добавляем в "базу данных" анкету пользователя
    # по ключу id пользователя
    user_dict[callback.from_user.id] = await state.get_data()
    # Завершаем машину состояний
    await state.clear()

    # Отправляем в чат сообщение о выходе из машины состояний
    #await callback.message.edit_text(text='Спасибо! Ваши данные сохранены!\n\n'
                                          #'Вы вышли из машины состояний')
    # Отправляем в чат сообщение с предложением посмотреть свою анкету
    await callback.message.answer(text='Чтобы посмотреть стоимость ворот '
                                       ' - отправьте команду /showdata')


# Этот хэндлер будет срабатывать, если во время согласия на клитку
# будет введено/отправлено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_door))
async def warning_not_wish_news(message: Message):
    await message.answer(text='Пожалуйста, воспользуйтесь кнопками!\n\n'
                              'Если вы хотите прервать заполнение анкеты - '
                              'отправьте команду /cancel')



# Этот хэндлер будет срабатывать на отправку команды /showdata
# и отправлять в чат данные анкеты, либо сообщение об отсутствии данных
@router.message(Command(commands='showdata'), StateFilter(default_state))
async def process_showdata_command(message: Message):
    # Отправляем пользователю анкету, если она есть в "базе данных"
    if message.from_user.id in user_dict:
        # Присваеваем стоимость приводу, калитке
        if user_dict[message.from_user.id]["motor"] == 'Электропривод':
            pr_motor=17000
        if user_dict[message.from_user.id]["motor"] == 'Ручной цепной привод':
            pr_motor = 11000
        if user_dict[message.from_user.id]["motor"] == 'Без привода':
            pr_motor = 0
        if user_dict[message.from_user.id]["door"] == 'Да':
            pr_door=44000
        if user_dict[message.from_user.id]["door"] == 'Нет':
            pr_door = 0
        pr_all= (int(prace(user_dict[message.from_user.id]["long"],
                          user_dict[message.from_user.id]["hight"]))+pr_motor+pr_door)*1.1

        await message.answer(
                    f'Ширина проема, мм: {user_dict[message.from_user.id]["long"]}\n'
                    f'Высота проема, мм: {user_dict[message.from_user.id]["hight"]}\n'
                    #f'Притолока, мм: {user_dict[message.from_user.id]["prit"]}\n'
                    f'Управление: {user_dict[message.from_user.id]["motor"]}\n'
                    f'Калитка: {user_dict[message.from_user.id]["door"]}\n'
                    f'Стоимость секционных ворот, руб: {pr_all//100*90}\n'
                    f'Стоимость монтажа в г. Кемерово, руб: {pr_all//100*10+600}\n')


    else:
        # Если анкеты пользователя в базе нет - предлагаем заполнить
        await message.answer(text='Вы еще не заполняли анкету. '
                                  'Чтобы приступить - отправьте '
                                  'команду /fillform')


# Этот хэндлер будет срабатывать на любые сообщения, кроме тех
# для которых есть отдельные хэндлеры, вне состояний
@router.message(StateFilter(default_state))
async def send_echo(message: Message):
    await message.reply(text='Извините, не понятное сообщение'
                             'Чтобы приступить - отправьте '
                             'команду /fillform')





