import unittest
from unittest.mock import patch, MagicMock
import json
import base64

# Add backend to python path for testing
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

import handler

class TestNewFeatures(unittest.TestCase):

    @patch('llm_service.analyze_transcript')
    @patch('database.save_note_item')
    def test_note_intent(self, mock_save_note, mock_analyze):
        mock_analyze.return_value = {
            "intent": "NOTE",
            "title": "the secret code for the vault is 9988."
        }
        mock_save_note.return_value = {
            "id": "test-note-id",
            "text": "the secret code for the vault is 9988.",
            "created_at": "2023-10-31T10:00:00Z"
        }

        event = {
            'httpMethod': 'POST',
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'transcript': 'Take a note that the secret code for the vault is 9988.'})
        }
        
        response = handler.handler(event, None)
        self.assertEqual(response['statusCode'], 200)
        
        body = json.loads(response['body'])
        self.assertEqual(body['type'], 'note')
        self.assertEqual(body['message'], 'Note saved')
        self.assertEqual(body['data']['id'], 'test-note-id')
        
        mock_analyze.assert_called_once()
        mock_save_note.assert_called_once_with("the secret code for the vault is 9988.")

    @patch('llm_service.analyze_transcript')
    def test_transport_intent(self, mock_analyze):
        mock_analyze.return_value = {
            "intent": "TRANSPORT",
            "destination": "Helsinki-Vantaa Airport"
        }

        event = {
            'httpMethod': 'POST',
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'transcript': 'How do I get to Helsinki-Vantaa Airport by train?'})
        }
        
        response = handler.handler(event, None)
        self.assertEqual(response['statusCode'], 200)
        
        body = json.loads(response['body'])
        self.assertEqual(body['type'], 'transport')
        self.assertEqual(body['message'], 'Directions ready')
        self.assertEqual(body['data']['destination'], 'Helsinki-Vantaa Airport')
        self.assertIn('deeplink', body['data'])

    @patch('llm_service.analyze_transcript')
    @patch('database.save_note_item')
    def test_finnish_note_intent(self, mock_save_note, mock_analyze):
        mock_analyze.return_value = {
            "intent": "NOTE",
            "title": "saunan lämpötila on 80 astetta"
        }
        mock_save_note.return_value = {
            "id": "test-finnish-note-id",
            "text": "saunan lämpötila on 80 astetta",
            "created_at": "2023-10-31T10:00:00Z"
        }

        event = {
            'httpMethod': 'POST',
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'transcript': 'Kirjoita muistiinpano että saunan lämpötila on 80 astetta.'})
        }
        
        response = handler.handler(event, None)
        self.assertEqual(response['statusCode'], 200)
        
        body = json.loads(response['body'])
        self.assertEqual(body['type'], 'note')
        self.assertEqual(body['message'], 'Note saved')
        
        mock_analyze.assert_called_once()

    @patch('database.delete_note_item')
    def test_delete_note(self, mock_delete_note):
        mock_delete_note.return_value = True

        event = {
            'httpMethod': 'DELETE',
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'id': 'test-note-id', 'type': 'note'})
        }
        
        response = handler.handler(event, None)
        self.assertEqual(response['statusCode'], 200)
        
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        mock_delete_note.assert_called_once_with('test-note-id')

if __name__ == '__main__':
    unittest.main()
