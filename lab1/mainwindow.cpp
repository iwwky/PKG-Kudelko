#include "mainwindow.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QFormLayout>
#include <QStringList>

MainWindow::MainWindow(QWidget *parent) : QMainWindow(parent)
{
    setupUi();
    connectControls();
    setWindowTitle("Цветовые модели · Вариант 1 · 10А");
    resize(800, 740);
    updateUi();
}

void MainWindow::setupUi()
{
    QWidget *centralWidget = new QWidget(this);
    QVBoxLayout *layout = new QVBoxLayout(centralWidget);
    layout->addWidget(createSettingsPanel());

    m_warningLabel = new QLabel();
    m_warningLabel->setStyleSheet("color: #e07830; font-weight: bold;");
    m_warningLabel->setWordWrap(true);
    layout->addWidget(m_warningLabel);

    layout->addWidget(createRgbGroup());
    layout->addWidget(createCmykGroup());
    layout->addWidget(createLabGroup());
    setCentralWidget(centralWidget);
}

QWidget *MainWindow::createSettingsPanel()
{
    QWidget *panel = new QWidget();
    QHBoxLayout *layout = new QHBoxLayout(panel);
    QVBoxLayout *previewLayout = new QVBoxLayout();

    m_colorPreview = new QWidget();
    m_colorPreview->setMinimumSize(240, 80);
    m_pickerButton = new QPushButton("Выбрать из палитры");
    previewLayout->addWidget(m_colorPreview);
    previewLayout->addWidget(m_pickerButton);
    layout->addLayout(previewLayout);

    QFormLayout *settingsLayout = new QFormLayout();
    m_illuminantCombo = new QComboBox();
    m_illuminantCombo->addItems({"D65", "D50", "E"});
    m_cmykMethodCombo = new QComboBox();
    m_cmykMethodCombo->addItems({"UCR — глубокие тени", "GCR — весь диапазон"});
    m_cmykMethodCombo->setCurrentIndex(1);
    m_gamutStrategyCombo = new QComboBox();
    m_gamutStrategyCombo->addItems({"Clipping", "Scaling"});
    settingsLayout->addRow("Источник света:", m_illuminantCombo);
    settingsLayout->addRow("Метод CMYK:", m_cmykMethodCombo);
    settingsLayout->addRow("Выход за диапазон:", m_gamutStrategyCombo);
    layout->addLayout(settingsLayout);
    return panel;
}

QGroupBox *MainWindow::createRgbGroup()
{
    QGroupBox *group = new QGroupBox("RGB · значения 0…255");
    QFormLayout *layout = new QFormLayout(group);
    layout->setFieldGrowthPolicy(QFormLayout::AllNonFixedFieldsGrow);

    m_rSpin = new QSpinBox();
    m_rSpin->setRange(0, 255);
    m_rSpin->setKeyboardTracking(false);
    m_rSlider = new QSlider(Qt::Horizontal);
    m_rSlider->setRange(0, 255);
    QHBoxLayout *rRow = new QHBoxLayout();
    rRow->addWidget(m_rSpin);
    rRow->addWidget(m_rSlider);
    layout->addRow("R:", rRow);

    m_gSpin = new QSpinBox();
    m_gSpin->setRange(0, 255);
    m_gSpin->setKeyboardTracking(false);
    m_gSlider = new QSlider(Qt::Horizontal);
    m_gSlider->setRange(0, 255);
    QHBoxLayout *gRow = new QHBoxLayout();
    gRow->addWidget(m_gSpin);
    gRow->addWidget(m_gSlider);
    layout->addRow("G:", gRow);

    m_bSpin = new QSpinBox();
    m_bSpin->setRange(0, 255);
    m_bSpin->setKeyboardTracking(false);
    m_bSlider = new QSlider(Qt::Horizontal);
    m_bSlider->setRange(0, 255);
    QHBoxLayout *bRow = new QHBoxLayout();
    bRow->addWidget(m_bSpin);
    bRow->addWidget(m_bSlider);
    layout->addRow("B:", bRow);

    QPushButton *paletteButton = new QPushButton("Палитра…");
    layout->addRow(paletteButton);
    connect(paletteButton, &QPushButton::clicked, this, &MainWindow::onColorPickerClicked);
    return group;
}

