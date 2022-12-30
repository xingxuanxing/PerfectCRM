from django import conf

def queenadmin_autodiscover_app():
    for app_name in conf.settings.INSTALLED_APPS:

        try:
            import importlib
            importlib.import_module('.queenadmin', app_name)

        except ModuleNotFoundError as e:
            pass