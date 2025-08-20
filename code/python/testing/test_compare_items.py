#!/usr/bin/env python3
"""
Test suite for the CompareItemsHandler method.
"""

import asyncio
import sys
import os
import unittest
from unittest.mock import Mock, patch, AsyncMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from methods.compare_items import CompareItemsHandler

class TestCompareItemsHandler(unittest.TestCase):

    def setUp(self):
        # Create a mock for the main handler
        self.mock_handler = Mock()
        self.mock_handler.site = "test_site"
        self.mock_handler.item_type = "test_item"
        self.mock_handler.query_params = {}
        # Make the send_message method an async mock
        self.mock_handler.send_message = AsyncMock()

    @patch('methods.compare_items.search', new_callable=AsyncMock)
    def test_no_items_found(self, mock_search):
        # Scenario: No items found for either item1 or item2

        # Configure the mock to return no results
        mock_search.return_value = []

        # Initialize the handler
        params = {'item1_name': 'item1', 'item2_name': 'item2'}
        handler = CompareItemsHandler(params, self.mock_handler)

        # Run the do() method
        asyncio.run(handler.do())

        # Assert that send_message was called
        self.mock_handler.send_message.assert_called_once()

        # Get the message that was sent
        sent_message = self.mock_handler.send_message.call_args[0][0]

        # Assertions on the message content
        self.assertEqual(sent_message['message_type'], 'compare_items')
        self.assertEqual(sent_message['item1']['name'], 'item1')
        self.assertEqual(sent_message['item1']['found'], False)
        self.assertEqual(sent_message['item2']['name'], 'item2')
        self.assertEqual(sent_message['item2']['found'], False)

    @patch('methods.compare_items.search', new_callable=AsyncMock)
    @patch('methods.compare_items.ask_llm', new_callable=AsyncMock)
    def test_one_item_found(self, mock_ask_llm, mock_search):
        # Scenario: item1 is found, item2 is not

        # Mock search to return a candidate for item1 and nothing for item2
        def search_side_effect(item_name, *args, **kwargs):
            if item_name == 'item1':
                return [('url1', '{}', 'item1_found', 'site')]
            return []
        mock_search.side_effect = search_side_effect

        # Mock LLM to return a high score for item1
        mock_ask_llm.return_value = {"score": 90}

        # Initialize the handler
        params = {'item1_name': 'item1', 'item2_name': 'item2'}
        handler = CompareItemsHandler(params, self.mock_handler)
        handler.found_items = {'item1': {'score': 90, 'item': ('url1', '{}', 'item1_found', 'site')}}

        # Run the do() method
        asyncio.run(handler.do())

        # Assert that send_message was called
        self.mock_handler.send_message.assert_called_once()

        # Get the message that was sent
        sent_message = self.mock_handler.send_message.call_args[0][0]

        # Assertions on the message content
        self.assertEqual(sent_message['message_type'], 'compare_items')
        self.assertEqual(sent_message['item1']['name'], 'item1')
        self.assertEqual(sent_message['item1']['found'], True)
        self.assertEqual(sent_message['item2']['name'], 'item2')
        self.assertEqual(sent_message['item2']['found'], False)

if __name__ == '__main__':
    # Run tests
    unittest.main()
