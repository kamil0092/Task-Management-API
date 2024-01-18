from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
db = SQLAlchemy()
db.init_app(app)


##Cafe TABLE Configuration
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


##HTTP GET - Read Record
@app.route("/all")
def all():
    result = db.session.execute(db.select(Task))
    all_result = result.scalars().all()
    return jsonify(tasks=[item.to_dict() for item in all_result])


##HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def post_new_task():
    title = request.form.get("title")
    description = request.form.get("description")
    due_date_str = request.form.get("due_date")
    status = request.form.get("status")

    try:
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify(response={"error": "Invalid date format. Please use YYYY-MM-DD."})

    new_task = Task(
        title=title,
        description=description,
        due_date=due_date,
        status=status
    )
    db.session.add(new_task)
    db.session.commit()
    if new_task.title == Task.title:
        return jsonify(response={"errors": "name you given is already saved"})
    else:
        return jsonify(response={"success": "Successfully added the new task."})


##HTTP /PATCH - Update Record
# Updating the particular task based on a particular id:
# PATCH http://127.0.0.1:5000/update-task/1?new_title=example title&new_description=example description&new_due_date=example due date&new_status=example

@app.route("/update-task/<int:task_id>", methods=["PATCH"])
def update_new_task(task_id):
    new_title = request.args.get("new_title")
    new_description = request.args.get("new_description")
    new_due_date_str = request.args.get("new_due_date")
    new_status = request.args.get("new_status")

    try:
        new_due_date = datetime.strptime(new_due_date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify(response={"error": "Invalid date format. Please use YYYY-MM-DD."})

    task = db.get_or_404(Task, task_id)

    if task:
        if new_title is not None:  # Check if new_title is provided
            task.title = new_title
        task.description = new_description
        task.due_date = new_due_date
        task.status = new_status

        db.session.commit()
        return jsonify(response={"success": "Successfully updated the task."}), 200
    else:
        # 404 = Resource not found
        return jsonify(error={"Not Found": "Sorry, a Task with that id was not found in the database."}), 404


##HTTP DELETE - Delete Record
# http://127.0.0.1:5000/delete-task/1?api-key=example.api_key
@app.route("/delete-task/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    api_key = request.args.get("api-key")
    if api_key == "TopSecretAPIKey":
        task = db.get_or_404(Task, task_id)
        if task:
            db.session.delete(task)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the task from the database."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a task with that id was not found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


if __name__ == '__main__':
    app.run(debug=True)
