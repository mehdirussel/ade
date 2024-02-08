from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from beautiful_date import Apr,Jan,Feb, hours

#TODO unfinished file


#add the path to your client secret json file here
#google_creds_file = ""
gc = GoogleCalendar(credentials_path=google_creds_file)

# ading a test event to the calendar
start = (22/Feb/2024)[12:00]
end = start + 2 * hours
event = Event('Meeting',
              start=start,
              end=end)


events = gc.get_events(query='hehe')
for event in events:
    print(event)
