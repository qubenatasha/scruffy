#!/usr/bin/python
"""
Add docstring here
"""
import os
import time
import unittest

import mock
from mock import patch
import mongomock


with patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient):
    os.environ['SCRUFFY_MONGOALCHEMY_CONNECTION_STRING'] = ''
    os.environ['SCRUFFY_MONGOALCHEMY_SERVER'] = ''
    os.environ['SCRUFFY_MONGOALCHEMY_PORT'] = ''
    os.environ['SCRUFFY_MONGOALCHEMY_DATABASE'] = ''

    from qube.src.models.scruffy import Scruffy
    from qube.src.services.scruffyservice import ScruffyService
    from qube.src.commons.context import AuthContext
    from qube.src.commons.error import ErrorCodes, ScruffyServiceError


class TestScruffyService(unittest.TestCase):
    @mock.patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def setUp(self):
        context = AuthContext("23432523452345", "tenantname",
                              "987656789765670", "orgname", "1009009009988",
                              "username", False)
        self.scruffyService = ScruffyService(context)
        self.scruffy_api_model = self.createTestModelData()
        self.scruffy_data = self.setupDatabaseRecords(self.scruffy_api_model)
        self.scruffy_someoneelses = \
            self.setupDatabaseRecords(self.scruffy_api_model)
        self.scruffy_someoneelses.tenantId = "123432523452345"
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            self.scruffy_someoneelses.save()
        self.scruffy_api_model_put_description \
            = self.createTestModelDataDescription()
        self.test_data_collection = [self.scruffy_data]

    def tearDown(self):
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            for item in self.test_data_collection:
                item.remove()
            self.scruffy_data.remove()

    def createTestModelData(self):
        return {'name': 'test123123124'}

    def createTestModelDataDescription(self):
        return {'description': 'test123123124'}

    @mock.patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def setupDatabaseRecords(self, scruffy_api_model):
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            scruffy_data = Scruffy(name='test_record')
            for key in scruffy_api_model:
                scruffy_data.__setattr__(key, scruffy_api_model[key])

            scruffy_data.description = 'my short description'
            scruffy_data.tenantId = "23432523452345"
            scruffy_data.orgId = "987656789765670"
            scruffy_data.createdBy = "1009009009988"
            scruffy_data.modifiedBy = "1009009009988"
            scruffy_data.createDate = str(int(time.time()))
            scruffy_data.modifiedDate = str(int(time.time()))
            scruffy_data.save()
            return scruffy_data

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_post_scruffy(self, *args, **kwargs):
        result = self.scruffyService.save(self.scruffy_api_model)
        self.assertTrue(result['id'] is not None)
        self.assertTrue(result['name'] == self.scruffy_api_model['name'])
        Scruffy.query.get(result['id']).remove()

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_put_scruffy(self, *args, **kwargs):
        self.scruffy_api_model['name'] = 'modified for put'
        id_to_find = str(self.scruffy_data.mongo_id)
        result = self.scruffyService.update(
            self.scruffy_api_model, id_to_find)
        self.assertTrue(result['id'] == str(id_to_find))
        self.assertTrue(result['name'] == self.scruffy_api_model['name'])

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_put_scruffy_description(self, *args, **kwargs):
        self.scruffy_api_model_put_description['description'] =\
            'modified for put'
        id_to_find = str(self.scruffy_data.mongo_id)
        result = self.scruffyService.update(
            self.scruffy_api_model_put_description, id_to_find)
        self.assertTrue(result['id'] == str(id_to_find))
        self.assertTrue(result['description'] ==
                        self.scruffy_api_model_put_description['description'])

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_get_scruffy_item(self, *args, **kwargs):
        id_to_find = str(self.scruffy_data.mongo_id)
        result = self.scruffyService.find_by_id(id_to_find)
        self.assertTrue(result['id'] == str(id_to_find))

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_get_scruffy_item_invalid(self, *args, **kwargs):
        id_to_find = '123notexist'
        with self.assertRaises(ScruffyServiceError):
            self.scruffyService.find_by_id(id_to_find)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_get_scruffy_list(self, *args, **kwargs):
        result_collection = self.scruffyService.get_all()
        self.assertTrue(len(result_collection) == 1,
                        "Expected result 1 but got {} ".
                        format(str(len(result_collection))))
        self.assertTrue(result_collection[0]['id'] ==
                        str(self.scruffy_data.mongo_id))

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_delete_toolchain_not_system_user(self, *args, **kwargs):
        id_to_delete = str(self.scruffy_data.mongo_id)
        with self.assertRaises(ScruffyServiceError) as ex:
            self.scruffyService.delete(id_to_delete)
        self.assertEquals(ex.exception.errors, ErrorCodes.NOT_ALLOWED)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_delete_toolchain_by_system_user(self, *args, **kwargs):
        id_to_delete = str(self.scruffy_data.mongo_id)
        self.scruffyService.auth_context.is_system_user = True
        self.scruffyService.delete(id_to_delete)
        with self.assertRaises(ScruffyServiceError) as ex:
            self.scruffyService.find_by_id(id_to_delete)
        self.assertEquals(ex.exception.errors, ErrorCodes.NOT_FOUND)
        self.scruffyService.auth_context.is_system_user = False

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_delete_toolchain_item_someoneelse(self, *args, **kwargs):
        id_to_delete = str(self.scruffy_someoneelses.mongo_id)
        with self.assertRaises(ScruffyServiceError):
            self.scruffyService.delete(id_to_delete)