QGroupBox *MainWindow::createCmykGroup()
{
    QGroupBox *group = new QGroupBox("CMYK · значения 0…1 (1 = 100%)");
    QFormLayout *layout = new QFormLayout(group);
    layout->setFieldGrowthPolicy(QFormLayout::AllNonFixedFieldsGrow);

    m_cSpin = new QDoubleSpinBox();
    m_cSpin->setRange(0, 1);
    m_cSpin->setKeyboardTracking(false);
    m_cSpin->setDecimals(5);
    m_cSpin->setSingleStep(0.01);
    m_cSlider = new QSlider(Qt::Horizontal);
    m_cSlider->setRange(0, 10000);
    QHBoxLayout *cRow = new QHBoxLayout();
    cRow->addWidget(m_cSpin);
    cRow->addWidget(m_cSlider);
    layout->addRow("C:", cRow);

    m_mSpin = new QDoubleSpinBox();
    m_mSpin->setRange(0, 1);
    m_mSpin->setKeyboardTracking(false);
    m_mSpin->setDecimals(5);
    m_mSpin->setSingleStep(0.01);
    m_mSlider = new QSlider(Qt::Horizontal);
    m_mSlider->setRange(0, 10000);
    QHBoxLayout *mRow = new QHBoxLayout();
    mRow->addWidget(m_mSpin);
    mRow->addWidget(m_mSlider);
    layout->addRow("M:", mRow);

    m_ySpin = new QDoubleSpinBox();
    m_ySpin->setRange(0, 1);
    m_ySpin->setKeyboardTracking(false);
    m_ySpin->setDecimals(5);
    m_ySpin->setSingleStep(0.01);
    m_ySlider = new QSlider(Qt::Horizontal);
    m_ySlider->setRange(0, 10000);
    QHBoxLayout *yRow = new QHBoxLayout();
    yRow->addWidget(m_ySpin);
    yRow->addWidget(m_ySlider);
    layout->addRow("Y:", yRow);

    m_kSpin = new QDoubleSpinBox();
    m_kSpin->setRange(0, 1);
    m_kSpin->setKeyboardTracking(false);
    m_kSpin->setDecimals(5);
    m_kSpin->setSingleStep(0.01);
    m_kSlider = new QSlider(Qt::Horizontal);
    m_kSlider->setRange(0, 10000);
    QHBoxLayout *kRow = new QHBoxLayout();
    kRow->addWidget(m_kSpin);
    kRow->addWidget(m_kSlider);
    layout->addRow("K:", kRow);

    QPushButton *paletteButton = new QPushButton("Палитра…");
    layout->addRow(paletteButton);
    connect(paletteButton, &QPushButton::clicked, this, &MainWindow::onColorPickerClicked);
    return group;
}

