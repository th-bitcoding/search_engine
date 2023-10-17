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
        user_unique_id = request.query_params.get('unique_id').lower()
        print('query', query)
        user_flag = None
        if user_unique_id:
            try:
                check_user_id = UserUnique.objects.get(unique_id=user_unique_id)
                user_flag = check_user_id.flag
                if not check_user_id.exists():
                    UserUnique.objects.create(unique_id=user_unique_id, flag=query_flag.capitalize())
                    user_flag = query_flag

            except Exception as e:
                print("An error occurred:", str(e))

        Channels = check_flag(user_flag)

        country_name_match = []
        exact_matches = []
        other_results = []
        country_name_nomatch = []
        recent_search = []
        favourite_list = []
        unique_recent_search = []
        recent_search_terms = Search.objects.values_list('search_data', flat=True)
        query_match = []
        recent_search.extend(recent_search_terms)
        unique_recent_search = list(set(data for data in recent_search if data))
        check_ratio = calculate_matching_ratio(query, Channels)

        spelling_related = []
        priority_matches = []  # New list for priority matches

        for channel in Channels:
            json_data = channel.json_data
            for key, data in json_data.items():
                if query_favourite == data['name'].lower() or (query_favourite == '' or None):
                    favourite_list.append(data)

                if query_country == data['country'].lower():
                    exact_matches.append(data)
                    priority_matches.append(data)  # Add to priority matches
                elif query_country in data['country'].lower():
                    exact_matches.append(data)
                else:
                    other_results.append(data)

                for i in check_ratio[:10]:
                    if i[0] == data['name']:
                        spelling_related.append(data)

        spel = []
        for spelling in spelling_related:
            for key, data in spelling.items():
                if key == 'name':
                    spel.append(data)
        detail = spelling_related[0]['name'].split(' ')

        perfect_word = str(difflib.get_close_matches(query.capitalize(), detail))

        random_selects = random_select(exact_matches)

        if (len(favourite_list) == 0) or favourite_list[0]['name'] in Favourite.objects.values_list('name', flat=True):
            pass
        else:
            favourite_data = Favourite.objects.create(country=favourite_list[0]['country'], name=favourite_list[0]['name'],
                                                      stream_video_url=favourite_list[0]['stream_video_url'],
                                                      thumbnail_url=favourite_list[0]['thumbnail_url'])
            favourite_data.save()

        if query:
            searching = Search.objects.create(search_data=query)
        else:
            searching = Search.objects.create(search_data=query_country)
        searching.save()

        for exact_match_data in exact_matches:
            if perfect_word[2:len(perfect_word) - 2].lower() in exact_match_data['name'].lower():
                country_name_match.append(exact_match_data)
            else:
                country_name_nomatch.append(exact_match_data)

        combined_results = country_name_match + country_name_nomatch + other_results

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
            'total_data': total_count,
            'suggestion': random_selects,
            'resent search': unique_recent_search[0:5],
            'priority_matches': priority_matches,  # Add priority matches to the response
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
    
class UniqueDevice(APIView):
    def post(self, request, *args, **kwargs):
        unique_id = request.query_params.get('unique_id', '') 
        flag = request.query_params.get('flag', '') 
        print(unique_id)
       
        serializer = UniqueUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(unique_id = unique_id , flag = flag)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





# class SearchChannels(APIView):
#     def get(self, request):
#         query = request.query_params.get('search_query', '').lower()
#         query_country = request.query_params.get('country_filter', '').lower()
#         query_flag = request.query_params.get('hot_filter', '')
#         query_favourite = request.query_params.get('favourite').lower()
#         user_unique_id = request.query_params.get('unique_id').lower()
#         print('query',query)
#         user_flag = None
#         if user_unique_id:
#             try:
#                 check_user_id = UserUnique.objects.get(unique_id=user_unique_id)
#                 user_flag = check_user_id.flag
#                 if not check_user_id.exists():
#                     UserUnique.objects.create(unique_id = user_unique_id,flag=query_flag.capitalize())
#                     user_flag = query_flag

#             except Exception as e:
#                 print("An error occurred:", str(e))

#         Channels = check_flag(user_flag)

#         country_name_match = []
#         exact_matches = []
#         other_results=[]
#         country_name_nomatch = []
#         recent_search = []
#         favourite_list = []
#         unique_recent_search=[]
#         recent_search_terms = Search.objects.values_list('search_data', flat=True)
#         query_match = []
#         recent_search.extend(recent_search_terms)
#         unique_recent_search = list(set(data for data in recent_search if data))
#         check_ratio = calculate_matching_ratio(query,Channels)
       
#         spelling_related=[]
#         for channel in Channels:
#             json_data = channel.json_data
#             for key, data in json_data.items():
#                 if query_favourite == data['name'].lower() or (query_favourite =='' or None):
#                     favourite_list.append(data)
#                 if query_country == data['country'].lower() or (query_country =='' or None) or (query_country in data['country'].lower()):
#                     exact_matches.append(data)
                
                
#                 else:
#                     other_results.append(data)
#                 for i in check_ratio[:10]:
#                     if i[0] == data['name']:
#                         spelling_related.append(data)
#         spel=[]
#         for spelling in spelling_related:
#             for key,data in spelling.items():
#                 if key == 'name':
#                     spel.append(data)
#         detail = spelling_related[0]['name'].split(' ')
        
      
#         perfect_word = str(difflib.get_close_matches(query.capitalize(), detail))
      
#         random_selects = random_select(exact_matches)

#         if (len(favourite_list) == 0) or favourite_list[0]['name'] in Favourite.objects.values_list('name',flat=True):
#             pass
#         else:
#             favourite_data = Favourite.objects.create(country = favourite_list[0]['country'],name = favourite_list[0]['name'],stream_video_url=favourite_list[0]['stream_video_url'],thumbnail_url=favourite_list[0]['thumbnail_url']) 
#             favourite_data.save()

      
#         if query:
#             searching = Search.objects.create(search_data=query)
#         else:
#             searching = Search.objects.create(search_data=query_country)
#         searching.save()
        
        
#         for exact_match_data in exact_matches:
#             if perfect_word[2:len(perfect_word)-2].lower() in exact_match_data['name'].lower():

#                 country_name_match.append(exact_match_data)
#             else:
#                 pass
#                 country_name_nomatch.append(exact_match_data)

#         combined_results =  country_name_match + country_name_nomatch  + other_results

        
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
#             'suggestion':random_selects,
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