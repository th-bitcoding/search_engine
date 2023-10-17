from django.contrib import admin
from django.urls import path, include
# from . import views
from rest_framework import routers
from .views import *

# router = routers.DefaultRouter()
# router.register(r'search', SearchengineViewSet)

urlpatterns = [
   # path('api/', include(router.urls)),
   path('api/search/', SearchChannels.as_view(), name='search_channels'),
   path('api/search/favourite/', FavouriteApiview.as_view(), name='favourite'),
   path('api/search/random/', RandomSelect.as_view(), name='random'),
   path('api/search/singlecountry/', SingleCountry.as_view(), name='singlecountry'),
   path('api/search/uniquedevice/', UniqueDevice.as_view(), name='uniquedevice'),
   path("api/deffer_sol/", DiffereSol.as_view()),
   

]