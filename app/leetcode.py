import requests
import pprint as p
import json
from datetime import datetime, timedelta


url = "https://leetcode.com/graphql"
REQUEST_TIMEOUT = 10


def _post_graphql(query, variables):
    """
    Safe GraphQL request helper.
    Returns parsed JSON on success, otherwise None.
    """
    try:
        r = requests.post(
            url,
            json={
                "query": query,
                "variables": variables
            },
            timeout=REQUEST_TIMEOUT
        )

        r.raise_for_status()

        data = r.json()

        if not isinstance(data, dict):
            print("LeetCode error: invalid JSON response")
            return None

        if data.get("errors"):
            print("LeetCode GraphQL error:", data["errors"])
            return None

        if "data" not in data:
            print("LeetCode error: 'data' missing in response")
            return None

        return data

    except requests.exceptions.Timeout:
        print("LeetCode request timed out.")
        return None

    except requests.exceptions.ConnectionError:
        print("Unable to connect to LeetCode.")
        return None

    except requests.exceptions.HTTPError as e:
        print("LeetCode HTTP error:", e)
        return None

    except requests.exceptions.RequestException as e:
        print("LeetCode request error:", e)
        return None

    except ValueError as e:
        print("LeetCode JSON decode error:", e)
        return None

    except Exception as e:
        print("Unexpected LeetCode request error:", e)
        return None


def get_user_stats(username):
    if not username:
        return None

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

    data = _post_graphql(
        query,
        {
            "username": username
        }
    )

    if data is None:
        return None

    try:
        matched_user = data["data"].get("matchedUser")

        if matched_user is None:
            return None

        submit_stats = matched_user.get("submitStats")

        if not submit_stats:
            return None

        stats = submit_stats.get("acSubmissionNum")

        if stats is None:
            return None

        solved = {}

        for item in stats:
            difficulty = item.get("difficulty")
            count = item.get("count", 0)

            if difficulty is not None:
                solved[difficulty] = count

        return {
            "solved": solved
        }

    except (KeyError, TypeError, AttributeError) as e:
        print("get_user_stats parsing error:", e)
        return None

    except Exception as e:
        print("get_user_stats unexpected error:", e)
        return None


def get_streak_counter(username):
    if not username:
        return None

    query = """
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
            }
          }
          submissionCalendar
        }
      }
    }
    """

    data = _post_graphql(
        query,
        {
            "username": username
        }
    )

    if data is None:
        return None

    try:
        matched_user = data["data"].get("matchedUser")

        if matched_user is None:
            return None

        stats = matched_user.get("userCalendar")

        if stats is None:
            return None

        submission_calendar = stats.get("submissionCalendar")

        if not submission_calendar:
            calendar = {}
        else:
            try:
                calendar = json.loads(submission_calendar)
            except (json.JSONDecodeError, TypeError) as e:
                print("submissionCalendar JSON error:", e)
                return None

        weeks = []

        # New/empty accounts may have no calendar entries.
        if calendar:
            fd = None
            ld = None

            for timestamp, count in calendar.items():
                try:
                    date = datetime.fromtimestamp(int(timestamp)).date()
                except (ValueError, TypeError, OSError) as e:
                    print("Invalid calendar timestamp:", timestamp, e)
                    continue

                if fd is None or date < fd:
                    fd = date

                if ld is None or date > ld:
                    ld = date

            if fd is not None and ld is not None:
                first_monday = fd - timedelta(days=fd.weekday())
                weeks_count = (ld - first_monday).days // 7 + 1
                today = datetime.now().date()

                for i in range(weeks_count):
                    week = []

                    for j in range(7):
                        date = first_monday + timedelta(
                            weeks=i,
                            days=j
                        )

                        if date > today:
                            week.append(None)
                        else:
                            week.append({
                                "date": date,
                                "count": 0
                            })

                    weeks.append(week)

                for timestamp, count in calendar.items():
                    try:
                        date = datetime.fromtimestamp(int(timestamp)).date()
                    except (ValueError, TypeError, OSError):
                        continue

                    if date > today:
                        continue

                    row = date.weekday()
                    col = (date - first_monday).days // 7

                    if 0 <= col < len(weeks):
                        weeks[col][row] = {
                            "date": date,
                            "count": count
                        }

        return {
            "streak": stats.get("streak", 0),
            "totalActiveDays": stats.get("totalActiveDays", 0),
            "activeYears": stats.get("activeYears", []),
            "dccBadges": stats.get("dccBadges", []),
            "submissionCalendar": stats.get("submissionCalendar", "{}"),
            "weeks": weeks
        }

    except (KeyError, TypeError, AttributeError) as e:
        print("get_streak_counter parsing error:", e)
        return None

    except Exception as e:
        print("get_streak_counter unexpected error:", e)
        return None