QGroupBox *MainWindow::createLabGroup()
{
    QGroupBox *group = new QGroupBox("LAB · светлота и цветовые координаты");
    QFormLayout *layout = new QFormLayout(group);
    layout->setFieldGrowthPolicy(QFormLayout::AllNonFixedFieldsGrow);

    m_lSpin = new QDoubleSpinBox();
    m_lSpin->setRange(0, 100);
    m_lSpin->setKeyboardTracking(false);
    m_lSpin->setDecimals(3);
    m_lSpin->setSingleStep(0.01);
    m_lSlider = new QSlider(Qt::Horizontal);
    m_lSlider->setRange(0, 10000);
    QHBoxLayout *lRow = new QHBoxLayout();
    lRow->addWidget(m_lSpin);
    lRow->addWidget(m_lSlider);
    layout->addRow("L:", lRow);

    m_aSpin = new QDoubleSpinBox();
    m_aSpin->setRange(-128, 127);
    m_aSpin->setKeyboardTracking(false);
    m_aSpin->setDecimals(3);
    m_aSpin->setSingleStep(0.01);
    m_aSlider = new QSlider(Qt::Horizontal);
    m_aSlider->setRange(-12800, 12700);
    QHBoxLayout *aRow = new QHBoxLayout();
    aRow->addWidget(m_aSpin);
    aRow->addWidget(m_aSlider);
    layout->addRow("a:", aRow);

    m_bLabSpin = new QDoubleSpinBox();
    m_bLabSpin->setRange(-128, 127);
    m_bLabSpin->setKeyboardTracking(false);
    m_bLabSpin->setDecimals(3);
    m_bLabSpin->setSingleStep(0.01);
    m_bLabSlider = new QSlider(Qt::Horizontal);
    m_bLabSlider->setRange(-12800, 12700);
    QHBoxLayout *bLabRow = new QHBoxLayout();
    bLabRow->addWidget(m_bLabSpin);
    bLabRow->addWidget(m_bLabSlider);
    layout->addRow("b:", bLabRow);

    QPushButton *paletteButton = new QPushButton("Палитра…");
    layout->addRow(paletteButton);
    connect(paletteButton, &QPushButton::clicked, this, &MainWindow::onColorPickerClicked);
    return group;
}

void MainWindow::connectControls()
{
    connect(m_rSpin, &QSpinBox::valueChanged, this, &MainWindow::onRgbChanged);
    connect(m_rSlider, &QSlider::valueChanged, this, [this](int value) {
        if (!m_isUpdating)
        {
            m_rSpin->setValue(value);
        }
    });
    connect(m_gSpin, &QSpinBox::valueChanged, this, &MainWindow::onRgbChanged);
    connect(m_gSlider, &QSlider::valueChanged, this, [this](int value) {
        if (!m_isUpdating)
        {
            m_gSpin->setValue(value);
        }
    });
    connect(m_bSpin, &QSpinBox::valueChanged, this, &MainWindow::onRgbChanged);
    connect(m_bSlider, &QSlider::valueChanged, this, [this](int value) {
        if (!m_isUpdating)
        {
            m_bSpin->setValue(value);
        }
    });
    connect(m_cSpin, &QDoubleSpinBox::valueChanged, this, &MainWindow::onCmykChanged);
    connect(m_cSlider, &QSlider::valueChanged, this, [this](int value) {
        if (!m_isUpdating)
        {
            m_cSpin->setValue(value / 10000.0);
        }
    });
    connect(m_mSpin, &QDoubleSpinBox::valueChanged, this, &MainWindow::onCmykChanged);
    connect(m_mSlider, &QSlider::valueChanged, this, [this](int value) {
        if (!m_isUpdating)
        {
            m_mSpin->setValue(value / 10000.0);
        }
    });
    connect(m_ySpin, &QDoubleSpinBox::valueChanged, this, &MainWindow::onCmykChanged);
    connect(m_ySlider, &QSlider::valueChanged, this, [this](int value) {
        if (!m_isUpdating)
        {
            m_ySpin->setValue(value / 10000.0);
        }
    });
    connect(m_kSpin, &QDoubleSpinBox::valueChanged, this, &MainWindow::onCmykChanged);
    connect(m_kSlider, &QSlider::valueChanged, this, [this](int value) {
        if (!m_isUpdating)
        {
            m_kSpin->setValue(value / 10000.0);
        }
    });
    connect(m_lSpin, &QDoubleSpinBox::valueChanged, this, &MainWindow::onLabChanged);
    connect(m_lSlider, &QSlider::valueChanged, this, [this](int value) {
        if (!m_isUpdating)
        {
            m_lSpin->setValue(value / 100.0);
        }
    });
    connect(m_aSpin, &QDoubleSpinBox::valueChanged, this, &MainWindow::onLabChanged);
    connect(m_aSlider, &QSlider::valueChanged, this, [this](int value) {
        if (!m_isUpdating)
        {
            m_aSpin->setValue(value / 100.0);
        }
    });
    connect(m_bLabSpin, &QDoubleSpinBox::valueChanged, this, &MainWindow::onLabChanged);
    connect(m_bLabSlider, &QSlider::valueChanged, this, [this](int value) {
        if (!m_isUpdating)
        {
            m_bLabSpin->setValue(value / 100.0);
        }
    });
    connect(m_pickerButton, &QPushButton::clicked, this, &MainWindow::onColorPickerClicked);
    connect(m_illuminantCombo, &QComboBox::currentIndexChanged, this,
            &MainWindow::onSettingsChanged);
    connect(m_cmykMethodCombo, &QComboBox::currentIndexChanged, this,
            &MainWindow::onSettingsChanged);
    connect(m_gamutStrategyCombo, &QComboBox::currentIndexChanged, this,
            &MainWindow::onSettingsChanged);
}

