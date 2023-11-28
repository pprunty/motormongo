import unittest
from unittest.mock import patch, MagicMock
from motormongo.abstracts.document import camel_to_snake, Document
import asyncio


class TestDocumentMethods(unittest.IsolatedAsyncioTestCase):

    async def test_camel_to_snake(self):
        self.assertEqual(camel_to_snake('CamelCaseTest'), 'camel_case_test')

    @patch('your_module.AsyncIOMotorClient')
    async def test_insert_one(self, mock_db_client):
        mock_collection = MagicMock()
        mock_db_client.return_value.__getitem__.return_value = mock_collection

        document = {'test_field': 'test_value'}
        mock_collection.insert_one.return_value = asyncio.Future()
        mock_collection.insert_one.return_value.set_result({'inserted_id': 'mock_id'})

        result = await Document.insert_one(document)
        self.assertIsNotNone(result)
        self.assertEqual(result.test_field, 'test_value')


if __name__ == '__main__':
    unittest.main()
