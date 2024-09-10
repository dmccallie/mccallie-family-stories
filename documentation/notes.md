## Quick notes to myself

### running the app locally:
```
    DEBUG=True python manage.py runserver 0.0.0.0:8000
```

### migrations
```
    python manage.py  makemigrations (--dry-run)[app_label]
    python manage.py  migrate [app_label]

### initialize testing data
```
stuff
```

### adding a new app, needs updates all over:
```
python manage.py startapp chats
settings.py - add to INSTALLED_APPS = [..., chats,... ]
add new tag if necessary in STANDARD_TAGS e.g. [, 'chats']

add models and views, then
    add chats/url.py with new urlpatterns = [ path('xxxx', func_name, name = 'func_name')]

update config/urls.py urlpatterns = [] to include the new paths added to chats/url.py

```