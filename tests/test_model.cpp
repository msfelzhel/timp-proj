#include <QtTest/QtTest>
#include <QFile>

#include "../model.h"

class TestModel : public QObject
{
    Q_OBJECT

private slots:

    void initTestCase();

    void testRegistration();
    void testDuplicateRegistration();
    void testAuthSuccess();
    void testAuthFail();
    void testEmailExists();
    void testPasswordReset();
};

void TestModel::initTestCase()
{
    QFile::remove("users.db");
}

void TestModel::testRegistration()
{
    Model m;

    bool ok = m.reg(
        "user111",
        "123",
        "user111@mail.com"
    );

    QVERIFY(ok);
}

void TestModel::testDuplicateRegistration()
{
    Model m;

    m.reg(
        "user222",
        "123",
        "user222@mail.com"
    );

    bool ok = m.reg(
        "user222",
        "123",
        "user222@mail.com"
    );

    QVERIFY(!ok);
}

void TestModel::testAuthSuccess()
{
    Model m;

    m.reg(
        "user333",
        "pass",
        "user333@mail.com"
    );

    QVERIFY(
        m.auth(
            "user333",
            "pass"
        )
    );
}

void TestModel::testAuthFail()
{
    Model m;

    QVERIFY(
        !m.auth(
            "bad",
            "bad"
        )
    );
}

void TestModel::testEmailExists()
{
    Model m;

    m.reg(
        "user444",
        "123",
        "user444@mail.com"
    );

    QVERIFY(
        m.emailExists(
            "user444@mail.com"
        )
    );

    QVERIFY(
        !m.emailExists(
            "none@mail.com"
        )
    );
}

void TestModel::testPasswordReset()
{
    Model m;

    m.reg(
        "user555",
        "old",
        "user555@mail.com"
    );

    QVERIFY(
        m.updatePasswordByEmail(
            "user555@mail.com",
            "new"
        )
    );

    QVERIFY(
        m.auth(
            "user555",
            "new"
        )
    );
}

QTEST_MAIN(TestModel)

#include "test_model.moc"