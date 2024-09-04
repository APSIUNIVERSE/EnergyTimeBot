import sqlite3 as sq


def sql_start():
    global base, cur
    base = sq.connect('dbases/games.db')
    cur = base.cursor()
    if base:
        print('Data base connected successfully!')
    base.execute('CREATE TABLE IF NOT EXISTS task(link, name, energy INTEGER, interval INTEGER, players INTEGER, info TEXT, photo TEXT, num INTEGER PRIMARY KEY AUTOINCREMENT)')
    base.commit()


async def sql_add_command(data):
    cur.execute('INSERT INTO task (link, name, energy, interval, players, info, photo) VALUES(?, ?, ?, ?, 0, "", "")', tuple(data.values()))
    base.commit()


async def sql_read():
    return cur.execute('SELECT * FROM task ORDER BY num DESC').fetchall()


async def sql_read_game(data):
    return cur.execute('SELECT * FROM task WHERE name = ?', (data,)).fetchone()


async def sql_read_only(data):
    return cur.execute('SELECT link FROM task WHERE name = ?', (data,)).fetchone()


async def sql_formula(data):
    return cur.execute('SELECT energy/interval FROM task WHERE name = ?', (data,)).fetchone()


async def sql_players_command(data):
    cur.execute('UPDATE task SET players = players + 1 WHERE name = ?', (data,))
    base.commit()


async def sql_sum_players():
    return cur.execute('SELECT SUM(players) FROM task').fetchall()


async def sql_formula_players(data):
    return cur.execute('SELECT players FROM task WHERE name = ?', (data,)).fetchone()


async def sql_info_command(info, data):
    cur.execute('UPDATE task SET info = ? WHERE name = ?', (info, data,))
    base.commit()


async def sql_photo_command(photo, data):
    cur.execute('UPDATE task SET photo = ? WHERE name = ?', (photo, data,))
    base.commit()


async def sql_delete_task(data):
    cur.execute('DELETE FROM task WHERE name == ?', (data,))
    base.commit()
