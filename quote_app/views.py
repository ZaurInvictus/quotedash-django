from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from django.urls import reverse
from django.http import HttpResponseRedirect
from quote_app.forms import DocumentForm

# LANDING
def index(request):
    return render(request, 'index.html')

# REGISTER
def register(request):
    if request.method == "GET":
        return redirect('/')
    errors = User.objects.validate(request.POST)
    
    if errors:
        for e in errors.values():
            messages.error(request, e)
        return redirect('/')
    else:
        new_user = User.objects.register(request.POST)
        request.session['user_id'] = new_user.id
        request.session['first_name'] = new_user.first_name
        request.session['last_name'] = new_user.last_name
        messages.success(request, "You have successfully registered!")
        return redirect('/quotes')

# LOG IN
def login(request):
    if request.method == "GET":
        return redirect('/')

    if not User.objects.authenticate(request.POST['email'], request.POST['password']):
        messages.error(request, 'Invalid Email/Password')
        return redirect('/')

    user = User.objects.get(email=request.POST['email'])
    request.session['user_id'] = user.id
    request.session['first_name'] = user.first_name
    request.session['last_name'] = user.last_name
    messages.success(request, "You have successfully logged in!")
    return redirect('/quotes')

# LOG OUT
def logout(request):
    request.session.clear()
    return redirect('/')


# GET ALL QUOTES
def quotes(request):
    if 'user_id' not in request.session:
        return redirect('/')
    user = User.objects.get(id=request.session['user_id'])
    images = Document.objects.all()
    context = { 
        'quotes': Quote.objects.all(),
        'user': user,
    }
    user = User.objects.get(id = request.session['user_id'])
    image = user.files.last()
    if image:
        request.session['image'] = image.docfile.url 
    return render(request, 'quotes.html', context)


# POST QUOTE
def post_quote(request):
    posted_by = User.objects.get(id=request.session['user_id'])
    Quote.objects.create(
        author = request.POST['author'],
        quote = request.POST['quote'],
        posted_by = posted_by
    )
    # print('quote created:', Quote.objects.last().__dict__)
    return redirect('/quotes')


# ADD LIKE
def add_like(request, q_id):
    # SELECT LIKED QUOTE
    liked_quote = Quote.objects.get(id=q_id)
    # SELECT USER BY USER_ID FROM SESSION
    user = User.objects.get(id=request.session['user_id'])
    # ADD liked_quote to user likes and pass user who liked it
    liked_quote.user_likes.add(user)
    # print(Quote.objects.get(id=q_id).__dict__)
    return redirect('/quotes')
    

# DISPLAY USER QUOTES
def profile(request, user_id):
    # Check if user is logged in
    if 'user_id' not in request.session:
        return redirect('/quotes')
    context = {
        'user_profile': User.objects.get(id=user_id)
    }
    return render(request, 'user-quotes.html', context)


# DELETE QUOTE
def delete_quote(request, quote_id, user_id):
    if request.session['user_id'] != user_id:
        messages.error(request, "Can delete only quotes created by you!")
        return redirect('/quotes')
    destroyed = Quote.objects.get(id=quote_id)
    destroyed.delete()
    messages.success(request, "You have successfully deleted quote!")
    return redirect('/quotes')


# UPDATE FUNCTIONALITY

# DISPLAY USER DETAILS
def account(request, user_id):
    if request.session['user_id'] == user_id:
        context = {
            'user': User.objects.get(id=user_id)
        }
        return render(request, 'account.html', context)
    return redirect('/quotes')


# EDIT USER DETAILS
def edit(request, user_id):
    # Check if logged in user is user in session
    if request.session['user_id'] != user_id:
        return redirect('/quotes')
    # Add validator
    errors = User.objects.validate_edit(request.POST)
    # print(errors)

    # CHECK IF EMAIL IS UNIQUE (ONLY IF HE IS ALTERING EMAIL)
    # name__iexact means that you are doing a case insensitive match on the field name
    email_check = User.objects.filter(email__iexact=request.POST['email'])
    if email_check:
        # print('email_check:', email_check[0].email)
        if user_id != email_check[0].id:
            errors['email'] = "Email is already in use!"
    
    if errors:
        for e in errors.values():
            messages.error(request, e)
        return redirect(f'/my_account/{user_id}')
    else:
        edit_user = User.objects.get(id=user_id)
        edit_user.first_name = request.POST['first_name']
        edit_user.last_name = request.POST['last_name']
        edit_user.email = request.POST['email']
        edit_user.save()
        request.session['first_name'] = edit_user.first_name
        request.session['last_name'] = edit_user.last_name
        return redirect('/quotes')



def post_comment(request, quote_id):
    user = User.objects.get(id=request.session['user_id'])
    quote = Quote.objects.get(id=quote_id)
    Comment.objects.create(
        comment = request.POST['comment'],
        user = user,
        quote = quote
    )
    # print(Comment.objects.last().__dict__)
    return redirect('/quotes')
    


def delete_comment(request, comment_id, comment_user_id):
    if request.session['user_id'] != comment_user_id:
        # print('first:', request.session['user_id'], user_id, comment_user_id)
        messages.error(request, "Can delete only comments created by you!")
        return redirect('/quotes')

    # print('second:', request.session['user_id'], user_id, comment_user_id)
    destroyed = Comment.objects.get(id=comment_id)
    destroyed.delete()
    messages.success(request, "You have successfully deleted a message!")
    return redirect('/quotes')


# UPLOAD
def upload(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(
                docfile = request.FILES['docfile'],
                user = User.objects.get(id=request.session['user_id'])
            )
            newdoc.save()
            # Redirect to the image after POST
            return HttpResponseRedirect(reverse('image'))
    else:
        form = DocumentForm() # A empty, unbound form

    # Load documents for the list page
    last_image = ''
    documents = Document.objects.all()
    user = User.objects.get(id = request.session['user_id'])
    images = user.files.all()
    if images:
        last_image = user.files.last()
        request.session['image'] = last_image.docfile.url 

    # Render image page with the documents and the form
    return render(request, 'image.html', {'documents': images, 'last': last_image, 'form': form})



# DELETE IMAGE
def delete_image(request, id):
    destroy = Document.objects.get(id=id)
    destroy.delete()
    return redirect('/upload')


# SELECT ONE OF PREVIOUS IMAGES AS PROFILE PICTURE
def set_profile(request, id):
    file = Document.objects.get(id=id)
    Document.objects.create(
        docfile = file.docfile,
        user = User.objects.get(id=request.session['user_id'])
    )
    delete_image(request, id)
    return redirect('/upload')


# EDIT QUOTE 
# (USER CAN EDIT ONLY QUOTES THAT BELONGS TO HIM)
def edit_quote(request, quote_id, user_id):
    edit_quote = Quote.objects.get(id=quote_id)
    edit_quote.author = request.POST['author']
    edit_quote.quote = request.POST['quote']
    edit_quote.posted_by = edit_quote.posted_by
    edit_quote.save()
    messages.success(request, "You have successfully updated a quote!")
    return redirect(f'/user_quotes/{user_id}')


