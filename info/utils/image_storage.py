from qiniu import Auth, put_data
# 在七牛云网站的个人面板/密钥管理/粘贴
access_key = 'ZVTXXdUfijulK_jzbkNnrX6DEHnpxSvsYrpjcKyz'
secret_key = 'rq-K1sQZTe5TLPDLqmQRFnFjf3g2_D8704g44tPf'
# 手动创建空间，指定空间名称
bucket_name = 'ihome20'


def storage(data):
    try:
        q = Auth(access_key, secret_key)
        token = q.upload_token(bucket_name)
        ret, info = put_data(token, None, data)
        print(ret, info)
    except Exception as e:
        raise e;

    if info.status_code != 200:
        raise Exception("上传图片失败")
    return ret["key"]


if __name__ == '__main__':
    file = input('请输入文件路径')
    with open(file, 'rb') as f:
        storage(f.read())