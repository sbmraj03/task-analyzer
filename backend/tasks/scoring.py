from datetime import date, timedelta

def calculate_priority_score(task_data, all_tasks=None, strategy='smart_balance'):
    """
    Calculate priority score for a task based on multiple factors
    Returns a score between 0-100 (higher = more priority)
    """
    
    # Extract task data
    due_date = task_data.get('due_date')
    estimated_hours = task_data.get('estimated_hours', 0)
    importance = task_data.get('importance', 5)
    dependencies = task_data.get('dependencies', [])
    
    # Handle missing or invalid data
    if not due_date or importance < 1 or importance > 10:
        return 0
    
    # Convert due_date string to date object if needed
    if isinstance(due_date, str):
        from datetime import datetime
        due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
    
    today = date.today()
    days_until_due = (due_date - today).days
    
    # Different scoring strategies
    if strategy == 'fastest_wins':
        return calculate_fastest_wins(estimated_hours, importance)
    elif strategy == 'high_impact':
        return calculate_high_impact(importance)
    elif strategy == 'deadline_driven':
        return calculate_deadline_driven(days_until_due, importance)
    else:  # smart_balance
        return calculate_smart_balance(days_until_due, importance, estimated_hours, dependencies, all_tasks)


def calculate_fastest_wins(estimated_hours, importance):
    """Prioritize low-effort tasks"""
    # Lower hours = higher score
    effort_score = max(0, 50 - (estimated_hours * 5))
    importance_score = importance * 5
    return effort_score + importance_score


def calculate_high_impact(importance):
    """Prioritize importance over everything"""
    return importance * 10


def calculate_deadline_driven(days_until_due, importance):
    """Prioritize based on due date"""
    if days_until_due < 0:  # Overdue
        urgency_score = 100
    elif days_until_due == 0:  # Due today
        urgency_score = 90
    elif days_until_due <= 3:
        urgency_score = 70
    elif days_until_due <= 7:
        urgency_score = 50
    else:
        urgency_score = max(0, 40 - days_until_due)
    
    # Add some importance weight
    return urgency_score + (importance * 2)


def calculate_smart_balance(days_until_due, importance, estimated_hours, dependencies, all_tasks):
    """Balance all factors intelligently"""
    
    # 1. Urgency Score (0-40 points)
    if days_until_due < 0:  # Overdue
        urgency_score = 40
    elif days_until_due == 0:  # Due today
        urgency_score = 35
    elif days_until_due <= 3:
        urgency_score = 30
    elif days_until_due <= 7:
        urgency_score = 20
    else:
        urgency_score = max(0, 15 - days_until_due * 0.5)
    
    # 2. Importance Score (0-35 points)
    importance_score = importance * 3.5
    
    # 3. Effort Score (0-15 points) - Quick wins get bonus
    if estimated_hours <= 2:
        effort_score = 15
    elif estimated_hours <= 4:
        effort_score = 10
    elif estimated_hours <= 8:
        effort_score = 5
    else:
        effort_score = 2
    
    # 4. Dependency Score (0-10 points)
    dependency_score = count_blocked_tasks(task_data, all_tasks) * 5
    dependency_score = min(dependency_score, 10)  # Cap at 10
    
    total_score = urgency_score + importance_score + effort_score + dependency_score
    return round(total_score, 2)


def count_blocked_tasks(task, all_tasks):
    """Count how many tasks are blocked by this task"""
    if not all_tasks:
        return 0
    
    task_id = task.get('id')
    blocked_count = 0
    
    for other_task in all_tasks:
        if task_id in other_task.get('dependencies', []):
            blocked_count += 1
    
    return blocked_count


def detect_circular_dependencies(tasks):
    """Check if there are circular dependencies"""
    # Simple check: if task A depends on task B and B depends on A
    for task in tasks:
        task_id = task.get('id')
        dependencies = task.get('dependencies', [])
        
        for dep_id in dependencies:
            # Find the dependency task
            dep_task = next((t for t in tasks if t.get('id') == dep_id), None)
            if dep_task:
                # Check if dependency depends back on this task
                if task_id in dep_task.get('dependencies', []):
                    return True
    
    return False