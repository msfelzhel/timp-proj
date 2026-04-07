#include "controller.h"

/**
 * @brief Основной обработчик команд
 */
QString Controller::handleRequest(const QString &request) {
    QStringList parts = view.parse(request);

    if (parts.isEmpty())
        return "";

    if (parts[0] == "auth" && parts.size() >= 3)
        return model.auth(parts[1], parts[2]) ? "auth+&" + parts[1] : "auth-";

    if (parts[0] == "reg" && parts.size() >= 4)
        return model.reg(parts[1], parts[2], parts[3]) ? "reg+&" + parts[1] : "reg-";

    if (parts[0] == "stat" && parts.size() >= 2)
        return model.stat(parts[1]);

    if (parts[0] == "check" && parts.size() >= 4)
        return model.check(parts[1].toInt(), parts[2], parts[3]) ? "check+" : "check-";

    return "error";
}
