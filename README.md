# Smart Task Analyzer

A web application that helps you decide which tasks to work on first by giving them priority scores.

## What This App Does

- Takes your tasks (with due dates, time needed, and importance)
- Calculates a priority score for each task
- Sorts them from most important to least important
- Shows you the top 3 tasks you should work on today

## How to Set Up and Run

### Step 1: Install Python
Make sure you have Python 3.8 or higher installed on your computer.

### Step 2: Set Up the Project

Open terminal and run these commands:

```bash
# Go to the backend folder
cd backend

# Create a virtual environment
python -m venv venv

# Turn on the virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install required packages
pip install django djangorestframework django-cors-headers
```

### Step 3: Set Up the Database

```bash
# Still in the backend folder
python manage.py makemigrations
python manage.py migrate
```

### Step 4: Start the Server

```bash
python manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`

### Step 5: Open the Frontend

1. Keep the server running
2. Open the file `frontend/index.html` in your web browser
3. Start using the app!

## How the Priority Scoring Works

The app uses a "Smart Balance" algorithm that gives each task a score out of 100 points. Higher score = higher priority.  
At a high level, every task is converted into a small set of numeric signals (urgency, importance, effort, and how many
other tasks it unblocks). Those signals are normalized into point ranges and then added together into a single score.  
This makes the algorithm easy to reason about and easy to tune: changing how much a factor matters is just changing how
many points it can contribute.

Smart Balance is designed to balance short‑term urgency (deadlines and overdue work) with long‑term impact (importance),
while still giving credit to "quick wins" and tasks that unlock others. Urgency and importance get the largest share of
the score, because missing a critical deadline or ignoring highly important work usually has the biggest cost. Effort is
treated as a modifier: very small tasks get a bonus so you can clear them quickly, but long tasks are not penalized too
heavily if they are truly important or urgent. Finally, dependency information is used to slightly boost tasks that block
others, so the system naturally encourages you to clear bottlenecks early.

If input data is clearly invalid (for example, importance outside the 1–10 range or missing required fields), the
algorithm returns a score of `0`. This keeps bad data from accidentally floating to the top and simplifies error
handling in the API and frontend. For dependencies, the backend first checks for simple circular references (A depends on
B and B depends on A). If a circular dependency is found, the API returns a clear error instead of trying to guess a
score from contradictory data. This decision favors correctness and transparency over being overly "smart" with broken
input. For valid dependency chains, the algorithm counts how many tasks are blocked by a given task and converts that
into a small bonus.

On top of Smart Balance, the backend exposes three simpler strategies: *Fastest Wins* (favoring low effort), *High
Impact* (pure importance), and *Deadline Driven* (pure urgency). All four strategies share the same task structure and
validation rules but use different scoring formulas, which makes the system easy to extend. For example, you could add a
fifth strategy later that heavily favors dependencies or that behaves differently on weekends—without changing the
frontend or the task model.

### The 4 Factors

**1. Urgency (40 points max)**
- How soon is the task due?
- Overdue tasks get 40 points
- Due today gets 35 points
- Due in 1-3 days gets 30 points
- Due in 4-7 days gets 20 points
- Tasks due later get fewer points

**2. Importance (35 points max)**
- Your importance rating (1-10) multiplied by 3.5
- Example: Rating of 10 = 35 points, Rating of 5 = 17.5 points

**3. Effort (15 points max)**
- Quick tasks get bonus points (we call these "quick wins")
- 1-2 hours = 15 points
- 3-4 hours = 10 points
- 5-8 hours = 5 points
- More than 8 hours = 2 points

**4. Dependencies (10 points max)**
- If other tasks are waiting for this task, it gets extra points
- 5 points for each task that depends on it (maximum 10 points)

### Example:

**Task: "Fix login bug"**
- Due tomorrow → 30 urgency points
- Importance 9/10 → 31.5 importance points
- Takes 2 hours → 15 quick win points
- 1 other task waiting → 5 dependency points
- **Total Score: 81.5** (HIGH PRIORITY!)

### Different Sorting Strategies:

The app has 4 ways to sort tasks:

1. **Smart Balance** - Considers all factors equally (recommended)
2. **Fastest Wins** - Focuses on tasks that take less time
3. **High Impact** - Focuses on importance rating only
4. **Deadline Driven** - Focuses on due dates only

