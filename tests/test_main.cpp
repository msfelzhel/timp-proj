#include <QCoreApplication>
#include <QtTest/QtTest>

#include "test_model.cpp"
#include "test_controller.cpp"

int main(int argc, char *argv[])
{
    QCoreApplication app(argc, argv);

    int status = 0;

    {
        TestModel tc;

        status |= QTest::qExec(
            &tc,
            argc,
            argv
        );
    }

    {
        TestController tc;

        status |= QTest::qExec(
            &tc,
            argc,
            argv
        );
    }

    return status;
}