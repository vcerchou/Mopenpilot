import gettext
from common.params import Params
from selfdrive.hardware import EON, TICI
from selfdrive.hardware.eon.hardware import getprop

locale_dir = '/data/openpilot/selfdrive/assets/locales'
supported_language = ['en-US', 'zh-TW', 'zh-CN', 'ja-JP']

def get_locale():
  locale = None
  if EON:
    locale = getprop("persist.sys.locale")
  elif TICI:
    locale = Params().get("SysLanguage", encoding='utf8')

  if locale is None:
    locale = 'en-US'
  return locale

def events():
  i18n = gettext.translation('events', localedir=locale_dir, fallback=True, languages=[get_locale()])
  i18n.install()
  return i18n.gettext

if __name__ == "__main__":
  _ = events()
  print(_("System Malfunction: Reboot Your Device"))

