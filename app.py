import boto3
from enum import Enum
import logging
import typer
from typing import Iterable
from kms_reencrypt.filters.base import Filter, Match
from kms_reencrypt.filters.kms import Kms as KmsFilter
from kms_reencrypt.executors.kms import Kms as KmsExec
from kms_reencrypt.executors.base import Executor

logger = logging.getLogger("app")


def first(itr: Iterable[object]) -> bool:
    try:
        return next(itr)
    except StopIteration:
        return False


class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


def map_log_level(log_level: LogLevel) -> int:
    if log_level == LogLevel.DEBUG:
        return logging.DEBUG
    if log_level == LogLevel.INFO:
        return logging.INFO
    if log_level == LogLevel.WARNING:
        return logging.WARNING
    if log_level == LogLevel.ERROR:
        return logging.ERROR

    raise RuntimeError("Invalid log level")


def process_prefix(
    client_s3,
    bucket: str,
    prefix: str,
    filter: Filter,
    filter_match: Match,
    keys_per_page: int,
    executor: Executor,
    dry_run: bool,
):
    paginator = client_s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(
        Bucket=bucket,
        Prefix=prefix,
        Delimiter="/",
        PaginationConfig={"MaxItems": keys_per_page, "PageSize": keys_per_page},
    )

    for page in pages:
        # "Files" in current "dir"
        if "Contents" in page and page["Contents"]:
            if filter_match == Match.FIRST:
                pred = first
            elif filter_match == Match.ANY:
                pred = any
            elif filter_match == Match.ALL:
                pred = all
            else:
                raise RuntimeError("Unexpected match type")

            # Make sure to wrap with () to use generator instead of []
            content_keys = (content_obj["Key"] for content_obj in page["Contents"])
            res = pred(filter.process(bucket=bucket, key=key) for key in content_keys)

            if not res:
                logger.debug("Skipping '%s'", prefix)
            else:
                logger.info("Found '%s'", prefix)

                for key in content_keys:
                    logger.info("Processing '%s'", key)
                    if not dry_run:
                        executor.process(bucket=bucket, key=key)

        # Traverse into next "dir"
        if "CommonPrefixes" in page:
            for next_prefix_obj in page["CommonPrefixes"]:
                # Next prefix already includes the current prefix, so no need to append
                next_prefix = next_prefix_obj["Prefix"]
                # Extract the right-most "dir" (always contains '/' at the end)
                additional_prefix = "{}/".format(next_prefix.split("/")[-2])

                process_prefix(
                    client_s3=client_s3,
                    bucket=bucket,
                    prefix=next_prefix,
                    filter=filter,
                    filter_match=filter_match,
                    keys_per_page=keys_per_page,
                    executor=executor,
                    dry_run=dry_run,
                )


def app(
    bucket: str = typer.Argument(default=None, help="Name of S3 bucket to target."),
    prefix: str = typer.Option(default="", help="Key prefix to start from."),
    kms_key_id: str = typer.Argument(
        default=None, help="KMS key id to match. Use 'alias/xxx' for key alias."
    ),
    filter_match: Match = typer.Option(
        default=Match.FIRST, help="Level of strictness to filter for processing."
    ),
    keys_per_page: int = typer.Option(
        default=1000, help="S3 list objects max keys per page"
    ),
    dry_run: bool = typer.Option(
        default=False, help="If set, performs filter without execution of KMS changes."
    ),
    log_level: LogLevel = typer.Option(
        default=LogLevel.INFO,
        help="Verbosity of log. Only 'debug' or 'info' is relevant.",
    ),
):
    logging.basicConfig()
    logger.setLevel(level=map_log_level(log_level))

    client_s3 = boto3.client("s3")
    client_kms = boto3.client("kms")

    kms_filter = KmsFilter(client_s3, client_kms, kms_key_id)
    kms_exec = KmsExec(client_s3, kms_filter.kms_key_arn)

    process_prefix(
        client_s3,
        bucket=bucket,
        prefix=prefix,
        filter=kms_filter,
        filter_match=filter_match,
        keys_per_page=keys_per_page,
        executor=kms_exec,
        dry_run=dry_run,
    )

    logger.debug("DONE!")


def main():
    typer.run(app)


if __name__ == "__main__":
    main()
