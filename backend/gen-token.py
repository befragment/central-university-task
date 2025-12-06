import sys
sys.path.insert(0, '.')

from core.security import create_access_token
from uuid import UUID

# user_id Ивана из seed данных
user_id = UUID('22222222-2222-2222-2222-222222222222')
session_id = UUID('00000000-0000-0000-0000-000000000002')

token = create_access_token(user_id, session_id)
print(token)