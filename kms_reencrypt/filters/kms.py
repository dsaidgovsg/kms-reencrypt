from kms_reencrypt.filters.base import Filter


class Kms(Filter):
    def __init__(self, client_s3, client_kms, kms_key_id: str):
        # For key alias, the value must be prefixed with "alias/"
        # In either case, the key id will always be returned
        rsp = client_kms.describe_key(KeyId=kms_key_id)

        if "KeyMetadata" not in rsp or "KeyId" not in rsp["KeyMetadata"]:
            raise RuntimeError("Invalid KMS key alias")

        self.kms_key_arn = rsp["KeyMetadata"]["Arn"]
        self.client_s3 = client_s3

    def process(self, bucket: str, key: str) -> bool:
        if key[-1] == "/":
            return False

        rsp = self.client_s3.get_object(
            Bucket=bucket,
            Key=key,
        )

        # The key id on the object is actually the full key ARN
        if "SSEKMSKeyId" in rsp and rsp["SSEKMSKeyId"] == self.kms_key_arn:
            return False

        return True
