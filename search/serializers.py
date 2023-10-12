from rest_framework import serializers
from .models import *

        
class SubObjectJSONSerializer(serializers.ModelSerializer):
    sub_objects = serializers.JSONField()
    
    
    class Meta:
        model = SubObjectJSON
        fields = '__all__'

class FavouriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favourite
        fields ='__all__'

class RandomObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields ='__all__'

class UniqueUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserUnique
        fields = ['unique_id','flag']


