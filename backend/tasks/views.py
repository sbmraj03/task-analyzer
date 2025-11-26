from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import TaskSerializer
from .scoring import calculate_priority_score, detect_circular_dependencies
from datetime import date

@api_view(['POST'])
def analyze_tasks(request):
    """
    Analyze and sort tasks by priority score
    """
    tasks_data = request.data.get('tasks', [])
    strategy = request.data.get('strategy', 'smart_balance')
    
    # Validate input
    if not tasks_data:
        return Response(
            {'error': 'No tasks provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check for circular dependencies
    if detect_circular_dependencies(tasks_data):
        return Response(
            {'error': 'Circular dependencies detected'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Calculate priority scores
    analyzed_tasks = []
    for task in tasks_data:
        try:
            score = calculate_priority_score(task, tasks_data, strategy)
            task['priority_score'] = score
            task['priority_explanation'] = generate_explanation(task, score, strategy)
            analyzed_tasks.append(task)
        except Exception as e:
            # Skip invalid tasks
            continue
    
    # Sort by priority score (highest first)
    analyzed_tasks.sort(key=lambda x: x['priority_score'], reverse=True)
    
    return Response({'tasks': analyzed_tasks})


@api_view(['POST'])
def suggest_tasks(request):
    """
    Return top 3 tasks user should work on today
    """
    tasks_data = request.data.get('tasks', [])
    strategy = request.data.get('strategy', 'smart_balance')
    
    if not tasks_data:
        return Response(
            {'error': 'No tasks provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Calculate scores
    analyzed_tasks = []
    for task in tasks_data:
        try:
            score = calculate_priority_score(task, tasks_data, strategy)
            task['priority_score'] = score
            task['priority_explanation'] = generate_explanation(task, score, strategy)
            analyzed_tasks.append(task)
        except Exception:
            continue
    
    # Sort and get top 3
    analyzed_tasks.sort(key=lambda x: x['priority_score'], reverse=True)
    top_tasks = analyzed_tasks[:3]
    
    return Response({'suggestions': top_tasks})


def generate_explanation(task, score, strategy):
    """Generate human-readable explanation for the priority score"""
    
    due_date = task.get('due_date')
    importance = task.get('importance', 5)
    estimated_hours = task.get('estimated_hours', 0)
    
    # Convert due_date if needed
    if isinstance(due_date, str):
        from datetime import datetime
        due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
    
    today = date.today()
    days_until_due = (due_date - today).days
    
    # Build explanation based on key factors
    reasons = []
    
    if days_until_due < 0:
        reasons.append("OVERDUE")
    elif days_until_due == 0:
        reasons.append("Due today")
    elif days_until_due <= 3:
        reasons.append("Due very soon")
    
    if importance >= 8:
        reasons.append("High importance")
    elif importance <= 3:
        reasons.append("Low importance")
    
    if estimated_hours <= 2:
        reasons.append("Quick win")
    
    if strategy == 'fastest_wins':
        reasons.append("Low effort prioritized")
    elif strategy == 'high_impact':
        reasons.append("Impact prioritized")
    elif strategy == 'deadline_driven':
        reasons.append("Deadline prioritized")
    
    if not reasons:
        reasons.append("Balanced priority")
    
    return " • ".join(reasons)