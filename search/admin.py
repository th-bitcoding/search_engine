from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(Search)
class SearchAdmin(admin.ModelAdmin):
    list_display=['search_data']

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    # list_display=['json_data','flag']
    list_display=['id','flag']
    list_filter = ['flag']


@admin.register(SubObjectJSON)
class SubObjectJSONAdmin(admin.ModelAdmin):
    list_display = [
        "id"
    ]

@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display= ['id','country','name','stream_video_url','thumbnail_url']

@admin.register(SearchAfg)
class SearchAfgAdmin(admin.ModelAdmin):
    # list_display=['json_data','flag']
    list_display=['id']

@admin.register(UserUnique)
class UserUnique(admin.ModelAdmin):
    list_display=['id','flag']
  
  
