from django.urls import path
from users.views import login, register, logout, profile, add_to_favorites, remove_from_favorites, delete_review

app_name = "users"

urlpatterns = [
    path('login', login, name="login"),
    path('register', register, name="register"),
    path('logout', logout, name="logout"),
    path('profile', profile, name="profile"),
    path('favorites/add/<int:product_id>/', add_to_favorites, name="add_to_favorites"),
    path('favorites/remove/<int:product_id>/', remove_from_favorites, name="remove_from_favorites"),
    path('reviews/delete/<int:review_id>/', delete_review, name="delete_review"),
]