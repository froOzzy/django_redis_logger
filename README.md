# django_redis_logger

Helps you conveniently store logs in redis.

## Settings

To configure it, it is enough to specify the data for connecting to redis in local_settings:

```python
DEFAULT_REDIS = {
    'host': '127.0.0.1',
    'port': 6379,
    'password': None,
    'max_connections_for_pool': 1000
}
```

## How to use it

To use this module, you need to import the Logger class from logger and initialize the class object with the ID:

```python
from django_redis_logger.logger import Logger

logger = Logger('test')
logger.create(my_field=1)
print(logger.all())
```

## Methods

This logger supports similar standard Django methods. In the future, they will be expanded to a full-fledged ORM. 

__Important!__ This module does not aim to replace Django ORM, there is another module for this purpose [rom](https://github.com/josiahcarlson/rom).
