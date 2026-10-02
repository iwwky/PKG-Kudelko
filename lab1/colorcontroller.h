#ifndef COLORCONTROLLER_H
#define COLORCONTROLLER_H
#include "colormodel.h"

class ColorController
{
public:
    ColorController();
    void setFromRgb(double r, double g, double b);
    void setFromCmyk(double c, double m, double y, double k);
    void setFromLab(double l, double a, double b);
    void setSettings(Illuminant light, CmykMethod method, GamutStrategy strategy);
    RgbColor getRgb() const
    {
        return rgb;
    }
    CmykColor getCmyk() const
    {
        return cmyk;
    }
    LabColor getLab() const
    {
        return lab;
    }
    bool isOutOfGamut() const
    {
        return corrected;
    }
    RgbColor previewLab(LabColor value) const;

private:
    enum class Source
    {
        Rgb,
        Cmyk,
        Lab
    };

    Source source = Source::Rgb;
    ColorModel model;
    CmykMethod method = CmykMethod::GCR;
    GamutStrategy strategy = GamutStrategy::Clipping;
    RgbColor inputRgb{255, 0, 0};
    RgbColor rgb{};
    CmykColor inputCmyk{};
    CmykColor cmyk{};
    LabColor inputLab{};
    LabColor lab{};
    bool corrected = false;

    void recalculate();
};

#endif
