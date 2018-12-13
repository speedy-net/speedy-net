def update_site_paths(settings):
    app_dir = settings['APP_DIR']
    settings['STATIC_ROOT'] = str(app_dir / 'static_serve')
    settings['LOCALE_PATHS'].append(str(app_dir / 'locale'))
    settings['TEMPLATES'][0]['DIRS'].insert(0, str(app_dir / 'templates'))
    settings['STATICFILES_DIRS'].insert(0, str(app_dir / 'static'))
