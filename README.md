# KMS Re-Encrypt

Python `boto3` script to recursively KMS re-encrypt objects.

This script is best suited for scenario where you have programs writing a "directory" of S3 objects
into your bucket, using the wrong KMS key (likely `aws/s3`) due to misconfiguration.

## Quick Start

Before running the script, do remember to set both your AWS profile and default region.

```bash
export AWS_PROFILE=my-aws-profile
export AWS_DEFAULT_REGION="ap-southeast-1"
```

```bash
# Starts scanning from root for S3 objects whose KMS key does not match and re-encrypt matches
poetry run app <bucket> <kms_key>
```

Both KMS key id and alias (not ARN) can be used. For key alias, prefix with "alias/" and followed by
the key alias name.

```bash
# Scans from prefix path for S3 objects whose KMS key does not match and re-encrypt matches
poetry run app <bucket> <kms_key> --prefix path/from/root
```

```bash
# Shows skipped directories alongside found directories
poetry run app <bucket> <kms_key> --log-level debug
```

```bash
# Scans only and do not re-encrypt matches
poetry run app <bucket> <kms_key> --dry-run
```

This mode is good if the purpose is to only detect and not act on the objects.

```bash
# If you need more details
poetry run app --help
```

## Prerequisites to Run Script

Minimum:
Python >= 3.9 (and `pip`)

There are two methods of running:

1. Raw `pip` install + direct Python run

```bash
pip install -r requirements.txt
python app.py ...
```

Good for people who just want a quick way to run the scripts and solve the KMS problems. You are
advised to use a virtual environment for the installation.

2. Via `poetry`

```bash
poetry install
poetry run app ...
```

Better for people who want to make some dev changes to the code here, or happens to have `poetry`
already installed.

## How Does the Script work

1. Lists and copy incorrectly KMS encrypted "files" in current "directory" prefix back into its own
   location, but using the correct KMS key.
2. Lists all the children "directories" in the given "directory" prefix (can be empty to indicate
   root)
3. Traverse into every children "directories" and repeat from 1.

## Interesting Note

The code is structured into 3 parts, first part being the main recursive loop where it is fixed. The
other two parts, the "filter" and "executor", are modular.

"Filter" is just like the functional programming term suggests, is a predicate implementation that
returns true or false based on the given S3 key. In this KMS context here, the "filter"
implementation returns true when the object is not KMS encrypted, or does not have the matching KMS
key.

"Executor is like the "foreach" / "map" that returns `None`, where it can perform any action on the
entry that the earlier "filter" has returned true. In this KMS context here, the "executor"
implementation runs the API call to copy the found object back into its own location, but with the
corrected KMS key.
