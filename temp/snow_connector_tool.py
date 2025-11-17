import os
from dotenv import load_dotenv
from google.adk.tools.application_integration_tool.application_integration_toolset import ApplicationIntegrationToolset

from google.adk.auth import AuthCredential, AuthCredentialTypes
from google.adk.auth.auth_credential import HttpAuth, HttpCredentials

load_dotenv()

SNOW_CONNECTION_PROJECT_ID=os.getenv("SNOW_CONNECTION_PROJECT_ID")
SNOW_CONNECTION_REGION=os.getenv("SNOW_CONNECTION_REGION")
SNOW_CONNECTION_NAME=os.getenv("SNOW_CONNECTION_NAME")

CONNECTOR_TOOL_INSTR="""
        **Tool Definition: ServiceNow Connector via Application Integration**

        This tool interacts with ServiceNow entities (Problems, Incidents) using an Apigee Integration Connector.
        It supports GET, LIST, and CREATE operations as defined for each entity.

        **CRITICAL: Authentication - `dynamic_auth_config` Parameter**

        *   **MANDATORY:** Every function call to this tool (e.g., `snow_connector_tool_list_problem`, `snow_connector_tool_get_incident`) **MUST** include the `dynamic_auth_config` parameter in the function call.
        *   **SYSTEM HANDLED:** This parameter is automatically populated with the necessary OAuth access token by the system. Your role is to ensure you *always* include `dynamic_auth_config` in your function call requests.
        *   **VALIDATION:** The system expects `dynamic_auth_config` to be present and valid. Do not attempt to generate or modify its value.

        **General Tool Usage:**

        *   **Tool Naming Convention:** Tool functions follow the pattern: `snow_connector_tool_<operation>_<entity_name_singular>`.
            *   Example: `snow_connector_tool_list_problem`, `snow_connector_tool_get_incident`.
        *   **Supported Entity Operations:**
            *   `Problem`: LIST, CREATE
            *   `Incident`: GET, LIST

        **Data Retrieval (GET and LIST Operations):**

        *   **Retrieve a Specific Record:**
            *   To retrieve a specific **Incident**, use the `GET` operation (e.g., `snow_connector_tool_get_incident`). The `entity_id` parameter **MUST** be the ServiceNow `sys_id` of the record.
            *   To retrieve a specific **Problem**, you **MUST** use the `LIST` operation (e.g., `snow_connector_tool_list_problem`) with a `filterClause` that uniquely identifies the record.
                *   **Example by Problem Number:** `filterClause="number='PRB000123'"`
                *   **Example by Sys ID:** `filterClause="sys_id='...'"`
        *   **Retrieve Multiple Records (LIST):**
            *   Use the `LIST` operation (e.g., `snow_connector_tool_list_problem`).
            *   **Filtering with `filterClause`:** This is essential for targeted data retrieval.
                *   **To retrieve Problem records assigned to a specific user:**
                    Use `snow_connector_tool_list_problem` with `filterClause="assigned_to='USER_SYS_ID'"` (where `USER_SYS_ID` is the `sys_id` of the user).
                *   **To retrieve related Incidents for a given Problem record:**
                    Use `snow_connector_tool_list_incident` with `filterClause="problem_id='PROBLEM_SYS_ID'"` (where `PROBLEM_SYS_ID` is the `sys_id` of the parent Problem).
        *   **Proactive Assistance with Related Incidents:**
            *   After successfully retrieving a Problem, inspect the result to see if it has associated Incidents.
            *   If related Incidents are present, you **MUST** proactively ask the user if they would like to view the details of these incidents.
            *   If they agree, use `snow_connector_tool_list_incident` with the correct `problem_id` in the `filterClause` to fetch and display the incident information.

        **Problem Creation:**

        *   **Tool:** Use `snow_connector_tool_create_problem`.
        *   **Information Gathering:**
            1.  Collect minimal information from the user to describe the new problem.
            2.  Deduce appropriate values for `category`, `impact`, and `urgency` based on the user-provided details.
        *   **User Confirmation:**
            1.  Before calling `snow_connector_tool_create_problem`, present the summarized details (description, deduced category, impact, urgency) to the user.
            2.  Ask for explicit confirmation from the user to proceed with creation.
        *   **Post-Creation Steps:**
            1.  After the problem is successfully created by `snow_connector_tool_create_problem` (which will return the new record including its `sys_id`).
            2.  Immediately call `snow_connector_tool_list_problem` using a `filterClause` with the `sys_id` of the newly created problem to fetch its complete and up-to-date details (e.g., `filterClause="sys_id='...'" `).
            3.  Present the **Problem Number** (e.g., "PRB0040001") and other key details (like description, state, priority) to the user. Do **NOT** show the `sys_id` as the primary identifier to the user.
"""

snow_connector_tool = ApplicationIntegrationToolset(
    project=SNOW_CONNECTION_PROJECT_ID, 
    location=SNOW_CONNECTION_REGION, 
    connection=SNOW_CONNECTION_NAME,
    entity_operations={
        "Problem": ["LIST", "CREATE", "UPDATE"],
        "Incident": ["GET", "LIST"],
    },
    tool_name_prefix="snow_connector_tool",
    tool_instructions=CONNECTOR_TOOL_INSTR,
    # auth_credential=oauth2_credential,
    # auth_scheme=oauth2_scheme,
    # auth_credential=oauth2_token,
)