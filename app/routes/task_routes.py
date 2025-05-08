from flask import Blueprint, request, Response
from flask import request, abort, make_response
from ..models.task import Task
from .route_utilities import validate_model
from ..db import db
from sqlalchemy import asc, desc
from datetime import datetime
import requests
import os
from dotenv import load_dotenv
load_dotenv()

bp = Blueprint("tasks_bp", __name__, url_prefix = "/tasks")

@bp.post("")
def create_new_task():
    request_body = request.get_json()
    if (
        not request_body
        or "title" not in request_body
        or "description" not in request_body
    ):
        abort(make_response({"details": "Invalid data"}, 400))
    new_task = Task.from_dict(request_body)
    db.session.add(new_task)
    db.session.commit()

    return {
            "task":{
            "id" : new_task.id,
            "title": new_task.title,
            "description": new_task.description,
            "is_complete": False
            }
        }, 201

@bp.get("")
def get_all_tasks():
    query = db.select(Task)
    sort_param = request.args.get("sort")

    if sort_param == "desc":
        query = db.select(Task).order_by(desc(Task.title))
    else:
        query = db.select(Task).order_by(asc(Task.title))
    
    tasks = db.session.scalars(query)
    tasks_response = []
    for task in tasks:
        tasks_response.append(task.to_dict())

    return tasks_response

@bp.get("/<id>")

def get_one_task(id):
    task = validate_model(Task, id)
    
    response = {        
            "id" : task.id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.completed_at is not None
        }
    if task.goal_id is not None:
        response["goal_id"] = task.goal_id
    return {"task": response}

@bp.put("/<id>")
def update_task(id):
    task = validate_model(Task, id)

    request_body = request.get_json()

    task.title = request_body["title"]
    task.description = request_body["description"]
    task.completed_at = request_body.get("is_complete",None)
 
    db.session.commit()

    return Response(status = 204, mimetype = "application/json")

@bp.patch("/<id>/mark_complete")
def mark_task_complete(id):
    task = validate_model(Task, id)
    if not task.completed_at:
        task.completed_at = datetime.utcnow()

        # Save the task updates in the database
        # Uncomment the following line if you want to test the Slack API, 
        # so that completed_at won't be stored and you can enter the if statement
        db.session.commit()
        
        slack_api_key = os.environ.get('SLACK_BOT_API')
        slack_channel = "test-slack-api"
        slack_message = f"Someone just completed the task {task.title}"

        if slack_api_key:
            headers = {
                "Authorization": f"Bearer {slack_api_key}"
            }
   
            query_param = f"channel={slack_channel}&text={slack_message}"
            
            # Send a POST request to the Slack API
            requests.post(f"https://slack.com/api/chat.postMessage?{query_param}", headers=headers)
            
    return "", 204

@bp.patch("/<id>/mark_incomplete")
def mark_task_incomplete(id):
    task = validate_model(Task, id)
    task.completed_at = None

    db.session.commit()
    return "", 204

@bp.delete("/<id>")
def delete_task(id):
    task = validate_model(Task, id)
    db.session.delete(task)
    db.session.commit()

    return Response(status = 204, mimetype = "application/json")