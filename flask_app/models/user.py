from flask_app.config.mysqlconnection import connectToMySQL
import re	# the regex module
# create a regular expression object that we'll use later   
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
from flask import flash

class User:
    db = "coding_dojo_wall"
    def __init__(self,data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        # Add these lines for the new columns
        self.reset_token = data.get('reset_token')  # Using get() handles NULL values
        self.reset_token_expires = data.get('reset_token_expires')
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        # [] can represent a currently empty place to store all of the posts that a single User instance has created, as a User creates MANY posts
        self.posts = [] 
        self.comments_user = []

    @classmethod
    def save(cls,data):
        query = "INSERT INTO users (first_name,last_name,email,password) VALUES(%(first_name)s,%(last_name)s,%(email)s,%(password)s)"
        return connectToMySQL(cls.db).query_db(query,data)

    @classmethod
    def get_all(cls):
        query = "SELECT * FROM users;"
        results = connectToMySQL(cls.db).query_db(query)
        users = []
        for row in results:
            users.append( cls(row))
        return users

    @classmethod
    def get_by_email(cls,data):
        query = "SELECT * FROM users WHERE email = %(email)s;"
        results = connectToMySQL(cls.db).query_db(query,data)
        if len(results) < 1:
            return False
        return cls(results[0])

    @classmethod
    def get_by_id(cls,data):
        query = "SELECT * FROM users WHERE id = %(id)s;"
        results = connectToMySQL(cls.db).query_db(query,data)
        return cls(results[0])

    @staticmethod
    def validate_register(user):
        is_valid = True
        query = "SELECT * FROM users WHERE email = %(email)s;"
        results = connectToMySQL(User.db).query_db(query,user)
        if len(results) >= 1:
            flash("Email already taken.","register")
            is_valid = False
        if not EMAIL_REGEX.match(user['email']):
            flash("Invalid Email!!!","register")
            is_valid = False
        if len(user['first_name']) < 3:
            flash("First name must be at least 3 characters","register")
            is_valid = False
        if len(user['last_name']) < 3:
            flash("Last name must be at least 3 characters","register")
            is_valid = False
        if len(user['password']) < 8:
            flash("Password must be at least 8 characters","register")
            is_valid = False
        if user['password'] != user['confirm']:
            flash("Passwords don't match","register")
            is_valid = False
        return is_valid