from random import SystemRandom
from hmac import compare_digest

_sysrand = SystemRandom()

randbits = _sysrand.getrandbits
choice = _sysrand.choice


zip_api_key = 'DemoOnly00N0dOLOa2oXQ33dORmC4EiQNplIbqvsHdaE0vHSPf6hRBVsZtX4IFfm'