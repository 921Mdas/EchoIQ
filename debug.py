# Test in Python shell
from auth.auth_helper import pwd_context
hashed = pwd_context.hash("test")
print(pwd_context.verify("test", hashed))  # Should return True