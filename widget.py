import sys
import math
import socket

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QLineEdit, QStackedWidget, QMessageBox,
    QDialog
)
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtGui import QPainter, QPen, QPolygonF, QColor, QFont, QPixmap


class TcpClient:
    def __init__(self, host="127.0.0.1", port=1234):
        self.host = host
        self.port = port

    def send(self, msg: str) -> str:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
                s.sendall((msg + "\n").encode("utf-8"))
                data = s.recv(65536).decode("utf-8", errors="replace").strip()
                return data
        except Exception as e:
            return f"error: {e}"

    def request_reset(self, email: str) -> str:
        return self.send(f"reset_request&{email}")

    def confirm_reset(self, email: str, code: str, new_pass: str) -> str:
        return self.send(f"reset_confirm&{email}&{code}&{new_pass}")


class CustomChartView(QChartView):
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.Antialiasing)
        chart = self.chart()
        if not chart:
            return

        left = chart.mapToPosition(QPointF(chart.plotArea().left(), 0))
        right = chart.mapToPosition(QPointF(chart.plotArea().right(), 0))
        bottom = chart.mapToPosition(QPointF(0, chart.plotArea().bottom()))
        top = chart.mapToPosition(QPointF(0, chart.plotArea().top()))

        pen = QPen(Qt.black, 1.5)
        painter.setPen(pen)
        painter.drawLine(left, right)
        painter.drawLine(bottom, top)

        size = 8
        arrow_x = right
        painter.drawPolygon(QPolygonF([
            arrow_x,
            QPointF(arrow_x.x() - size, arrow_x.y() - size / 2),
            QPointF(arrow_x.x() - size, arrow_x.y() + size / 2)
        ]))

        arrow_y = top
        painter.drawPolygon(QPolygonF([
            arrow_y,
            QPointF(arrow_y.x() - size / 2, arrow_y.y() + size),
            QPointF(arrow_y.x() + size / 2, arrow_y.y() + size)
        ]))


class ForgotPasswordDialog(QDialog):
    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self.email = ""

        self.setWindowTitle("Восстановление пароля")
        self.setModal(True)
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Email")
        self.email_edit.setMinimumWidth(250)

        self.code_edit = QLineEdit()
        self.code_edit.setPlaceholderText("Код из письма")
        self.code_edit.setMinimumWidth(250)

        self.new_pass = QLineEdit()
        self.new_pass.setPlaceholderText("Новый пароль")
        self.new_pass.setEchoMode(QLineEdit.Password)
        self.new_pass.setMinimumWidth(250)

        self.confirm_pass = QLineEdit()
        self.confirm_pass.setPlaceholderText("Повторите пароль")
        self.confirm_pass.setEchoMode(QLineEdit.Password)
        self.confirm_pass.setMinimumWidth(250)

        self.send_btn = QPushButton("Получить код")
        self.send_btn.setFixedWidth(200)
        self.reset_btn = QPushButton("Сменить пароль")
        self.reset_btn.setFixedWidth(200)

        layout.addWidget(self.email_edit, alignment=Qt.AlignCenter)
        layout.addWidget(self.send_btn, alignment=Qt.AlignCenter)
        layout.addWidget(self.code_edit, alignment=Qt.AlignCenter)
        layout.addWidget(self.new_pass, alignment=Qt.AlignCenter)
        layout.addWidget(self.confirm_pass, alignment=Qt.AlignCenter)
        layout.addWidget(self.reset_btn, alignment=Qt.AlignCenter)

        self.send_btn.clicked.connect(self.send_code)
        self.reset_btn.clicked.connect(self.reset_password)

    def send_code(self):
        email = self.email_edit.text().strip()
        if not email:
            QMessageBox.warning(self, "Ошибка", "Введите email")
            return

        resp = self.client.request_reset(email)
        if resp == "reset_sent":
            self.email = email
            QMessageBox.information(self, "Успех", "Код отправлен на почту")
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось отправить код")

    def reset_password(self):
        if not self.email:
            QMessageBox.warning(self, "Ошибка", "Сначала запросите код")
            return

        code = self.code_edit.text().strip()
        new_pass = self.new_pass.text()
        confirm = self.confirm_pass.text()

        if not code or not new_pass or not confirm:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        if new_pass != confirm:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
            return

        resp = self.client.confirm_reset(self.email, code, new_pass)
        if resp == "reset_ok":
            QMessageBox.information(self, "Успех", "Пароль изменён")
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный код или ошибка сброса")


class ProjectInfoScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(50, 50, 50, 50)

        title = QLabel("О курсовом проекте")
        title.setFont(QFont("Arial", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        layout.addSpacing(30)

        info = QLabel(
            "Тема: Разработка программного приложения для параллельного просмотра "
            "цифровой и графической информации\n\n"
            "Выполнили: Азнаурьян Игорь Эдуардович, Елисеев Денис Александрович, Жельвис Феликс Альбертович, Филитович Федор Михайлович \n"
            "Группа: 251-371\n"
            "Университет: Московский Политех\n"
            "Курс: Технологии и методы программирования\n"
            "Год: 2026\n\n"
            "Приложение позволяет:\n"
            "• Вычислять значения кусочно-заданной функции с параметрами.\n"
            "• Отображать таблицу значений на интервале [-10; 10].\n"
            "• Строить график функции с возможностью изменения параметров.\n"
            "• Авторизация и регистрация пользователей с хранением данных на сервере.\n"
            "• Восстановление пароля по email."
        )
        info.setFont(QFont("Arial", 13))
        info.setWordWrap(True)
        layout.addWidget(info)
        layout.addSpacing(40)

        btn_layout = QHBoxLayout()
        self.back_btn = QPushButton("← Назад")
        self.back_btn.setFixedSize(140, 45)
        self.back_btn.setFont(QFont("Arial", 12))
        self.back_btn.clicked.connect(self.go_back)
        self.next_btn = QPushButton("Далее →")
        self.next_btn.setFixedSize(140, 45)
        self.next_btn.setFont(QFont("Arial", 12))
        self.next_btn.clicked.connect(self.go_next)
        btn_layout.addWidget(self.back_btn)
        btn_layout.addWidget(self.next_btn)
        layout.addLayout(btn_layout)
        layout.setAlignment(btn_layout, Qt.AlignCenter)

    def go_back(self):
        self.parent_app.show_title_screen()

    def go_next(self):
        self.parent_app.show_function_info_screen()


class FunctionInfoScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(50, 50, 50, 50)

        title = QLabel("Исследуемая функция и её особенности")
        title.setFont(QFont("Arial", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        layout.addSpacing(20)

        # Формула
        formula_label = QLabel()
        pixmap = QPixmap("formula.png")
        if not pixmap.isNull():
            scaled = pixmap.scaledToWidth(600, Qt.SmoothTransformation)
            formula_label.setPixmap(scaled)
        else:
            formula_label.setText(
                "f(x) = \n"
                "  cos(a·x)   при x < -π\n"
                "  b/(x+π)    при -π ≤ x < 0\n"
                "  cot(c+x)   при x ≥ 0"
            )
            formula_label.setFont(QFont("Courier New", 16))
            formula_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(formula_label, alignment=Qt.AlignCenter)
        layout.addSpacing(30)

        # Особенности – изображение или текст
        features_label = QLabel()
        pixmap2 = QPixmap("features.png")
        if not pixmap2.isNull():
            # Масштабируем изображение, сохраняя пропорции, чтобы не "отъезжало"
            scaled2 = pixmap2.scaledToWidth(600, Qt.SmoothTransformation)
            features_label.setPixmap(scaled2)
        else:
            features_label.setText(
                "Особенности:\n\n"
                "• cos(a·x) имеет циклические нули в точках x = (2n+1)π/(2a) при a≠0.\n"
                "• b/(x+π) имеет вертикальную асимптоту при x = -π.\n"
                "• cot(c+x) имеет вертикальные асимптоты в точках x = nπ - c, n∈Z.\n"
                "• При b=0 второй участок тождественно равен нулю (кроме точки разрыва).\n"
                "• Функция может иметь разрывы первого или второго рода в точках стыковки.\n"
                "• Диапазон отображения: x ∈ [-10; 10]."
            )
            features_label.setFont(QFont("Arial", 13))
            features_label.setWordWrap(True)
        layout.addWidget(features_label, alignment=Qt.AlignCenter)
        layout.addSpacing(40)

        btn_layout = QHBoxLayout()
        self.back_btn = QPushButton("← Назад")
        self.back_btn.setFixedSize(140, 45)
        self.back_btn.setFont(QFont("Arial", 12))
        self.back_btn.clicked.connect(self.go_back)
        self.next_btn = QPushButton("Далее →")
        self.next_btn.setFixedSize(140, 45)
        self.next_btn.setFont(QFont("Arial", 12))
        self.next_btn.clicked.connect(self.go_next)
        btn_layout.addWidget(self.back_btn)
        btn_layout.addWidget(self.next_btn)
        layout.addLayout(btn_layout)
        layout.setAlignment(btn_layout, Qt.AlignCenter)

    def go_back(self):
        self.parent_app.show_project_info_screen()

    def go_next(self):
        self.parent_app.show_auth_screen()


class TitleScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Добро пожаловать!")
        title.setFont(QFont("Arial", 32, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Приложение для визуализации кусочно-заданной функции")
        subtitle.setFont(QFont("Arial", 16))
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(40)

        self.start_btn = QPushButton("Начать")
        self.start_btn.setFixedSize(240, 55)
        self.start_btn.setFont(QFont("Arial", 14, QFont.Bold))
        self.start_btn.clicked.connect(self.go_to_project_info)
        layout.addWidget(self.start_btn, alignment=Qt.AlignCenter)

    def go_to_project_info(self):
        self.parent_app.show_project_info_screen()


class FunctionScreen(QWidget):
    def __init__(self, client, main_window, parent=None):
        super().__init__(parent)
        self.client = client
        self.main_window = main_window
        self.a, self.b, self.c = 0.0, 0.0, 0.0
        self._dynamic_series = []
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setAlignment(Qt.AlignTop)

        formula_pixmap = QLabel()
        pixmap = QPixmap("formula.png")
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaledToWidth(500, Qt.SmoothTransformation)
            formula_pixmap.setPixmap(scaled_pixmap)
        else:
            formula_pixmap.setText("Изображение формулы не найдено")
            formula_pixmap.setFont(QFont("Arial", 12))
        left_layout.addWidget(formula_pixmap)
        left_layout.addSpacing(20)

        def make_slider(name, minv, maxv, val):
            group = QGroupBox(name)
            group.setFont(QFont("Arial", 12))
            group.setStyleSheet("QGroupBox { background-color: #FFFFFF; border-radius: 10px; }")
            hbox = QHBoxLayout(group)
            slider = QSlider(Qt.Horizontal)
            slider.setRange(minv, maxv)
            slider.setValue(val)
            label = QLabel(f"{val / 10:.2f}")
            label.setFont(QFont("Arial", 12))
            hbox.addWidget(slider)
            hbox.addWidget(label)
            left_layout.addWidget(group)
            return slider, label

        self.slider_a, self.label_a = make_slider("Параметр a (cos a·x)", -100, 100, 0)
        self.slider_b, self.label_b = make_slider("Параметр b (b/(x+π))", -100, 100, 0)
        self.slider_c, self.label_c = make_slider("Параметр c (cot(c+x))", -100, 100, 0)

        left_layout.addSpacing(20)

        table_label = QLabel("Таблица значений")
        table_label.setFont(QFont("Arial", 14, QFont.Bold))
        table_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(table_label)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["x", "f(x)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setFont(QFont("Arial", 12))
        self.table.verticalHeader().setDefaultSectionSize(32)
        self.table.setStyleSheet("alternate-background-color: #F5F5FF; background-color: white; border-radius: 10px;")
        left_layout.addWidget(self.table)

        self.back_btn = QPushButton("Выйти из аккаунта")
        self.back_btn.setFixedSize(200, 40)
        self.back_btn.setFont(QFont("Arial", 12))
        self.back_btn.setStyleSheet("QPushButton { background-color: #D8BFD8; border-radius: 8px; padding: 6px; }"
                                    "QPushButton:hover { background-color: #DDA0DD; }")
        self.back_btn.clicked.connect(self.go_back)
        left_layout.addWidget(self.back_btn, alignment=Qt.AlignCenter)

        left.setMinimumWidth(550)
        left.setStyleSheet("background: transparent;")
        layout.addWidget(left)

        self.chart = QChart()
        self.update_chart_title()
        self.chart.legend().hide()

        self.series_left = QLineSeries()
        self.series_mid = QLineSeries()
        self.series_right = QLineSeries()

        self.series_left.setPen(QPen(QColor(255, 0, 0), 2))
        self.series_mid.setPen(QPen(QColor(0, 255, 0), 2))
        self.series_right.setPen(QPen(QColor(0, 0, 255), 2))

        self.chart.addSeries(self.series_left)
        self.chart.addSeries(self.series_mid)
        self.chart.addSeries(self.series_right)

        self.axis_x = QValueAxis()
        self.axis_x.setRange(-10, 10)
        self.axis_x.setTitleText("x")
        self.axis_x.setTitleFont(QFont("Arial", 12))
        self.axis_x.setLabelsFont(QFont("Arial", 11))

        self.axis_y = QValueAxis()
        self.axis_y.setRange(-10, 10)          # фиксированный масштаб
        self.axis_y.setTitleText("f(x)")
        self.axis_y.setTitleFont(QFont("Arial", 12))
        self.axis_y.setLabelsFont(QFont("Arial", 11))

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
        self.y_line.append(0, -10)   # изменено с -1 на -10
        self.y_line.append(0, 10)    # изменено с 1 на 10

        black_pen = QPen(Qt.black, 1.5)
        self.x_line.setPen(black_pen)
        self.y_line.setPen(black_pen)

        self.chart.addSeries(self.x_line)
        self.chart.addSeries(self.y_line)
        self.x_line.attachAxis(self.axis_x)
        self.x_line.attachAxis(self.axis_y)
        self.y_line.attachAxis(self.axis_x)
        self.y_line.attachAxis(self.axis_y)

        self.chart_view = CustomChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setStyleSheet("background-color: white; border-radius: 15px;")
        layout.addWidget(self.chart_view, 1)

        self.slider_a.valueChanged.connect(self.update_all)
        self.slider_b.valueChanged.connect(self.update_all)
        self.slider_c.valueChanged.connect(self.update_all)

        self.update_all()

    def update_chart_title(self):
        # Увеличенный шрифт заголовка графика (14px)
        title_html = f"""
        <div style="font-size:14pt;">
            <span style="color:#FF0000;">cos(a·x)</span>
            <span style="color:#00FF00;">b/(x+π)</span>
            <span style="color:#0000FF;">cot(c+x)</span><br>
            <span style="font-size:12pt;">a = {self.a:.2f}, b = {self.b:.2f}, c = {self.c:.2f}</span>
        </div>
        """
        self.chart.setTitle(title_html)

    def go_back(self):
        self.main_window.show_auth_screen()
        auth = self.main_window.auth_screen
        auth.login_username.clear()
        auth.login_password.clear()
        auth.login_username.setFocus()

    def f(self, x: float) -> float:
        pi = math.pi
        if x < -pi:
            return math.cos(self.a * x)
        elif x < 0:
            denom = x + pi
            if abs(denom) < 1e-12:
                return float('nan')
            return self.b / denom
        else:
            arg = self.c + x
            sin_val = math.sin(arg)
            cos_val = math.cos(arg)
            if abs(sin_val) < 1e-12:
                return float('nan')
            return cos_val / sin_val

    def _request_points(self, x_min: float, x_max: float, step: float):
        points = []
        x = x_min
        while x <= x_max + step/2:
            y = self.f(x)
            if math.isfinite(y):
                points.append((x, y))
            x += step
        return points

    def _clear_dynamic_series(self):
        for s in self._dynamic_series:
            self.chart.removeSeries(s)
        self._dynamic_series.clear()

    def update_all(self):
        self.a = self.slider_a.value() / 10.0
        self.b = self.slider_b.value() / 10.0
        self.c = self.slider_c.value() / 10.0
        self.label_a.setText(f"{self.a:.2f}")
        self.label_b.setText(f"{self.b:.2f}")
        self.label_c.setText(f"{self.c:.2f}")
        self.update_chart_title()
        self.update_table()
        self.update_plot()

    def update_table(self):
        points = self._request_points(-10.0, 10.0, 0.5)
        self.table.setRowCount(len(points))
        for i, (x, y) in enumerate(points):
            self.table.setItem(i, 0, QTableWidgetItem(f"{x:.2f}"))
            self.table.setItem(i, 1, QTableWidgetItem(f"{y:.2f}"))
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

    def _add_segment(self, points, color):
        if len(points) < 2:
            return
        series = QLineSeries()
        series.setPen(QPen(color, 2))
        for x, y in points:
            series.append(x, y)
        self.chart.addSeries(series)
        series.attachAxis(self.axis_x)
        series.attachAxis(self.axis_y)
        self._dynamic_series.append(series)

    def update_plot(self):
        self._clear_dynamic_series()
        self.series_left.clear()
        self.series_mid.clear()
        self.series_right.clear()

        points = self._request_points(-10.0, 10.0, 0.05)
        if not points:
            # оси всё равно перерисовываем для фиксированного диапазона
            self.y_line.clear()
            self.y_line.append(0, -10)
            self.y_line.append(0, 10)
            return

        left_pts, mid_pts, right_pts = [], [], []
        pi = math.pi
        for x, y in points:
            if x < -pi:
                left_pts.append((x, y))
            elif x < 0:
                mid_pts.append((x, y))
            else:
                right_pts.append((x, y))

        def split_and_add(src, color):
            if not src:
                return
            segment = [src[0]]
            prev_x, prev_y = src[0]
            for x, y in src[1:]:
                if not math.isfinite(y) or abs(y) > 1e6:
                    if len(segment) >= 2:
                        self._add_segment(segment, color)
                    segment = []
                    prev_x, prev_y = x, y
                    continue
                if abs(y - prev_y) > 25 or abs(x - prev_x) > 0.2:
                    if len(segment) >= 2:
                        self._add_segment(segment, color)
                    segment = [(x, y)]
                else:
                    segment.append((x, y))
                prev_x, prev_y = x, y
            if len(segment) >= 2:
                self._add_segment(segment, color)

        split_and_add(left_pts, QColor(255, 0, 0))
        split_and_add(mid_pts, QColor(0, 255, 0))
        split_and_add(right_pts, QColor(0, 0, 255))

        # Блок динамического масштаба полностью удалён.
        # Ось Y остаётся зафиксированной в пределах [-10, 10].


class AuthScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.client = TcpClient()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)

        # Кнопка "Назад" в левом верхнем углу
        back_btn = QPushButton("← Назад")
        back_btn.setFixedSize(100, 35)
        back_btn.setFont(QFont("Arial", 11))
        back_btn.clicked.connect(self.go_back)
        layout.addWidget(back_btn, alignment=Qt.AlignLeft)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # ---- Форма входа ----
        self.login_widget = QWidget()
        login_layout = QVBoxLayout(self.login_widget)
        login_layout.setAlignment(Qt.AlignCenter)
        login_layout.setSpacing(12)

        login_title = QLabel("Вход в систему")
        login_title.setFont(QFont("Arial", 18, QFont.Bold))
        login_title.setAlignment(Qt.AlignCenter)
        login_layout.addWidget(login_title)

        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Логин")
        self.login_username.setFont(QFont("Arial", 13))
        self.login_username.setFixedWidth(800)
        login_layout.addWidget(self.login_username, alignment=Qt.AlignCenter)

        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Пароль")
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_password.setFont(QFont("Arial", 13))
        self.login_password.setFixedWidth(800)
        login_layout.addWidget(self.login_password, alignment=Qt.AlignCenter)

        self.login_btn = QPushButton("Войти")
        self.login_btn.setFont(QFont("Arial", 13))
        self.login_btn.setFixedWidth(800)
        login_layout.addWidget(self.login_btn, alignment=Qt.AlignCenter)

        self.forgot_btn = QPushButton("Забыли пароль?")
        self.forgot_btn.setFont(QFont("Arial", 12))
        self.forgot_btn.setFixedWidth(800)
        login_layout.addWidget(self.forgot_btn, alignment=Qt.AlignCenter)

        self.to_register_btn = QPushButton("Нет аккаунта? Зарегистрироваться")
        self.to_register_btn.setFont(QFont("Arial", 12))
        self.to_register_btn.setFixedWidth(800)
        login_layout.addWidget(self.to_register_btn, alignment=Qt.AlignCenter)

        # ---- Форма регистрации ----
        self.register_widget = QWidget()
        reg_layout = QVBoxLayout(self.register_widget)
        reg_layout.setAlignment(Qt.AlignCenter)
        reg_layout.setSpacing(12)

        reg_title = QLabel("Регистрация")
        reg_title.setFont(QFont("Arial", 18, QFont.Bold))
        reg_title.setAlignment(Qt.AlignCenter)
        reg_layout.addWidget(reg_title)

        self.reg_username = QLineEdit()
        self.reg_username.setPlaceholderText("Логин")
        self.reg_username.setFont(QFont("Arial", 13))
        self.reg_username.setFixedWidth(800)
        reg_layout.addWidget(self.reg_username, alignment=Qt.AlignCenter)

        self.reg_password = QLineEdit()
        self.reg_password.setPlaceholderText("Пароль")
        self.reg_password.setEchoMode(QLineEdit.Password)
        self.reg_password.setFont(QFont("Arial", 13))
        self.reg_password.setFixedWidth(800)
        reg_layout.addWidget(self.reg_password, alignment=Qt.AlignCenter)

        self.reg_confirm = QLineEdit()
        self.reg_confirm.setPlaceholderText("Подтвердите пароль")
        self.reg_confirm.setEchoMode(QLineEdit.Password)
        self.reg_confirm.setFont(QFont("Arial", 13))
        self.reg_confirm.setFixedWidth(800)
        reg_layout.addWidget(self.reg_confirm, alignment=Qt.AlignCenter)

        self.reg_email = QLineEdit()
        self.reg_email.setPlaceholderText("Email")
        self.reg_email.setFont(QFont("Arial", 13))
        self.reg_email.setFixedWidth(800)
        reg_layout.addWidget(self.reg_email, alignment=Qt.AlignCenter)

        self.register_btn = QPushButton("Зарегистрироваться")
        self.register_btn.setFont(QFont("Arial", 13))
        self.register_btn.setFixedWidth(800)
        reg_layout.addWidget(self.register_btn, alignment=Qt.AlignCenter)

        self.to_login_btn = QPushButton("Уже есть аккаунт? Войти")
        self.to_login_btn.setFont(QFont("Arial", 12))
        self.to_login_btn.setFixedWidth(800)
        reg_layout.addWidget(self.to_login_btn, alignment=Qt.AlignCenter)

        self.stack.addWidget(self.login_widget)
        self.stack.addWidget(self.register_widget)

        self.login_btn.clicked.connect(self.do_login)
        self.register_btn.clicked.connect(self.do_register)
        self.forgot_btn.clicked.connect(self.open_forgot_dialog)
        self.to_register_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.register_widget))
        self.to_login_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.login_widget))

    def go_back(self):
        self.parent_app.show_function_info_screen()

    def open_forgot_dialog(self):
        dlg = ForgotPasswordDialog(self.client, self)
        dlg.exec_()

    def do_login(self):
        username = self.login_username.text().strip()
        password = self.login_password.text()
        response = self.client.send(f"auth&{username}&{password}")
        if response.startswith("auth+"):
            QMessageBox.information(self, "Успех", f"Добро пожаловать, {username}!")
            self.parent_app.show_function_screen()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")

    def do_register(self):
        username = self.reg_username.text().strip()
        password = self.reg_password.text()
        confirm = self.reg_confirm.text()
        email = self.reg_email.text().strip()
        if not username or not password or not email:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return
        if password != confirm:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
            return
        response = self.client.send(f"reg&{username}&{password}&{email}")
        if response.startswith("reg+"):
            QMessageBox.information(self, "Успех", "Регистрация успешна! Теперь войдите.")
            self.stack.setCurrentWidget(self.login_widget)
            self.login_username.setText(username)
            self.login_password.clear()
        else:
            QMessageBox.warning(self, "Ошибка", "Пользователь уже существует")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Кусочно-заданная функция")
        self.setMinimumSize(1300, 750)

        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.main_layout = QVBoxLayout(self.central)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        self.title_screen = TitleScreen(self)
        self.project_info_screen = ProjectInfoScreen(self)
        self.function_info_screen = FunctionInfoScreen(self)
        self.auth_screen = AuthScreen(self)
        self.function_screen = FunctionScreen(self.auth_screen.client, self)

        self.stacked_widget.addWidget(self.title_screen)
        self.stacked_widget.addWidget(self.project_info_screen)
        self.stacked_widget.addWidget(self.function_info_screen)
        self.stacked_widget.addWidget(self.auth_screen)
        self.stacked_widget.addWidget(self.function_screen)

        self.setStyleSheet("""
            QWidget {
                background-color: #E6E6FA;
            }
            QGroupBox {
                background-color: #F0F0FF;
                border: 1px solid #B0B0D0;
                border-radius: 10px;
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
                border-radius: 10px;
            }
            QPushButton {
                background-color: #D8BFD8;
                border: 1px solid #8B008B;
                border-radius: 8px;
                padding: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #DDA0DD;
            }
            QLineEdit {
                background-color: white;
                border: 1px solid #8B008B;
                border-radius: 5px;
                padding: 5px;
            }
        """)

    def show_title_screen(self):
        self.stacked_widget.setCurrentWidget(self.title_screen)

    def show_project_info_screen(self):
        self.stacked_widget.setCurrentWidget(self.project_info_screen)

    def show_function_info_screen(self):
        self.stacked_widget.setCurrentWidget(self.function_info_screen)

    def show_auth_screen(self):
        self.stacked_widget.setCurrentWidget(self.auth_screen)

    def show_function_screen(self):
        self.stacked_widget.setCurrentWidget(self.function_screen)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Arial", 12)
    app.setFont(font)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())