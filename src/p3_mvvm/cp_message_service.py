# ---------------------------------------------------------------------------- +
#region cp_message_service.py module
""" cp_message_service.py implements the class CPMessageService.
"""
#endregion cp_message_service.py module
#------------------------------------------------------------------------------+
#region Imports
# python standard library modules and packages
import logging, queue
from typing import Optional
# third-party modules and packages
import p3_utils as p3u, p3logging as p3l
from splurge_pub_sub import PubSub, Message, Callback
# local modules and packages
from budman_namespace import BDMSingletonMeta
from .mvvm_namespace import *

#endregion Imports
# ---------------------------------------------------------------------------- +
#region Globals and Constants
logger = logging.getLogger(__name__)  # create logger for the module
#endregion Globals and Constants
# ---------------------------------------------------------------------------- +

# ---------------------------------------------------------------------------- +
#region   cp_user_message_callback decorator
def cp_user_message_callback(func: Callback) -> Callback:
    """Decorator to mark a function as a PubSub callback for user messages.
    
        User messages are intended to be shown to the user in some fashion. The
        decoratof converts the splurge_pub_sub.Message to a CPUserOutputMessage
        before passing it to the decorated function.
    """
    def wrapper(*args, **kwargs) -> None:
        # Expecting first argument to be a Message
        message: Message = args[0]
        msg: str = message.data.get('message', '')
        tag: str = message.data.get('tag', 'INFO')
        obj: CPUserOutputMessage = CPUserOutputMessage(message=msg, tag=tag)
        return func(obj)
    return wrapper
#endregion cp_user_message_callback decorator
# ---------------------------------------------------------------------------- +
#region   cp_cmd_result_message_callback decorator
def cp_cmd_result_message_callback(func: Callback) -> Callback:
    """Decorator to mark a function as a PubSub callback for command result messages.
    
        Command result messages are intended to convey the result of a command 
        execution. The decorator converts the splurge_pub_sub.Message to a 
        CMD_RESULT_TYPE before passing it to the decorated function.
    """
    def wrapper(*args, **kwargs) -> None:
        # Expecting first argument to be a Message
        message: Message = args[0]
        cmd_result: CMD_RESULT_TYPE = message.data.get('message', '')
        return func(cmd_result)
    return wrapper
#endregion cp_cmd_result_message_callback decorator
# ---------------------------------------------------------------------------- +

# ---------------------------------------------------------------------------- +
#region   CPUserOutputMessage class
class CPUserOutputMessage(Message):
    # ------------------------------------------------------------------------ +
    #region    CPUserOutputMessage class Intrinsics
    # ------------------------------------------------------------------------ +
    #region    CPUserOutputMessage doc string
    """ CPUserOutputMessage class.
        The CPUserOutputMessage class implements a message structure for
        user messages for the Command Processor.

        splurge_pub_sub.Message is leveraged to handle messaging in a 
        thread-safe fashion, but the cp_message_service does not expose the
        splurge_pub_sub API directly to clients.
    """
    #endregion CPUserOutputMessage doc string
    # ------------------------------------------------------------------------ +
    #region    __init__() 
    def __init__(self, message: Dict[str,Any], tag: str = 'INFO') -> None:
        super().__init__(topic=CP_USER_MSG_TOPIC, data={'message': message, 'tag': tag})
    #endregion  __init__()
    # ------------------------------------------------------------------------ +
    #region    CPUserOutputMessage class Properties
    @property
    def message(self) -> str:
        """Get the user message."""
        return self.data.get('message', '')
    @property
    def tag(self) -> str:
        """Get the message tag."""
        return self.data.get('tag', 'INFO')
    @property
    def type(self) -> str:
        """Get the message topic."""
        return self.topic
    #endregion CPUserOutputMessage class Properties
    # ------------------------------------------------------------------------ +
    #endregion CPUserOutputMessage class Intrinsics
    # ------------------------------------------------------------------------ +
#endregion   CPUserOutputMessage class
# ---------------------------------------------------------------------------- +

