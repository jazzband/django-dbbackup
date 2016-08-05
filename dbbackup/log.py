DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
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
        'dbbackup': {
            'handlers': ['console'],
            'level': 'DEBUG'
        },
        'dbbackup.storage': {
            'handlers': ['console'],
            'level': 'DEBUG'
        }
    }
}
