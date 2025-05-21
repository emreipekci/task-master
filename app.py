from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timezone
from flask_cors import CORS

app = Flask(__name__)
CORS(app) #Enable CORS for all domains (GitHub Pages needs this)

#Configure SQLite database
import os
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'test.db')

#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#Define the Todo model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    due_date = db.Column(db.Date)

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'completed': bool(self.completed),
            'date_created': self.date_created.isoformat(),
            'due_date': self.due_date.isoformat() if self.due_date else None
        }
    
with app.app_context():
    db.create_all()

#API ROUTES
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content'].strip()
        if not task_content:
            tasks = Todo.query.order_by(Todo.date_created).all()
            return render_template("index.html", tasks=tasks, error="Task content cannot be empty")
        
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template("index.html", tasks=tasks)
    
@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)    
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'
    
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']
        due_date_str = request.form['due_date']

        if due_date_str:
            task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        else:
            task.due_date = None

        try:
            db.session.commit()
            return redirect(url_for('index'))
        except:
            return 'There was an issue updating your task'
        
    else:
        return render_template('update.html', task=task) 
    



# --- JSON API ROUTES for frontend integration---

# Get all tasks (JSON)
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = Todo.query.order_by(Todo.date_created).all()
    return jsonify([task.to_dict() for task in tasks])

# Create a new task
@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()

    content = data.get('content', '').strip()
    due_date_str = data.get('due_date', '').strip()

    if not content:
        return jsonify({'error': 'Task content cannot be empty'}), 400
    
    due_date = None
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid due date format. Use YYYY-MM-DD'}), 400
        
    if due_date and due_date < date.today():
        return jsonify({'error': 'Due date cannot be in the past'}), 400

    new_task = Todo(content=content, due_date=due_date)

    try:
        db.session.add(new_task)
        db.session.commit()
        return jsonify(new_task.to_dict()), 201
    except:
        return jsonify({'error': 'Failed to create task'}), 500

# Update a task (e.g., content or completed)
@app.route('/api/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    task = Todo.query.get_or_404(id)
    data = request.get_json()
    task.content = data.get('content', task.content)
    task.completed = int(data.get('completed', task.completed))

    due_date_str = data.get('due_date')
    if due_date_str is not None:
        try:
            task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid due date format'}), 400
        
    try:
        db.session.commit()
        return jsonify(task.to_dict())
    except:
        return jsonify({'error': 'Failed to update task'}), 500

# Delete a task
@app.route('/api/tasks/<int:id>', methods=['DELETE'])
def delete_task_api(id):
    task = Todo.query.get_or_404(id)
    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deleted'})
    except:
        return jsonify({'error': 'Failed to delete task'}), 500

if __name__ == "__main__":
    app.run(debug=True)

