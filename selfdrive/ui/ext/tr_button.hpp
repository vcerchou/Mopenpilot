#pragma once
#include "selfdrive/ui/ui.h"

bool handle_tr_button_touch(UIState *s, int touch_x, int touch_y);

void ui_draw_tr_button(QPainter &p, UIState *s);
