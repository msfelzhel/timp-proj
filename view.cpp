#include "view.h"

/**
 * @brief Разделение строки по символу &
 */
QStringList View::parse(const QString &request) {
    QString clean = request.trimmed();

    if (clean.isEmpty())
        return {};

    return clean.split("&");
}
