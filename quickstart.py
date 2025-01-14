from datetime import datetime, timedelta
from getInfo import get_info
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# datetime(year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None, *, fold=0)
# Assume starting day begins on the day of instruction. For example, UCI 2024 winter quarter started on January 8th.
YEAR = 2025
# Jan: 1, Feb: 2, Mar: 3, Apr: 4, May: 5, ...
MONTH = 1
DAY = 6
STARTING_DAY = datetime(YEAR, MONTH, DAY)
DISC_DEFAULT_COLOR = "purple"

# delta days from the starting day Mon - Friday
Day_Delta = {
    'Mo': timedelta(days=0),
    'Tu': timedelta(days=1),
    'We': timedelta(days=2),
    'Th': timedelta(days=3),
    'Fr': timedelta(days=4),
}

def get_credentials():
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())
  return creds 

  
def create_event(service, info : list):
  
  for class_info in info:
    name = class_info.class_name if class_info.front_label == "LEC" else f"{class_info.front_label}: {class_info.class_name}"
    time_info = class_info.class_time
    # We get the first occurence of the class from class_info.days which should be at index 0
    start_time = STARTING_DAY + Day_Delta[class_info.days[0]] + timedelta(hours=time_info.start_hour if not time_info.isPm1 else time_info.start_hour + 12, minutes=time_info.start_min)
    end_time = STARTING_DAY + Day_Delta[class_info.days[0]] + timedelta(hours=time_info.end_hour if not time_info.isPm2 else time_info.end_hour + 12, minutes=time_info.end_min)
    byDay = ""
    for i in range(len(class_info.days)):
      byDay += class_info.days[i].upper()
      if i != len(class_info.days) - 1:
        byDay += ','
    
    RRULE = f'RRULE:FREQ=WEEKLY;COUNT={1 * 10 * len(class_info.days)};WKST=SU;BYDAY={byDay}'
    
    event = {
      'summary': name,
      'colorId': 3,
      'location': class_info.location,
      'start': {
        'dateTime': datetime.isoformat(start_time),
        'timeZone': 'America/Los_Angeles',
      },
      'end': {
        'dateTime': datetime.isoformat(end_time),
        'timeZone': 'America/Los_Angeles',
      },
      'recurrence': [
        RRULE
      ],
      'reminders': {
        'useDefault': False,
        'overrides': [
          {'method': 'popup', 'minutes': 30},
        ],
      },
    }
    
    event = service.events().insert(calendarId='primary', body=event).execute()
    print(f"Event created ({name}): {(event.get('htmlLink'))}")
  
def main():
  creds = get_credentials()
  try:
    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API
    print("Adding event")
    info = get_info()
    create_event(service, info)
    

  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()