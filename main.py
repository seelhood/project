import sys
<<<<<<< HEAD
import re  # Для проверок ввода (телефон, имена)
from dataclasses import dataclass
from datetime import datetime
=======
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import database as db

>>>>>>> 9f591a27ce86bd47ceece09884943a4014f842fa

from PyQt5.QtCore import QDateTime, QTime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QStackedWidget,
    QFormLayout, QLineEdit, QComboBox, QDateTimeEdit, QLabel,
<<<<<<< HEAD
    QAbstractItemView, QMessageBox
)

import database as db
=======
    QAbstractItemView, QMessageBox, QDialog
)

DB_PATH = Path(__file__).with_name("vet_clinic.db")
>>>>>>> 9f591a27ce86bd47ceece09884943a4014f842fa

@dataclass
class Appointment:
    id: int
    owner: str
    phone: str
    pet: str
    species: str
    vet: str
    dt: datetime
    service: str
    status: str = "Запланирована"

def validate_appointment(new_appt, existing, now=None):
<<<<<<< HEAD
    """Проверка бизнес-правил (RULE-01, CR-01) и валидация данных"""
    now = now or datetime.now()
    
    # 1. Проверка на пустые поля
    required = [new_appt.owner, new_appt.phone, new_appt.pet, new_appt.species, new_appt.vet, new_appt.service]
    if not all(str(x).strip() for x in required):
        return False, "Заполните все обязательные поля."

    # 2. Валидация ФИО владельца
    if not re.match(r"^[А-Яа-яЁёA-Za-z\s\-]{2,50}$", new_appt.owner.strip()):
        return False, "Имя владельца должно содержать только буквы (от 2 до 50 символов)."

    # 3. Валидация телефона
    if not re.match(r"^\+?[0-9]{10,15}$", new_appt.phone.strip()):
        return False, "Неверный формат телефона. Введите от 10 до 15 цифр (можно с +)."

    # 4. Валидация клички питомца
    if not re.match(r"^[А-Яа-яЁёA-Za-z\s\-]{2,30}$", new_appt.pet.strip()):
        return False, "Кличка питомца должна содержать только буквы (от 2 до 30 символов)."

    # 5. Валидация вида питомца
    if not re.match(r"^[А-Яа-яЁёA-Za-z\s\-]{2,30}$", new_appt.species.strip()):
        return False, "Вид питомца должен содержать только буквы (например: кошка, собака)."

    # 6. Проверка даты (CR-01: нельзя в прошлое)
    if new_appt.dt <= now:
        return False, "Нельзя записать на прошедшую дату/время."
    
    existing_objs = [Appointment(
        id=a['id'], owner=a['owner'], phone=a['phone'], pet=a['pet'], 
        species=a['species'], vet=a['vet'], dt=datetime.fromisoformat(a['dt']), 
        service=a['service'], status=a['status']
    ) for a in existing]

    # 7. Проверка занятости слота (RULE-01)
    for a in existing_objs:
        if (a.status in ("Запланирована", "Подтверждена") and a.vet == new_appt.vet and a.dt == new_appt.dt):
            return False, f"У ветеринара {new_appt.vet} уже есть запись на {new_appt.dt:%d.%m.%Y %H:%M}."
            
    return True, "OK"

=======
    now = now or datetime.now()
    required = [new_appt.owner, new_appt.phone, new_appt.pet, new_appt.species, new_appt.vet, new_appt.service]
    if not all(str(x).strip() for x in required):
        return False, "Заполните обязательные поля."
    if new_appt.dt <= now:
        return False, "Нельзя записать на прошедшую дату/время."
    for a in existing:
        if (a.status in ("Запланирована", "Подтверждена") and a.vet == new_appt.vet and a.dt == new_appt.dt):
            return False, f"У ветеринара {new_appt.vet} уже есть запись на {new_appt.dt:%d.%m.%Y %H:%M}."
    return True, "OK"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

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

