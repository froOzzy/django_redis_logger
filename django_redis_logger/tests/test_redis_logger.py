"""Тесты для Redis Logger"""

import datetime

from django.test import TestCase

from ..logger import Logger


class RedisLoggerTestCase(TestCase):
    """Класс для тестирования логгера Redis"""

    @classmethod
    def setUpTestData(cls):
        """Класс инициализации тестов"""
        cls.identifier = 'test'
        cls.logger = Logger(cls.identifier)
        cls.now = datetime.datetime.now()

    def test_correct_type(self):
        """Тест на проверку корректности типов"""
        self.logger.all().delete()
        self.assertListEqual(list(self.logger.all()), [])
        self.logger.create(
            test_int=1,
            test_float=0.1,
            test_bool=True,
            test_str='str',
            test_datetime=self.now,
            test_date=self.now.date(),
            test_time=self.now.time()
        )
        log = self.logger.all()[0]
        self.assertTrue(isinstance(log.test_int, int))
        self.assertTrue(isinstance(log.test_float, float))
        self.assertTrue(isinstance(log.test_bool, bool))
        self.assertTrue(isinstance(log.test_str, str))
        self.assertTrue(isinstance(log.test_datetime, datetime.datetime))
        self.assertTrue(isinstance(log.test_date, datetime.date))
        self.assertTrue(isinstance(log.test_time, datetime.time))

    def test_filter(self):
        """Проверка фильтрации логов"""
        self.logger.all().delete()
        self.assertListEqual(list(self.logger.all()), [])
        self.logger.create(
            test_field=1
        )
        self.logger.create(
            test_field=2
        )
        log = self.logger.filter(test_field=1).first()
        self.assertTrue(log.test_field == 1)

    def test_exclude(self):
        """Проверка исключения логгов"""
        self.logger.all().delete()
        self.assertListEqual(list(self.logger.all()), [])
        self.logger.create(
            test_field=1
        )
        self.logger.create(
            test_field=2
        )
        log = self.logger.exclude(test_field=1).first()
        self.assertTrue(log.test_field == 2)

    def test_exists(self):
        """Проверка функции существования логов"""
        self.logger.all().delete()
        self.assertListEqual(list(self.logger.all()), [])
        self.logger.create(
            test_field=1
        )
        self.assertTrue(self.logger.exists())

    def test_querylog_order_by(self):
        """Проверка сортировки логов"""
        self.logger.all().delete()
        self.assertListEqual(list(self.logger.all()), [])
        self.logger.create(
            test_field=0
        )
        self.logger.create(
            test_field=1
        )
        logs = self.logger.all().order_by('test_field')
        for index, log in enumerate(logs):
            self.assertTrue(log.test_field == index)

        logs = self.logger.all().order_by('-test_field')
        self.assertTrue(logs[0].test_field == 1)
        self.assertTrue(logs[1].test_field == 0)

    def test_querylog_count(self):
        """Проверка сортировки логов"""
        self.logger.all().delete()
        self.assertListEqual(list(self.logger.all()), [])
        self.logger.create(
            test_field=0
        )
        self.logger.create(
            test_field=1
        )
        self.assertTrue(self.logger.all().count() == 2)

    def test_querylog_first(self):
        """Проверка получения первого элемента"""
        self.logger.all().delete()
        self.assertListEqual(list(self.logger.all()), [])
        self.logger.create(
            test_field=0
        )
        self.logger.create(
            test_field=1
        )
        self.assertTrue(self.logger.all().first() is not None)
