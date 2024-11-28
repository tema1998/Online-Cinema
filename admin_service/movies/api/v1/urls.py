from django.urls import path

from movies.api.v1.views import MoviesListApi, MoviesDetailApi

urlpatterns = [
    path('movies/', MoviesListApi.as_view()),
    path('movies/<uuid:pk>/', MoviesDetailApi.as_view())
]
