DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'dbbackup.console': {
            'formatter': 'base',
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        }
    },
    'filters': {},
    'formatters': {
        'base': {'format': '%(message)s'},
        'simple': {'format': '%(levelname)s %(message)s'}
    },
    'loggers': {
        'dbbackup.storage': {
            'handlers': ['dbbackup.console'],
            'level': 'INFO'
        },
        'dbbackup.command': {
            'handlers': ['dbbackup.console'],
            'level': 'INFO'
        }
    }
}
