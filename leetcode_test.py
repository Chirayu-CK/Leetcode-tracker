import requests
import pprint as p
import json 
from datetime import datetime, timedelta


def get_user_stats(username):

    url = "https://leetcode.com/graphql"

    query = """
        query userSessionProgress($username: String!) {
            allQuestionsCount { 
                difficulty
                count
            }

            matchedUser(username: $username) { 
                submitStats {  
                    acSubmissionNum { 
                        difficulty 
                        count 
                        submissions
                    }

                    totalSubmissionNum {
                        difficulty 
                        count 
                        submissions
                    }
                }
            }
        }
    """

    r = requests.post(
        url,
        json={
            'query': query,
            'variables': {
                'username': username
            }
        }
    )

    data = r.json()

    if data['data']['matchedUser'] is None:
        return None

    stats = data['data']['matchedUser']['submitStats']['acSubmissionNum']

    solved = {}

    for item in stats:
        solved[item['difficulty']] = item['count']

    return {
        "solved": solved
    }







def get_streak_counter(username):
    url="https://leetcode.com/graphql"
    query="""
    query userProfileCalendar($username: String!, $year: Int) {
      matchedUser(username: $username) {
        userCalendar(year: $year) {
          activeYears
            streak
            totalActiveDays
            dccBadges {
            timestamp
            badge {
            name
             icon
            } } submissionCalendar
            }
            }
            }
    """


    r=requests.post(url, json={'query':query,'variables': {'username':username}})
    data=r.json()
    if data['data']['matchedUser'] is None:
        return None

    stats=data['data']['matchedUser']['userCalendar']
    calendar=json.loads(stats['submissionCalendar'])
    fd=None
    ld=None
    for timestaps, count in calendar.items():
        date=datetime.fromtimestamp(int(timestaps)).date()
        if(fd is None or fd>date):
            fd=date

        if (ld is None or date>ld):
            ld=date

    first_monday=fd-timedelta(days=fd.weekday())
    weeks_count=(ld-first_monday).days//7+1
    weeks=[]
    for i in range(weeks_count):
        weeks.append([0]*7)

    for i in calendar.items():
        timestap=i[0]
        count=i[1]
        date=datetime.fromtimestamp(int(timestap)).date()
        row=date.weekday()
        col=(date-first_monday).days//7
        weeks[col][row]=count

    
    

    
    return {
        "streak": stats["streak"],
        "totalActiveDays": stats["totalActiveDays"],
        "activeYears": stats["activeYears"],
        "dccBadges": stats["dccBadges"],
        "submissionCalendar": stats["submissionCalendar"],
        "weeks":weeks
    }


    

    # p.pprint(data)



    


if __name__ == "__main__":

    username = input("Enter your username: ")

    stats = get_streak_counter(username)

    if stats is None:
        print("Invalid username")
    else:
        p.pprint(stats)

