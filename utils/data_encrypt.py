import uuid
from hashlib import sha256
from BugManagePlatform import settings


def encrypt(password):
    # 加盐，配置里面的SECRET_KEY
    sha_obj = sha256(settings.SECRET_KEY.encode('utf-8'))
    sha_obj.update(password.encode('utf-8'))
    return sha_obj.hexdigest()


def uid(string):
    return encrypt(f'{string}-str({uuid.uuid4()})')
