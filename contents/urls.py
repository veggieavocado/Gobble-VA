from django.conf.urls import url

from contents.views import (
    WantedContentAPIView,
    WantedContentDetailsAPIView,
    WantedUrlAPIView,
    WantedUrlDetailsAPIView,
    WantedDataAPIView,
    WantedDataDetailsAPIView,
    NaverContentAPIView,
    NaverContentDetailsAPIView,
    NaverDataAPIView,
    NaverDataDetailsAPIView,
)

urlpatterns = [
    url(r'^job_contents/$', WantedContentAPIView.as_view(), name='job-contents'),
    url(r'^job_contents/(?P<pk>[\w.@+-]+)/$', WantedContentDetailsAPIView.as_view(), name='job-contents-details'),
    url(r'^wanted_url/$', WantedUrlAPIView.as_view(), name='wanted-url'),
    url(r'^wanted_url/(?P<pk>[\w.@+-]+)/$', WantedUrlDetailsAPIView.as_view(), name='wanted-url-details'),
    url(r'^wanted_data/$', WantedDataAPIView.as_view(), name='wanted-data'),
    url(r'^wanted_data/(?P<pk>[\w.@+-]+)/$', WantedDataDetailsAPIView.as_view(), name='wanted-data-details'),
    url(r'^naver_contents/$', NaverContentAPIView.as_view(), name='naver-contents'),
    url(r'^naver_contents/(?P<pk>[\w.@+-]+)/$', NaverContentDetailsAPIView.as_view(), name='naver-contents-details'),
    url(r'^naver_data/$', NaverDataAPIView.as_view(), name='naver-data'),
    url(r'^naver_data/(?P<pk>[\w.@+-]+)/$', NaverDataDetailsAPIView.as_view(), name='naver-data-details'),
    ]
