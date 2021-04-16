# KMS Re-Encrypt

Python `boto3` script to recursively KMS re-encrypt objects.

## Quick Start

```bash
# Starts scanning from root for S3 objects whose KMS key does not match
poetry run app <bucket> <kms_key>
```

Both KMS key id and alias (not ARN) can be used. For key alias, prefix with "alias/" and followed by
the key alias name.

```bash
# Scans from prefix path for S3 objects whose KMS key does not match
poetry run app <bucket> <kms_key> --prefix path/from/root
```
