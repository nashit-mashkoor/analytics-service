import os
import json

from envs import env
from google.cloud import storage
from google.oauth2 import service_account
from singleton_decorator import singleton


@singleton
class CloudStorage:
    def __init__(self):

        self.GCP_BUCKET_NAME = env("GCP_BUCKET_NAME", var_type="string", allow_none=False)
        GOOGLE_APPLICATION_CREDENTIALS = env(
            "GOOGLE_APPLICATION_CREDENTIALS", var_type="dict", allow_none=False
        )
        GOOGLE_APPLICATION_SCOPES = env(
            "GOOGLE_APPLICATION_SCOPES", var_type="list", allow_none=False
        )

        credentials = "credentials"
        if not os.path.exists(credentials):
            os.makedirs(credentials)

        gcp_creds_file = f"{credentials}/gcp_creds_file.json"
        with open(gcp_creds_file, "w") as f:
            json.dump(GOOGLE_APPLICATION_CREDENTIALS, f)

        gcp_credentials = service_account.Credentials.from_service_account_file(
            filename=gcp_creds_file, scopes=GOOGLE_APPLICATION_SCOPES
        )
        self.gcp_storage_client = storage.Client(credentials=gcp_credentials)


    def upload_file(self, path, file_name, bucket_name=None):
        if bucket_name != None:
            self.GCP_BUCKET_NAME = bucket_name
        export_gcp_bucket = self.gcp_storage_client.get_bucket(self.GCP_BUCKET_NAME)
        blob = export_gcp_bucket.blob(path)
        blob.upload_from_filename(file_name)
