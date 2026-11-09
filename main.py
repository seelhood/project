import sys
import re  # Для проверок ввода (телефон, имена)
from dataclasses import dataclass
from datetime import datetime

from PyQt5.QtCore import QDateTime, QTime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QStackedWidget,
    QFormLayout, QLineEdit, QComboBox, QDateTimeEdit, QLabel,
    QAbstractItemView, QMessageBox
)

import database as db

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

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация - Ветклиника")
        self.resize(800, 600)
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
        self.user_edit = QLineEdit()
        self.pass_edit = QLineEdit()
        self.pass_edit.setEchoMode(QLineEdit.Password)
        
        form.addRow("Логин:", self.user_edit)
        form.addRow("Пароль:", self.pass_edit)
        
        btn_login = QPushButton("Войти")
        btn_login.setMinimumHeight(35)
        btn_login.clicked.connect(self.check_login)
        
        layout.addLayout(form)
        layout.addWidget(btn_login)
        
        hint = QLabel("Admin: admin / 123\nВетеринар: vet / 123")
        hint.setStyleSheet("color: gray;")
        layout.addWidget(hint)
        
        self.setLayout(layout)
        self.main_window = None

    def check_login(self):
        user = self.user_edit.text().strip()
        pwd = self.pass_edit.text().strip()
        
        role = db.get_user_role(user, pwd)
        
        if role:
            self.main_window = VetClinicApp(role)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль!")

class VetClinicApp(QMainWindow):
    def __init__(self, role):
        super().__init__()
        self.role = role
        self.setWindowTitle(f"Ветклиника — запись питомца [{self.role}]")
        self.resize(1200, 700)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.stack.addWidget(self.build_list_page())
        self.stack.addWidget(self.build_form_page())
        self.stack.addWidget(self.build_result_page())

        self.refresh_list()
        self.stack.setCurrentWidget(self.stack.widget(0))

    def build_list_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        
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
        self.owner_edit.setPlaceholderText("Иванов Иван Иванович")
        
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("+79001234567")
        
        self.pet_edit = QLineEdit()
        self.pet_edit.setPlaceholderText("Мурка")
        
        self.species_edit = QLineEdit()
        self.species_edit.setPlaceholderText("Кошка")
        
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
        btn_save.setMinimumHeight(35)
        btn_save.clicked.connect(self.save_appointment)
        
        btn_back = QPushButton("Назад к списку")
        btn_back.setMinimumHeight(35)
        btn_back.clicked.connect(lambda: self.stack.setCurrentWidget(self.stack.widget(0)))

        layout.addLayout(form)
        layout.addWidget(btn_save)
        layout.addWidget(btn_back)
        page.setLayout(layout)
        return page

    def build_result_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        
        self.result_label = QLabel()
        self.result_label.setWordWrap(True)
        
        btn_back = QPushButton("Вернуться к списку")
        btn_back.setMinimumHeight(35)
        btn_back.clicked.connect(lambda: self.stack.setCurrentWidget(self.stack.widget(0)))
        
        layout.addWidget(self.result_label)
        layout.addWidget(btn_back)
        page.setLayout(layout)
        return page

    def refresh_list(self):
        appointments = db.load_all_appointments()
        self.table.setRowCount(0)
        for a in appointments:
            row = self.table.rowCount()
            self.table.insertRow(row)
            dt_formatted = datetime.fromisoformat(a['dt']).strftime("%d.%m.%Y %H:%M")
            values = [str(a['id']), a['owner'], a['pet'], a['vet'], dt_formatted, a['service'], a['status']]
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(value))

    def save_appointment(self):
        new_appt = Appointment(
            id=0, owner=self.owner_edit.text(), phone=self.phone_edit.text(),
            pet=self.pet_edit.text(), species=self.species_edit.text(),
            vet=self.vet_combo.currentText(), dt=self.dt_edit.dateTime().toPyDateTime(),
            service=self.service_combo.currentText(),
        )

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

    def cancel_selected(self):
        row = self.table.currentRow()
        if row < 0:
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
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())