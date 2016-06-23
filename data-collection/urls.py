from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'data-collection.views.home', name='home'),
    url(r'^storeGameLevelData$', 'data-collection.views.storeGameLevelData', name='storeGameLevelData'),
)
