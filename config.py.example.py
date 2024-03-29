# coding=utf-8

DB_config = {
    # 'db_type': 'mongodb',
    'db_type': 'mysql',

    'mysql': {
        'host': 'localhost',
        'port': 8889,
        'user': 'root',
        'password': 'root',
        'charset': 'utf8',
    },
    'redis': {
        'host': 'localhost',
        'port': 6379,
        'password': '',
        'db': 1,
    },
    'mongodb':{
        'host': 'localhost',
        'port': 27017,
        'username': '',
        'password': '',
    }
}

database = 'py_proxy'
free_ipproxy_table = 'free_ipproxy'
httpbin_table = 'httpbin'

data_port = 8000
