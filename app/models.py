from . import db
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime
from flask_login import UserMixin
from . import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):

    __tablename__ = 'users'
    
    id = db.Column(db.Integer , primary_key= True)
    username = db.Column(db.String(20), unique= True, nullable= False)
    email = db.Column(db.String(120), unique= True ,nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default = 'default.jpg')
    password = db.Column(db.String(60),nullable = False)
    posts = db.relationship('Post', backref='author', lazy=True)
    comment= db.relationship('Comment', backref='comment', lazy=True)

    # @property
    # def password(self):
    #     raise AttributeError('You cannot read the password attribute')
    
# @password.setter
    # def password(self, password):
    #     self.pass_secure = generate_password_hash(password)

    # #method that takes ,hashes and compares our password
    # def verify_password(self,password):
    #     # return check_password_hash(self.pass_secure,password)



    def __repr__(self):
        return f"User('{self.username}','{self.email}', '{self.image_file}')"



class Post(db.Model):
    id = db.Column(db.Integer , primary_key= True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable= False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    comment = db.relationship('Comment', backref='cmt', lazy=True)
    

    def __repr__(self):
        return f"Post('{self.title}','{self.date_posted}')"


class Comment(db.Model):
    
    
    id = db.Column(db.Integer, primary_key = True)
    comment_post = db.Column(db.String(255), index=True)
    time = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def save_comments(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_comments(cls, id):
        comments = Comment.query.filter_by(post_id=id).all()
        return comments
    
     