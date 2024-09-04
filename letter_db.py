import sqlite3 as sq


def letter_sql_start():
    global base, cur
    base = sq.connect('dbases/letters.db')
    cur = base.cursor()
    if base:
        print('Data base connected successfully!')
    base.execute('CREATE TABLE IF NOT EXISTS task(id TEXT PRIMARY KEY, sent TEXT, games TEXT)')
    base.commit()


async def sql_add_users_command(id):
    cur.execute('INSERT INTO task VALUES(?, "no", "")', (id,))
    base.commit()


async def sql_send_command(ident):
    cur.execute('UPDATE task SET sent = "yes" WHERE id = ?', (ident,))
    base.commit()


async def sql_no_send_command(ident):
    cur.execute('UPDATE task SET sent = "no" WHERE id = ?', (ident,))
    base.commit()


async def sql_read_users():
    return cur.execute('SELECT * FROM task').fetchall()


async def sql_add_game(data, id):
    cur.execute('UPDATE task SET games = games || ? WHERE id = ?', (data, id,))
    base.commit()


async def sql_delete_users_task():
    cur.execute('DELETE FROM task')
    base.commit()
