from django.contrib import admin

# from .models import Question
from .models import Tweet
# Register your models here.

# admin.site.register(Question)
admin.site.register(Tweet)



# Wei Wang add Message, User
from .models import Message, User
admin.site.register(Message)
admin.site.register(User)
