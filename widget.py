import sys
import math
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QLineEdit, QStackedWidget, QMessageBox
)
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtGui import QPainter, QPen, QPolygonF, QColor, QFont


# ---------------------- Кастомный вид для осей со стрелками ----------------------
class CustomChartView(QChartView):
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.Antialiasing)
        chart = self.chart()
        if not chart:
            return
        # Ось X
        left = chart.mapToPosition(QPointF(chart.plotArea().left(), 0))
        right = chart.mapToPosition(QPointF(chart.plotArea().right(), 0))
        # Ось Y
        bottom = chart.mapToPosition(QPointF(0, chart.plotArea().bottom()))
        top = chart.mapToPosition(QPointF(0, chart.plotArea().top()))
        pen = QPen(Qt.black, 1.5)
        painter.setPen(pen)
        painter.drawLine(left, right)
        painter.drawLine(bottom, top)
        # Стрелки
        size = 8
        arrow_x = right
        painter.drawPolygon(QPolygonF([
            arrow_x,
            QPointF(arrow_x.x() - size, arrow_x.y() - size/2),
            QPointF(arrow_x.x() - size, arrow_x.y() + size/2)
        ]))
        arrow_y = top
        painter.drawPolygon(QPolygonF([
            arrow_y,
            QPointF(arrow_y.x() - size/2, arrow_y.y() + size),
            QPointF(arrow_y.x() + size/2, arrow_y.y() + size)
        ]))


