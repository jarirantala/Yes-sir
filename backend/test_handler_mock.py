import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import handler

class TestHandler(unittest.TestCase):

    @patch('handler.llm_service.analyze_transcript')
    @patch('handler.database.save_todo_item')
    def test_todo_flow(self, mock_save, mock_analyze):
        # Mock LLM response
        mock_analyze.return_value = {
            "intent": "TODO",
            "title": "Buy milk",
            "priority": "high"
        }
        
        # Mock DB response
        mock_save.return_value = {
            "id": "123",
            "text": "Buy milk",
            "priority": "high",
            "status": "pending"
        }

        # Mock Event
        event = {
            "body": json.dumps({"transcript": "Remind me to buy milk urgent"}),
            "headers": {"content-type": "application/json"}
        }

        response = handler.handler(event, None)
        
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['type'], 'todo')
        self.assertEqual(body['parsed_data']['intent'], 'TODO')
        self.assertEqual(body['data']['id'], '123')
        
    @patch('handler.llm_service.analyze_transcript')
    def test_meeting_flow(self, mock_analyze):
        # Mock LLM response
        mock_analyze.return_value = {
            "intent": "MEETING",
            "title": "Sync",
            "datetime": "2023-10-30T10:00:00",
            "duration": 30
        }
        
        event = {
            "body": json.dumps({
                "transcript": "Sync tomorrow", 
                "email": "test@example.com"
            }),
            "headers": {"content-type": "application/json"}
        }

        response = handler.handler(event, None)
        
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['type'], 'meeting')
        self.assertEqual(body['parsed_data']['intent'], 'MEETING')

if __name__ == '__main__':
    unittest.main()
