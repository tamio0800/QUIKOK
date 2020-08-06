# Create your models here.
from django.contrib.auth.models import User
from django.db import models



class chat_room(models.Model):
    member1= models.ForeignKey(User, on_delete=models.CASCADE,related_name='member1')
    member2= models.ForeignKey(User, on_delete=models.CASCADE,related_name='member2')
    date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
      
        return 'member:{},{}'.format(self.member1,self.member2)


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
