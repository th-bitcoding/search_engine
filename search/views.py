import difflib
import random
import nltk
from .models import *
import concurrent.futures
from .serializers import *
from functools import reduce
from collections import deque
from django.db.models import Q
from django.db.models import F
from collections import Counter
from collections import defaultdict
from rest_framework import viewsets
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from rest_framework.pagination import PageNumberPagination
from difflib import SequenceMatcher 
from rest_framework import status
from django.core.paginator import Paginator, EmptyPage
from rest_framework.response import Response
from spellchecker import SpellChecker


class CustomPagination(PageNumberPagination):
    page_size = 10 
    page_size_query_param = 'page_size'
    max_page_size = 1000

class SearchChannels(APIView):
    def get(self, request):
        query = request.query_params.get('search_query', '').lower()
        query_country = request.query_params.get('country_filter', '').lower()
        query_flag = request.query_params.get('hot_filter', '')
        query_favourite = request.query_params.get('favourite').lower()
        user_unique_id = request.query_params.get('unique_id')
     
        conversion_dict = {'': False, None: False, 'false': False, 'true': True}
        query_flag = conversion_dict.get(query_flag.lower(), query_flag)
        print('user_id',user_unique_id)
        country_name_match = []
        exact_matches = []
        name_matches = []
        other_results = []
        country_name_nomatch = []
        recent_search = []
        favourite_list = []
        unique_recent_search=[]
        recent_search_terms = Search.objects.values_list('search_data', flat=True)

        recent_search.extend(recent_search_terms)
        unique_recent_search = list(set(data for data in recent_search if data))
        user_flag = None
        if query_flag !="":
            user_flag = query_flag
        elif user_unique_id:
            try:
                check_user_id = UserUnique.objects.get(unique_id=user_unique_id)
                user_flag = check_user_id.flag
                if not check_user_id.exists():
                    UserUnique.objects.create(unique_id=user_unique_id, flag=query_flag.capitalize())
                    user_flag = query_flag
                else:
                    user_flag = query_flag
                    
            except Exception as e:
                print("An error occurred:", str(e))
        words = ['adult','sexy','hot','fuck','fucked','xxx','anal','massage','teen','naked','pussy','adultbrazzers','porn','boobs',
                 'lesbian','blacked','milf','tiava','hentai','xmaster','HqPorner','faketaxi','gay','mms','amateur','redwap','kiss',
                 'nude','teens','fingering','orgasm','sucking','breastfeeding','18+','playboy','pornhub','dirty','xvideo','sex']
        
        if query == words or query in words:
            user_flag =True
        Channels = check_flag(user_flag)
        spell = SpellChecker()

        query=spell.correction(query)
        for channel in Channels:
            json_data = channel.json_data
            for key, data in json_data.items():
                if query_favourite == data['name'].lower() or (query_favourite =='' or None):
                    favourite_list.append(data)
                
                if query_country == data['country'].lower() or (query_country =='' or None) or (query_country in data['country'].lower()):
                    exact_matches.append(data)
    
                elif query in data['name'].lower() or query in data['country'].lower() or (query == '' or None):
                    name_matches.append(data)

                else:
                    other_results.append(data)

        random_queryset =random.sample([data['name'] for data in exact_matches if data.get('name')],5)

        if len(favourite_list) == 0:
            pass

        elif favourite_list[0]['name'] in Favourite.objects.values_list('name',flat=True):
            pass
        
        else:
            favourite_data = Favourite.objects.create(country = favourite_list[0]['country'],name = favourite_list[0]['name'],stream_video_url=favourite_list[0]['stream_video_url'],thumbnail_url=favourite_list[0]['thumbnail_url']) 
            favourite_data.save()
      
        if query:
            searching = Search.objects.create(search_data=query)
        else:
            searching = Search.objects.create(search_data=query_country)
        searching.save()

        for exact_match_data in exact_matches:
            if query in exact_match_data['name'].lower():
                country_name_match.append(exact_match_data)
            else:
                country_name_nomatch.append(exact_match_data)

        combined_results = country_name_match + country_name_nomatch + name_matches + other_results

        paginator = Paginator(combined_results, per_page=10)  
        page_number = request.query_params.get('page', 1)  

        try:
            page_number = int(page_number)
        except (ValueError, TypeError):
            return Response({'error': 'Invalid page number'}, status=400)

        try:
            result_page = paginator.page(page_number)
        except EmptyPage:
            return Response({'error': 'Invalid page number'}, status=400)
       
        total_count = paginator.count
        response_data = {
            'next_page': None,
            'previous_page': None,
            'current_page': result_page.number,
            'total_pages': paginator.num_pages,
            'total_data':total_count,
            "flag":user_flag,
            'suggestion':random_queryset,
            'resent search': unique_recent_search[0:5],
            'results': result_page.object_list,
        }

        if result_page.has_next():
            query_params = request.GET.copy()
            query_params['page'] = result_page.next_page_number()
            response_data['next_page'] = request.build_absolute_uri(request.path_info) + '?' + query_params.urlencode()

        if result_page.has_previous():
            query_params = request.GET.copy()
            query_params['page'] = result_page.previous_page_number()
            response_data['previous_page'] = request.build_absolute_uri(request.path_info) + '?' + query_params.urlencode()

        return Response(response_data)

