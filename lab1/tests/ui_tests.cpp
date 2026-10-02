#include "../mainwindow.h"
#include <QtTest>
#include <QApplication>
class UiTests : public QObject
{
    Q_OBJECT
private slots:
    void controls()
    {
        MainWindow w;
        w.show();
        QList<QSpinBox *> rgb = w.findChildren<QSpinBox *>();
        QList<QDoubleSpinBox *> decimals = w.findChildren<QDoubleSpinBox *>();
        QList<QSlider *> sliders = w.findChildren<QSlider *>();
        QList<QComboBox *> settings = w.findChildren<QComboBox *>();
        QCOMPARE(rgb.size(), 3);
        QCOMPARE(decimals.size(), 7);
        QCOMPARE(sliders.size(), 10);
        const QString oldGradient = sliders[1]->styleSheet();
        rgb[0]->setValue(128);
        rgb[1]->setValue(128);
        rgb[2]->setValue(128);
        QVERIFY(std::abs(decimals[4]->value() - 53.585) < .002);
        QVERIFY(sliders[1]->styleSheet() != oldGradient);
        settings[1]->setCurrentIndex(0);
        QCOMPARE(decimals[3]->value(), 0.0);
        settings[1]->setCurrentIndex(1);
        QVERIFY(std::abs(decimals[3]->value() - .49804) < .00001);
        decimals[0]->setValue(.2);
        QCOMPARE(decimals[0]->value(), .2);
        sliders[7]->setValue(5000);
        QCOMPARE(decimals[4]->value(), 50.0);
        sliders[8]->setValue(12000);
        QCOMPARE(decimals[5]->value(), 120.0);
        sliders[9]->setValue(12000);
        QCOMPARE(decimals[6]->value(), 120.0);
        bool warning = false;
        for (QLabel *label : w.findChildren<QLabel *>())
        {
            if (label->text().contains("Внимание"))
            {
                warning = true;
            }
        }
        QVERIFY(warning);
        settings[2]->setCurrentIndex(1);
        QCOMPARE(decimals[5]->value(), 120.0);
        settings[0]->setCurrentIndex(1);
        QCOMPARE(decimals[5]->value(), 120.0);
        settings[0]->setCurrentIndex(2);
        QCOMPARE(decimals[5]->value(), 120.0);
        rgb[0]->setValue(255);
        rgb[1]->setValue(255);
        rgb[2]->setValue(255);
        QVERIFY(std::abs(decimals[4]->value() - 100) < .001);
        QVERIFY(std::abs(decimals[5]->value()) < .001);
    }
};

QTEST_MAIN(UiTests)
#include "ui_tests.moc"
