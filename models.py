from datetime import date

from django.db import models

class VoterManager(models.Manager):
    '''Get voter with this voter id, or create one if voterid is None'''
    def get_or_create(self, voterid):
        if not voterid:
            v = Voter(name='None')
            v.save()
            return v
        else:
            return self.get(pk=voterid)

class Voter(models.Model):
    '''A voter is an internal data structure. Not visible to the user.
    
    Automatically created and stored in sessions.
    Note: none of these fields are currently being used.
    If ever we need to have real security and real voter
    authentication, and if we end up using oauth for
    authentication, (e.g. using facebook or twitter account
    for authentication) then we will use these fields.'''
    name = models.CharField(max_length=40)
    email = models.CharField(max_length=80)
    auth_token = models.CharField(max_length=255, blank=True, null=True)
    auth_token_secret = models.CharField(max_length=255, blank=True, null=True)

    objects = VoterManager()

    def __unicode__(self):
        return self.id

    def vote(self, item, **args):
        return Vote.objects.vote(self, item, **args)

    def votes(self, topic, voter):
        return Vote.objects.filter(voter=voter, item__topic=topic)

class Topic(models.Model):
    '''A topic for voting and suggestions

    created is usually filled in automatically
    closed indicates that this topic is no longer open for voting
    '''
    title = models.CharField(max_length=72)
    description = models.TextField(blank=True, null=True)
    created = models.DateField(verbose_name='Date this topic was created',
                               blank=True)
    closed = models.BooleanField()

    @models.permalink
    def get_absolute_url(self):
        return('dovote-topic', (), dict(topicid=self.pk))
        
    def __unicode__(self):
        return self.title

    def save(self):
        if not self.created:
            self.created = date.today()
        return super(Topic, self).save()

class Item(models.Model):
    '''An item for which people can vote

    Note: in our system, individual items can be retired from the vote
    by settings closed=True. In that case, it is good form to specify
    a reason.

    Note: 'created' is currently unused, but I'm hoping to use it to
    highlight "new" items.
    '''
    topic = models.ForeignKey(Topic)
    title = models.CharField(max_length=72)
    description = models.TextField(blank=True, null=True,
                                   verbose_name='Description (optional)')
    closed = models.BooleanField(default=False)
    closed_reason = models.CharField(max_length=255, blank=True, null=True)
    created = models.DateField(blank=True)

    @models.permalink
    def get_vote_url(self):
        return('dovote-vote', (), dict(itemid=self.pk))

    def save(self):
        if not self.created:
            self.created = date.today()
        return super(Item, self).save()

    def votes(self):
        return self.vote_set.count()

    def __unicode__(self):
        return self.title

class VoteManager(models.Manager):
    def vote(self, voter, item, ip_address=None):
        '''Vote for this item, by this voter

        Return True if this resulted in a new vote being registered.
        Return False if this voter had already voted for this item.
        '''
        try:
            self.get(voter=voter, item=item)
            return False
        except self.model.DoesNotExist:
            v = Vote(voter=voter, item=item, ip_address=ip_address)
            v.save()
            return True

class Vote(models.Model):
    '''A single vote.

    Not sure how we plan to use IP address. Maybe as a simplistic
    scheme for detecting vote fraud...
    '''
    voter = models.ForeignKey(Voter)
    item = models.ForeignKey(Item)
    date = models.DateField()
    ip_address = models.CharField(max_length=20)

    objects = VoteManager()

    def __unicode__(self):
        return '%s by %s' % (self.item, self.voter)

    def save(self):
        if not self.date:
            self.date = date.today()
        return super(Vote, self).save()