void MainWindow::onSettingsChanged()
{
    Illuminant light = Illuminant::D65;
    if (m_illuminantCombo->currentIndex() == 1)
    {
        light = Illuminant::D50;
    }
    else if (m_illuminantCombo->currentIndex() == 2)
    {
        light = Illuminant::E;
    }

    CmykMethod method = CmykMethod::GCR;
    if (m_cmykMethodCombo->currentIndex() == 0)
    {
        method = CmykMethod::UCR;
    }

    GamutStrategy strategy = GamutStrategy::Clipping;
    if (m_gamutStrategyCombo->currentIndex() == 1)
    {
        strategy = GamutStrategy::Scaling;
    }

    m_controller.setSettings(light, method, strategy);
    updateUi();
}

void MainWindow::onRgbChanged()
{
    if (m_isUpdating)
    {
        return;
    }
    m_controller.setFromRgb(m_rSpin->value(), m_gSpin->value(), m_bSpin->value());
    updateUi();
}

void MainWindow::onCmykChanged()
{
    if (m_isUpdating)
    {
        return;
    }
    m_controller.setFromCmyk(m_cSpin->value(), m_mSpin->value(), m_ySpin->value(),
                             m_kSpin->value());
    updateUi();
}

void MainWindow::onLabChanged()
{
    if (m_isUpdating)
    {
        return;
    }
    m_controller.setFromLab(m_lSpin->value(), m_aSpin->value(), m_bLabSpin->value());
    updateUi();
}

void MainWindow::onColorPickerClicked()
{
    RgbColor rgb = m_controller.getRgb();
    QColor initial(qRound(rgb.r), qRound(rgb.g), qRound(rgb.b));
    QColor color = QColorDialog::getColor(initial, this, "Выберите цвет");

    if (color.isValid())
    {
        m_controller.setFromRgb(color.red(), color.green(), color.blue());
        updateUi();
    }
}

