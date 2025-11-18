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
import dotenv
dotenv.load_dotenv()

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.genai import types

from.prompts import root_agent_instructions, cloud_bqoauth_agent_instructions
from .tools import app_int_cloud_bqoauth_connector


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)

print("Libraries imported.")


project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

# Define the bqoauth Agent with tools and instructions
cloud_bqoauth_agent = Agent(
    model="gemini-2.5-flash",
    name="cloud_bqoauth_agent",
    instruction=cloud_bqoauth_agent_instructions,
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

