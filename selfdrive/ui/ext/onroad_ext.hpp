#pragma once
#include "selfdrive/ui/ui.h"
#include "selfdrive/ui/qt/util.h"

void drawIcon(QPainter &p, int x, int y, QPixmap &img, QBrush bg, float opacity);
void drawText(QPainter &p, int x, int y, const QString &text, QColor color);

void ui_draw_ext(QPainter &p, UIState *s);
