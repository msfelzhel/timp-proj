#include "model.h"
#include "sqlite3.h"
#include <QDebug>
#include <QCryptographicHash>

QString hashPassword(const QString &password) {
    QByteArray hash = QCryptographicHash::hash(
        password.toUtf8(),
        QCryptographicHash::Sha256
        );
    return hash.toHex();
}

sqlite3 *db;

/**
 * @brief Конструктор модели
 */
Model::Model() {
    initDB();
    createTable();
}

/**
 * @brief Инициализация базы
 */
void Model::initDB() {
    sqlite3_open("users.db", &db);
}

/**
 * @brief Создание таблицы пользователей
 */
void Model::createTable() {
    const char *sql =
        "CREATE TABLE IF NOT EXISTS users ("
        "login TEXT PRIMARY KEY,"
        "password TEXT,"
        "email TEXT);";

    char *err = nullptr;
    sqlite3_exec(db, sql, 0, 0, &err);
}

/**
 * @brief Регистрация пользователя
 */
bool Model::reg(const QString &login, const QString &password, const QString &email) {
    QString hashed = hashPassword(password);
    QString query = "INSERT INTO users VALUES('" + login + "','" + hashed + "','" + email + "');";

    char *err = nullptr;
    int rc = sqlite3_exec(db, query.toUtf8().data(), 0, 0, &err);

    if (rc != SQLITE_OK) {
        qDebug() << "SQL error:" << err;
        sqlite3_free(err);
        return false;
    }

    return true;
}

/**
 * @brief Авторизация
 */
bool Model::auth(const QString &login, const QString &password) {
    QString hashed = hashPassword(password);

    QString query = "SELECT * FROM users WHERE login='" + login + "' AND password='" + hashed + "';";

    bool found = false;

    auto callback = [](void *data, int, char **, char **)->int {
        bool *f = (bool*)data;
        *f = true;
        return 0;
    };

    sqlite3_exec(db, query.toUtf8().data(), callback, &found, 0);

    return found;
}

/**
 * @brief Получение статистики
 */
QString Model::stat(const QString &) {
    return "stat&3$6&21";
}

/**
 * @brief Проверка решения задачи
 */
bool Model::check(int task, const QString &, const QString &answer) {
    return task == 1 && answer == "42";
}
QString Model::calc(double a, double b, double c) {
    QString result = "calc&";

    const double PI = acos(-1.0);
    const double EPS = 1e-9;

    for (double x = -10; x <= 10.0; x += 0.05) {
        double y;
        bool ok = true;

        if (x < -PI) {
            y = cos(a * x);
        } else if (x < 0) {
            if (fabs(x + PI) < EPS) ok = false;
            else y = b / (x + PI);
        } else {
            double s = sin(c + x);
            if (fabs(s) < EPS) ok = false;
            else y = cos(c + x) / s;
        }

        if (ok && std::isfinite(y)) {
            if (fabs(y) > 1000) continue; // защита от бесконечностей
            result += QString::number(x) + "," + QString::number(y) + ";";
        }
    }

    return result;
}
