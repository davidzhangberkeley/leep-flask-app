from datetime import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import LlmAgent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from pydantic import BaseModel, Field
from typing import List
from tools import google_tasks_tool
from typing import Union, Dict, Any, AsyncGenerator
from dotenv import load_dotenv
import os
import json


import vertexai
from vertexai.preview import reasoning_engines

PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
STAGING_BUCKET = os.getenv("STAGING_BUCKET")

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)


# class Task(BaseModel):
#     title: str
#     subtasks: List[str]

#     class Config:
#         extra = "forbid"


# class Milestone(BaseModel):
#     title: str
#     tasks: List[Task]

#     class Config:
#         extra = "forbid"


# class ProjectPlan(BaseModel):
#     milestones: List[Milestone]

#     class Config:
#         extra = "forbid"

from pydantic import BaseModel
from typing import List, Optional


class Timestamp(BaseModel):
    _seconds: int
    _nanoseconds: int


class Subtask(BaseModel):
    id: str
    label: str
    checked: bool
    description: Optional[str]


class Task(BaseModel):
    id: str
    name: str
    status: str
    description: Optional[str]
    dueDate: Optional[str]
    createdAt: Optional[str]
    summary: Optional[str]
    subtasks: List[Subtask]


class Milestone(BaseModel):
    id: str
    workflowId: str
    createdAt: Timestamp
    name: str
    status: str
    description: Optional[str]
    dueDate: Optional[str]
    order: int
    tasks: List[Task]
    userId: str


class Workflow(BaseModel):
    owner: str
    userId: str
    name: str
    description: Optional[str]
    createdAt: Timestamp
    members: List[str]
    id: str
    milestones: List[Milestone]


# Calendar Subagent:
calendar_subagent = LlmAgent(
    name="calendar_subagent",
    model="gemini-2.5-pro",  # or your chosen model
    description=(
        """
        You are an agent that helps users figure out deadlines and add tasks to Google Tasks.
        Use the tool google_tasks_tool(title, due_date) when the user asks to create or schedule a task. 
        Args for google_tasks_tool:
            task_name: Title of the task (string)
            date: Due date as a string in 'YYYY-MM-DD' format
    """
    ),
    instruction=(
        f"""
        1. Given the workflow (in JSON format), determine realistic due dates for each task and subtask, keeping note that each task must be completed after all subtasks under the task have been completed. Consider factors like how difficult the tasks/subtasks are. Keep in mind today's date is {datetime.today().strftime('%Y-%m-%d')}.
        2. Using the google_tasks_tool, put each and every one of the task/subtask into Google Tasks, using the task/subtask name and due date. Note that the due_date argument MUST be a string with the following format: 'YYYY-MM-DD'. 
        """
    ),
    tools=[google_tasks_tool],
)


# ROOT AGENT: main agent
root_agent1 = LlmAgent(
    name="taskSplitter",
    model="gemini-2.0-flash",
    description=(
        "You are a helper to break down goals and create a workflow. Your role is to take a goal from the user and break the goal down into multiple realistic milestones, each with a set of tasks. Make sure that each task has a set of subtasks. Your response will be in JSON format. "
    ),
    instruction=(
        "1. Split the goal up into 3-5 multiple realistic milestones that are each 1 sentence long"
        "2. For each milestone, come up with multiple realistic tasks that are part of the milestone. Each task should be 1 sentence long. "
        "3. For each task, come up with multiple realistic subtasks that are part of the task. Each subtask should be 1 sentence long. "
        "4. Output a structured object with the following keys: "
        "  - 'milestones': an array of MILESTONE objects that each contain: "
        "  - 'title': the 1-sentence-long title of the milestone"
        "  - 'tasks': an array of TASK objects that correspond to that specific milestone that each contain: "
        "  - 'title': the 1-sentence-long title of the task"
        "  - 'subtasks': an array of strings of 1-sentence-long subtasks that correspond to that specific task"
        "5. Wait for the user to approve or make modifications. You should expect a 'yes' or a suggestion. If there are any suggestions, remake the workflow given the suggestions, still in JSON format, and return to the user. If the user approves, move onto the next step."
        "6. Once the JSON is approved by the user, give full control to the nextSteps subagent."
    ),
    output_schema=Workflow,
)

root_agent = LlmAgent(
    name="rootAgent",
    model="gemini-2.0-flash",
    description=(
        "You are the main coordinator agent for the root_agent1 and the calendar_subagent."
        "root_agent1 is responsible for turning a goal into a workflow"
        "calendar_subagent is responsible for coming up with due dates and putting them in the calendar"
    ),
    instruction=(
        """
        1. If the user inputs a task, such as "dunk a basketball" or "make a profitable business out of my XYZ idea", then run root_agent1 and output the workflow JSON
        2. Only after the user has supplied a task, move onto step 3
        3. ONLY if the user expresses interest in creating due dates OR in putting things in the calendar, ex: "what are the due dates for these" or "can you put this in my calendar", ONLY THEN will you use the calendar_subagent tool.
        """
    ),
    sub_agents=[root_agent1, calendar_subagent],
)


vertexApp = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

# session = vertexApp.create_session(user_id="u_123")
# print(session.id)


# for event in app.stream_query(
#     user_id="u_123",
#     session_id=session.id,
#     message="make me a workflow: dunk a basketball",
# ):
#     print(event)

# for event in app.stream_query(
#     user_id="u_123",
#     session_id=session.id,
#     message="i don't like this workflow, make this workflow easier to follow, considering that i am 5 foot 8.",
# ):
#     print(event)
