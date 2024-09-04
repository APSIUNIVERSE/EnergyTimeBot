import sqlite3 as sq
import pandas as pd


def users_sql_start():
    global base, cur
    base = sq.connect('dbases/users.db')
    cur = base.cursor()
    if base:
        print('Data base connected successfully!')
    base.execute('CREATE TABLE IF NOT EXISTS task(id TEXT PRIMARY KEY, username, timer INTEGER, notifications INTEGER, on_off TEXT, games TEXT)')
    base.commit()


async def sql_add_users_command(identificator, username):
    cur.execute('INSERT INTO task VALUES(?, ?, 0, 0, "on", "")', (identificator, username,))
    base.commit()


async def sql_timer_command(data):
    cur.execute('UPDATE task SET timer = timer + 1 WHERE id = ?', (data,))
    base.commit()


async def sql_notifications_command(data):
    cur.execute('UPDATE task SET notifications = notifications + 1 WHERE id = ?', (data,))
    base.commit()


async def sql_read_users():
    return cur.execute('SELECT * FROM task').fetchall()


async def sql_read_user(data):
    return cur.execute('SELECT * FROM task WHERE id = ?', (data,)).fetchone()


async def sql_users_stats():
    cur.execute("SELECT * FROM task")
    data = cur.fetchall()
    cur.execute("PRAGMA table_info(task)")
    column_names = [column[1] for column in cur.fetchall()]
    df = pd.DataFrame(data, columns=column_names)
    file = "Statistics.xlsx"
    df.to_excel(file, index=False)
    return file


async def sql_notifications_on(data):
    cur.execute('UPDATE task SET on_off = "on" WHERE id = ?', (data,))
    base.commit()


async def sql_notifications_off(data):
    cur.execute('UPDATE task SET on_off = "off" WHERE id = ?', (data,))
    base.commit()


async def sql_add_game(data, identificator):
    cur.execute('UPDATE task SET games = games || ? WHERE id = ?', (data, identificator,))
    base.commit()


async def sql_update_game(data, identificator):
    cur.execute('UPDATE task SET games = ? WHERE id = ?', (data, identificator,))
    base.commit()


async def sql_delete_users_task(data):
    cur.execute('DELETE FROM task WHERE id == ?', (data,))
    base.commit()