# class SearchChannels(APIView):
#     def get(self, request):
#         query = request.query_params.get('search_query', '').lower()
#         query_country = request.query_params.get('country_filter', '').lower()
#         query_flag = request.query_params.get('hot_filter', '')
#         query_favourite = request.query_params.get('favourite').lower()
#         user_unique_id = request.query_params.get('unique_id')
     
#         conversion_dict = {'': False, None: False, 'false': False, 'true': True}
#         query_flag = conversion_dict.get(query_flag.lower(), query_flag)
#         country_name_match = []
#         exact_matches = []
#         name_matches = []
#         other_results = []
#         country_name_nomatch = []
#         recent_search = []
#         favourite_list = []
#         unique_recent_search=[]
#         recent_search_terms = Search.objects.values_list('search_data', flat=True)

#         recent_search.extend(recent_search_terms)
#         unique_recent_search = list(set(data for data in recent_search if data))
#         user_flag = None

#         words = ['adult','sexy','hot','fuck','fucked','xxx','anal','massage','teen','naked','pussy','adultbrazzers','porn','boobs',
#                  'lesbian','blacked','milf','tiava','hentai','xmaster','HqPorner','faketaxi','gay','mms','amateur','redwap','kiss',
#                  'nude','teens','fingering','orgasm','sucking','breastfeeding','18+','playboy','pornhub','dirty','xvideo','sex']
    
#         if query_flag:
#             user_flag = query_flag
        
#         elif query in words:
#             user_flag = True

#         elif user_unique_id:
#             try:
#                 check_user_id = UserUnique.objects.get(unique_id=user_unique_id)
#                 user_flag = check_user_id.flag
#                 if not check_user_id.exists():
#                     UserUnique.objects.create(unique_id=user_unique_id, flag=query_flag.capitalize())
#                     user_flag = query_flag
#                 else:
#                     user_flag = query_flag

#             except Exception as e:
#                 print("An error occurred:", str(e))
 
#         Channels = check_flag(user_flag)
#         spell = SpellChecker()

#         query=spell.correction(query)
#         query_country = spell.correction(query_country)
#         for channel in Channels:
#             json_data = channel.json_data
#             for key, data in json_data.items():
#                 if query_favourite == data['name'].lower() or (query_favourite =='' or None):
#                     favourite_list.append(data)
                
#                 if query_country == data['country'].lower() or (query_country =='' or None) or (query_country in data['country'].lower()):
#                     exact_matches.append(data)
    
#                 elif query in data['name'].lower() or query in data['country'].lower() or (query == '' or None):
#                         name_matches.append(data)

#                 else:
#                     other_results.append(data)
      
#         random_queryset =random.sample([data['name'] for data in exact_matches if data.get('name')],5)
        
#         if len(favourite_list) == 0:
#             pass

#         elif favourite_list[0]['name'] in Favourite.objects.values_list('name',flat=True):
#             pass
        
#         else:
#             favourite_data = Favourite.objects.create(country = favourite_list[0]['country'],name = favourite_list[0]['name'],stream_video_url=favourite_list[0]['stream_video_url'],thumbnail_url=favourite_list[0]['thumbnail_url']) 
#             favourite_data.save()
      
#         if query:
#             searching = Search.objects.create(search_data=query)
#         else:
#             searching = Search.objects.create(search_data=query)
#         searching.save()

#         for exact_match_data in exact_matches:
            
#             if query in exact_match_data['name'].lower():
#                 country_name_match.append(exact_match_data)
#             else:
#                 country_name_nomatch.append(exact_match_data)

#         combined_results = country_name_match + country_name_nomatch + name_matches + other_results

#         paginator = Paginator(combined_results, per_page=10)  
#         page_number = request.query_params.get('page', 1)  

#         try:
#             page_number = int(page_number)
#         except (ValueError, TypeError):
#             return Response({'error': 'Invalid page number'}, status=400)

