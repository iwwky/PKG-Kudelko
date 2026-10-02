#include "colorcontroller.h"

ColorController::ColorController()
{
    recalculate();
}

void ColorController::setFromRgb(double r, double g, double b)
{
    source = Source::Rgb;
    inputRgb = {r, g, b};
    recalculate();
}

void ColorController::setFromCmyk(double c, double m, double y, double k)
{
    source = Source::Cmyk;
    inputCmyk = {c, m, y, k};
    recalculate();
}

void ColorController::setFromLab(double l, double a, double b)
{
    source = Source::Lab;
    inputLab = {l, a, b};
    recalculate();
}

void ColorController::setSettings(Illuminant light, CmykMethod nextMethod,
                                  GamutStrategy nextStrategy)
{
    model.setIlluminant(light);
    method = nextMethod;
    strategy = nextStrategy;
    recalculate();
}

void ColorController::recalculate()
{
    RgbColor rawRgb = inputRgb;

    if (source == Source::Cmyk)
    {
        rawRgb = ColorModel::cmykToRgb(inputCmyk);
    }
    else if (source == Source::Lab)
    {
        rawRgb = model.labToRgb(inputLab);
    }

    rgb = ColorModel::mapGamut(rawRgb, strategy, corrected);

    if (source == Source::Cmyk)
    {
        cmyk = inputCmyk;
    }
    else
    {
        cmyk = ColorModel::rgbToCmyk(rgb, method);
    }

    if (source == Source::Lab)
    {
        lab = inputLab;
    }
    else
    {
        lab = model.rgbToLab(rgb);
    }
}

RgbColor ColorController::previewLab(LabColor value) const
{
    bool changed = false;
    RgbColor rawRgb = model.labToRgb(value);
    return ColorModel::mapGamut(rawRgb, strategy, changed);
}
