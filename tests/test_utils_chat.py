import unittest
import tempfile
import shutil
import os
import sys

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/api-service/api/utils")),
)

from chat_utils import ChatHistoryManager


class TestChatHistoryManager(unittest.TestCase):

    def setUp(self):
        # set up a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.model_name = "test_model"
        self.manager = ChatHistoryManager(model=self.model_name, history_dir=self.test_dir)

    def tearDown(self):
        #clean up the temporary dir after tests
        shutil.rmtree(self.test_dir)

    def test_save_and_get_chat(self):
        # test saving and retrieving a chat
        session_id = "session_1"
        chat_id = "chat_1"
        chat_data = {
            "chat_id": chat_id,
            "messages": [{"message_id": 1, "text": "Hello"}],
        }

        self.manager.save_chat(chat_data, session_id=session_id)

        retrieved_chat = self.manager.get_chat(chat_id=chat_id, session_id=session_id)

        self.assertIsNotNone(retrieved_chat)
        self.assertEqual(retrieved_chat["chat_id"], chat_id)
        self.assertEqual(retrieved_chat["messages"], chat_data["messages"])

    def test_get_recent_chats(self):
        # test retrieving recent chats
        session_id = "session_1"
        chat_data_1 = {"chat_id": "chat_1", "messages": [], "dts": 1}
        chat_data_2 = {"chat_id": "chat_2", "messages": [], "dts": 2}

        self.manager.save_chat(chat_data_1, session_id=session_id)
        self.manager.save_chat(chat_data_2, session_id=session_id)

        recent_chats = self.manager.get_recent_chats(session_id=session_id, limit=1)

        self.assertEqual(len(recent_chats), 1)
        self.assertEqual(recent_chats[0]["chat_id"], "chat_2")

    def test_nonexistent_chat(self):
        # test trying to retrieve a nonexistent chat
        chat = self.manager.get_chat(chat_id="nonexistent", session_id="session_1")
        self.assertIsNone(chat)

if __name__ == "__main__":
    unittest.main()