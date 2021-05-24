from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('register', views.register),
    path('login', views.login),
    path('logout', views.logout),
    path('like/<int:q_id>', views.add_like),

    # PROFILE
    path('user_quotes/<int:user_id>', views.profile),

    # QUOTES
    path('quotes', views.quotes),
    path('post_quote', views.post_quote),
    path('delete/<int:quote_id>/<int:user_id>', views.delete_quote),
    # UPDATE
    path('user_quotes/edit_quote/<int:quote_id>/<int:user_id>', views.edit_quote),

    # UPDATE FUNCTIONALITY
    path('my_account/<int:user_id>', views.account),
    path('my_account/edit/<int:user_id>', views.edit),

    # COMMENT FUNCTIONALITY
    path('post-comment/<int:quote_id>', views.post_comment),
    path('delete-comment/<int:comment_id>/<int:comment_user_id>', views.delete_comment),

    # UPLOAD FILE, Delete File
    path('upload', views.upload, name='image'),
    path('delete_image/<int:id>', views.delete_image),
    path('set_profile/<int:id>', views.set_profile)
]