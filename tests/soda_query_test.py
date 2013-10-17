import random
import unittest
from soda import SodaQuery

class TestSoda(unittest.TestCase):

    def setUp(self):
        self.query = SodaQuery('http://data.sfgov.org/resource/rqzj-sfat.json')

    def test_where(self):
        self.assertEquals({'$where': 'foo==bar AND NOT bar==baz'}, self.query.where(foo='bar', bar__not_eq='baz')._SodaQuery__build_query())

    def test_select(self):
        self.assertEquals({'$select': 'title, description'}, self.query.select('title').select('description')._SodaQuery__build_query())

    def test_order(self):
        self.assertEquals({'$order': 'title'}, self.query.order('title')._SodaQuery__build_query())
        self.assertEquals({'$order': 'title DESC'}, self.query.order('-title')._SodaQuery__build_query())

    def test_limit(self):
        self.assertEquals({'$limit': 10}, self.query.limit(10)._SodaQuery__build_query())

    def test_offset(self):
        self.assertEquals({'$offset': 20}, self.query.offset(20)._SodaQuery__build_query())