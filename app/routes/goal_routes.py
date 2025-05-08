from flask import Blueprint, request, Response
from flask import request, abort, make_response
from ..models.goal import Goal
from ..models.task import Task
from .route_utilities import validate_model, create_model, get_models_with_filters
from ..db import db
from sqlalchemy import asc, desc
from flask import jsonify


bp = Blueprint("goals_bp", __name__, url_prefix = "/goals")

@bp.post("")
def create_new_goal():
    request_body = request.get_json()
    if (
        not request_body
        or "title" not in request_body
    ):
        abort(make_response({"details": "Invalid data"}, 400))
    new_goal = Goal.from_dict(request_body)
    db.session.add(new_goal)
    db.session.commit()

    return {
            "goal":{
            "id" : new_goal.id,
            "title": new_goal.title
            }
        }, 201

@bp.post("/<id>/tasks")
def create_tasks_with_goal_id(id):
    goal = validate_model(Goal, id)
    request_body = request.get_json()
    task_ids = request_body.get("task_ids", [])
    if not isinstance(task_ids, list):
        abort(make_response({"details": "Invalid data"}, 400))
    tasks = db.session.query(Task).filter(Task.id.in_(task_ids)).all()

    if len(tasks) != len(task_ids):
        abort(make_response({"detail": "Not Found"}, 400))
    #clear previous associated task  
    for task in goal.tasks:
        task.goal_id = None
    # Associate tasks with the goal
    for task in tasks:
        task.goal_id = goal.id

    db.session.commit()

    return {
        "id": goal.id,
        "task_ids": task_ids
    }, 200


@bp.get("")
def get_all_goals():
    query = db.select(Goal)
    
    goals = db.session.scalars(query)
    goals_response = []
    for goal in goals:
        goals_response.append(goal.to_dict())

    return goals_response

@bp.get("/<id>/tasks")
def get_all_goal_tasks(id):
    goal = validate_model(Goal, id)
    tasks = []
    for task in goal.tasks:
        tasks.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.completed_at is not None,
            "goal_id": task.goal_id
        })

    response = {
        "id": goal.id,
        "title": goal.title,
        "tasks": tasks
    }
    return jsonify(response)

@bp.get("/<id>")
def get_one_goal(id):
    goal = validate_model(Goal, id)
    
    return {
            "goal":{
            "id" : goal.id,
            "title": goal.title
            }
        }

@bp.put("/<id>")
def update_goal(id):
    goal = validate_model(Goal, id)

    request_body = request.get_json()

    goal.title = request_body["title"]
 
    db.session.commit()

    return Response(status = 204, mimetype = "application/json")


@bp.delete("/<id>")
def delete_goal(id):
    goal = validate_model(Goal, id)
    db.session.delete(goal)
    db.session.commit()

    return Response(status = 204, mimetype = "application/json")