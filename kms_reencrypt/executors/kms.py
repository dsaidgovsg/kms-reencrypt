from kms_reencrypt.executors.base import Executor


class Kms(Executor):
    def __init__(self, client_s3, kms_key_arn: str):
        self.client_s3 = client_s3
        self.kms_key_arn = kms_key_arn

    def process(self, bucket: str, key: str):
        self.client_s3.copy_object(
            Bucket=bucket,
            Key=key,
            CopySource={
                "Bucket": bucket,
                "Key": key,
            },
            ServerSideEncryption="aws:kms",
            SSEKMSKeyId=self.kms_key_arn,
        )
