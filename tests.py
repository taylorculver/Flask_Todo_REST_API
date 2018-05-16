import unittest
from peewee import *

from app import app
from models import Todo


TEST_DB = SqliteDatabase(':memory:')
TEST_DB.connect()
TEST_DB.create_tables([Todo], safe=True)
MODELS = (Todo,)


def use_test_database(fn):
    """Build test database"""
    def inner(self):
        with TEST_DB.bind_ctx(MODELS):
            TEST_DB.create_tables(MODELS)
            try:
                fn(self)
            finally:
                TEST_DB.drop_tables(MODELS)
    return inner


class TodoModelTestCase(unittest.TestCase):
    """Instantiate new database, add new Todo, verify that it exists"""
    @use_test_database
    def test_create_todo(self):
        Todo.create(name="Building test database")
        self.assertEqual(Todo.select().count(), 1)


class ViewTestCase(unittest.TestCase):
    """Configuration before running all test cases"""
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()


class AppViewsTestCase(ViewTestCase):
    """Test that the homepage can successfully be called"""
    def test_homepage_401(self):
        api_call = self.app.get('/')
        self.assertEqual(api_call.status_code, 200)


class TodoResourceTestCase(ViewTestCase):
    @staticmethod
    def create_todos():
        """Create dummy data for tests below"""
        Todo.create(name="TEST Todo Number 1")
        Todo.create(name="TEST Todo Number 2")

    @use_test_database
    def test_create_todo_resource(self):
        """POST new todo to database"""
        api_call = self.app.post('/api/v1/todos',
                                 data={'name': 'Wash your car'})
        self.assertEqual(api_call.status_code, 201)

    @use_test_database
    def test_get_todos_list(self):
        """GET all todos"""
        api_call = self.app.get('/api/v1/todos')
        self.assertEqual(api_call.status_code, 200)

    @use_test_database
    def test_get_single_todo(self):
        """GET single specified todo"""
        self.create_todos()
        api_call = self.app.get('/api/v1/todos/1')
        self.assertEqual(api_call.status_code, 200)
        self.assertIn('TEST Todo Number 1', api_call.get_data(as_text=True))

    @use_test_database
    def test_get_single_todo_fail(self):
        """Test for 404 error"""
        api_call = self.app.get('/api/v1/todos/1')
        self.assertEqual(api_call.status_code, 404)
        self.assertRaises(Todo.DoesNotExist)

    @use_test_database
    def test_update_todo(self):
        """PUT new value to single todo list"""
        self.create_todos()
        api_call = self.app.put('/api/v1/todos/1',
                                data={'name': 'Todo Number One TEST'})
        self.assertEqual(api_call.status_code, 200)
        self.assertIn('Todo Number One TEST', api_call.get_data(as_text=True))

    @use_test_database
    def test_delete_todo(self):
        """DELETE first todo, verify proper 204 response"""
        self.create_todos()
        api_call = self.app.delete('/api/v1/todos/1')
        self.assertEqual(api_call.status_code, 204)
        self.assertNotIn('TEST Todo Number 1', api_call.get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()
