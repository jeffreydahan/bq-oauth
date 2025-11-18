import os
from dotenv import load_dotenv

from google.adk.auth import AuthCredential, AuthCredentialTypes, OAuth2Auth

from fastapi.openapi.models import OAuth2
from fastapi.openapi.models import OAuthFlowAuthorizationCode
from fastapi.openapi.models import OAuthFlows

load_dotenv()

project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

# oauth setup
from google.cloud import secretmanager

def get_secret(secret_id, version_id="latest"):
    """
    Fetches a secret from Google Cloud Secret Manager.
    """
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

try:
    # Get Secret values from Secret Manager
    my_client_id = get_secret("bqoauth-client-id") 
    my_client_secret = get_secret("bqoauth")
    print("✅ Successfully fetched credentials from Secret Manager")
except Exception as e:
    print(f"❌ Error fetching secrets: {e}")
    # Fallback or exit here if secrets fail

bq_client_id = os.getenv("BQ_SECMGR_ID")
bq_client_secret = os.getenv("BQ_SECMGR_SECRET")
bq_gcp_redirect_uri = os.getenv("BQ_OAUTH_REDIRECT_URI")
bq_adk_local_redirect_uri = os.getenv("BQ_ADK_LOCAL_REDIRECT_URI")
bq_auth_scopes = os.getenv("BQ_OAUTH_SCOPES")

oauth2_scheme = OAuth2(
   flows=OAuthFlows(
      authorizationCode=OAuthFlowAuthorizationCode(
            authorizationUrl="https://accounts.google.com/o/oauth2/v2/auth",
            tokenUrl="https://oauth2.googleapis.com/token",
            scopes={
                f"{bq_auth_scopes}" : "default",
            }
      )
   )
)

oauth2_credential = AuthCredential(
  auth_type=AuthCredentialTypes.OAUTH2,
  oauth2=OAuth2Auth(
    client_id=get_secret(bq_client_id),
    client_secret=get_secret(bq_client_secret),
    redirect_uri=bq_adk_local_redirect_uri # This is the ADK Web UI
  )
)