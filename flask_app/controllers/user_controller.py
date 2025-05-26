from flask_app.config.mysqlconnection import connectToMySQL
from flask import render_template,redirect,session,request, flash, url_for
import uuid  # For generating tokens
from datetime import datetime, timedelta
from flask_app import app,mail
from flask_mail import Message
from flask_app.models.user import User
from flask_app.models.post import Post
from flask_app.models.comment import Comment
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register',methods=['POST'])
def register():

    if not User.validate_register(request.form):
        return redirect('/')
    data ={ 
        "first_name": request.form['first_name'],
        "last_name": request.form['last_name'],
        "email": request.form['email'],
        "password": bcrypt.generate_password_hash(request.form['password'])
    }
    id = User.save(data)
    session['user_id'] = id

    return redirect('/wall')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Handle GET request - render the login page
    if request.method == 'GET':
        return render_template('index.html')
    
    # Handle POST request - process the login form
    user = User.get_by_email(request.form)

    if not user:
        flash("Invalid Email", "login")
        return redirect('/')
    if not bcrypt.check_password_hash(user.password, request.form['password']):
        flash("Invalid Password", "login")
        return redirect('/')
    session['user_id'] = user.id
    return redirect('/wall')

@app.route('/wall')
def dashboard():
    if 'user_id' not in session:
        return redirect('/logout')
    data ={
        'id': session['user_id']
    }
    # all_posts = Post.get_all_posts_with_creator()
    all_posts = Post.get_all_posts_comments_with_creator()
    return render_template("dashboard.html",user=User.get_by_id(data), all_posts = all_posts)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/user_post', methods=['POST'])
def user_post():
    if 'user_id' not in session:
        return redirect('/logout')
    print("validate post...")
    if not Post.validate_post(request.form):
        return redirect('/wall')
    print(request.form)
    
    Post.save(request.form)
    return redirect('/wall')

@app.route('/posts/delete/<int:post_id>')
def delete_post(post_id):
    data = {
        'id':post_id,
    }
    Post.destroy_post(data)
    return redirect('/wall')

@app.route('/posts/<int:post_id>/post_comment', methods=['post'])
def post_comment(post_id):
    if 'user_id' not in session:
        return redirect('/logout')
    data ={
        'comment': request.form['comment'],
        'user_id': request.form['user_id'],
        'post_id': post_id,
    }
    Comment.save_comment(data)
    return redirect('/wall')


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template('forgot_password.html')
    
    # Handle POST request
    email = request.form['email']
    
    # Create database connection and check if user exists
    db = connectToMySQL('coding_dojo_wall')  # Replace with your actual database name
    query = "SELECT * FROM users WHERE email = %(email)s;"
    user = db.query_db(query, {'email': email})
    
    if not user:
        flash("If that email exists in our system, a reset link has been sent.")
        return redirect('/login')
    
    # Generate token and expiration
    token = str(uuid.uuid4())
    expires = datetime.now() + timedelta(hours=24)
    
    # Save token to database
    db = connectToMySQL('coding_dojo_wall')  # New connection for this query
    query = """
        UPDATE users 
        SET reset_token = %(token)s, reset_token_expires = %(expires)s
        WHERE email = %(email)s;
    """
    data = {
        'token': token,
        'expires': expires,
        'email': email
    }
    db.query_db(query, data)
    
    # ... rest of your code
    
    # Send email with reset link
    send_reset_email(email, token)
    
    flash("If that email exists in our system, a reset link has been sent.")
    return redirect('/login')

# ADD THIS NEW FUNCTION
def send_reset_email(email, token):
  
    reset_url = request.host_url + f"reset- password/{token}"
    msg = Message(
        subject='Password Reset Request',
        recipients=[email],
        html=f'''
        <h2>Password Reset Request</h2>
        <p>You requested a password reset. Click the link below:</p>
        <a href="{reset_url}">Reset Your Password</a>
        <p>This link expires in 24 hours.</p>
        <p>If you didn't request this, ignore this email.</p>
        '''
    )
    mail.send(msg)
        


@app.route('/reset-password/<path:token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'GET':
        # Check if token is valid
        db = connectToMySQL('coding_dojo_wall')
        query = """
            SELECT * FROM users 
            WHERE reset_token = %(token)s 
            AND reset_token_expires > NOW();
        """
        user = db.query_db(query, {'token': token})
        
        if not user:
            print("Invalid token or expired")  # Debug: See if this is the issue
            flash("Invalid or expired password reset link.")
            return redirect('/login')
        
        return render_template('reset_password.html', token=token)
    
    # Handle POST request
    password = request.form['password']
    confirm = request.form['confirm_password']
    
    if password != confirm:
        flash("Passwords do not match.")
        return redirect(f'/reset-password/{token}')
    
    if len(password) < 8:
        flash("Password must be at least 8 characters.")
        return redirect(f'/reset-password/{token}')
    
    # Hash the new password
    hashed_pw = bcrypt.generate_password_hash(password)
    
    # Update user's password and clear token
    db = connectToMySQL('coding_dojo_wall')
    query = """
        UPDATE users 
        SET password = %(password)s, reset_token = NULL, reset_token_expires = NULL
        WHERE reset_token = %(token)s AND reset_token_expires > NOW();
    """
    data = {
        'password': hashed_pw,
        'token': token
    }
    db.query_db(query, data)
    
    flash("Your password has been updated. Please log in.")
    return redirect('/login')



