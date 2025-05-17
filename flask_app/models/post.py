from flask_app.config.mysqlconnection import connectToMySQL

from flask import flash
from flask_app.models import user
from flask_app.models import comment

class Post:
    db = "coding_dojo_wall"
    def __init__(self,data):
        self.id = data['id']
        self.content = data['content']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        # None can represent a currently empty space for a single User dictionary to be placed here, as a Tweet is made by ONE User. We want a User instance and all their attributes to be placed here, so something like data['...'] will not work as we have to make the User instance ourselves.
        self.creator = None
        self.comments_post=[]

    @classmethod
    def save(cls,data):
        query = "INSERT INTO posts (content,user_id) VALUES(%(content)s,%(user_id)s)"
        return connectToMySQL(cls.db).query_db(query,data)
    
    @classmethod
    def destroy_post(cls,data):
        query = "DELETE from posts WHERE id = %(id)s;"
        return connectToMySQL(cls.db).query_db(query,data)

    @classmethod
    def get_all_posts_comments_with_creator(cls):
        # Get all posts, and their one associated User that created it
        query = '''SELECT * FROM posts 
        JOIN users as post_authors
        ON posts.user_id = post_authors.id
        LEFT JOIN comments ON comments.post_id = posts.id 
        LEFT JOIN users as comment_authors
        on comment_authors.id = comments.user_id
        order by posts.created_at DESC;'''
        results = connectToMySQL(cls.db).query_db(query)
        all_posts = []
        
        
        for row in results:
            # print(type(row['id']), type(all_posts[-1].id))
            # print(type(row['id']))
            if not all_posts or all_posts[-1].id != row["id"]: 
                this_post = cls(row) 
                print("********* print a post instance  *****")  
                print(this_post.content)
                all_posts.append(this_post)
                post_author_data = {
                    "id": row['post_authors.id'],
                    "first_name":row['first_name'],
                    "last_name":row['last_name'],
                    "email":row['email'],
                    "password":row['password'],
                    "created_at":row['post_authors.created_at'],
                    "updated_at":row['post_authors.updated_at']
                }
                this_post.creator = user.User(post_author_data)
                print("%%%%  print this post user  %%%%%%%%%%%%%")
                print(this_post.creator.first_name)

            if row["comments.id"]:  
                one_comment_for_post = {
                    "id": row['comments.id'], 
                    "comment": row['comment'],
                    "created_at": row['comments.created_at'],
                    "updated_at": row['comments.updated_at']
            }
    
                print(one_comment_for_post)
                one_comment_instance = comment.Comment(one_comment_for_post)
                this_post.comments_post.append(one_comment_instance)
                print("$$$$$$$$$$$$$ print all comments for a post")
                print(this_post.comments_post)

                comment_author_data = {            
                    "id": row['comment_authors.id'],
                    "first_name":row['comment_authors.first_name'],
                    "last_name":row['comment_authors.last_name'],
                    "email":row['comment_authors.email'],
                    "password":row['comment_authors.password'],
                    "created_at":row['comment_authors.created_at'],
                    "updated_at":row['comment_authors.updated_at']                             
                }
                comment_author_instance = user.User(comment_author_data)
                one_comment_instance.comment_owner=  comment_author_instance
                print ("&&&&&&   comment user ************")
                print(one_comment_instance.comment_owner.first_name)
            # Prepare to make a User class instance, looking at the class in models/user.py
            # one_posts_author_info = {
            #     # Any fields that are used in BOTH tables will have their name changed, which depends on the order you put them in the JOIN query, use a print statement in your classmethod to show this.
            #     "id": row['users.id'], 
            #     "first_name": row['first_name'],
            #     "last_name": row['last_name'],
            #     "email": row['email'],
            #     "password": row['password'],
            #     "created_at": row['users.created_at'],
            #     "updated_at": row['users.updated_at']
            # }
            # Create the User class instance that's in the user.py model file
            # author = user.User(one_posts_author_info)
            # Associate the Tweet class instance with the User class instance by filling in the empty creator attribute in the Tweet class
            # one_post.creator = author
            # Append the Tweet containing the associated User to your list of tweets
        print("############# print all posts ###############")
        print(all_posts)   
        return all_posts
    

    #it works with only posts and users, the following
    @classmethod
    def get_all_posts_with_creator(cls):
        # Get all posts, and their one associated User that created it
        query = '''SELECT * FROM posts 
        JOIN users ON posts.user_id = users.id 
        order by posts.created_at DESC;'''
        results = connectToMySQL(cls.db).query_db(query)
        all_posts = []
        for row in results:
            # Create a post class instance from the information from each db row
            one_post = cls(row)
            # Prepare to make a User class instance, looking at the class in models/user.py
            one_posts_author_info = {
                # Any fields that are used in BOTH tables will have their name changed, which depends on the order you put them in the JOIN query, use a print statement in your classmethod to show this.
                "id": row['users.id'], 
                "first_name": row['first_name'],
                "last_name": row['last_name'],
                "email": row['email'],
                "password": row['password'],
                "created_at": row['users.created_at'],
                "updated_at": row['users.updated_at']
            }
            # Create the User class instance that's in the user.py model file
            author = user.User(one_posts_author_info)
            # Associate the Tweet class instance with the User class instance by filling in the empty creator attribute in the Tweet class
            one_post.creator = author
            # Append the Tweet containing the associated User to your list of tweets
            all_posts.append(one_post)
        return all_posts
    
    @staticmethod
    def validate_post(post):
        is_valid = True
        if len(post['content']) < 1:
            flash("post must not be blank")
            is_valid = False
        
        return is_valid

