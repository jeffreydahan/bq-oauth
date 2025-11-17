# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys, re, json

import logging
import warnings


from typing import Any, Dict, Optional
from google.adk.agents import Agent, LlmAgent
from dotenv import load_dotenv
from google.adk.tools.application_integration_tool.application_integration_toolset import ApplicationIntegrationToolset
from google.adk.tools.apihub_tool.clients.secret_client import SecretManagerClient
from google.adk.auth import AuthCredential, AuthCredentialTypes, OAuth2Auth
from google.adk.auth.auth_credential import HttpAuth, HttpCredentials
from google.adk.tools.tool_context import ToolContext
from google.adk.agents.callback_context import CallbackContext
from google.oauth2.credentials import Credentials
from google.adk.tools.base_tool import BaseTool


from fastapi.openapi.models import OAuth2
from fastapi.openapi.models import OAuthFlowAuthorizationCode
from fastapi.openapi.models import OAuthFlowsfrom .prompts import root_agent_instructions, app_int_cloud_bqoauth_instructions


_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

# oauth setup
from google.adk.tools.openapi_tool.auth.auth_helpers import dict_to_auth_scheme
from google.adk.auth import AuthCredential
from google.adk.auth import AuthCredentialTypes
from google.adk.auth import OAuth2Auth
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
    # Assuming you named your secrets 'oauth-client-id' and 'oauth-client-secret' in Cloud Console
    my_client_id = get_secret("bqoauth-client-id") 
    my_client_secret = get_secret("bqoauth")
    print("✅ Successfully fetched credentials from Secret Manager")
except Exception as e:
    print(f"❌ Error fetching secrets: {e}")
    # Fallback or exit here if secrets fail

def dynamic_token_injection(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext) -> Optional[Dict]:
    token_key = None
    # Uncomment when you want to test locally, you must obtain a valid access token yourself.
    # tool_context.state['temp:'+AGENTSPACE_AUTH_ID+'_0'] = "ABC123"
    pattern = re.compile(r'^temp:'+auth_id+'.*')

    state_dict = tool_context.state.to_dict()
    matched_auth = {key: value for key, value in state_dict.items() if pattern.match(key)}
    if len(matched_auth) > 0:
        token_key = list(matched_auth.keys())[0]
    else:
        print("No valid tokens found")
        return None
    access_token = tool_context.state[token_key]
    dynamic_auth_config = {DYNAMIC_AUTH_INTERNAL_KEY: access_token}
    args[DYNAMIC_AUTH_PARAM_NAME] = json.dumps(dynamic_auth_config)
    return None

# Build Integration Connector object - Cloud SQL SQL Server
app_int_cloud_bqoauth_connector = ApplicationIntegrationToolset(
    project=project_id,
    location="us-central1", 
    connection="bqcitibike", 
    actions=["ExecuteCustomQuery"],
    tool_name_prefix="bqcitibike",
    tool_instructions=app_int_cloud_bqoauth_instructions,
    auth_scheme=oauth_scheme,
    auth_credential=auth_credential,
)

# Define the bqoauth Agent with tools and instructions
cloud_bqoauth_agent = Agent(
    model="gemini-2.5-flash",
    name="cloud_bqoauth_agent",
    instruction="""

    You are an agent that can query the Citi Bike BigQuery dataset using the provided tool.
    Use the tool to execute SQL queries against the dataset as needed to answer user questions.
    
    """,
    tools=[app_int_cloud_bqoauth_connector],
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)

# Define the root agent with tools and instructions
root_agent = Agent(
    model="gemini-2.5-flash",
    name="RootAgent",
    instruction=root_agent_instructions,
    tools=[AgentTool(agent=cloud_bqoauth_agent)],
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)

app = App(root_agent=root_agent, name="app")
