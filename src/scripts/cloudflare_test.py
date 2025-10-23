#!/usr/bin/env python3
# coding=utf-8
"""Try something. """

import os
# import boto3
# from botocore.client import Config
from cloudflare import Cloudflare

if __name__ == "__main__":

    try:
        print("All CLOUDFLARE env vars:")
        # for key, value in os.environ.items():
        #     if "CLOUDFLARE" in key:
        #         print(f"{key}: {value[:10]}..." if value else f"{key}: None")
        bucket = os.environ.get("MY_BUCKET_NAME")
        acct_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
        print(os.environ.get("CLOUDFLARE_API_TOKEN"))
        print(os.environ.get("CLOUDFLARE_ACCOUNT_ID"))

        token = os.environ.get("CLOUDFLARE_API_TOKEN")
        account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
        cf = Cloudflare(api_token=token)
        buckets = cf.r2.buckets.list(account_id=account_id)
        for bucket in buckets:
            print(f"Bucket: {bucket['name']}")
        # bucket = cf.r2.buckets.get(
        #     account_id=acct_id,
        #     bucket_name="painter1")
        exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)
