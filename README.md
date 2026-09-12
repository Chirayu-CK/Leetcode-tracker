# LeetCode Tracker

A Flask-based web application that allows users to connect their LeetCode account, view coding statistics, track streaks and topic progress, and compare contest ratings with friends inside private rooms.

## Features

* Google authentication using Supabase
* LeetCode account verification
* Solved problem statistics

  * Easy
  * Medium
  * Hard
* Current streak
* Total active days
* Submission heatmap
* Active years
* LeetCode badges
* Topic-wise solved problem statistics
* Contest rating tracking
* Create private rooms
* Join rooms using a 6-character room code
* Compare LeetCode contest ratings with room members
* Room-based leaderboard
* Logout support
* Error handling for LeetCode API and Supabase failures

## Tech Stack

### Backend

* Python
* Flask
* Gunicorn

### Database and Authentication

* Supabase
* PostgreSQL
* Google OAuth

### APIs

* LeetCode GraphQL API

### Frontend

* HTML
* CSS
* JavaScript
* Jinja2
* Chart.js

## Project Structure

```text
leetcode-tracker/
│
├── app/
│   ├── templates/
│   ├── static/
│   ├── __init__.py
│   └── leetcode.py
│
├── config.py
├── run.py
├── requirements.txt
├── README.md
├── .gitignore
└── .env
```

## Installation

Clone the repository:

```bash
git clone https://github.com/Chirayu-CK/Leetcode-tracker.git
cd Leetcode-tracker
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it.

Linux/macOS:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the root directory:

```env
FLASK_SECRET_KEY=your_secret_key
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
OAUTH_REDIRECT_URL=http://localhost:5000/auth/callback
```

Do not commit the `.env` file to GitHub.

## Run Locally

Using Flask:

```bash
python run.py
```

The application will run at:

```text
http://localhost:5000
```

For production-style local testing with Gunicorn:

```bash
gunicorn run:app
```

The application will normally run at:

```text
http://127.0.0.1:8000
```

If using Gunicorn locally, update:

```env
OAUTH_REDIRECT_URL=http://localhost:8000/auth/callback
```

## Authentication Flow

1. User clicks **Login with Google**
2. Google OAuth authentication is handled through Supabase
3. The application creates or retrieves the user's profile
4. The user connects their LeetCode account
5. A verification key is generated
6. The user places the verification key in their LeetCode profile About section
7. The application verifies ownership of the LeetCode account
8. The user is redirected to their dashboard

## LeetCode Data

The application uses LeetCode's GraphQL API to retrieve:

* Solved problem counts
* Submission calendar
* Current streak
* Active days
* Active years
* Badges
* Topic statistics
* Contest rating history

Network errors, timeouts, invalid responses, and missing data are handled to prevent the application from crashing.

## Rooms

Users can create private rooms and receive a unique 6-character join code.

Example:

```text
A7K2P9
```

Other users can enter this code to join the room.

Each room displays a leaderboard based on the members' latest LeetCode contest ratings.

## Database Tables

### profiles

Stores application users and their connected LeetCode account.

Important fields:

```text
id
email
leetcode_username
leetcode_verified
created_at
```

### rooms

Stores created rooms.

Important fields:

```text
id
name
join_code
created_by
```

### room_members

Stores the relationship between users and rooms.

Important fields:

```text
room_id
user_id
joined_at
```

## Recommended Database Constraints

Room codes should be unique:

```sql
ALTER TABLE rooms
ADD CONSTRAINT rooms_join_code_unique
UNIQUE (join_code);
```

A user should only exist once inside the same room:

```sql
ALTER TABLE room_members
ADD CONSTRAINT room_members_unique
UNIQUE (room_id, user_id);
```

## Deployment

The application can be deployed using services such as Render.

Production start command:

```bash
gunicorn run:app
```

Required environment variables:

```text
FLASK_SECRET_KEY
SUPABASE_URL
SUPABASE_ANON_KEY
OAUTH_REDIRECT_URL
```

For production, `OAUTH_REDIRECT_URL` should point to the deployed application:

```text
https://your-domain.onrender.com/auth/callback
```

The same callback URL must also be configured in the Supabase authentication settings.

## Future Improvements

* Friend system
* Direct user comparison
* Language statistics
* Contest history graphs
* Improved room leaderboards
* Global ranking system
* More profile analytics
* UI improvements
* Caching LeetCode API responses

## Author

**Chirayu Kale**

GitHub: `Chirayu-CK`

## Disclaimer

This project is not affiliated with or officially supported by LeetCode.
# LeetCode Tracker

A Flask-based web application that allows users to connect their LeetCode account, view coding statistics, track streaks and topic progress, and compare contest ratings with friends inside private rooms.

## Features

* Google authentication using Supabase
* LeetCode account verification
* Solved problem statistics

  * Easy
  * Medium
  * Hard
* Current streak
* Total active days
* Submission heatmap
* Active years
* LeetCode badges
* Topic-wise solved problem statistics
* Contest rating tracking
* Create private rooms
* Join rooms using a 6-character room code
* Compare LeetCode contest ratings with room members
* Room-based leaderboard
* Logout support
* Error handling for LeetCode API and Supabase failures

## Tech Stack

### Backend

* Python
* Flask
* Gunicorn

### Database and Authentication

* Supabase
* PostgreSQL
* Google OAuth

### APIs

* LeetCode GraphQL API

### Frontend

* HTML
* CSS
* JavaScript
* Jinja2
* Chart.js

## Project Structure

```text
leetcode-tracker/
│
├── app/
│   ├── templates/
│   ├── static/
│   ├── __init__.py
│   └── leetcode.py
│
├── config.py
├── run.py
├── requirements.txt
├── README.md
├── .gitignore
└── .env
```

## Installation

Clone the repository:

```bash
git clone https://github.com/Chirayu-CK/Leetcode-tracker.git
cd Leetcode-tracker
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it.

