import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from client.http_client import HttpClient


class TestHttpClient(unittest.TestCase):

    @patch('client.http_client.requests.Session')
    def test_get_request(self, mock_session_class):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'{"result": "success"}'
        mock_response.json.return_value = {"result": "success"}
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        client = HttpClient("https://api.example.com")
        result = client.get("/users", params={"page": 1})

        mock_session.get.assert_called_once()
        call_args = mock_session.get.call_args
        self.assertEqual(call_args[0][0], "https://api.example.com/users")
        self.assertEqual(call_args[1]["params"], {"page": 1})
        self.assertEqual(result, {"result": "success"})

    @patch('client.http_client.requests.Session')
    def test_post_request(self, mock_session_class):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.content = b'{"id": 123}'
        mock_response.json.return_value = {"id": 123}
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session

        client = HttpClient("https://api.example.com")
        result = client.post("/users", data={"name": "test"})

        mock_session.post.assert_called_once()
        call_args = mock_session.post.call_args
        self.assertEqual(call_args[0][0], "https://api.example.com/users")
        self.assertEqual(call_args[1]["json"], {"name": "test"})
        self.assertEqual(result, {"id": 123})


if __name__ == '__main__':
    unittest.main()
