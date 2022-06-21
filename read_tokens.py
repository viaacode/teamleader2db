from app.models.teamleader_auth import TeamleaderAuth
from viaa.configuration import ConfigParser
import json

config = ConfigParser()
token_store = TeamleaderAuth(
    config.app_cfg['postgresql_teamleader'],
    config.app_cfg['table_names']
)
code, token, refresh_token = token_store.read()

auth_data = {
    'code': code,
    'token': token,
    'refresh_token': refresh_token
}

json.dumps(auth_data)
