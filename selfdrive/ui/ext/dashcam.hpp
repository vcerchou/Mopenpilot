#pragma once
#include "selfdrive/ui/ui.h"

void update_dashcam(UIState *s);

bool handle_dashcam_button_touch(UIState *s, int touch_x, int touch_y);

void ui_draw_dashcam_button(QPainter &p, UIState *s);
