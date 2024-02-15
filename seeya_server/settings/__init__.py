import os

from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("SEEYA_ENV", "local")

match ENV:
    case "local":
        from .local import *
    case "dev":
        from .dev import *
    case "prod":
        from .prod import *
    case _:
        raise ValueError(f"Unknown environment: {ENV}")