def get_topic_stats(username):
    if not username:
        return None

    query = """
    query skillStats($username: String!) {
      matchedUser(username: $username) {
        tagProblemCounts {
          advanced {
            tagName
            tagSlug
            problemsSolved
          }
          intermediate {
            tagName
            tagSlug
            problemsSolved
          }
          fundamental {
            tagName
            tagSlug
            problemsSolved
          }
        }
      }
    }
    """

    data = _post_graphql(
        query,
        {
            "username": username
        }
    )

    if data is None:
        return None

    try:
        matched_user = data["data"].get("matchedUser")

        if matched_user is None:
            return None

        t_data = matched_user.get("tagProblemCounts")

        if not t_data:
            return {}

        topic = {}

        for level in ["fundamental", "intermediate", "advanced"]:
            for item in (t_data.get(level) or []):
                tag_name = item.get("tagName")

                if tag_name:
                    topic[tag_name] = item.get("problemsSolved", 0)

        return topic

    except (KeyError, TypeError, AttributeError) as e:
        print("get_topic_stats parsing error:", e)
        return None

    except Exception as e:
        print("get_topic_stats unexpected error:", e)
        return None


def leetcode_readme(username):
    if not username:
        return None

    query = """
    query userPublicProfile($username: String!) {
      matchedUser(username: $username) {
        isBlocked
        isBlocker
        contestBadge {
          name
          expired
          hoverText
          icon
        }
        username
        githubUrl
        twitterUrl
        linkedinUrl
        profile {
          ranking
          userAvatar
          realName
          aboutMe
          school
          websites
          countryName
          company
          jobTitle
          skillTags
          postViewCount
          postViewCountDiff
          reputation
          reputationDiff
          solutionCountDiff
          categoryDiscussCountDiff
          certificationLevel
          isFollowingMe
          isFollowedByMe
          hideFollowers
          hideFollowing
        }
      }

      ugcArticleUserSolutionArticles(username: $username, skip: 0, first: 0) {
        totalNum
      }

      ugcArticleUserDiscussionArticles(username: $username, skip: 0, first: 0) {
        totalNum
      }
    }
    """

    data = _post_graphql(
        query,
        {
            "username": username
        }
    )

    if data is None:
        return None

    try:
        matched_user = data["data"].get("matchedUser")

        if matched_user is None:
            return None

        profile = matched_user.get("profile")

        if profile is None:
            return None

        # aboutMe can legitimately be None/empty.
        return profile.get("aboutMe") or ""

    except (KeyError, TypeError, AttributeError) as e:
        print("leetcode_readme parsing error:", e)
        return None

    except Exception as e:
        print("leetcode_readme unexpected error:", e)
        return None


def contestrating(username):
    if not username:
        return 0

    query = """
    query userContestRankingInfo($username: String!) {
      userContestRanking(username: $username) {
        attendedContestsCount
        rating
        globalRanking
        totalParticipants
        topPercentage
        badge {
          name
        }
      }

      userContestRankingHistory(username: $username) {
        attended
        trendDirection
        problemsSolved
        totalProblems
        finishTimeInSeconds
        rating
        ranking
        contest {
          title
          startTime
        }
      }
    }
    """

    data = _post_graphql(
        query,
        {
            "username": username
        }
    )

    if data is None:
        return 0

    try:
        history = data["data"].get("userContestRankingHistory")

        if not history:
            return 0

        # Prefer the latest attended contest instead of blindly taking
        # the last history item if LeetCode returns non-attended entries.
        attended_history = [
            item for item in history
            if item and item.get("attended")
        ]

        if not attended_history:
            return 0

        rating = attended_history[-1].get("rating")

        if rating is None:
            return 0

        return rating

    except (KeyError, TypeError, AttributeError) as e:
        print("contestrating parsing error:", e)
        return 0

    except Exception as e:
        print("contestrating unexpected error:", e)
        return 0


if __name__ == "__main__":
    username = input("Enter your username: ").strip()

    if not username:
        print("Username cannot be empty.")
    else:
        stats = contestrating(username)

        if stats is None:
            print("Invalid username")
        else:
            p.pprint(stats)