# ---------------------- Основной экран с функцией ----------------------
class FunctionScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.a, self.b, self.c = 1.0, 1.0, 1.0
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)

        # Левая панель
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setAlignment(Qt.AlignTop)

        formula = QLabel(
            "<html>"
            "<p style='font-size:12pt; font-weight:bold;'>f(x) = </p>"
            "<p style='margin-left:20px;'>"
            "cos(a·x) &nbsp;&nbsp;&nbsp; при x &lt; -π<br>"
            "b / (x + π) &nbsp;&nbsp; при -π ≤ x &lt; 0<br>"
            "cot(c + x) &nbsp;&nbsp;&nbsp; при x ≥ 0"
            "</p>"
            "<p>x ∈ [-10; 10]</p>"
            "</html>"
        )
        formula.setWordWrap(True)
        left_layout.addWidget(formula)
        left_layout.addSpacing(20)

        # Ползунки
        def make_slider(name, minv, maxv, val):
            group = QGroupBox(name)
            hbox = QHBoxLayout(group)
            slider = QSlider(Qt.Horizontal)
            slider.setRange(minv, maxv)
            slider.setValue(val)
            label = QLabel(f"{val/10:.2f}")
            hbox.addWidget(slider)
            hbox.addWidget(label)
            left_layout.addWidget(group)
            return slider, label

        self.slider_a, self.label_a = make_slider("Параметр a (cos a·x)", 0, 100, 10)
        self.slider_b, self.label_b = make_slider("Параметр b (b/(x+π))", -100, 100, 10)
        self.slider_c, self.label_c = make_slider("Параметр c (cot(c+x))", -100, 100, 10)

        left_layout.addSpacing(20)

        # Таблица
        self.table = QTableWidget(11, 2)
        self.table.setHorizontalHeaderLabels(["x", "f(x)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        left_layout.addWidget(self.table)

        left.setFixedWidth(350)
        layout.addWidget(left)

        # График
        self.chart = QChart()
        self.chart.setTitle("График функции")
        self.chart.legend().hide()

        self.series_left = QLineSeries()   # красный
        self.series_mid = QLineSeries()    # зелёный
        self.series_right = QLineSeries()  # синий
        self.series_left.setPen(QPen(QColor(255, 0, 0), 1.5))
        self.series_mid.setPen(QPen(QColor(0, 255, 0), 1.5))
        self.series_right.setPen(QPen(QColor(0, 0, 255), 1.5))

        self.chart.addSeries(self.series_left)
        self.chart.addSeries(self.series_mid)
        self.chart.addSeries(self.series_right)

        self.axis_x = QValueAxis()
        self.axis_x.setRange(-10, 10)
        self.axis_x.setTitleText("x")
        self.axis_y = QValueAxis()
        self.axis_y.setTitleText("f(x)")
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)

        for s in (self.series_left, self.series_mid, self.series_right):
            s.attachAxis(self.axis_x)
            s.attachAxis(self.axis_y)

        self.axis_x.setLineVisible(False)
        self.axis_y.setLineVisible(False)

        self.x_line = QLineSeries()
        self.y_line = QLineSeries()
        self.x_line.append(-10, 0)
        self.x_line.append(10, 0)
        self.y_line.append(0, -100)
        self.y_line.append(0, 100)
        pen = QPen(Qt.black, 1.5)
        self.x_line.setPen(pen)
        self.y_line.setPen(pen)
        self.chart.addSeries(self.x_line)
        self.chart.addSeries(self.y_line)
        self.x_line.attachAxis(self.axis_x)
        self.x_line.attachAxis(self.axis_y)
        self.y_line.attachAxis(self.axis_x)
        self.y_line.attachAxis(self.axis_y)

        self.chart_view = CustomChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(self.chart_view, 1)

        # Подключение сигналов
        self.slider_a.valueChanged.connect(self.update_all)
        self.slider_b.valueChanged.connect(self.update_all)
        self.slider_c.valueChanged.connect(self.update_all)

        self.update_all()

    def f(self, x):
        pi = math.pi
        if x < -pi:
            return math.cos(self.a * x)
        if x < 0:
            denom = x + pi
            return self.b / denom if abs(denom) > 1e-12 else float('nan')
        arg = self.c + x
        s, c_ = math.sin(arg), math.cos(arg)
        return c_ / s if abs(s) > 1e-12 else float('nan')

    def update_all(self):
        self.a = self.slider_a.value() / 10.0
        self.b = self.slider_b.value() / 10.0
        self.c = self.slider_c.value() / 10.0
        self.label_a.setText(f"{self.a:.2f}")
        self.label_b.setText(f"{self.b:.2f}")
        self.label_c.setText(f"{self.c:.2f}")
        self.update_table()
        self.update_plot()

    def update_table(self):
        xs = [-10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10]
        self.table.setRowCount(len(xs))
        for i, x in enumerate(xs):
            y = self.f(x)
            self.table.setItem(i, 0, QTableWidgetItem(f"{x:.2f}"))
            if math.isfinite(y):
                self.table.setItem(i, 1, QTableWidgetItem(f"{y:.6f}"))
            else:
                self.table.setItem(i, 1, QTableWidgetItem("не опр."))
        self.table.resizeColumnsToContents()

    def update_plot(self):
        self.series_left.clear()
        self.series_mid.clear()
        self.series_right.clear()
        step = 0.05
        pi = math.pi

        def fill(series, x1, x2):
            x = x1
            while x <= x2 + step/2:
                y = self.f(x)
                if math.isfinite(y):
                    series.append(x, y)
                x += step

        fill(self.series_left, -10.0, -pi - 1e-9)
        fill(self.series_mid, -pi, -0.0001)
        fill(self.series_right, 0.0, 10.0)

        all_pts = []
        for s in (self.series_left, self.series_mid, self.series_right):
            all_pts.extend(s.pointsVector())
        if all_pts:
            ymin = min(p.y() for p in all_pts)
            ymax = max(p.y() for p in all_pts)
            margin = (ymax - ymin) * 0.05 or 0.5
            self.axis_y.setRange(ymin - margin, ymax + margin)
        else:
            self.axis_y.setRange(-1, 1)

        y_min, y_max = self.axis_y.min(), self.axis_y.max()
        self.y_line.clear()
        self.y_line.append(0, y_min)
        self.y_line.append(0, y_max)

        self.chart.setTitle(f"График  |  a = {self.a:.2f}, b = {self.b:.2f}, c = {self.c:.2f}")


# ---------------------- Титульный экран ----------------------
class TitleScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Добро пожаловать!")
        title_font = QFont("Arial", 24, QFont.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Приложение для визуализации кусочно-заданной функции")
        subtitle_font = QFont("Arial", 12)
        subtitle.setFont(subtitle_font)
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(40)

        self.start_btn = QPushButton("Начать")
        self.start_btn.setFixedSize(200, 40)
        layout.addWidget(self.start_btn, alignment=Qt.AlignCenter)


# ---------------------- Авторизация / регистрация ----------------------
class AuthScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        # Простая база пользователей (логин -> пароль)
        self.users = {"admin": "admin123"}  # demo

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # Форма входа
        self.login_widget = QWidget()
        login_layout = QVBoxLayout(self.login_widget)
        login_layout.setAlignment(Qt.AlignCenter)

        login_layout.addWidget(QLabel("Вход в систему"))
        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Логин")
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Пароль")
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_btn = QPushButton("Войти")
        self.to_register_btn = QPushButton("Нет аккаунта? Зарегистрироваться")

        login_layout.addWidget(self.login_username)
        login_layout.addWidget(self.login_password)
        login_layout.addWidget(self.login_btn)
        login_layout.addWidget(self.to_register_btn)

        # Форма регистрации
        self.register_widget = QWidget()
        reg_layout = QVBoxLayout(self.register_widget)
        reg_layout.setAlignment(Qt.AlignCenter)

        reg_layout.addWidget(QLabel("Регистрация"))
        self.reg_username = QLineEdit()
        self.reg_username.setPlaceholderText("Логин")
        self.reg_password = QLineEdit()
        self.reg_password.setPlaceholderText("Пароль")
        self.reg_password.setEchoMode(QLineEdit.Password)
        self.reg_confirm = QLineEdit()
        self.reg_confirm.setPlaceholderText("Подтвердите пароль")
        self.reg_confirm.setEchoMode(QLineEdit.Password)
        self.register_btn = QPushButton("Зарегистрироваться")
        self.to_login_btn = QPushButton("Уже есть аккаунт? Войти")

        reg_layout.addWidget(self.reg_username)
        reg_layout.addWidget(self.reg_password)
        reg_layout.addWidget(self.reg_confirm)
        reg_layout.addWidget(self.register_btn)
        reg_layout.addWidget(self.to_login_btn)

        self.stack.addWidget(self.login_widget)
        self.stack.addWidget(self.register_widget)

        # Сигналы
        self.login_btn.clicked.connect(self.do_login)
        self.register_btn.clicked.connect(self.do_register)
        self.to_register_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.register_widget))
        self.to_login_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.login_widget))

    def do_login(self):
        username = self.login_username.text().strip()
        password = self.login_password.text()
        if username in self.users and self.users[username] == password:
            QMessageBox.information(self, "Успех", f"Добро пожаловать, {username}!")
            # Переключение на главный экран
            self.parent_app.show_function_screen()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")

    def do_register(self):
        username = self.reg_username.text().strip()
        password = self.reg_password.text()
        confirm = self.reg_confirm.text()
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return
        if password != confirm:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
            return
        if username in self.users:
            QMessageBox.warning(self, "Ошибка", "Пользователь уже существует")
            return
        self.users[username] = password
        QMessageBox.information(self, "Успех", "Регистрация успешна! Теперь войдите.")
        self.stack.setCurrentWidget(self.login_widget)
        self.login_username.setText(username)
        self.login_password.clear()


