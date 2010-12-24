from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('dovote.views',
                       url(r'^$', 'topics', name='dovote-topics'),
                       url(r'^topic/(?P<topicid>\d+)/$', 'topic', 
                           name='dovote-topic'),
                       url(r'^vote/(?P<itemid>\d+)/$', 'vote',
                           name='dovote-vote'),
                       url(r'^add-topic/$', 'add_topic',
                           name='dovote-add-topic'),
                       url(r'^add-item/(?P<topicid>\d+)/$', 'add_item',
                           name='dovote-add-item'),)
