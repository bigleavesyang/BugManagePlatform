from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from qcloud_cos import CosServiceError
from qcloud_cos import CosClientError
from sts.sts import Sts
from BugManagePlatform import settings
from django.http import JsonResponse

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


def credential(request, bucket_name, region='ap-beijing'):
    config = {
        # 请求URL，域名部分必须和domain保持一致
        # 使用外网域名时：https://sts.tencentcloudapi.com/
        # 使用内网域名时：https://sts.internal.tencentcloudapi.com/
        'url': 'https://sts.tencentcloudapi.com/',
        # 域名，非必须，默认为 sts.tencentcloudapi.com
        # 内网域名：sts.internal.tencentcloudapi.com
        'domain': 'sts.tencentcloudapi.com',
        # 临时密钥有效时长，单位是秒
        'duration_seconds': 1800,
        'secret_id': settings.TENCENT_APP_ID,
        # 固定密钥
        'secret_key': settings.TENCENT_APP_KEY,
        # 换成你的 bucket
        'bucket': bucket_name,
        # 换成 bucket 所在地区
        'region': region,
        # 这里改成允许的路径前缀，可以根据自己网站的用户登录态判断允许上传的具体路径
        # 例子： a.jpg 或者 a/* 或者 * (使用通配符*存在重大安全风险, 请谨慎评估使用)
        'allow_prefix': '*',
        # 密钥的权限列表。简单上传和分片需要以下的权限，其他权限列表请看 https://cloud.tencent.com/document/product/436/31923
        'allow_actions': [
            # 简单上传
            'name/cos:PutObject',
            # 'name/cos:PostObject',
            # # 分片上传
            # 'name/cos:InitiateMultipartUpload',
            # 'name/cos:ListMultipartUploads',
            # 'name/cos:ListParts',
            # 'name/cos:UploadPart',
            # 'name/cos:CompleteMultipartUpload'
        ],
    }
    try:
        sts = Sts(config)
        response = sts.get_credential()
        return response
    except Exception as e:
        print(e)
        return JsonResponse({'error': str(e)})


# 校验文件是否存在
def check_file(bucket_name, file_name, region='ap-beijing'):
    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)
    try:
        response = client.head_object(Bucket=bucket_name, Key=file_name)
        return response
    except CosServiceError as e:
        print('Service error:', e.get_error_code(), e.get_error_msg())
    except CosClientError as e:
        print('Client error:', e)


# 删除桶
def delete_bucket(bucket_name, region='ap-beijing'):
    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)
    try:
        # 循环选择桶中文件先进行删除，判断桶中文件是否为空，不为空则删除，空了则跳出循环，单词最大返回值默认为1000
        while True:
            part_objects = client.list_objects(Bucket=bucket_name)
            contents = part_objects.get('Contents')
            if not contents:
                break
            # 批量删除文件
            objects = {
                "Quiet": "true",
                "Object": [{"Key": item.get('Key')} for item in contents]
            }
            response = client.delete_objects(Bucket=bucket_name, Delete=objects)
            # 如果传输没有数据流了，则跳出循环
            if part_objects.get('IsTruncated') == 'false':
                break
        # 批量删除桶中碎片文件
        while True:
            # 获取桶中所有碎片
            multipart_uploads = client.list_multipart_uploads(Bucket=bucket_name)
            uploads = multipart_uploads.get('Upload')
            if not uploads:
                break
            for item in uploads:
                # 删除碎片文件
                response = client.abort_multipart_upload(Bucket=bucket_name, Key=item.get('Key'), UploadId=item.get('UploadId'))
            if part_objects.get('IsTruncated') == 'false':
                break

        # 删除桶
        client.delete_bucket(Bucket=bucket_name)
    except CosServiceError as e:
        print(e)
    except CosClientError as e:
        print(e)

