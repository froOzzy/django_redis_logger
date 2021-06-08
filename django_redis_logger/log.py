from redis import Redis

from .utils import _prepared_data_to_redis


class Log:
    """Класс для имитации объекта логов"""

    def __init__(self, **kwargs):
        """Метод инициализации класса"""
        self._id: int = kwargs['id']
        self._identifier: str = kwargs['identifier']
        self._r_con: Redis = redis_connection()
        self._pipeline = self._r_con.pipeline()

    def save(self):
        """Метод для сохранения лога"""
        self.dt_updated = datetime.datetime.now()  # noqa: W0201
        prepared_data = {
            name: getattr(self, name)
            for name
            in dir(self)
            if not name.startswith('__') and not name.startswith('_') and not callable(getattr(self, name))
        }
        self._pipeline.lset(
            name=self._identifier,
            index=self._id,
            value=json.dumps(_prepared_data_to_redis(**prepared_data), sort_keys=True)
        )
        self._pipeline.execute()