## Design Decisions and Trade-offs

### Why These Weights?

- **Urgency gets 40%**: Deadlines are hard limits, missing them has consequences
- **Importance gets 35%**: What you work on matters as much as when you do it
- **Effort gets 15%**: Quick wins build momentum and motivation
- **Dependencies get 10%**: Don't block teammates, but not always the top priority

### Handling Edge Cases:

**1. Overdue Tasks**
- Get maximum urgency score (40 points)
- Still considers importance so critical overdue tasks rank higher than minor ones

**2. Missing Data**
- If a task is missing required information or has invalid data (like importance 15), the score returns 0
- This prevents errors and moves invalid tasks to the bottom

**3. Circular Dependencies**
- If Task A depends on Task B, and Task B depends on Task A, the API returns an error
- The algorithm checks for this before calculating scores

**4. Multiple Strategies**
- Users can switch between strategies based on their needs
- Example: Use "Deadline Driven" during crunch time, "Fastest Wins" when feeling overwhelmed

### Trade-offs Made:

**Simple vs Complex**
- Chose a simple linear scoring system instead of complex machine learning
- Easier to understand and explain to users
- Faster to calculate

**Fixed Weights vs User Preferences**
- Used fixed weights for each factor
- Could add user customization in the future (let users adjust importance of urgency vs importance)

**Dependency Detection**
- Only checks for direct circular dependencies (A→B, B→A)
- Doesn't check for longer chains (A→B→C→A)
- Simpler and faster, covers most real-world cases

## Time Breakdown

Approximate time spent on each part of the assignment (within the 3–4 hour target):

- **Algorithm design & scoring experiments**: ~1.5 hours  
- **Backend APIs (`analyze`, `suggest`) + validation & CORS**: ~1.0 hour  
- **Frontend UI (form, strategies dropdown, results view)**: ~1.0 hour  
- **Unit tests for scoring & dependency handling**: ~0.5 hour  
- **Debugging, manual testing, and documentation**: ~0.5 hour  

Total: ~4.5 hours.

## Running Tests

To run the unit tests:

```bash
cd backend
python manage.py test tasks
```

You should see 7 tests pass:
- Overdue tasks get high urgency scores
- Quick wins (low effort) get a bonus
- Tasks that block others get a higher score
- Circular dependencies are detected
- Valid dependency chains are allowed
- Invalid data returns a score of 0
- Different strategies all return valid scores

## Bonus Challenges

From the bonus list in the assignment, I implemented:

- **Unit Tests**: The scoring logic and dependency detection are covered by 7 unit tests in `backend/tasks/tests.py`.

I did **not** implement the other bonuses (graph visualization, date intelligence beyond simple day counts, Eisenhower
matrix, or learning system) to keep focus on the core assignment within the time limit.

## Future Improvements

If I had more time, I would add:

1. **Save Tasks to Database**
   - Currently tasks are only stored temporarily in the browser
   - Add ability to save and load tasks from the database

2. **User Accounts**
   - Let multiple people use the app with their own task lists
   - Add login and authentication

3. **Smart Date Handling**
   - Skip weekends when counting days until due
   - Account for holidays
   - Handle different time zones

## Technologies Used

- **Backend**: Python 3.x, Django 4.x, Django REST Framework
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Database**: SQLite (Django default)

## Project Structure

```
task-analyzer/
├── backend/
│   ├── manage.py
│   ├── task_analyzer/          # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── tasks/                  # Main app
│   │   ├── models.py           # Task database model
│   │   ├── views.py            # API endpoints
│   │   ├── serializers.py      # Data conversion
│   │   ├── scoring.py          # Priority algorithm
│   │   ├── urls.py             # URL routing
│   │   └── tests.py            # Unit tests
├── frontend/
│   ├── index.html              # Main page
│   ├── styles.css              # Styling
│   └── script.js               # User interactions
└── README.md                   # This file
```

## API Endpoints

**POST /api/tasks/analyze/**
- Accepts: List of tasks and strategy
- Returns: All tasks sorted by priority with scores

**POST /api/tasks/suggest/**
- Accepts: List of tasks and strategy
- Returns: Top 3 tasks to work on today

