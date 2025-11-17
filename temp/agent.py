import logging
import warnings

from google.adk.agents import Agent

# adk deploy agent_engine --staging_bucket gs://adk_as_auth_example --display_name as_oauth_example_v2 --env_file agentspace_oauth2_connector_example/.env --trace_to_cloud agentspace_oauth2_connector_example
# uncomment when deploying to agent engine
# from prompts import ROOT_AGENT_INSTR
# from snow_connector_tool import snow_connector_tool
# from dynamic_auth_tool import dynamic_token_injection

# uncomment when running locally on adk web
from .prompts import ROOT_AGENT_INSTR
from .snow_connector_tool import snow_connector_tool
from .dynamic_auth_tool import dynamic_token_injection


# Ignore all warnings
warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)

print("Libraries imported.")

root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='servicenow_agent',
    description="ServiceNow Agent to help with Problems and Incidents.",
    instruction=ROOT_AGENT_INSTR,
    tools= [snow_connector_tool],
    # this callback is required for the dynamic access token injection to use Agentspace auth
    before_tool_callback=dynamic_token_injection
)
