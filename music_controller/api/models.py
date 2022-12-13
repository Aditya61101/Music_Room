from django.db import models
import string, random

# function to generate unique code
def generate_unique_code():
    length = 6
    while True:
        code = ''.join(random.choices(string.ascii_uppercase, k=length))
        # to check if the generated code is already used by one of the room using .count method
        if Room.objects.filter(code=code).count() == 0:
            break
    return code

# Create your models here.
class Room(models.Model):
    # defining the fields/columns
    code = models.CharField(max_length=8, default=generate_unique_code, unique=True)
    host = models.CharField(max_length=50, unique=True)
    guest_can_pause = models.BooleanField(null=False, default=False)
    votes_to_skip = models.IntegerField(null=False, default=1)
    created_At = models.DateTimeField(auto_now_add=True)
    curr_song = models.CharField(max_length=50, null=True)

