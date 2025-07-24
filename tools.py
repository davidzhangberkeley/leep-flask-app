# import datetime
# import os.path
# from zoneinfo import ZoneInfo
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from google.auth.transport.requests import Request
# from pathlib import Path

# BASE_DIR = Path(__file__).resolve().parent
# TOKEN_PATH = BASE_DIR / "token.json"
# CREDENTIALS_PATH = BASE_DIR / "credentials.json"


# # Scope for managing tasks
# # SCOPES = ["https://www.googleapis.com/auth/tasks"]


# def get_service():
#     creds = None
#     if os.path.exists(TOKEN_PATH):
#         creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
#             creds = flow.run_local_server(port=8080)

#         # Save the credentials for next run
#         with open(TOKEN_PATH, "w") as token:
#             token.write(creds.to_json())

#     return build("tasks", "v1", credentials=creds)


# def add_task(task_name, date):
#     """
#     Add a task with a due date to the user's default task list.
#     :param task_name: Title of the task
#     :param date: Due date as a string in 'YYYY-MM-DD' format
#     """
#     service = get_service()

#     due_datetime = (
#         datetime.datetime.strptime(date, "%Y-%m-%d").isoformat() + "Z"
#     )  # Z = UTC time
#     task = {"title": task_name, "due": due_datetime}

#     result = service.tasks().insert(tasklist="@default", body=task).execute()
#     print(f"Task added: {result.get('title')} (due {result.get('due')})")


# def google_tasks_tool(task_name: str, date: str) -> dict:
#     """Add a task with a due dater to the user's default task list.

#     Args:
#         ;param task_name: Title of the task
#         :param date: Due date as a string in 'YYYY-MM-DD' format

#     Returns:
#         dict: status and result or error msg.
#     """
#     try:
#         add_task(task_name, date)
#         return {"status": "success", "report": "Added the task to your Google tasks!"}
#     except Exception as e:
#         return {
#             "status": "error",
#             "error_message": str(e),
#         }


# if __name__ == "__main__":
#     add_task("walk da dog", "2026-09-01")


def google_tasks_tool(task_name: str, date: str) -> dict:
    # DUMMY TASK
    """Add a task with a due dater to the user's default task list.

    Args:
        ;param task_name: Title of the task
        :param date: Due date as a string in 'YYYY-MM-DD' format

    Returns:
        dict: status and result or error msg.
    """
    return {"status": "success", "report": "Added the task to your Google tasks!"}