def init_db():
    conn = get_connection()
    try:
        with conn:
            # Создание таблиц
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS owners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                phone TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS pets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                species TEXT NOT NULL,
                FOREIGN KEY(owner_id) REFERENCES owners(id)
            );
            CREATE TABLE IF NOT EXISTS vets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL UNIQUE,
                specialization TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER NOT NULL,
                vet_id INTEGER NOT NULL,
                dt TEXT NOT NULL,
                service TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Запланирована',
                FOREIGN KEY(pet_id) REFERENCES pets(id),
                FOREIGN KEY(vet_id) REFERENCES vets(id)
            );
            """)

            # Создание учетных записей (admin/123 и vet/123)
            conn.execute("INSERT OR IGNORE INTO users(username, password, role) VALUES ('admin', '123', 'Администратор')")
            conn.execute("INSERT OR IGNORE INTO users(username, password, role) VALUES ('vet', '123', 'Ветеринар')")

            # Добавление врачей
            for full_name, spec in [("Петрова А.С.", "терапевт"), ("Смирнов В.В.", "хирург"), ("Кузнецова Е.А.", "дерматолог")]:
                conn.execute("INSERT OR IGNORE INTO vets(full_name, specialization) VALUES (?, ?)", (full_name, spec))

            # Тестовая запись (если база пустая)
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

def load_appointments():
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
        return [Appointment(id=r["id"], owner=r["owner"], phone=r["phone"], pet=r["pet"], species=r["species"], 
                            vet=r["vet"], dt=datetime.fromisoformat(r["dt"]), service=r["service"], status=r["status"]) for r in rows]
    finally:
        conn.close()

def save_appointment(appt):
    conn = get_connection()
    try:
        with conn:
            owner_id = get_or_create_owner(conn, appt.owner, appt.phone)
            pet_id = get_or_create_pet(conn, owner_id, appt.pet, appt.species)
            vet = conn.execute("SELECT id FROM vets WHERE full_name=?", (appt.vet,)).fetchone()
            cur = conn.execute("INSERT INTO appointments(pet_id, vet_id, dt, service, status) VALUES (?, ?, ?, ?, ?)",
                               (pet_id, vet["id"], appt.dt.isoformat(sep=" "), appt.service.strip(), "Запланирована"))
            return cur.lastrowid
    finally:
        conn.close()

def cancel_appointment(appt_id):
    conn = get_connection()
    try:
        with conn:
            cur = conn.execute("UPDATE appointments SET status='Отменена' WHERE id=? AND status='Запланирована'", (appt_id,))
            return cur.rowcount
    finally:
        conn.close()

# --- ОКНО АВТОРИЗАЦИИ ---
>>>>>>> 9f591a27ce86bd47ceece09884943a4014f842fa
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация - Ветклиника")
<<<<<<< HEAD
        self.resize(800, 600)
=======
        self.resize(300, 200)
>>>>>>> 9f591a27ce86bd47ceece09884943a4014f842fa
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
        self.user_edit = QLineEdit()
        self.pass_edit = QLineEdit()
        self.pass_edit.setEchoMode(QLineEdit.Password)
        
        form.addRow("Логин:", self.user_edit)
        form.addRow("Пароль:", self.pass_edit)
        
        btn_login = QPushButton("Войти")
<<<<<<< HEAD
        btn_login.setMinimumHeight(35)
=======
>>>>>>> 9f591a27ce86bd47ceece09884943a4014f842fa
        btn_login.clicked.connect(self.check_login)
        
        layout.addLayout(form)
        layout.addWidget(btn_login)
        
        hint = QLabel("Admin: admin / 123\nВетеринар: vet / 123")
<<<<<<< HEAD
        hint.setStyleSheet("color: gray;")
=======
        hint.setStyleSheet("color: gray; font-size: 10px;")
>>>>>>> 9f591a27ce86bd47ceece09884943a4014f842fa
        layout.addWidget(hint)
        
        self.setLayout(layout)
        self.main_window = None

    def check_login(self):
        user = self.user_edit.text().strip()
        pwd = self.pass_edit.text().strip()
        
<<<<<<< HEAD
        role = db.get_user_role(user, pwd)
        
        if role:
=======
        conn = get_connection()
        row = conn.execute("SELECT role FROM users WHERE username=? AND password=?", (user, pwd)).fetchone()
        conn.close()
        
        if row:
            role = row["role"]
>>>>>>> 9f591a27ce86bd47ceece09884943a4014f842fa
            self.main_window = VetClinicApp(role)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль!")

<<<<<<< HEAD
=======
# --- ГЛАВНОЕ ОКНО ПРОГРАММЫ ---
>>>>>>> 9f591a27ce86bd47ceece09884943a4014f842fa
class VetClinicApp(QMainWindow):
    def __init__(self, role):
        super().__init__()
        self.role = role
        self.setWindowTitle(f"Ветклиника — запись питомца [{self.role}]")
<<<<<<< HEAD
        self.resize(1200, 700)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.stack.addWidget(self.build_list_page())
        self.stack.addWidget(self.build_form_page())
        self.stack.addWidget(self.build_result_page())

        self.refresh_list()
        self.stack.setCurrentWidget(self.stack.widget(0))
=======
        self.resize(1000, 560)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        self.list_page = self.build_list_page()
        self.form_page = self.build_form_page()
        self.result_page = self.build_result_page()

        self.stack.addWidget(self.list_page)
        self.stack.addWidget(self.form_page)
        self.stack.addWidget(self.result_page)

        self.refresh_list()
        self.stack.setCurrentWidget(self.list_page)
>>>>>>> 9f591a27ce86bd47ceece09884943a4014f842fa

    def build_list_page(self):
        page = QWidget()
        layout = QVBoxLayout()
<<<<<<< HEAD
        
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["ID", "Владелец", "Питомец", "Врач", "Дата/время", "Услуга", "Статус"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True) # Растянуть последнюю колонку
        
        buttons = QHBoxLayout()
        if self.role == "Администратор":
            btn_new = QPushButton("Новая запись")
            btn_new.setMinimumHeight(35)
            btn_new.clicked.connect(lambda: self.stack.setCurrentWidget(self.stack.widget(1)))
            
            btn_cancel = QPushButton("Отменить выбранную")
            btn_cancel.setMinimumHeight(35)
            btn_cancel.clicked.connect(self.cancel_selected)
            
            buttons.addWidget(btn_new)
            buttons.addWidget(btn_cancel)
            
=======
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["ID", "Владелец", "Питомец", "Врач", "Дата/время", "Услуга", "Статус"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        buttons = QHBoxLayout()
        
        # Если роль Администратор - показываем кнопки. Если Ветеринар - скрываем.
        if self.role == "Администратор":
            btn_new = QPushButton("Новая запись")
            btn_new.clicked.connect(self.show_form)
            btn_cancel = QPushButton("Отменить выбранную")
            btn_cancel.clicked.connect(self.cancel_selected)
            buttons.addWidget(btn_new)
            buttons.addWidget(btn_cancel)
        
>>>>>>> 9f591a27ce86bd47ceece09884943a4014f842fa
        layout.addWidget(QLabel(f"Список записей (Вы вошли как: {self.role})"))
        layout.addWidget(self.table)
        layout.addLayout(buttons)
        page.setLayout(layout)
        return page

    def build_form_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        form = QFormLayout()

        self.owner_edit = QLineEdit()
<<<<<<< HEAD
        self.owner_edit.setPlaceholderText("Иванов Иван Иванович")
        
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("+79001234567")
        
        self.pet_edit = QLineEdit()
        self.pet_edit.setPlaceholderText("Мурка")
        
        self.species_edit = QLineEdit()
        self.species_edit.setPlaceholderText("Кошка")
        
=======
        self.phone_edit = QLineEdit()
        self.pet_edit = QLineEdit()
        self.species_edit = QLineEdit()
>>>>>>> 9f591a27ce86bd47ceece09884943a4014f842fa
        self.vet_combo = QComboBox()
        self.vet_combo.addItems(["Петрова А.С.", "Смирнов В.В.", "Кузнецова Е.А."])
        
        default_dt = QDateTime.currentDateTime().addDays(1)
        default_dt.setTime(QTime(10, 0))
        self.dt_edit = QDateTimeEdit(default_dt)
        self.dt_edit.setDisplayFormat("dd.MM.yyyy HH:mm")
        self.dt_edit.setCalendarPopup(True)
        
        self.service_combo = QComboBox()
        self.service_combo.addItems(["Осмотр", "Вакцинация", "Консультация", "Стрижка когтей"])

        form.addRow("Владелец*", self.owner_edit)
        form.addRow("Телефон*", self.phone_edit)
        form.addRow("Питомец*", self.pet_edit)
        form.addRow("Вид*", self.species_edit)
        form.addRow("Врач*", self.vet_combo)
        form.addRow("Дата/время*", self.dt_edit)
        form.addRow("Услуга*", self.service_combo)

        btn_save = QPushButton("Сохранить")
<<<<<<< HEAD
        btn_save.setMinimumHeight(35)
        btn_save.clicked.connect(self.save_appointment)
        
        btn_back = QPushButton("Назад к списку")
        btn_back.setMinimumHeight(35)
        btn_back.clicked.connect(lambda: self.stack.setCurrentWidget(self.stack.widget(0)))
=======
        btn_save.clicked.connect(self.save_appointment)
        btn_back = QPushButton("Назад к списку")
        btn_back.clicked.connect(self.go_list)
>>>>>>> 9f591a27ce86bd47ceece09884943a4014f842fa

        layout.addLayout(form)
        layout.addWidget(btn_save)
        layout.addWidget(btn_back)
        page.setLayout(layout)
        return page

    def build_result_page(self):
        page = QWidget()
        layout = QVBoxLayout()
<<<<<<< HEAD
        
        self.result_label = QLabel()
        self.result_label.setWordWrap(True)
        
        btn_back = QPushButton("Вернуться к списку")
        btn_back.setMinimumHeight(35)
        btn_back.clicked.connect(lambda: self.stack.setCurrentWidget(self.stack.widget(0)))
        
=======
        self.result_label = QLabel()
        self.result_label.setWordWrap(True)
        btn_back = QPushButton("Вернуться к списку")
        btn_back.clicked.connect(self.go_list)
>>>>>>> 9f591a27ce86bd47ceece09884943a4014f842fa
        layout.addWidget(self.result_label)
        layout.addWidget(btn_back)
        page.setLayout(layout)
        return page

    def refresh_list(self):
<<<<<<< HEAD
        appointments = db.load_all_appointments()
=======
        appointments = load_appointments()
>>>>>>> 9f591a27ce86bd47ceece09884943a4014f842fa
        self.table.setRowCount(0)
        for a in appointments:
            row = self.table.rowCount()
            self.table.insertRow(row)
<<<<<<< HEAD
            dt_formatted = datetime.fromisoformat(a['dt']).strftime("%d.%m.%Y %H:%M")
            values = [str(a['id']), a['owner'], a['pet'], a['vet'], dt_formatted, a['service'], a['status']]
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(value))

=======
            values = [str(a.id), a.owner, a.pet, a.vet, a.dt.strftime("%d.%m.%Y %H:%M"), a.service, a.status]
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(value))

    def show_form(self):
        self.owner_edit.clear()
        self.phone_edit.clear()
        self.pet_edit.clear()
        self.species_edit.clear()
        self.stack.setCurrentWidget(self.form_page)

>>>>>>> 9f591a27ce86bd47ceece09884943a4014f842fa
    def save_appointment(self):
        new_appt = Appointment(
            id=0, owner=self.owner_edit.text(), phone=self.phone_edit.text(),
            pet=self.pet_edit.text(), species=self.species_edit.text(),
            vet=self.vet_combo.currentText(), dt=self.dt_edit.dateTime().toPyDateTime(),
            service=self.service_combo.currentText(),
        )

<<<<<<< HEAD
        ok, message = validate_appointment(new_appt, db.load_all_appointments())

        if ok:
            appt_id = db.save_new_appointment(new_appt.owner, new_appt.phone, new_appt.pet, new_appt.species, new_appt.vet, new_appt.dt.isoformat(sep=" "), new_appt.service)
            self.refresh_list()
            self.result_label.setText(f"Успех. Запись №{appt_id} создана.")
            self.result_label.setStyleSheet("color: green;") # Оставил только цвет
        else:
            self.result_label.setText(f"Отказ. {message}")
            self.result_label.setStyleSheet("color: red;") # Оставил только цвет
            
        self.stack.setCurrentWidget(self.stack.widget(2))
=======
        ok, message = validate_appointment(new_appt, load_appointments())

        if ok:
            appt_id = save_appointment(new_appt)
            self.refresh_list()
            self.show_result(True, f"Запись №{appt_id} создана.")
        else:
            self.show_result(False, message)
>>>>>>> 9f591a27ce86bd47ceece09884943a4014f842fa

    def cancel_selected(self):
        row = self.table.currentRow()
        if row < 0:
<<<<<<< HEAD
            self.result_label.setText("Отказ. Выберите запись в списке.")
            self.result_label.setStyleSheet("color: red;")
            self.stack.setCurrentWidget(self.stack.widget(2))
            return
        appt_id = int(self.table.item(row, 0).text())
        
        affected = db.cancel_appointment_by_id(appt_id)
        
        if affected:
            self.refresh_list()
            self.result_label.setText(f"Успех. Запись №{appt_id} отменена.")
            self.result_label.setStyleSheet("color: green;")
        else:
            self.result_label.setText("Отказ. Отменить можно только запланированную запись.")
            self.result_label.setStyleSheet("color: red;")
            
        self.stack.setCurrentWidget(self.stack.widget(2))

if __name__ == "__main__":
    db.init_db() 
=======
            self.show_result(False, "Выберите запись в списке.")
            return
        appt_id = int(self.table.item(row, 0).text())
        affected = cancel_appointment(appt_id)
        if affected:
            self.refresh_list()
            self.show_result(True, f"Запись №{appt_id} отменена.")
        else:
            self.show_result(False, "Отменить можно только запланированную запись.")

    def show_result(self, ok, message):
        prefix = "Успех. " if ok else "Отказ. "
        self.result_label.setText(prefix + message)
        self.stack.setCurrentWidget(self.result_page)

    def go_list(self):
        self.refresh_list()
        self.stack.setCurrentWidget(self.list_page)

if __name__ == "__main__":
    init_db()
>>>>>>> 9f591a27ce86bd47ceece09884943a4014f842fa
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())