# ---------------------- Главное окно со стеком ----------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Кусочно-заданная функция")
        self.setMinimumSize(1000, 600)

        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.main_layout = QVBoxLayout(self.central)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        # Создаём экраны
        self.title_screen = TitleScreen()
        self.auth_screen = AuthScreen(self)   # передаём ссылку на главное окно
        self.function_screen = FunctionScreen()

        self.stacked_widget.addWidget(self.title_screen)
        self.stacked_widget.addWidget(self.auth_screen)
        self.stacked_widget.addWidget(self.function_screen)

        # Подключаем кнопку "Начать"
        self.title_screen.start_btn.clicked.connect(self.show_auth_screen)

        # Лавандовый фон для всех экранов
        self.setStyleSheet("""
            QWidget {
                background-color: #E6E6FA;
            }
            QGroupBox {
                background-color: #F0F0FF;
                border: 1px solid #B0B0D0;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                background-color: transparent;
            }
            QTableWidget {
                background-color: #FFFFFF;
                alternate-background-color: #F5F5FF;
            }
            QPushButton {
                background-color: #D8BFD8;
                border: 1px solid #8B008B;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #DDA0DD;
            }
            QLineEdit {
                background-color: white;
                border: 1px solid #8B008B;
                border-radius: 3px;
                padding: 3px;
            }
        """)

    def show_auth_screen(self):
        self.stacked_widget.setCurrentWidget(self.auth_screen)

    def show_function_screen(self):
        self.stacked_widget.setCurrentWidget(self.function_screen)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())