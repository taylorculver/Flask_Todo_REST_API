from flask import Blueprint, abort
from flask_restful import (Resource, Api, reqparse,
                           marshal, marshal_with,
                           fields, url_for)

import models

# governs data output of API
todo_fields = {
    'id': fields.Integer,
    'name': fields.String
}


def todo_or_404(todo_id):
    """Get todo or throw error"""
    try:
        todo = models.Todo.get(models.Todo.id == todo_id)
    except models.Todo.DoesNotExist:
        abort(404)
    else:
        return todo


class TodoList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'name',
            required=True,
            help="No task name provided",
            location=['form', 'json']
        )
        super().__init__()

    def get(self):
        """Pull all todos from database"""
        todos = [marshal(todo, todo_fields)  # converts to JSON object
                 for todo in models.Todo.select()]
        return todos

    @marshal_with(todo_fields)
    def post(self):
        """Post new todos to database"""
        args = self.reqparse.parse_args()
        todo = models.Todo.create(**args)
        return (todo, 201,
                {'Location': url_for('resources.todos.todos', id=todo.id)})


class Todo(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'name',
            required=True,
            help="No task name provided",
            location=['form', 'json']
        )
        super().__init__()

    @marshal_with(todo_fields)
    def get(self, id):
        """Pull single field by primary key value"""
        return todo_or_404(id)

    @marshal_with(todo_fields)
    def put(self, id):
        """Edit single field by primary key value"""
        args = self.reqparse.parse_args()
        query = models.Todo.update(**args).where(models.Todo.id == id)
        query.execute()
        return (models.Todo.get(models.Todo.id == id), 200,
                {'Location': url_for('resources.todos.todo', id=id)})

    def delete(self, id):
        """Delete single field by primary key value"""
        query = models.Todo.delete().where(models.Todo.id == id)
        query.execute()
        return '', 204, {'Location': url_for('resources.todos.todos')}


todos_api = Blueprint('resources.todos', __name__)
api = Api(todos_api)
api.add_resource(
    TodoList,
    '/api/v1/todos',
    endpoint='todos'
)
api.add_resource(
    Todo,
    '/api/v1/todos/<int:id>',
    endpoint='todo'
)