# ---------------------------------------------------------------------------- +
#region   CPMessageService class
class CPMessageService(PubSub, metaclass=BDMSingletonMeta):
    # ------------------------------------------------------------------------ +
    #region    class methods
    @classmethod
    def getCPMessageService(cls) -> 'CPMessageService':
        """Get the singleton instance of CPMessageService."""
        return cls()
    #endregion class methods
    # ------------------------------------------------------------------------ +
    #region    CPMessageService class Intrinsics
    # ------------------------------------------------------------------------ +
    #region    CPMessageService doc string
    """ CPMessageService class.
        The CPMessageService class implements a singleton message service for
        the Command Processor.
    """
    #endregion CPMessageService doc string
    # ------------------------------------------------------------------------ +
    #region    __init__() 
    def __init__(self) -> None:
        super().__init__()
        self.verbose_log: bool = False
    #endregion  __init__()
    # ------------------------------------------------------------------------ +
    #endregion CPMessageService class Intrinsics
    # ------------------------------------------------------------------------ +

    # ------------------------------------------------------------------------ +
    #region    CPMessageService class Methods
    # ------------------------------------------------------------------------ +
    #region CP_USER_MSG_TOPIC Methods
    def subscribe_user_message(self, callback: Callback) -> str:
        """Subscribe to user messages."""
        return self.subscribe(CP_USER_MSG_TOPIC, callback)

    def user_message(self, message: str, tag: str = CP_INFO) -> None:
        """Publish a user message."""
        self.publish(topic=CP_USER_MSG_TOPIC, 
                      data={'message': message, 'tag': tag})

    def user_info_message(self, message: str, log: bool = True) -> None:
        """Publish a user INFO message."""
        self.user_message(message, CP_INFO)
        if log:
            logger.info(message)

    def user_warning_message(self, message: str, log: bool = True) -> None:
        """Publish a user WARNING message."""
        self.user_message(message, CP_WARNING)
        if log:
            logger.warning(message)
            
    def user_error_message(self, message: str, log: bool = True) -> None:
        """Publish a user ERROR message."""
        self.user_message(message, CP_ERROR)
        if log:
            logger.error(message)

    def user_debug_message(self, message: str, log: bool = True) -> None:
        """Publish a user DEBUG message."""
        self.user_message(message, CP_DEBUG)
        if log:
            logger.debug(message)

    def user_verbose_message(self, message: str, log: bool = True) -> None:
        """Publish a user VERBOSE message."""
        if self.verbose_log:    
            self.user_message(message, CP_VERBOSE)
        if log:
            logger.debug(message)
    #endregion CP_USER_MSG_TOPIC Methods
    # ------------------------------------------------------------------------ +
    #region CP_CMD_RESULT_TOPIC Methods
    def subscribe_cmd_result_message(self, callback: Callback) -> str:
        """Subscribe to command result messages."""
        return self.subscribe(CP_CMD_RESULT_TOPIC, callback)    

    def publish_cmd_result(self, cmd_result: CMD_RESULT_TYPE) -> None:
        """Publish a command result message."""
        self.publish(topic=CP_CMD_RESULT_TOPIC, 
                      data={'message': cmd_result})

    #endregion CP_CMD_RESULT_TOPIC Methods
    # ------------------------------------------------------------------------ +
    #endregion CPMessageService class Methods
    # ------------------------------------------------------------------------ +
#endregion    CPMessageService class Methods
# ---------------------------------------------------------------------------- +

# ---------------------------------------------------------------------------- +
#region cp_msg_svc variable - reference to Singleton CPMessageService
cp_msg_svc: CPMessageService = CPMessageService()
#endregion cp_msg_svc variable - reference to Singleton CPMessageService
# ---------------------------------------------------------------------------- +
#region cp_print_user_message() function - sample callback
@cp_user_message_callback
def cp_print_user_message(message: CPUserOutputMessage) -> None:
    """Sample user message callback."""
    print(f"[{message.tag:>7}]: {message.message}")

#endregion cp_print_user_message() function - sample callback
# ---------------------------------------------------------------------------- +
#region user_message functions
def cp_subscribe_user_message(callback: Callback) -> str:
    """Subscribe to user messages."""
    return cp_msg_svc.subscribe(CP_USER_MSG_TOPIC, callback)

def cp_user_message(message: str, tag: str = CP_INFO) -> None:
    """Publish a user message."""
    cp_msg_svc.publish(topic=CP_USER_MSG_TOPIC, 
                    data={'message': message, 'tag': tag})

def cp_user_info_message(message: str, log: bool = True) -> None:
    """Publish a user INFO message."""
    cp_msg_svc.user_message(message, CP_INFO)
    if log:
        logger.info(message)

def cp_user_warning_message(message: str, log: bool = True) -> None:
    """Publish a user WARNING message."""
    cp_msg_svc.user_message(message, CP_WARNING)
    if log:
        logger.warning(message)
        
def cp_user_error_message(message: str, log: bool = True) -> None:
    """Publish a user ERROR message."""
    cp_msg_svc.user_message(message, CP_ERROR)
    if log:
        logger.error(message)

def cp_user_debug_message(message: str, log: bool = True) -> None:
    """Publish a user DEBUG message."""
    cp_msg_svc.user_message(message, CP_DEBUG)
    if log:
        logger.debug(message)

def cp_user_verbose_message(message: str, log: bool = True) -> None:
    """Publish a user VERBOSE message."""
    cp_msg_svc.user_message(message, CP_VERBOSE)
    if log:
        logger.debug(message)
#endregion user_message functions
# ---------------------------------------------------------------------------- +
#region cmd_result functions
def cp_subscribe_cmd_result_message(callback: Callback) -> str:
    """Subscribe to command result messages."""
    return cp_msg_svc.subscribe(CP_CMD_RESULT_TOPIC, callback)    

def cp_publish_cmd_result(cmd_result: CMD_RESULT_TYPE) -> None:
    """Publish a command result message."""
    cp_msg_svc.publish(topic=CP_CMD_RESULT_TOPIC, 
                    data={'message': cmd_result})

#endregion cmd_result functions
# ---------------------------------------------------------------------------- +

