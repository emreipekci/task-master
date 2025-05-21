console.log("main.js loaded");


document.getElementById('addTaskForm').addEventListener('submit', function(e) {
    e.preventDefault();
        const content = document.getElementById('content').value.trim();
        const dueDate = document.getElementById('dueDate').value;

    console.log("Submitting task:", content);

    if (!content) {
        alert('Task content cannot be empty');
        return;
    }
    
    fetch('/api/tasks', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: content,  due_date: dueDate })
    })
    .then(response => response.json())
    .then(data => {
        if (data.id) {
            const noTasksText = document.getElementById('noTasksText');
            if (noTasksText){
              noTasksText.remove();  
            } 

            const taskRow = document.createElement('tr');
            taskRow.id = `task-${data.id}`;
            taskRow.innerHTML = `
                <td>${data.content}</td>
                <td>${data.due_date ? new Date(data.due_date).toLocaleDateString() : ''}</td>
                <td>
                    <button onclick="deleteTask(${data.id})">Delete</button>
                    <button onclick="editTask(${data.id})">Update</button>
                </td>
            `;
            const tasksBody = document.getElementById('tasksBody');
                if (tasksBody) {
                    tasksBody.appendChild(taskRow);
                } else {
                    console.error('tasksBody element not found!');
            }
            document.getElementById('content').value = '';
            document.getElementById('content').focus();
        } else {
            alert('Failed to add task');
        }
    })
    .catch(error => console.error('Error:', error));
});

function deleteTask(taskId) {
    fetch(`/api/tasks/${taskId}`, {
        method: 'DELETE',
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            const taskRow = document.getElementById(`task-${taskId}`);
            if (taskRow) taskRow.remove();

            const rows = document.querySelectorAll('#tasksBody tr');
            if (rows.length === 0) {
                const msg = document.createElement('h4');
                msg.id = 'noTasksText';
                msg.innerText = 'There are no tasks. Create one below!';
                document.querySelector('.content').insertBefore(msg, document.querySelector('.form'));
            }
        } else {
            alert('Failed to delete task');
        }
    })
    .catch(error => console.error('Error:', error));
}

function editTask(taskId) {
    const taskRow = document.querySelector(`#task-${taskId}`);
    const currentContent = taskRow.querySelector('td:nth-child(1)').innerText;
    const currentDueDate = taskRow.querySelector('td:nth-child(2)').innerText;
    const newContent = prompt('Edit task content:', currentContent);
    const newDueDate = prompt('Edit due date (YYYY-MM-DD):', currentDueDate);

    if (newContent && newContent.trim()) {
        fetch(`/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: newContent.trim(),
                due_date: newDueDate.trim()
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.id) {
                taskRow.querySelector('td:nth-child(1)').innerText = data.content;
                taskRow.querySelector('td:nth-child(2)').innerText = data.due_date
                    ? new Date(data.due_date).toLocaleDateString()
                    : '';
            } else {
                alert(data.error || 'Failed to update task');
            }
        })
        .catch(error => console.error('Error updating task:', error));
    }
}
