# Evasion modules package
from .proxy_rotator      import ProxyRotator, get_xff_headers
from .useragent_manager  import UserAgentManager, get_random_ua
from .jitter_engine      import JitterEngine, async_jitter
from .session_rotator    import SessionRotator, get_session_headers
from .header_manipulator import HeaderManipulator, get_evasion_headers

__all__ = [
    "ProxyRotator", "get_xff_headers",
    "UserAgentManager", "get_random_ua",
    "JitterEngine", "async_jitter",
    "SessionRotator", "get_session_headers",
    "HeaderManipulator", "get_evasion_headers",
]
