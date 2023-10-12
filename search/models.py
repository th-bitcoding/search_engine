
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
# Create your models here.
class Search(models.Model):
    search_data = models.CharField(max_length=100)

    

# @receiver(post_save, sender=Search)
# def search_post_save(sender, instance, **kwargs):
#     json_data = instance.search_data
#     try:
#         sub_obj = json_data['TV_Data']['Channel_List']['main']['sub']
#     except:
#         pass
#     for obj, sub_obj_data in sub_obj.items():
#         if len(str(sub_obj_data)) <= 1048575:
#             SubObjectJSON.objects.update_or_create(
#                 sub_objects=sub_obj_data
#             )


class SubObjectJSON(models.Model):
    sub_objects = models.JSONField()

class Channel(models.Model):
    flag =models.BooleanField(default=False)
    json_data = models.JSONField()

class Favourite(models.Model):
    country = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    stream_video_url = models.CharField(max_length=255)
    thumbnail_url = models.CharField(max_length=255)

class SearchAfg(models.Model):
    json_file =models.JSONField()

class UserUnique(models.Model):
    unique_id = models.CharField(max_length=10,unique=True)
    flag = models.BooleanField()




    