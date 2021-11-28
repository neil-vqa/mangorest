LOG_HANDLERS = ["console"]

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "{levelname} | {module} | {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "level": "DEBUG",
        },
    },
    "loggers": {},
    "root": {"level": "INFO", "handlers": LOG_HANDLERS},
}
