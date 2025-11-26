// Store tasks in memory
let tasks = [];
let nextTaskId = 1;

// Add a single task
function addTask() {
    const title = document.getElementById('taskTitle').value.trim();
    const dueDate = document.getElementById('taskDueDate').value;
    const hours = parseFloat(document.getElementById('taskHours').value);
    const importance = parseInt(document.getElementById('taskImportance').value);
    
    // Validate inputs
    if (!title || !dueDate || !hours || !importance) {
        showError('Please fill in all fields');
        return;
    }
    
    if (importance < 1 || importance > 10) {
        showError('Importance must be between 1 and 10');
        return;
    }
    
    // Create task object
    const task = {
        id: nextTaskId++,
        title: title,
        due_date: dueDate,
        estimated_hours: hours,
        importance: importance,
        dependencies: []
    };
    
    tasks.push(task);
    
    // Clear form
    document.getElementById('taskTitle').value = '';
    document.getElementById('taskDueDate').value = '';
    document.getElementById('taskHours').value = '';
    document.getElementById('taskImportance').value = '';
    
    updateTasksList();
    hideError();
}

// Load tasks from JSON input
function loadBulkTasks() {
    const bulkInput = document.getElementById('bulkTasks').value.trim();
    
    if (!bulkInput) {
        showError('Please enter JSON tasks');
        return;
    }
    
    try {
        const parsedTasks = JSON.parse(bulkInput);
        
        if (!Array.isArray(parsedTasks)) {
            showError('JSON must be an array of tasks');
            return;
        }
        
        // Validate each task
        for (let task of parsedTasks) {
            if (!task.title || !task.due_date || !task.estimated_hours || !task.importance) {
                showError('Each task must have title, due_date, estimated_hours, and importance');
                return;
            }
        }
        
        tasks = parsedTasks;
        
        // Update nextTaskId to avoid conflicts
        const maxId = Math.max(...tasks.map(t => t.id || 0), 0);
        nextTaskId = maxId + 1;
        
        document.getElementById('bulkTasks').value = '';
        updateTasksList();
        hideError();
        
    } catch (error) {
        showError('Invalid JSON format: ' + error.message);
    }
}

// Update the tasks list display
function updateTasksList() {
    const tasksList = document.getElementById('tasksList');
    const taskCount = document.getElementById('taskCount');
    
    taskCount.textContent = tasks.length;
    
    if (tasks.length === 0) {
        tasksList.innerHTML = '<p style="color: #666; padding: 10px;">No tasks yet. Add some tasks to get started!</p>';
        return;
    }
    
    tasksList.innerHTML = tasks.map(task => `
        <div class="task-item">
            <div class="task-item-info">
                <strong>${task.title}</strong>
                <div class="task-item-details">
                    Due: ${task.due_date} | Hours: ${task.estimated_hours} | Importance: ${task.importance}/10
                </div>
            </div>
            <button class="btn-delete" onclick="deleteTask(${task.id})">Delete</button>
        </div>
    `).join('');
}

// Delete a task
function deleteTask(taskId) {
    tasks = tasks.filter(task => task.id !== taskId);
    updateTasksList();
    
    // Hide results if no tasks left
    if (tasks.length === 0) {
        document.getElementById('results').classList.add('hidden');
    }
}

// Analyze tasks by calling the API
async function analyzeTasks() {
    if (tasks.length === 0) {
        showError('Please add some tasks first');
        return;
    }
    
    const strategy = document.getElementById('strategy').value;
    
    // Show loading
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('results').classList.add('hidden');
    hideError();
    
    try {
        // Call analyze API
        const analyzeResponse = await fetch('http://127.0.0.1:8000/api/tasks/analyze/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tasks: tasks,
                strategy: strategy
            })
        });
        
        if (!analyzeResponse.ok) {
            throw new Error('Failed to analyze tasks');
        }
        
        const analyzeData = await analyzeResponse.json();
        
        // Call suggest API
        const suggestResponse = await fetch('http://127.0.0.1:8000/api/tasks/suggest/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tasks: tasks,
                strategy: strategy
            })
        });
        
        if (!suggestResponse.ok) {
            throw new Error('Failed to get suggestions');
        }
        
        const suggestData = await suggestResponse.json();
        
        // Display results
        displayResults(analyzeData.tasks, suggestData.suggestions);
        
    } catch (error) {
        showError('Error analyzing tasks: ' + error.message);
    } finally {
        document.getElementById('loading').classList.add('hidden');
    }
}

// Display the results
function displayResults(sortedTasks, suggestions) {
    const resultsSection = document.getElementById('results');
    const topSuggestions = document.getElementById('topSuggestions');
    const sortedTasksDiv = document.getElementById('sortedTasks');
    
    // Display top 3 suggestions
    topSuggestions.innerHTML = '<h3>🎯 Top 3 Recommendations</h3>' + 
        suggestions.map((task, index) => `
            <div class="suggestion-card">
                <h3>#${index + 1}: ${task.title}</h3>
                <div style="margin: 10px 0;">
                    <span class="suggestion-badge">Score: ${task.priority_score}</span>
                    <span class="suggestion-badge">Due: ${task.due_date}</span>
                    <span class="suggestion-badge">${task.estimated_hours}h</span>
                </div>
                <p><strong>Why:</strong> ${task.priority_explanation}</p>
            </div>
        `).join('');
    
    // Display all sorted tasks
    sortedTasksDiv.innerHTML = '<h3>All Tasks (Sorted by Priority)</h3>' +
        sortedTasks.map(task => {
            const priorityLevel = getPriorityLevel(task.priority_score);
            return `
                <div class="task-card">
                    <div class="task-card-header">
                        <div class="task-title">${task.title}</div>
                        <div class="priority-badge priority-${priorityLevel}">
                            ${priorityLevel.toUpperCase()} - ${task.priority_score}
                        </div>
                    </div>
                    <div class="task-details">
                        <div>📅 Due: ${task.due_date}</div>
                        <div>⏱️ Effort: ${task.estimated_hours} hours</div>
                        <div>⭐ Importance: ${task.importance}/10</div>
                    </div>
                    <div class="task-explanation">
                        💡 ${task.priority_explanation}
                    </div>
                </div>
            `;
        }).join('');
    
    resultsSection.classList.remove('hidden');
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Determine priority level based on score
function getPriorityLevel(score) {
    if (score >= 70) return 'high';
    if (score >= 40) return 'medium';
    return 'low';
}

// Show error message
function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = '⚠️ ' + message;
    errorDiv.classList.remove('hidden');
}

// Hide error message
function hideError() {
    document.getElementById('errorMessage').classList.add('hidden');
}

// Set default date to tomorrow
window.onload = function() {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const dateString = tomorrow.toISOString().split('T')[0];
    document.getElementById('taskDueDate').value = dateString;
};