from flask_app.config.mysqlconnection import connectToMySQL

from flask import flash
from flask_app.models import user
from flask_app.models import post

class Comment:
    db = "coding_dojo_wall"
    def __init__(self,data):
        self.id = data['id']
        self.comment = data['comment']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        # None can represent a currently empty space for a single User dictionary to be placed here, as a Tweet is made by ONE User. We want a User instance and all their attributes to be placed here, so something like data['...'] will not work as we have to make the User instance ourselves.
        self.for_post = None
        self.comment_owner = None

    @classmethod
    def save_comment(cls,data):
        query = '''INSERT INTO comments (comment,user_id, post_id) 
        VALUES(%(comment)s,%(user_id)s,%(post_id)s);'''
        return connectToMySQL(cls.db).query_db(query,data)
    
    @classmethod
    def destroy_comment(cls,data):
        query = "DELETE from comments WHERE id = %(id)s;"
        return connectToMySQL(cls.db).query_db(query,data)

    @classmethod
    def get_all_comments_with_post_user(cls):
        # Get all posts, and their one associated User that created it
        query = '''SELECT * FROM comments 
        JOIN posts ON comments.post_id = posts.id 
        JOIN users ON users.id = posts.user_id
        order by posts.created_at DESC;'''
        results = connectToMySQL(cls.db).query_db(query)
        all_comments = []
        for row in results:
            # Create a post class instance from the information from each db row
            one_comment = cls(row)
            # Prepare to make a post class instance, looking at the class in models/user.py
            one_comment_post_info = {
                # Any fields that are used in BOTH tables will have their name changed, which depends on the order you put them in the JOIN query, use a print statement in your classmethod to show this.
                "id": row['posts.id'], 
                "content": row['content'],
                "created_at": row['posts.created_at'],
                "updated_at": row['posts.updated_at']
            }
            # Prepare to make a User class instance, as comment owner, the person who posts the comments for specific post
            one_comment_post_user_infor = {
                "id":row['users.id'],
                "first_name":row['first_name'],
                "last_name":row['last_name'],
                "email":row['email'],
                "password":row['password'],
                "created_at":row['users.created_at'],
                "updated_at":row['users.updated_at'],

            }
            # Create the User class instance that's in the user.py model file
            one_post = post.Post(one_comment_post_info)
            comment_owner_ = user.User(one_comment_post_user_infor)
            # Associate the Tweet class instance with the User class instance by filling in the empty creator attribute in the Tweet class
            one_comment.for_post = one_post
            one_comment.comment_owner = comment_owner_
            # Append the Tweet containing the associated User to your list of tweets
            all_comments.append(one_comment)
        return all_comments
    
  

