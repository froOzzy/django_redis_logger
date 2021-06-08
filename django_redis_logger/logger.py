import json
import datetime

from typing import List

from .log import Log
from .querylog import QueryLog
from .pool import redis_connection
from .utils import to_seconds, _prepared_data_to_redis


DEFAULT_TIME_FORMAT = '%H:%M:%S'
DEFAULT_DATE_FORMAT = '%Y-%m-%d'
DEFAULT_DATE_TIME_FORMAT = '{} {}'.format(DEFAULT_DATE_FORMAT, DEFAULT_TIME_FORMAT)


class Logger:
    """
    Класс для логгирования логов в redis.
    Данные логи НЕ должны быть слишком важными, во избежании их потери
    """

    START_INDEX = 0
    EXPIRED_DAYS = 3
    ICONTAINS = '__icontains'
    GT = '__gt'
    GTE = '__gte'
    LT = '__lt'
    LTE = '__lte'
    UNDERSCORE = '__'

    def __init__(self, identifier: str, quantity: int = 100):
        """
        Инициализация класса
        :param identifier: идентификатор в redis
        :param quantity: количество логов в списке
        """
        self.identifier = identifier
        self.quantity = quantity
        self._r_con = redis_connection()
        self._pipeline = self._r_con.pipeline()
        self._now = datetime.datetime.now()
        self._format_now = self._now.strftime(DEFAULT_DATE_TIME_FORMAT)

    def _trim_log(self, is_pipeline: bool = False):
        """
        Обрезает старые логи
        :param is_pipeline: выполнение запроса к redis через pipeline
        """
        if is_pipeline:
            self._pipeline.ltrim(self.identifier, self.START_INDEX, self.quantity)
        else:
            self._r_con.ltrim(self.identifier, self.START_INDEX, self.quantity)

    def create(self, **kwargs):
        """
        Метод для записи лога в redis. Параметры должны быть простых типов!
        Лог хранится в формате json
        :param kwargs: параметры которые нужно залоггировать
        """
        if not kwargs:
            raise ValueError

        prepared_log = _prepared_data_to_redis(**kwargs)
        prepared_log['dt_created'] = {
            'type': 'datetime',
            'value': self._format_now
        }
        prepared_log['dt_updated'] = {
            'type': 'datetime',
            'value': self._format_now
        }
        self._pipeline.lpush(self.identifier, json.dumps(prepared_log, sort_keys=True))
        self._pipeline.expire(name=self.identifier, time=to_seconds(days=self.EXPIRED_DAYS))
        self._trim_log(is_pipeline=True)
        self._pipeline.execute()

    def all(self) -> QueryLog:  # noqa: A003
        """
        Чтение логов из redis
        :return: список логов
        """
        logs = []
        untrained_logs = self._r_con.lrange(self.identifier, self.START_INDEX, self.quantity)
        for index, untrained_log in enumerate(untrained_logs):
            prepared_log = json.loads(untrained_log)
            log = Log(id=index, identifier=self.identifier)
            for param_name in prepared_log:
                param_type = prepared_log[param_name]['type']
                param_value = prepared_log[param_name]['value']
                if param_type == 'datetime':
                    setattr(log, param_name, datetime.datetime.strptime(param_value, DEFAULT_DATE_TIME_FORMAT))
                    continue

                if param_type == 'date':
                    setattr(log, param_name, datetime.datetime.strptime(param_value, DEFAULT_DATE_FORMAT).date())
                    continue

                if param_type == 'time':
                    setattr(log, param_name, datetime.datetime.strptime(param_value, DEFAULT_TIME_FORMAT).time())
                    continue

                if param_type == 'bool':
                    setattr(log, param_name, bool(param_value))
                    continue

                if param_type == 'int':
                    setattr(log, param_name, int(param_value))
                    continue

                if param_type == 'float':
                    setattr(log, param_name, float(param_value))
                    continue

                if param_type == 'str':
                    setattr(log, param_name, str(param_value))
                    continue

                if param_type == 'none':
                    setattr(log, param_name, None)
                    continue

                raise TypeError

            logs.append(log)

        return QueryLog(*logs, identifier=self.identifier)

    def _check_conditions(self, instance, *args, is_exclude: bool = False, **kwargs):
        """
        Генератор для условий фильтрации
        todo: расширить со временем
        :param log: объект класса Log
        :param kwargs: параметры фильтрации
        :return: генератор
        """
        def additional_filter(obj, name, value, result):  # noqa: R0911
            """
            Метод для фильтрации дополнительными фильтрами
            :param obj: объект Log
            :param name: название параметра
            :param value: значение параметра
            :param result: список исходных состояний выполнения условий
            :return: выходный список состояний выполнения условий
            """
            additional_filter_start = name.find('__')
            clean_name = name[:additional_filter_start] if additional_filter_start != -1 else name
            instance_value = getattr(obj, clean_name, None)
            if isinstance(instance_value, str):
                if name.endswith(self.ICONTAINS):
                    value = value.lower()
                    instance_value = instance_value.lower()
                    result.append(value in instance_value)
                    return result

                if self.UNDERSCORE not in name:
                    result.append(value in instance_value)
                    return result

                raise TypeError

            if isinstance(instance_value, bool):
                if self.UNDERSCORE not in name:
                    result.append(value == instance_value)
                    return result

                raise TypeError

            if isinstance(instance_value, int):
                if self.UNDERSCORE not in name:
                    result.append(value == instance_value)
                    return result

                raise TypeError

            if isinstance(instance_value, float):
                if self.UNDERSCORE not in name:
                    result.append(value == instance_value)
                    return result

                raise TypeError

            if instance_value is None:
                if self.UNDERSCORE not in name:
                    result.append(value == instance_value)
                    return result

                raise TypeError

            if isinstance(instance_value, (datetime.date, datetime.datetime, datetime.time)):
                if name.endswith(self.GT):
                    result.append(value > instance_value)
                    return result

                if name.endswith(self.GTE):
                    result.append(value >= instance_value)
                    return result

                if name.endswith(self.LT):
                    result.append(value < instance_value)
                    return result

                if name.endswith(self.LTE):
                    result.append(value <= instance_value)
                    return result

                if self.UNDERSCORE not in param_name:
                    result.append(value == instance_value)
                    return result

            raise TypeError

        and_condition: List[bool] = []
        for item in args:
            children = item.children
            or_condition: List[bool] = []
            for param_name, param_value in children:
                or_condition = additional_filter(instance, param_name, param_value, or_condition)

            and_condition.append(any(or_condition))

        for param_name, param_value in kwargs.items():
            and_condition = additional_filter(instance, param_name, param_value, and_condition)

        return not all(and_condition) if is_exclude else all(and_condition)

    def filter(self, *args, **kwargs) -> QueryLog:  # noqa: A003
        """
        Фильтрация логов по необходимым параметрам
        Поддерживает условия только через AND
        :param kwargs: параметры для фильтрации
        :return: список логов
        """
        logs = self.all()
        return QueryLog(
            *[log for log in logs if self._check_conditions(log, *args, is_exclude=False, **kwargs)],
            identifier=self.identifier
        )

    def exclude(self, *args, **kwargs) -> QueryLog:
        """
        Фильтрация логов по необходимым параметрам
        Поддерживает условия только через AND
        :param kwargs: параметры для фильтрации
        :return: список логов
        """
        logs = self.all()
        return QueryLog(
            *[log for log in logs if self._check_conditions(log, *args, is_exclude=True, **kwargs)],
            identifier=self.identifier
        )

    def exists(self):
        """Метод для проверки наличия логов в Redis"""
        return bool(self._r_con.llen(self.identifier))
