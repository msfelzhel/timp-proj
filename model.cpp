#include "model.h"
#include "sqlite3.h"

sqlite3 *db;

Model::Model() {
    initDB();
    createTable();
}

void Model::initDB() {
    sqlite3_open("users.db", &db);
}

void Model::createTable() {
    const char *sql =
        "CREATE TABLE IF NOT EXISTS users ("
        "login TEXT PRIMARY KEY,"
        "password TEXT,"
        "email TEXT);";

    char *err = nullptr;
    sqlite3_exec(db, sql, 0, 0, &err);
}

bool Model::reg(const QString &login, const QString &password, const QString &email) {
    QString query = "INSERT INTO users VALUES('" + login + "','" + password + "','" + email + "');";
    return sqlite3_exec(db, query.toUtf8().data(), 0, 0, 0) == SQLITE_OK;
}

bool Model::auth(const QString &login, const QString &password) {
    QString query = "SELECT * FROM users WHERE login='" + login + "' AND password='" + password + "';";

    bool found = false;

    auto callback = [](void *data, int, char **, char **)->int {
        bool *f = (bool*)data;
        *f = true;
        return 0;
    };

    sqlite3_exec(db, query.toUtf8().data(), callback, &found, 0);

    return found;
}

QString Model::stat(const QString &) {
    return "stat&3$6&21";
}

bool Model::check(int task, const QString &, const QString &answer) {
    return task == 1 && answer == "42";
}
