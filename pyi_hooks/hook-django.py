import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Django settings'ni hook ishlayotgan payt ham topishi uchun
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

hiddenimports = []
datas = []

# Django'ning o'zini to'liq collect qilamiz (eng ishonchli)
hiddenimports += collect_submodules("django")
datas += collect_data_files("django")

# Django setup qilib, INSTALLED_APPS migrations'larini ham olib ketamiz
try:
    import django
    django.setup()
    from django.conf import settings

    for app in getattr(settings, "INSTALLED_APPS", []):
        # migrations modullarini ham qo'shamiz
        hiddenimports += collect_submodules(f"{app}.migrations")
except Exception:
    # Agar setup bo'lmasa ham build yiqilmasin
    pass

# DRF ba'zan hook paytida "settings are not configured" deb qoladi
try:
    hiddenimports += collect_submodules("rest_framework")
except Exception:
    pass