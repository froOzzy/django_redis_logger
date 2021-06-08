from redis import Redis


class QueryLog:
    """Класс для имитации списка объектов логов"""

    _count_remove_item: int = 0
    _deleted = '__DELETED__'

    def __init__(self, *args, **kwargs):
        """Метод инициализации класса"""
        self.items = list(args)
        self._identifier: str = kwargs['identifier']
        self._r_con: Redis = redis_connection()
        self._pipeline = self._r_con.pipeline()

    def __iter__(self):
        """Метод для итерации"""
        yield from self.items

    def __len__(self):
        """Метод для получения длины"""
        return len(self.items)

    def __getitem__(self, index):
        """Метод для использования slice"""
        return self.items[index]

    def first(self):
        """Метод для получения первого элемента"""
        return self.items[0] if self.items else None

    def exists(self):
        """Метод для проверки наличия элементов"""
        return len(self.items) > 0

    def delete(self):
        """Метод для удаления объектов из Redis"""
        for item in self.items:
            self._pipeline.lset(self._identifier, item._id, self._deleted)  # noqa: W0212

        self._pipeline.lrem(self._identifier, self._count_remove_item, self._deleted)
        self._pipeline.execute()

    def count(self):
        """Метод для получения количества элементов в списке"""
        if self.items:
            return len(self.items)

        return 0

    def order_by(self, *args):
        """
        Метод для сортировки объектов логов
        :param args: параметры сортировки
        """
        for param_name in args:
            clean_param_name = param_name.replace('-', '')
            self.items = sorted(self.items, key=lambda x: getattr(x, clean_param_name))  # noqa: W0640
            if '-' in param_name:
                self.items = list(reversed(self.items))

        return self