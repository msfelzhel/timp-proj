#include "controller.h"
#include "email_service.h"
#include "view.h"

#include <QMap>

    // хранилище кодов
    static QMap<QString, QString> resetCodes;

/**
 * @brief Основной обработчик команд
 */
QString Controller::handleRequest(const QString &request) {

    // если не хочешь зависеть от view, можно так:
    // QStringList parts = request.split("&");

    QStringList parts = view.parse(request);

    if (parts.isEmpty())
        return "";

    if (parts[0] == "--help") {
        return "Commands:\n"
               "auth&login&password\n"
               "reg&login&password&email\n"
               "stat&login\n"
               "check&task&variant&answer\n"
               "reset_request&email\n"
               "reset_confirm&email&code&newpass\n";
    }

    // ===== AUTH =====
    if (parts[0] == "auth" && parts.size() >= 3)
        return model.auth(parts[1], parts[2]) ? "auth+&" + parts[1] : "auth-";

    // ===== REGISTER =====
    if (parts[0] == "reg" && parts.size() >= 4)
        return model.reg(parts[1], parts[2], parts[3]) ? "reg+&" + parts[1] : "reg-";

    // ===== STAT =====
    if (parts[0] == "stat" && parts.size() >= 2)
        return model.stat(parts[1]);

    // ===== CHECK =====
    if (parts[0] == "check" && parts.size() >= 4)
        return model.check(parts[1].toInt(), parts[2], parts[3]) ? "check+" : "check-";

    // ===== CALC =====
    if (parts[0] == "calc" && parts.size() >= 4) {
        double a = parts[1].toDouble();
        double b = parts[2].toDouble();
        double c = parts[3].toDouble();
        return model.calc(a, b, c);
    }

    // ===== RESET REQUEST =====
    if (parts[0] == "reset_request" && parts.size() >= 2) {
        QString email = parts[1];

        if (!model.emailExists(email))
            return "reset_fail";

        QString code = EmailService::generateCode();
        resetCodes[email] = code;

        if (EmailService::sendCode(email, code))
            return "reset_sent";
        else
            return "reset_fail";
    }

    // ===== RESET CONFIRM =====
    if (parts[0] == "reset_confirm" && parts.size() >= 4) {
        QString email = parts[1];
        QString code = parts[2];
        QString newPass = parts[3];

        if (resetCodes.contains(email) && resetCodes[email] == code) {
            if (model.updatePasswordByEmail(email, newPass)) {
                resetCodes.remove(email);
                return "reset_ok";
            }
        }
        return "reset_fail";
    }

    return "error";
}

