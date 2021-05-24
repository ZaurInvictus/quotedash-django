from django.db import models, IntegrityError
import re
import bcrypt



EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class UserManager(models.Manager):
    def validate(self, form):
        errors = {}
        if len(form['first_name']) < 2:
            errors['first_name'] = 'First Name must be at least 2 characters'

        if len(form['last_name']) < 2:
            errors['last_name'] = 'Last Name must be at least 2 characters'

        if not EMAIL_REGEX.match(form['email']):
            errors['email'] = 'Invalid Email Address'
        
        email_check = self.filter(email=form['email'])
        if email_check:
            errors['email'] = "Email already in use"

        if len(form['password']) < 3:
            errors['password'] = 'Password must be at least 3 characters'
        
        if form['password'] != form['confirm']:
            errors['password'] = 'Passwords do not match'
        
        return errors

    def validate_edit(self, form):
        errors = {}
        if len(form['first_name']) < 2:
            errors['first_name'] = 'First Name must be at least 2 characters'
        if len(form['last_name']) < 2:
            errors['last_name'] = 'Last Name must be at least 2 characters'
        if not EMAIL_REGEX.match(form['email']):
            errors['email'] = 'Invalid Email Address'

        # CHECK IF EMAIL IS UNIQUE
        # name__iexact means that you are doing a case insensitive match on the field name
        # email_check = self.filter(email__iexact=form['email'])
        # if email_check:
        #     errors['email'] = "Email already in use"

        return errors

    
    def authenticate(self, email, password):
        users = self.filter(email=email)
        if not users:
            return False

        user = users[0]
        return bcrypt.checkpw(password.encode(), user.password.encode())

    def register(self, form):
        pw = bcrypt.hashpw(form['password'].encode(), bcrypt.gensalt()).decode()
        
        return self.create(
            first_name = form['first_name'],
            last_name = form['last_name'],
            email = form['email'],
            password = pw,
        )
        
# USER
class User(models.Model):
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()
    # user.liked_quotes
    # user.comments
    # user.user_quotes
    # user.files


# DOCUMENT
class Document(models.Model):
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')
    user = models.ForeignKey(User, related_name='files', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # document.files


# QUOTE
class Quote(models.Model):
    author = models.CharField(max_length=45)
    quote = models.CharField(max_length=255)
    posted_by = models.ForeignKey(User, related_name='user_quotes', on_delete=models.CASCADE)
    user_likes = models.ManyToManyField(User, related_name='liked_quotes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # quote.comments


# COMMENT
class Comment(models.Model):
    comment = models.CharField(max_length=255)
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    quote = models.ForeignKey(Quote, related_name='comments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # comment.user
    # comment.quote

