import schedule
import datetime
import requests
import time
import json




def get_key():
    config_file = open("canvaskey.json")
    data = json.load(config_file)
    key = data["canvas_token"]
    config_file.close()

    return key

def get_course_id():
    config_file = open("canvaskey.json")
    data = json.load(config_file)
    course = data["course"]
    config_file.close()

    return course



class Announcement():
    def __init__(self, name:str, id:int, date:str):
        self.name = name
        self.id = id
        self.date = date
        self.days_posted = (datetime.datetime.now()-date).days
    
    def __str__(self):
        return f"{self.name} - {self.id} - Posted {self.days_posted} days ago."


key = get_key()
BASE_URL = "https://dexterschools.instructure.com/api/v1"
course_id = get_course_id()

def get_current_announcements():
    discussion_topics_list = requests.get(f"{BASE_URL}/courses/{course_id}/discussion_topics",{"access_token":key,"only_announcements":True})
    data = discussion_topics_list.json()
    
    
    announcement_list = []
    print("\n Obtaining Canvas Course Announcements... \n")
    for i in range(len(data)):
        title = data[i]["title"]
        date = datetime.datetime.strptime(data[i]["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        announcement_id = data[i]["id"]

        announcement = Announcement(title, announcement_id, date)

        announcement_list.append(announcement)
        print(announcement)

    return announcement_list
        
def main():
    print("Starting script...")
    daily_time = "08:00"
    schedule.every().day.at(daily_time).do(daily_job)

    while True:
        schedule.run_pending()
        time.sleep(60)

def daily_job():
    announcement_list = get_current_announcements()
    if announcement_list == []:
        print("No announcements available, skipping today!")
        return
    delete_old_announcements(announcement_list)
    print("Job complete, waiting until tomorrow...")
    return 


def delete_old_announcements(announcement_list:list[Announcement]):
    for announcement in announcement_list:
        if announcement.days_posted > 30:
            x = requests.delete(f"{BASE_URL}/courses/{course_id}/discussion_topics/{announcement.id}",params={"access_token":key})
            response = x.status_code
            print(response)
            if response == 200:
                print(f"Successfully removed {announcement.name}")
            elif response == 401:
                print("Authentication error, unable to delete announcements")
                return
    return


if __name__ == "__main__":
    main()
