from django.urls import path, register_converter
from . import views, converters

register_converter(converters.FloatUrlParameterConverter, 'float')

urlpatterns = [
    path('', views.index, name='index'),
    path('input/', views.input, name='input'),
    path('search/', views.search_main, name='search_main'),
    path('search/<str:illustrator>', views.search, name='search'),
    path('search/searching/', views.search_searching, name='search_searching'),
    path('story/', views.story_main, name='story_main'),
    path('story/<str:title>/<float:wgenre>/<float:wauthor>', views.story, name='story'),
    path('story/searching/', views.story_searching, name='story_searching'),
    path('download/', views.download, name='download'),
    path('help/', views.help, name='help')
]