#         try:
#             result_page = paginator.page(page_number)
#         except EmptyPage:
#             return Response({'error': 'Invalid page number'}, status=400)
       
#         total_count = paginator.count
#         response_data = {
#             'next_page': None,
#             'previous_page': None,
#             'current_page': result_page.number,
#             'total_pages': paginator.num_pages,
#             'total_data':total_count,
#             "flag":user_flag,
#             'suggestion':random_queryset,
#             'resent search': unique_recent_search[0:5],
#             'results': result_page.object_list,
#         }

#         if result_page.has_next():
#             query_params = request.GET.copy()
#             query_params['page'] = result_page.next_page_number()
#             response_data['next_page'] = request.build_absolute_uri(request.path_info) + '?' + query_params.urlencode()

#         if result_page.has_previous():
#             query_params = request.GET.copy()
#             query_params['page'] = result_page.previous_page_number()
#             response_data['previous_page'] = request.build_absolute_uri(request.path_info) + '?' + query_params.urlencode()

#         return Response(response_data)
    
class UniqueDevice(APIView):
    def post(self, request, *args, **kwargs):
        unique_id = request.query_params.get('unique_id', '')  
        flag = request.query_params.get('flag', '') 
        
        existing_user = UserUnique.objects.filter(unique_id=unique_id).first()
        print('898980', existing_user)

        if existing_user:
            return Response({'message': 'User with this unique_id already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        
        UserUnique.objects.create(unique_id=unique_id, flag=flag.capitalize())
       
        new_user = UserUnique.objects.get(unique_id=unique_id)
        serializer = UniqueUserSerializer(new_user)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def put(self, request, *args, **kwargs):
        unique_id = request.query_params.get('unique_id', '')
        flag = request.query_params.get('flag', '')

        existing_user = UserUnique.objects.filter(unique_id=unique_id).first()
        
        if not existing_user:
            return Response({'message': 'User with this unique_id does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        existing_user.flag = flag.capitalize()
        existing_user.save()
       
        serializer = UniqueUserSerializer(existing_user)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

        




# class SearchChannels(APIView):
#     def get_queryset(self):
#         return Search.objects.all()
    
#     def filter_data(self, data, query_params):
#         for key, value in query_params.items():
#             if value and (value.lower() not in str(data.get(key, '')).lower()):
#                 return False
#         return True
    
#     def get(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         query_params = {
#             'query': request.query_params.get('search_query', ''),
#             'country': request.query_params.get('country_filter', ''),
#         }

#         # Convert values to lowercase
#         query_params['query'] = query_params['query'].lower()
#         query_params['country'] = query_params['country'].lower()

#         match_data = []
#         print('query', query_params)
#         for search_data in queryset:
#             # Parse search_data as a dictionary (assuming it's in JSON format)
#             try:
#                 search_data_dict = json.loads(search_data.search_data)
#             except json.JSONDecodeError:
#                 # Handle the case where search_data is not valid JSON
#                 continue
            
#             for key, data in search_data_dict.items():
#                 if self.filter_data(data, query_params):
#                     match_data.append(data)

#         print('/*/*', match_data)
        
#         # Return a JSON response with the matched data
#         return Response(match_data)
def calculate_matching_ratio(query,Channels):
    matching_ratios = {}
    for channel in Channels:
        json_data = channel.json_data
        for key, data in json_data.items():
            if data is not None and data != "":
                data = str(data['name'])
                ratio = SequenceMatcher(None, query, data).ratio()
                
                matching_ratios[data] = ratio
        sorted_matching = sorted(matching_ratios.items(), key=lambda x: x[1], reverse=True)
        # print('matching',matching_ratios.items())
        
        return sorted_matching
    
def calculate_country_ratio(query,Channels):
    matching_ratios = {}
    for channel in Channels:
        json_data = channel.json_data
        for key, data in json_data.items():
            if data is not None and data != "":
                data = str(data['country'])
                ratio = SequenceMatcher(None, query, data).ratio()
                
                matching_ratios[data] = ratio
        sorted_matching = sorted(matching_ratios.items(), key=lambda x: x[1], reverse=True)
        # print('matching',matching_ratios.items())
        
        return sorted_matching
    
def random_select(exact_matches):
    random_queryset =random.sample([data['name'] for data in exact_matches if data.get('name')],5)
    return random_queryset

def check_flag(query_flag):
    conversion_dict = {'': False, None: False, 'false': False, 'true': True}
    query_flag = conversion_dict.get(query_flag, query_flag)
    Channels = Channel.objects.filter(flag=query_flag)
    return Channels


class FavouriteApiview(APIView):
    def get(self,request,*args,**kwargs):
        queryset = Favourite.objects.all()
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset( queryset, request)
        serializers = FavouriteSerializer(result_page,many=True)

        return paginator.get_paginated_response(serializers.data)
    
class RandomSelect(APIView):
    def get(self,request,*args,**kwargs):
        recent_search=[]
        recent_search_terms = Search.objects.values_list('search_data', flat=True)
 
        recent_search.extend(recent_search_terms)
        unique_recent_search = list(set(data for data in recent_search if data))
        # query = request.query_params.get('countrysearch_query', '').lower()
        country_datas = Channel.objects.all()
        for country_data in country_datas:
            json_data = country_data.json_data
        random_check=[]
        for key,value in json_data.items():
            random_check.append(value)
        # pick_name_random =[]
        pick_name_random=[f"{data['name']} - {data['country']}" for data in random_check if data.get('name')]
        # pick_name_random = [f"{data['country']} - {data['name']}" for data in random_check if data.get('name')]
        
        random_queryset = random.sample(pick_name_random,len(pick_name_random))
        response_data={
            'suggestion':unique_recent_search[:10],
            'random':random_queryset,
            
        }
        return Response(response_data)
    
class SingleCountry(APIView):
    def get(self,request,*args,**kwargs):
        queryset = SearchAfg.objects.all()
        query = request.query_params.get('search_query', '').lower()
        match_name = []
        other_match =[]
        for json in queryset:
            sub_objects = json.json_file.get("TV_Data", {}).get("Channel_List", {}).get("main", {}).get("sub", {})
            for key,value in sub_objects.items():
                if query == value['name'].lower() or query in value['name'].lower() or query == value['name_original'].lower() or query in value['name_original'].lower():
                    # value.pop('id')
                    match_name.append(value)
                else:
                    # value.pop('id')
                    other_match.append(value)

        combine_data =match_name + other_match
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(combine_data , request)
        
        # data = list(name)  
        return paginator.get_paginated_response(result_page)
    
class DiffereSol(APIView):
    def get(self, request):
        pass
        # search_value = self.request.GET.get("search", None)
        # if search_value:
        #     sub_objects = SubObjectJSON.objects.all()
        #     for obj in sub_objects:
        #         try:
        #             obj_dict = json.loads(obj.sub_objects)
        #             if search_value.lower() in obj_dict['name'].lower():
        #                 results.append(obj_dict)
        #         except:
        #             pass
        
        # return Response(results)
    
# class MyModelSearchView(generics.ListAPIView):
#     serializer_class = SubObjectJSONSerializer

#     def get_queryset(self):
#         keywords = str(self.request.query_params.get('search', '')).split()
#         print(keywords)
#         q_objects = Q()
#         for keyword in keywords:
#             q_objects |= Q(sub_objects__icontains=keyword)
#         return SubObjectJSON.objects.filter(q_objects)
    
# class MyModelSearchView(generics.ListAPIView):
#     serializer_class = SubObjectJSONSerializer

#     def get_queryset(self):
#         keywords = self.request.query_params.get('search', '').split()
#         suffixes = ['s', 'es', 'ed', 'ing']
#         q_objects = Q()
#         for keyword in keywords:
#             q_objects |= Q(sub_objects__icontains=keyword)
#             for suffix in suffixes:
#                 q_objects |= Q(sub_objects__icontains=keyword + suffix)
#                 q_objects |= Q(sub_objects__icontains=keyword[:-1] + suffix)
#         return SubObjectJSON.objects.filter(q_objects)
    
# class MyModelSearchView(generics.ListAPIView):
#     serializer_class = SubObjectJSONSerializer

#     def get_queryset(self):
#         keywords = self.request.query_params.get('search', '').split()
#         suffixes = ['s', 'es', 'ed', 'ing']
#         q_objects = Q()
#         for keyword in keywords:
#             keyword_q_objects = Q()
#             for suffix in suffixes:
#                 keyword_q_objects |= Q(sub_objects__icontains=keyword + suffix)
#                 keyword_q_objects |= Q(sub_objects__icontains=keyword[:-1] + suffix)
#             q_objects |= keyword_q_objects
#         return SubObjectJSON.objects.filter(q_objects)
    
# class SearchengineViewSet(viewsets.ModelViewSet):
#     serializer_class = SubObjectJSONSerializer

#     def search(self, query):
#         return SubObjectJSON.objects.filter(
#             Q(sub_objects__icontains=query)
#         )

#     def get_queryset(self):
#         queryset = super().get_queryset()
#         query = self.request.query_params.get('search', None)
#         if query:
#             queryset = self.search(query)
#         return queryset