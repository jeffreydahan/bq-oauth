import os, re, json, warnings, logging

from dotenv import load_dotenv
from typing import Any, Dict, Optional

from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext

# Ignore all warnings
warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)

load_dotenv()
AGENTSPACE_AUTH_ID = os.getenv("AGENTSPACE_AUTH_ID")

DYNAMIC_AUTH_PARAM_NAME = "dynamic_auth_config" # Name of the parameter to inject
DYNAMIC_AUTH_INTERNAL_KEY = "oauth2_auth_code_flow.access_token" # Internal key for the token

# callback utility to grab the access token which was acquired in the Agentspace authorization resource
def dynamic_token_injection(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext) -> Optional[Dict]:
    token_key = None
    # Uncomment when you want to test locally, you must obtain a valid access token yourself.
    # tool_context.state['temp:'+AGENTSPACE_AUTH_ID+'_0'] = "ABC123"
    pattern = re.compile(r'^temp:'+AGENTSPACE_AUTH_ID+'.*')
    
    state_dict = tool_context.state.to_dict()
    matched_auth = {key: value for key, value in state_dict.items() if pattern.match(key)}

    if len(matched_auth) > 0:
        token_key = list(matched_auth.keys())[0]
        logger.info(f"**** token_key:::: {token_key}")
    else:
        logger.warning("No valid tokens found")
        return None

    logger.info(f"*** Before tool callback for tool: {tool.name}")
    logger.info(f"*** OAuth object::: {tool_context.state[token_key]}")

    access_token = tool_context.state[token_key]
    logger.info(f"Access token found in session state with key '{token_key}'. Injecting dynamic auth.")
    dynamic_auth_config = {DYNAMIC_AUTH_INTERNAL_KEY: access_token}
    args[DYNAMIC_AUTH_PARAM_NAME] = json.dumps(dynamic_auth_config)
    logger.info(f"Arguments after injection: {args}")
    return None