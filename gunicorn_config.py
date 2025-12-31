# gunicorn_config.py
bind = "0.0.0.0:10000"
workers = 1
timeout = 120  # Increased from default 30s
worker_class = "sync"
```

Then update your Render start command to:
```
gunicorn -c gunicorn_config.py app_local:app
