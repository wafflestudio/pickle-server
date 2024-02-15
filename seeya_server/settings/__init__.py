import logging
import os

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

ENV = os.getenv("SEEYA_ENV", "local")
logger.info(f"Loading settings for environment: {ENV}")

match ENV:
    case "local":
        from .local import *
    case "dev":
        from .dev import *
    case "prod":
        from .prod import *
    case _:
        raise ValueError(f"Unknown environment: {ENV}")
