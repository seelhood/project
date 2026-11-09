import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).with_name("vet_clinic.db")

def get_connection():
    """Возвращает соединение с базой данных SQLite3."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Создает таблицы, учетные записи и тестовые данные при первом запуске."""
    conn = get_connection()
    try:
        with conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, password TEXT NOT NULL, role TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS owners (id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT NOT NULL, phone TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS pets (id INTEGER PRIMARY KEY AUTOINCREMENT, owner_id INTEGER NOT NULL, name TEXT NOT NULL, species TEXT NOT NULL, FOREIGN KEY(owner_id) REFERENCES owners(id));
            CREATE TABLE IF NOT EXISTS vets (id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT NOT NULL UNIQUE, specialization TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS appointments (id INTEGER PRIMARY KEY AUTOINCREMENT, pet_id INTEGER NOT NULL, vet_id INTEGER NOT NULL, dt TEXT NOT NULL, service TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Запланирована', FOREIGN KEY(pet_id) REFERENCES pets(id), FOREIGN KEY(vet_id) REFERENCES vets(id));
            """)
            
            # Добавляем пользователей
            conn.execute("INSERT OR IGNORE INTO users(username, password, role) VALUES ('admin', '123', 'Администратор')")
            conn.execute("INSERT OR IGNORE INTO users(username, password, role) VALUES ('vet', '123', 'Ветеринар')")
            
            # Добавляем врачей
            for full_name, spec in [("Петрова А.С.", "терапевт"), ("Смирнов В.В.", "хирург"), ("Кузнецова Е.А.", "дерматолог")]:
                conn.execute("INSERT OR IGNORE INTO vets(full_name, specialization) VALUES (?, ?)", (full_name, spec))

            # Тестовая запись
            count = conn.execute("SELECT COUNT(*) AS c FROM appointments").fetchone()["c"]
            if count == 0:
                owner_id = get_or_create_owner(conn, "Иванов И.И.", "+7-900-000-00-01")
                pet_id = get_or_create_pet(conn, owner_id, "Мурка", "кошка")
                vet = conn.execute("SELECT id FROM vets WHERE full_name=?", ("Петрова А.С.",)).fetchone()
                dt = (datetime.now() + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
                conn.execute("INSERT INTO appointments(pet_id, vet_id, dt, service, status) VALUES (?, ?, ?, ?, ?)", 
                             (pet_id, vet["id"], dt.isoformat(sep=" "), "Осмотр", "Запланирована"))
    finally:
        conn.close()

def get_or_create_owner(conn, full_name, phone):
    row = conn.execute("SELECT id FROM owners WHERE full_name=? AND phone=?", (full_name.strip(), phone.strip())).fetchone()
    if row: return row["id"]
    cur = conn.execute("INSERT INTO owners(full_name, phone) VALUES (?, ?)", (full_name.strip(), phone.strip()))
    return cur.lastrowid

def get_or_create_pet(conn, owner_id, name, species):
    row = conn.execute("SELECT id FROM pets WHERE owner_id=? AND name=? AND species=?", (owner_id, name.strip(), species.strip())).fetchone()
    if row: return row["id"]
    cur = conn.execute("INSERT INTO pets(owner_id, name, species) VALUES (?, ?, ?)", (owner_id, name.strip(), species.strip()))
    return cur.lastrowid

def get_user_role(username, password):
    """Проверяет логин/пароль и возвращает роль."""
    conn = get_connection()
    try:
        row = conn.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        return row["role"] if row else None
    finally:
        conn.close()

def load_all_appointments():
    """Возвращает список всех записей в виде словарей."""
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT a.id, o.full_name AS owner, o.phone, p.name AS pet, p.species, v.full_name AS vet, a.dt, a.service, a.status
            FROM appointments a 
            JOIN pets p ON p.id = a.pet_id 
            JOIN owners o ON o.id = p.owner_id 
            JOIN vets v ON v.id = a.vet_id 
            ORDER BY a.dt
        """).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def save_new_appointment(owner, phone, pet, species, vet_name, dt_str, service):
    conn = get_connection()
    try:
        with conn:
            owner_id = get_or_create_owner(conn, owner, phone)
            pet_id = get_or_create_pet(conn, owner_id, pet, species)
            vet = conn.execute("SELECT id FROM vets WHERE full_name=?", (vet_name,)).fetchone()
            cur = conn.execute("INSERT INTO appointments(pet_id, vet_id, dt, service, status) VALUES (?, ?, ?, ?, ?)", 
                               (pet_id, vet["id"], dt_str, service.strip(), "Запланирована"))
            return cur.lastrowid
    finally:
        conn.close()

def cancel_appointment_by_id(appt_id):
    conn = get_connection()
    try:
        with conn:
            cur = conn.execute("UPDATE appointments SET status='Отменена' WHERE id=? AND status='Запланирована'", (appt_id,))
            return cur.rowcount
    finally:
        conn.close()