from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from qcloud_cos import CosServiceError
from qcloud_cos import CosClientError
from BugManagePlatform import settings

# 设置腾讯云 COS 的 SecretId 和 SecretKey
secret_id = settings.TENCENT_APP_ID
secret_key = settings.TENCENT_APP_KEY


def create_bucket(bucket_name, region='ap-beijing'):
    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)
    try:
        # ACL 权限有三种设置，分别为 private、public-read、public-read-write，默认为 private
        response = client.create_bucket(Bucket=bucket_name, ACL='public-read')
        # 为 Bucket 设置跨域规则
        cors_config = {
            'CORSRule': [
                {
                    'AllowedOrigin': '*',
                    'AllowedMethod': ['GET', 'PUT', 'HEAD', 'POST', 'DELETE'],
                    'AllowedHeader': "*",
                    'ExposeHeader': "*",
                    'MaxAgeSeconds': 500
                }
            ]
        }
        client.put_bucket_cors(Bucket=bucket_name, CORSConfiguration=cors_config)
        print('创建成功')
        return response
    except CosServiceError as e:
        print(e)
    except CosClientError as e:
        print(e)


def upload_file(file_obj, new_file_name, bucket_name, region='ap-beijing'):
    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)
    try:
        # 上传文件到 COS。body是一个支持read()方法的对象，例如文件对象、StringIO对象等.
        # key是文件路径和文件名
        response = client.upload_file_from_buffer(
            Bucket=bucket_name,
            Body=file_obj,
            Key=new_file_name
        )
        url = 'https://{}.cos.{}.myqcloud.com/{}'.format(bucket_name, region, new_file_name)
        return url
    except CosServiceError as e:
        print('Service error:', e.get_error_code(), e.get_error_msg())
    except CosClientError as e:
        print('Client error:', e)


def del_file(bucket_name, file_name, region='ap-beijing'):
    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)
    try:
        response = client.delete_object(Bucket=bucket_name, Key=file_name)
        print('删除成功')
        return response
    except CosServiceError as e:
        print('Service error:', e.get_error_code(), e.get_error_msg())
    except CosClientError as e:
        print('Client error:', e)


# 批量删除文件
"""
# 批量删除文件参数格式
            objects = {
                "Quiet": "true",
                "Object": [
                    {
                        "Key": "file_name1"
                    },
                    {
                        "Key": "file_name2"
                    }
                ]
            }
"""


def batch_del_file(bucket_name, file_list, region='ap-beijing'):
    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)
    # 注意批量删除的参数格式。
    objects = {
        "Quiet": "true",
        "Object": file_list
    }
    try:
        response = client.delete_objects(Bucket=bucket_name, Delete=objects)
        print('批量删除成功')
        return response
    except CosServiceError as e:
        print('Service error:', e.get_error_code(), e.get_error_msg())
    except CosClientError as e:
        print('Client error:', e)
