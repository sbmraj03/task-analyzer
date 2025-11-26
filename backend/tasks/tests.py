from django.test import TestCase
from datetime import date, timedelta
from .scoring import (
    calculate_priority_score,
    calculate_smart_balance,
    detect_circular_dependencies,
    count_blocked_tasks
)

class ScoringAlgorithmTests(TestCase):
    
    def test_overdue_task_gets_high_score(self):
        """Overdue tasks should receive high urgency score"""
        task = {
            'id': 1,
            'title': 'Overdue task',
            'due_date': (date.today() - timedelta(days=2)).strftime('%Y-%m-%d'),
            'estimated_hours': 3,
            'importance': 7,
            'dependencies': []
        }
        
        score = calculate_priority_score(task, [task], 'smart_balance')
        
        # Should get 40 urgency + 24.5 importance + 10 effort = 74.5+
        self.assertGreater(score, 70)
    
    
    def test_quick_win_bonus(self):
        """Tasks with low effort should get quick win bonus"""
        quick_task = {
            'id': 1,
            'title': 'Quick task',
            'due_date': (date.today() + timedelta(days=5)).strftime('%Y-%m-%d'),
            'estimated_hours': 1.5,  # Under 2 hours
            'importance': 5,
            'dependencies': []
        }
        
        long_task = {
            'id': 2,
            'title': 'Long task',
            'due_date': (date.today() + timedelta(days=5)).strftime('%Y-%m-%d'),
            'estimated_hours': 10,  # Over 8 hours
            'importance': 5,
            'dependencies': []
        }
        
        quick_score = calculate_priority_score(quick_task, [quick_task], 'smart_balance')
        long_score = calculate_priority_score(long_task, [long_task], 'smart_balance')
        
        # Quick task should score higher due to effort bonus
        self.assertGreater(quick_score, long_score)
    
    
    def test_dependency_blocking_increases_priority(self):
        """Tasks that block other tasks should get priority boost"""
        blocking_task = {
            'id': 1,
            'title': 'Blocking task',
            'due_date': (date.today() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'estimated_hours': 3,
            'importance': 5,
            'dependencies': []
        }
        
        dependent_task = {
            'id': 2,
            'title': 'Dependent task',
            'due_date': (date.today() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'estimated_hours': 3,
            'importance': 5,
            'dependencies': [1]  # Depends on task 1
        }
        
        all_tasks = [blocking_task, dependent_task]
        
        blocking_score = calculate_priority_score(blocking_task, all_tasks, 'smart_balance')
        dependent_score = calculate_priority_score(dependent_task, all_tasks, 'smart_balance')
        
        # Blocking task should score higher
        self.assertGreater(blocking_score, dependent_score)
    
    
    def test_circular_dependency_detection(self):
        """Should detect circular dependencies"""
        tasks = [
            {
                'id': 1,
                'title': 'Task A',
                'due_date': '2025-12-01',
                'estimated_hours': 2,
                'importance': 5,
                'dependencies': [2]  # Depends on task 2
            },
            {
                'id': 2,
                'title': 'Task B',
                'due_date': '2025-12-01',
                'estimated_hours': 2,
                'importance': 5,
                'dependencies': [1]  # Depends on task 1 (circular!)
            }
        ]
        
        has_circular = detect_circular_dependencies(tasks)
        self.assertTrue(has_circular)
    
    
    def test_no_circular_dependency(self):
        """Should return False when no circular dependencies"""
        tasks = [
            {
                'id': 1,
                'title': 'Task A',
                'due_date': '2025-12-01',
                'estimated_hours': 2,
                'importance': 5,
                'dependencies': []
            },
            {
                'id': 2,
                'title': 'Task B',
                'due_date': '2025-12-01',
                'estimated_hours': 2,
                'importance': 5,
                'dependencies': [1]  # Depends on task 1 (valid)
            }
        ]
        
        has_circular = detect_circular_dependencies(tasks)
        self.assertFalse(has_circular)
    
    
    def test_missing_importance_returns_zero(self):
        """Tasks with invalid data should return 0 score"""
        invalid_task = {
            'id': 1,
            'title': 'Invalid task',
            'due_date': '2025-12-01',
            'estimated_hours': 2,
            'importance': 15,  # Invalid: over 10
            'dependencies': []
        }
        
        score = calculate_priority_score(invalid_task, [invalid_task], 'smart_balance')
        self.assertEqual(score, 0)
    
    
    def test_different_strategies(self):
        """Test that different strategies produce different scores"""
        task = {
            'id': 1,
            'title': 'Test task',
            'due_date': (date.today() + timedelta(days=5)).strftime('%Y-%m-%d'),
            'estimated_hours': 2,
            'importance': 8,
            'dependencies': []
        }
        
        smart_score = calculate_priority_score(task, [task], 'smart_balance')
        fastest_score = calculate_priority_score(task, [task], 'fastest_wins')
        impact_score = calculate_priority_score(task, [task], 'high_impact')
        deadline_score = calculate_priority_score(task, [task], 'deadline_driven')
        
        # All strategies should return valid scores
        self.assertGreater(smart_score, 0)
        self.assertGreater(fastest_score, 0)
        self.assertGreater(impact_score, 0)
        self.assertGreater(deadline_score, 0)
        
        # High impact should prioritize importance most
        self.assertEqual(impact_score, 80)  # 8 * 10