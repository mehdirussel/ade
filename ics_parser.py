from common_imports import *
from ade_scrape import edt_retriever


def read_ics_file(file_path):
    # reads ics file into icalendar.calendar object
    with open(file_path) as f:
        calendar = icalendar.Calendar.from_ical(f.read())
    return calendar

def get_unix_timestamp(cal_element):
    return datetime.fromisoformat(str(cal_element.get('DTSTART').dt)).timestamp()

#TODO improve dis, add new events finder
def compare_events(cal1, cal2,cmp_limit=10): 
    # new is cal1; old is cal2
    # cmp_limit number of mismatched events afterwhich we stop comparing
    available_attrs = ('SUMMARY', 'DTSTART', 'DTEND', 'DTSTAMP','UID','SEQUENCE')
    attrs_to_compare = ('UID')#'SUMMARY', 'DTSTART')
    # trier les 2 tableaux par dates
    c1 = sorted(list(cal1.walk('VEVENT')), key=get_unix_timestamp)
    c2 = sorted(list(cal2.walk('VEVENT')), key=get_unix_timestamp)
    i = 1
    if(len(c1) == len(c2)): # meme taille
        for (ev1,ev2) in zip(c1,c2): # loop through the 2 lists in parallel
            for attr in attrs_to_compare:
                if(ev1.get(attr) != ev2.get(attr)):
                    print(f"Mismatch {i}: ",end="")
                    print(ev1.get('SUMMARY'),f" at {ev1.get('DTSTART').dt} | ",ev2.get('SUMMARY')," at ",ev2.get('DTSTART').dt)
                    i+=1
                    if(i > cmp_limit): # stop condition
                        print("Comparaison limit reached")
                        return
        print("No mismatch found between the 2 files!")
    else:
        print("Calendars have different lengths!")
        set1 = set([str(ev.get('UID')) for ev in c1])
        set2 = set([str(ev.get('UID')) for ev in c2])
        # Find the IDs present in calendar1(n events) but not in calendar1(m<n events)
        difference_set = set1 - set2 # new - old
        for diff in difference_set:
            if(i > cmp_limit): # stop condition
                print("Comparaison limit reached")
                return
            print(f"added event {i}: ",end='')
            for ev in c1:
                if(str(ev.get('UID')) == diff):
                    print(ev.get('SUMMARY')," at ",ev.get('DTSTART').dt)
            i+=1

    

def main():
    
    file_path1 = 'old.ics'  # old ics file to compare with
    creds_path = "credentials.json"

    ics_content1 = read_ics_file(file_path1)

    # path needs to finsih with /
    scraper = edt_retriever(["eTudiants","EnsiSa","inGénieurS","1A","InFormatiqUe"],"ics_files/",timeout=20,headless_mode=0)
    scraper.login(creds_path) # login
    
    newly_scraped_ics = scraper.get_ics("02-01-2024","20-03-2024",save_ics_to_path = 1) # grab (deez) ics link and dl the file
    scraper.get_pdf()
    ics_content2 = read_ics_file(newly_scraped_ics)

    print(compare_events(ics_content1, ics_content2))

def main2():
    #to compare between new and old
    calendar_new = read_ics_file("new.ics")
    calendar_old = read_ics_file("old.ics")
    #available_attrs = ('SUMMARY', 'DTSTART', 'DTEND', 'DTSTAMP','UID','SEQUENCE')
    
    compare_events(calendar_new,calendar_old)
    

if __name__ == "__main__":
    main()
