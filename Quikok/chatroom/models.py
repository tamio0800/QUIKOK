# Create your models here.
from django.contrib.auth.models import User
from django.db import models
from account.models import student_profile, teacher_profile


class chat_room(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE,related_name='student_set')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE,related_name='teacher_set')
    date= models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return 'member:{},{}'.format(self.student,self.teacher)


class Messages(models.Model):
    """
    Model to represent user submitted changed to a resource guide
    """
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    group = models.ForeignKey(chat_room, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        String to represent the message
        """
        return self.message

#class user_info_chat(models.Model):
#    member1= models.ForeignKey(User, on_delete=models.CASCADE,related_name='member1')
 #   member2= models.ForeignKey(User, on_delete=models.CASCADE,related_name='member2')
 #   member1_snapshot = models.TextField(null = True)
 #   member2_snapshot = models.TextField(null = True)

 #   def __str__(self):
 #       return self.user_info_chat

