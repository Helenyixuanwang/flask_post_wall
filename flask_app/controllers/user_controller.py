from flask import render_template,redirect,session,request, flash
from flask_app import app
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

@app.route('/login',methods=['POST'])
def login():
    user = User.get_by_email(request.form)

    if not user:
        flash("Invalid Email","login")
        return redirect('/')
    if not bcrypt.check_password_hash(user.password, request.form['password']):
        flash("Invalid Password","login")
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