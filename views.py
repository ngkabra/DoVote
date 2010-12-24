from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from forms import ItemForm, TopicForm
from models import *


def get_voter(request):
    '''Get 'voter' object associated with this session, or create one

    We don't want to bother people with having to register/login,
    and we don't want to force them to use their facebook/twitter
    accounts either. Voting should simply be a matter of clicking.

    However, we do want to make some feeble attempts at preventing
    a person from voting multiple times. We do that using sessions.
    Not a great solution, but should work in most casual cases.
    '''
    voterid = request.session.get('voterid')
    voter = Voter.objects.get_or_create(voterid)
    if not voterid:
        request.session['voterid'] = voter.id
    return voter

def goto_topic(t, msg=None):
    '''Redirect user to topic t, and display msg at the top of his screen'''
    return HttpResponseRedirect(t.get_absolute_url() + '?user_msg=%s' % (msg,))

def topics(request):
    '''The "home page". Shows list of topics that are up for voting'''
    topic_list = Topic.objects.filter(closed=False).order_by('-created')
    return render_to_response('dovote/topics.html',
                              dict(topic_list=topic_list),
                              context_instance=RequestContext(request))

def topic(request, topicid):
    '''Show the page for this topic'''
    t = get_object_or_404(Topic, pk=topicid)
    voter = get_voter(request)
    options = t.item_set.annotate(votes=Count('vote')).order_by('-votes')
    return render_to_response('dovote/topic.html',
                              dict(topic=t,
                                   options=options),
                              context_instance=RequestContext(request))

def vote(request, itemid):
    '''Register a vote for this item.

    Also remember the 'voterid' in the session in a lame
    attempt to prevent him from voting for the same item
    multiple times'''
    item = get_object_or_404(Item, pk=itemid)
    voter = get_voter(request)

    '''Note: we just remember the IP address of the voter.
    This is just so that, if some day in the future it is discovered
    that someone voted too many times for the same item, we can
    use the IP address to remove those votes.

    Yes, I know, this is another lame attempt at partial security.
    '''
    if voter.vote(item, ip_address=request.META.get('REMOTE_ADDR')):
        msg = 'Your vote for %s has been registered' % item.title
    else:
        msg = 'You have already voted for this item'
    return goto_topic(item.topic, msg)

def add_topic(request):
    '''Add a new topic'''
    tform = None
    if request.method == 'POST':
        tform = TopicForm(request.POST)
        if tform.is_valid():
            t = tform.save()
            'If topic was added successfully, send them to that topic page'
            return goto_topic(t, 'Now you can start adding options')
    
    if not tform:
        tform = TopicForm()

    return render_to_response('dovote/add_topic.html',
                              dict(tform=tform),
                              context_instance=RequestContext(request))

def add_item(request, topicid):
    '''Add a new item to this topic

    Sadly, we have no way of detecting near-duplicates. Oh well'''
    t = get_object_or_404(Topic, pk=topicid)
    iform = None
    if request.method == 'POST':
        iform = ItemForm(request.POST)
        if iform.is_valid():
            iform.save()
            'If item added successfully, go back to topic page'
            return goto_topic(t, 'New option added to topic')

    if not iform:
        iform = ItemForm(initial=dict(topic=t.pk))

    return render_to_response('dovote/item.html',
                              dict(topic=t,
                                   iform=iform),
                              context_instance=RequestContext(request))