void MainWindow::updateUi()
{
    m_isUpdating = true;

    RgbColor rgb = m_controller.getRgb();
    CmykColor cmyk = m_controller.getCmyk();
    LabColor lab = m_controller.getLab();

    m_rSpin->setValue(qRound(rgb.r));
    m_rSlider->setValue(qRound(rgb.r));
    m_gSpin->setValue(qRound(rgb.g));
    m_gSlider->setValue(qRound(rgb.g));
    m_bSpin->setValue(qRound(rgb.b));
    m_bSlider->setValue(qRound(rgb.b));

    m_cSpin->setValue(cmyk.c);
    m_cSlider->setValue(qRound(cmyk.c * 10000));
    m_mSpin->setValue(cmyk.m);
    m_mSlider->setValue(qRound(cmyk.m * 10000));
    m_ySpin->setValue(cmyk.y);
    m_ySlider->setValue(qRound(cmyk.y * 10000));
    m_kSpin->setValue(cmyk.k);
    m_kSlider->setValue(qRound(cmyk.k * 10000));

    m_lSpin->setValue(lab.l);
    m_lSlider->setValue(qRound(lab.l * 100));
    m_aSpin->setValue(lab.a);
    m_aSlider->setValue(qRound(lab.a * 100));
    m_bLabSpin->setValue(lab.b);
    m_bLabSlider->setValue(qRound(lab.b * 100));

    m_colorPreview->setStyleSheet(
        QString("border: 1px solid gray; background-color: rgb(%1,%2,%3);")
            .arg(qRound(rgb.r))
            .arg(qRound(rgb.g))
            .arg(qRound(rgb.b)));

    if (m_controller.isOutOfGamut())
    {
        m_warningLabel->setText(
            "⚠️ Внимание: Выход за границы цветового охвата! Применена коррекция.");
    }
    else
    {
        m_warningLabel->setText("");
    }

    updateGradients();
    m_isUpdating = false;
}

RgbColor MainWindow::gradientColor(Channel channel, double position) const
{
    RgbColor rgb = m_controller.getRgb();
    CmykColor cmyk = m_controller.getCmyk();
    LabColor lab = m_controller.getLab();

    switch (channel)
    {
    case Channel::Red:
        rgb.r = 255 * position;
        return rgb;
    case Channel::Green:
        rgb.g = 255 * position;
        return rgb;
    case Channel::Blue:
        rgb.b = 255 * position;
        return rgb;
    case Channel::Cyan:
        cmyk.c = position;
        return ColorModel::cmykToRgb(cmyk);
    case Channel::Magenta:
        cmyk.m = position;
        return ColorModel::cmykToRgb(cmyk);
    case Channel::Yellow:
        cmyk.y = position;
        return ColorModel::cmykToRgb(cmyk);
    case Channel::Black:
        cmyk.k = position;
        return ColorModel::cmykToRgb(cmyk);
    case Channel::Lightness:
        lab.l = 100 * position;
        return m_controller.previewLab(lab);
    case Channel::LabA:
        lab.a = -128 + 255 * position;
        return m_controller.previewLab(lab);
    case Channel::LabB:
        lab.b = -128 + 255 * position;
        return m_controller.previewLab(lab);
    }
    return rgb;
}

void MainWindow::setSliderGradient(QSlider *slider, Channel channel)
{
    QStringList stops;
    for (int i = 0; i <= 24; i++)
    {
        double position = i / 24.0;
        RgbColor color = gradientColor(channel, position);
        QString stop = QString("stop:%1 rgb(%2,%3,%4)")
                           .arg(position, 0, 'f', 4)
                           .arg(qRound(color.r))
                           .arg(qRound(color.g))
                           .arg(qRound(color.b));
        stops.append(stop);
    }

    QString style = QString("QSlider::groove:horizontal {"
                            "height:12px; border-radius:5px; border:1px solid #777;"
                            "background:qlineargradient(x1:0,y1:0,x2:1,y2:0,%1); }"
                            "QSlider::handle:horizontal {"
                            "background:white; border:2px solid #333; width:12px;"
                            "margin:-5px 0; border-radius:6px; }")
                        .arg(stops.join(","));
    slider->setStyleSheet(style);
}

void MainWindow::updateGradients()
{
    setSliderGradient(m_rSlider, Channel::Red);
    setSliderGradient(m_gSlider, Channel::Green);
    setSliderGradient(m_bSlider, Channel::Blue);
    setSliderGradient(m_cSlider, Channel::Cyan);
    setSliderGradient(m_mSlider, Channel::Magenta);
    setSliderGradient(m_ySlider, Channel::Yellow);
    setSliderGradient(m_kSlider, Channel::Black);
    setSliderGradient(m_lSlider, Channel::Lightness);
    setSliderGradient(m_aSlider, Channel::LabA);
    setSliderGradient(m_bLabSlider, Channel::LabB);
}
