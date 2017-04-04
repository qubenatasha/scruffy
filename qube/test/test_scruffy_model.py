#!/usr/bin/python
"""
Add docstring here
"""
import time
import unittest

import mock

from mock import patch
import mongomock


class TestScruffyModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("before class")

    @mock.patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def test_create_scruffy_model(self):
        from qube.src.models.scruffy import Scruffy
        scruffy_data = Scruffy(name='testname')
        scruffy_data.tenantId = "23432523452345"
        scruffy_data.orgId = "987656789765670"
        scruffy_data.createdBy = "1009009009988"
        scruffy_data.modifiedBy = "1009009009988"
        scruffy_data.createDate = str(int(time.time()))
        scruffy_data.modifiedDate = str(int(time.time()))
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            scruffy_data.save()
            self.assertIsNotNone(scruffy_data.mongo_id)
            scruffy_data.remove()

    @classmethod
    def tearDownClass(cls):
        print("After class")


if __name__ == '__main__':
    unittest.main()