Linux/macOS:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the root directory:

```env
FLASK_SECRET_KEY=your_secret_key
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
OAUTH_REDIRECT_URL=http://localhost:5000/auth/callback
```

Do not commit the `.env` file to GitHub.

## Run Locally

Using Flask:

```bash
python run.py
```

The application will run at:

```text
http://localhost:5000
```

For production-style local testing with Gunicorn:

```bash
gunicorn run:app
```

The application will normally run at:

```text
http://127.0.0.1:8000
```

If using Gunicorn locally, update:

```env
OAUTH_REDIRECT_URL=http://localhost:8000/auth/callback
```

## Authentication Flow

1. User clicks **Login with Google**
2. Google OAuth authentication is handled through Supabase
3. The application creates or retrieves the user's profile
4. The user connects their LeetCode account
5. A verification key is generated
6. The user places the verification key in their LeetCode profile About section
7. The application verifies ownership of the LeetCode account
8. The user is redirected to their dashboard

## LeetCode Data

The application uses LeetCode's GraphQL API to retrieve:

* Solved problem counts
* Submission calendar
* Current streak
* Active days
* Active years
* Badges
* Topic statistics
* Contest rating history

Network errors, timeouts, invalid responses, and missing data are handled to prevent the application from crashing.

## Rooms

Users can create private rooms and receive a unique 6-character join code.

Example:

```text
A7K2P9
```

Other users can enter this code to join the room.

Each room displays a leaderboard based on the members' latest LeetCode contest ratings.

## Database Tables

### profiles

Stores application users and their connected LeetCode account.

Important fields:

```text
id
email
leetcode_username
leetcode_verified
created_at
```

### rooms

Stores created rooms.

Important fields:

```text
id
name
join_code
created_by
```

### room_members

Stores the relationship between users and rooms.

Important fields:

```text
room_id
user_id
joined_at
```

## Recommended Database Constraints

Room codes should be unique:

```sql
ALTER TABLE rooms
ADD CONSTRAINT rooms_join_code_unique
UNIQUE (join_code);
```

A user should only exist once inside the same room:

```sql
ALTER TABLE room_members
ADD CONSTRAINT room_members_unique
UNIQUE (room_id, user_id);
```

## Deployment

The application can be deployed using services such as Render.

Production start command:

```bash
gunicorn run:app
```

Required environment variables:

```text
FLASK_SECRET_KEY
SUPABASE_URL
SUPABASE_ANON_KEY
OAUTH_REDIRECT_URL
```

For production, `OAUTH_REDIRECT_URL` should point to the deployed application:

```text
https://your-domain.onrender.com/auth/callback
```

The same callback URL must also be configured in the Supabase authentication settings.

## Future Improvements

* Friend system
* Direct user comparison
* Language statistics
* Contest history graphs
* Improved room leaderboards
* Global ranking system
* More profile analytics
* UI improvements
* Caching LeetCode API responses

## Author

**Chirayu Kale**

GitHub: `Chirayu-CK`

## Disclaimer

This project is not affiliated with or officially supported by LeetCode.

LeetCode data is accessed through publicly available GraphQL endpoints and may change if LeetCode modifies its API.
