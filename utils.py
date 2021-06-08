import datetime


def to_seconds(days=0, minutes=0, hours=0, weeks=0):
    return int(datetime.timedelta(
        days=days,
        minutes=minutes,
        hours=hours,
        weeks=weeks
    ).total_seconds())


def _prepared_data_to_redis(**kwargs):
    """
    Метод для подготовки данных к сохранению в Redis
    :param kwargs: данные
    :return: подготовленный список параметров
    """
    prepared_log = {}
    for param_name in kwargs:
        prepared_log[param_name] = {}
        param_value = kwargs[param_name]
        if isinstance(param_value, datetime.datetime):
            prepared_log[param_name]['type'] = 'datetime'
            prepared_log[param_name]['value'] = param_value.strftime(DEFAULT_DATE_TIME_FORMAT)
            continue

        if isinstance(param_value, datetime.date):
            prepared_log[param_name]['type'] = 'date'
            prepared_log[param_name]['value'] = param_value.strftime(DEFAULT_DATE_FORMAT)
            continue

        if isinstance(param_value, datetime.time):
            prepared_log[param_name]['type'] = 'time'
            prepared_log[param_name]['value'] = param_value.strftime(DEFAULT_TIME_FORMAT)
            continue

        if isinstance(param_value, bool):
            prepared_log[param_name]['type'] = 'bool'
            prepared_log[param_name]['value'] = param_value
            continue

        if isinstance(param_value, int):
            prepared_log[param_name]['type'] = 'int'
            prepared_log[param_name]['value'] = param_value
            continue

        if isinstance(param_value, float):
            prepared_log[param_name]['type'] = 'float'
            prepared_log[param_name]['value'] = param_value
            continue

        if isinstance(param_value, str):
            prepared_log[param_name]['type'] = 'str'
            prepared_log[param_name]['value'] = param_value
            continue

        if param_value is None:
            prepared_log[param_name]['type'] = 'none'
            prepared_log[param_name]['value'] = param_value
            continue

        raise TypeError

    return prepared_log
