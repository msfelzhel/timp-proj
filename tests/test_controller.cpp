#include <QtTest/QtTest>
#include <QFile>

#include "../controller.h"

class TestController : public QObject
{
    Q_OBJECT

private slots:

    void initTestCase();

    void testHelp();
    void testRegister();
    void testDuplicateRegister();
    void testAuthSuccess();
    void testAuthFail();
    void testCalc();
    void testCheckSuccess();
    void testCheckFail();
    void testStat();
    void testWrongCommand();
};

void TestController::initTestCase()
{
    QFile::remove("users.db");
}

void TestController::testHelp()
{
    Controller c;

    QString result =
        c.handleRequest("--help");

    QVERIFY(
        result.contains("auth")
    );
}

void TestController::testRegister()
{
    Controller c;

    QString result =
        c.handleRequest(
            "reg&testuser12345&123&test@mail.com"
        );

    QVERIFY(
        result.startsWith("reg+")
    );
}

void TestController::testDuplicateRegister()
{
    Controller c;

    c.handleRequest(
        "reg&dup12345&123&dup@mail.com"
    );

    QString result =
        c.handleRequest(
            "reg&dup12345&123&dup@mail.com"
        );

    QVERIFY(
        result == "reg-"
    );
}

void TestController::testAuthSuccess()
{
    Controller c;

    c.handleRequest(
        "reg&login12345&123&login@mail.com"
    );

    QString result =
        c.handleRequest(
            "auth&login12345&123"
        );

    QVERIFY(
        result.startsWith("auth+")
    );
}

void TestController::testAuthFail()
{
    Controller c;

    QString result =
        c.handleRequest(
            "auth&bad&bad"
        );

    QVERIFY(
        result == "auth-"
    );
}

void TestController::testCalc()
{
    Controller c;

    QString result =
        c.handleRequest(
            "calc&1&1&1"
        );

    QVERIFY(
        result.startsWith("calc&")
    );
}

void TestController::testCheckSuccess()
{
    Controller c;

    QString result =
        c.handleRequest(
            "check&1&1&42"
        );

    QVERIFY(
        result == "check+"
    );
}

void TestController::testCheckFail()
{
    Controller c;

    QString result =
        c.handleRequest(
            "check&1&1&41"
        );

    QVERIFY(
        result == "check-"
    );
}

void TestController::testStat()
{
    Controller c;

    QString result =
        c.handleRequest(
            "stat&user"
        );

    QVERIFY(
        result.startsWith("stat&")
    );
}

void TestController::testWrongCommand()
{
    Controller c;

    QString result =
        c.handleRequest(
            "abracadabra"
        );

    QVERIFY(
        result == "error"
    );
}

QTEST_MAIN(TestController)

#include "test_controller.moc"