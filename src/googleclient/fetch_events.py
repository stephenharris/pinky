from __future__ import print_function
import datetime
import logging
from googleapiclient.discovery import build
from googleclient.client import authenticate
from dateutil import parser

def fetch_events(calendar_id):
    creds = authenticate()
    service = build('calendar', 'v3', credentials=creds)

    try:
        service.calendarList().insert(body={"id": calendar_id}).execute()
        logging.info(f"Calendar {calendar_id} added")
    except Exception as e:
        logging.error(f"Inserting calendar failed: {e}")


    # Get events for today
    now = datetime.datetime.utcnow()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=59, second=59)

    events_result = service.events().list(
        calendarId=calendar_id,  # or your specific calendar ID
        timeMin=start_of_day.isoformat() + 'Z',
        timeMax=end_of_day.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    colors = service.colors().get().execute()
    calendar = service.calendarList().get(calendarId=calendar_id).execute()
    default_color = calendar.get("backgroundColor", "#0c0d0f")

    output = []
    for e in events:
        start = e['start'].get('dateTime', e['start'].get('date'))
        end = e['end'].get('dateTime', e['end'].get('date'))

        all_day = 'date' in e['start']

        start_time = None
        end_time = None
        if not all_day:
            start_dt = parser.isoparse(start)
            end_dt = parser.isoparse(end)
            start_time = start_dt.strftime("%H:%M")
            end_time = end_dt.strftime("%H:%M")

        color_id = e.get("colorId")
        color = colors['event'][color_id]['background'] if color_id else default_color

        output.append({
            "title": e.get('summary', '(No title)'),
            "start": start_time,
            "end": end_time,
            "all_day": all_day,
            "color": color
        })

    logging.info(f"Found {len(output)} events")
    return output

