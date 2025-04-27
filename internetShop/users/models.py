from django.db import models
from django.contrib.auth.models import AbstractUser

# Дочерний класс от AbstractUser (от Джанго - auth.models)
class User(AbstractUser):
    #Добавляем новое поле - фото(будут хранятся в media/users_images), фото пользователь может и не поставить
    image = models.ImageField(upload_to="users_images", blank=True)

