import sys
import math
import socket

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QLineEdit, QStackedWidget, QMessageBox
)
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtGui import QPainter, QPen, QPolygonF, QColor, QFont


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


class FunctionScreen(QWidget):
    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self.a, self.b, self.c = 1.0, 1.0, 1.0
        self._dynamic_series = []
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)

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

        def make_slider(name, minv, maxv, val):
            group = QGroupBox(name)
            hbox = QHBoxLayout(group)
            slider = QSlider(Qt.Horizontal)
            slider.setRange(minv, maxv)
            slider.setValue(val)
            label = QLabel(f"{val / 10:.2f}")
            hbox.addWidget(slider)
            hbox.addWidget(label)
            left_layout.addWidget(group)
            return slider, label

        self.slider_a, self.label_a = make_slider("Параметр a (cos a·x)", 0, 100, 10)
        self.slider_b, self.label_b = make_slider("Параметр b (b/(x+π))", -100, 100, 10)
        self.slider_c, self.label_c = make_slider("Параметр c (cot(c+x))", -100, 100, 10)

        left_layout.addSpacing(20)

        self.table = QTableWidget(11, 2)
        self.table.setHorizontalHeaderLabels(["x", "f(x)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        left_layout.addWidget(self.table)

        left.setFixedWidth(350)
        layout.addWidget(left)

        self.chart = QChart()
        self.chart.setTitle("График функции")
        self.chart.legend().hide()

        self.series_left = QLineSeries()
        self.series_mid = QLineSeries()
        self.series_right = QLineSeries()

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
        self.y_line.append(0, -1)
        self.y_line.append(0, 1)

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
        layout.addWidget(self.chart_view, 1)

        self.slider_a.valueChanged.connect(self.update_all)
        self.slider_b.valueChanged.connect(self.update_all)
        self.slider_c.valueChanged.connect(self.update_all)

        self.update_all()

    def _request_points(self, x_min: float, x_max: float, step: float):
        response = self.client.send(
            f"calc&{self.a}&{self.b}&{self.c}&{x_min}&{x_max}&{step}"
        )
        if not response.startswith("calc&"):
            return []

        payload = response.split("&", 1)[1].strip()
        if not payload:
            return []

        points = []
        for item in payload.split(";"):
            item = item.strip()
            if not item or "," not in item:
                continue
            xs, ys = item.split(",", 1)
            try:
                x = float(xs)
                y = float(ys)
            except ValueError:
                continue
            if math.isfinite(x) and math.isfinite(y):
                points.append((x, y))
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
        self.update_table()
        self.update_plot()

    def update_table(self):
        points = self._request_points(-10.0, 10.0, 2.0)
        self.table.setRowCount(len(points))

        for i, (x, y) in enumerate(points):
            self.table.setItem(i, 0, QTableWidgetItem(f"{x:.2f}"))
            self.table.setItem(i, 1, QTableWidgetItem(f"{y:.6f}"))

        self.table.resizeColumnsToContents()

    def _add_segment(self, points, color):
        if len(points) < 2:
            return

        series = QLineSeries()
        series.setPen(QPen(color, 1.5))

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
            self.axis_y.setRange(-1, 1)
            self.y_line.clear()
            self.y_line.append(0, -1)
            self.y_line.append(0, 1)
            self.chart.setTitle(f"График  |  a = {self.a:.2f}, b = {self.b:.2f}, c = {self.c:.2f}")
            return

        left_points = []
        mid_points = []
        right_points = []

        for x, y in points:
            if x < -math.pi:
                left_points.append((x, y))
            elif x < 0:
                mid_points.append((x, y))
            else:
                right_points.append((x, y))

        def split_and_add(src_points, color):
            if not src_points:
                return
            segment = [src_points[0]]
            prev_x, prev_y = src_points[0]

            for x, y in src_points[1:]:
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

        split_and_add(left_points, QColor(255, 0, 0))
        split_and_add(mid_points, QColor(0, 255, 0))
        split_and_add(right_points, QColor(0, 0, 255))

        all_pts = points
        # режем выбросы
        filtered = [y for _, y in all_pts if abs(y) < 50]

        if not filtered:
            filtered = [0]

        ymin = min(filtered)
        ymax = max(filtered)

        # фиксируем границы если надо
        ymin = max(ymin, -20)
        ymax = min(ymax, 20)

        ymin = min(ymin, 0.0)
        ymax = max(ymax, 0.0)

        if abs(ymax - ymin) < 1e-9:
            ymin -= 1.0
            ymax += 1.0
        else:
            margin = (ymax - ymin) * 0.05
            ymin -= margin
            ymax += margin

        self.axis_y.setRange(ymin, ymax)

        self.y_line.clear()
        self.y_line.append(0, ymin)
        self.y_line.append(0, ymax)

        self.chart.setTitle(f"График  |  a = {self.a:.2f}, b = {self.b:.2f}, c = {self.c:.2f}")


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


class AuthScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.client = TcpClient()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

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

        self.login_btn.clicked.connect(self.do_login)
        self.register_btn.clicked.connect(self.do_register)
        self.to_register_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.register_widget))
        self.to_login_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.login_widget))

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

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        if password != confirm:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
            return

        response = self.client.send(f"reg&{username}&{password}&test@mail.com")

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
        self.setMinimumSize(1000, 600)

        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.main_layout = QVBoxLayout(self.central)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        self.title_screen = TitleScreen()
        self.auth_screen = AuthScreen(self)
        self.function_screen = FunctionScreen(self.auth_screen.client)

        self.stacked_widget.addWidget(self.title_screen)
        self.stacked_widget.addWidget(self.auth_screen)
        self.stacked_widget.addWidget(self.function_screen)

        self.title_screen.start_btn.clicked.connect(self.show_auth_screen)

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
