# ---------------------------------------------------------------------------- +
#region tests/test_p3_mvvm/test_cp_message_service.py
"""Tests for the p3_mvvm.cp_message_service module."""
#endregion tests/test_p3_mvvm/test_cp_message_service.py
# ---------------------------------------------------------------------------- +
#region    Imports
# python standard libraries
import pytest, logging, time
# third-party libraries
from splurge_pub_sub import PubSub, Message

# local libraries
from p3_mvvm.command_processor import CommandProcessor, is_CMD_OBJECT
from p3_mvvm.cp_message_service import CPMessageService
from p3_mvvm.mvvm_namespace import *
#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals
logger = logging.getLogger(__name__)
#endregion Globals
# ---------------------------------------------------------------------------- +
class TestCPMessageService:
    """Tests for the CPMessageService class."""
    def setup_method(self) -> None:
        """Setup for each test method."""
        self.cp_message_service = CPMessageService()

    def test_construction(self) -> None:
        """Test construction of CPMessageService."""
        logger.info(f"{self.test_construction.__name__}(): {self.test_construction.__doc__}")
        assert self.cp_message_service is not None, "CPMessageService instance should not be None."
        assert isinstance(self.cp_message_service, CPMessageService), "cp_message_service should be an instance of CPMessageService."

    def test_simple_msg(self) -> None:
        """Test sending and receiving a simple message."""
        logger.info(f"{self.test_simple_msg.__name__}(): {self.test_simple_msg.__doc__}")
        test_topic = "test_topic"
        test_payload = {"key": "value"}
        received_messages = []
        def subscriber_callback(msg: Message) -> None:
            received_messages.append(msg)
        self.cp_message_service.subscribe(test_topic, subscriber_callback)
        # test_message = Message(topic=test_topic, data=test_payload)
        self.cp_message_service.publish(test_topic, test_payload)
        time.sleep(0.1)
        assert len(received_messages) == 1, "Should have received one message."
        assert received_messages[0].topic == test_topic, "Received message topic should match."
        assert received_messages[0].data == test_payload, "Received message payload should match."

    def test_user_message(self) -> None:
        """Test sending and receiving a user message."""
        logger.info(f"{self.test_user_message.__name__}(): {self.test_user_message.__doc__}")
        received_messages = []
        def user_msg_callback(msg: Message) -> None:
            received_messages.append(msg)
        self.cp_message_service.subscribe_user_message(user_msg_callback)
        test_message = "This is a test user message."
        self.cp_message_service.user_output(test_message, tag='TEST')
        time.sleep(0.1)
        assert len(received_messages) == 1, "Should have received one user message."
        assert received_messages[0].topic == CP_USER_MSG_TOPIC, "Received user message topic should match."
        assert received_messages[0].data['msg'] == test_message, "Received user message content should match."
        assert received_messages[0].data['tag'] == 'TEST', "Received user message tag should match."