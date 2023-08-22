import sqlite3 as sq
#from create_bot import bot

def sql_start():
    global base, cur
    base = sq.connect('gate_cool.db')
    cur = base.cursor()
    if base:
        print('Data base connected OK!')
    base.execute('CREATE TABLE IF NOT EXISTS cost(phone TEXT PRIMARY KEY,name TEXT , address TEXT, time TEXT) ')
    base.commit()


async def sql_add_command(state):
    #async with state.proxy() as data:
        cur.execute('INSERT INTO cost VALUES(?,?,?,?)', tuple(state.values()))
        base.commit()

async def sql_read(message):
    for ret in cur.execute('SELECT * FROM cost').fetchall():
        await message.answer(text=f'тел. {ret[0]}, имя {ret[1]}, адрес: {ret[2]}, Время {ret[-1]}')