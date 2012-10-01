"""
The data models for polls, choices and votes
"""
import datetime

from django.db import models
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.db.models import permalink
from django.conf import settings
from django.http import Http404
from settings import AUTHENTICATION_REQUIRED

MULTIPLE_SITES = getattr(settings, 'POLLIT_MULTIPLE_SITES', False)

POLL_STATUS = (
    (1, 'Controlled By Expire Date'),
    (2, 'Open'),
    (3, 'Closed')
)
POLL_COMMENT_STATUS = (
    (1, 'Disabled'),
    (2, 'Show Only'),
    (3, 'Enabled'),
)

class AlreadyVoted(Exception):
    """
    The user has already voted
    """
    pass

class PollExpired(Exception):
    """
    The poll has expired
    """
    pass

class PollManager(models.Manager):
    """
    Adds some basic utility functions for the Poll objects as a whole
    """
    def get_latest_polls(self, count=10, include_expired=False):
        """
        Return the latest <count> polls, optionally including the expired polls
        """
        queryset = super(PollManager, self).get_query_set()
        params = {
            'pub_date__lt': datetime.datetime.now()
        }
        args = []
        if not include_expired:
            from django.db.models import Q
            args = [
                Q(status=1, expire_date__isnull=True) |
                Q(status=1, expire_date__gt=datetime.datetime.now()) |
                Q(status=2)
            ]
        if MULTIPLE_SITES:
            params['sites__pk'] = settings.SITE_ID
        
        polls = queryset.filter(*args, **params).order_by('-pub_date')
        
        return polls[:count]
    
    def update_total_votes(self):
        """
        Just in case the total_votes field in the Poll model isn't or wasn't
        getting updated properly, this function will recalculate it by summing
        the choice totals.
        """
        sql = """UPDATE pollit_poll SET total_votes = v.votes
            FROM (SELECT poll_id, SUM(votes) as votes FROM pollit_pollchoice 
            GROUP BY poll_id) v WHERE pollit_poll.id = v.poll_id"""
        from django.db import connection, transaction
        cursor = connection.cursor()
        cursor.execute(sql)
        transaction.commit_unless_managed()


class Poll(models.Model):
    """
    The basic model for a poll. It includes the question and how it should
    expire (by date, or manually)
    """
    question = models.CharField(max_length=255)
    slug = models.SlugField()
    pub_date = models.DateTimeField(auto_now_add=True)
    if MULTIPLE_SITES:
        sites = models.ManyToManyField(Site, 
            related_name="polls")
    status = models.PositiveIntegerField(default=2, choices=POLL_STATUS)
    expire_date = models.DateTimeField(blank=True, null=True)
    total_votes = models.IntegerField(editable=False, default=0)
    comment_status = models.IntegerField('Comments', 
        default=3, choices=POLL_COMMENT_STATUS)
    
    objects = PollManager()
    
    class Meta:
        ordering = ('-pub_date',)
    
    def __unicode__(self):
        return self.question
    
    @permalink
    def get_absolute_url(self):
        """
        The absolute url for this poll
        """
        return ('pollit_detail', None, {
                'year': self.pub_date.year,
                'month': self.pub_date.strftime('%b').lower(),
                'day': self.pub_date.day,
                'slug': self.slug })
    
    @permalink
    def get_absolute_results_url(self):
        """
        The absolute url for the results of this poll
        """
        from django.core.urlresolvers import reverse
        return ('pollit_results', None, {
                'year': self.pub_date.year,
                'month': self.pub_date.strftime('%b').lower(),
                'day': self.pub_date.day,
                'slug': self.slug })
    
    @permalink
    def get_absolute_comments_url(self):
        """
        The absolute url for comments of this poll
        """
        return ('pollit_comments', None, {
                'year': self.pub_date.year,
                'month': self.pub_date.strftime('%b').lower(),
                'day': self.pub_date.day,
                'slug': self.slug })
    
    def user_can_vote(self, user, poll_choice_data_id, ip):
        """
        Make sure the user is able to vote: Thus if they are logged in 
        see if their user has voted yet, else if IP then check by IP. Otherwise
        they are not allowed to vote
        """

        if AUTHENTICATION_REQUIRED and not user or \
                (AUTHENTICATION_REQUIRED and user and not user.is_authenticated()):
            return False

        if self.get_poll_choice(user, poll_choice_data_id, ip) == None:
            return True
        else:
            return False
    
    def get_poll_choice(self, user, poll_choice_data_id, ip):
        """ Get poll choice. if they are logged in get it by their user otherwise
        get it by the IP """
        
        poll_data_qs = None
        if user and user.is_authenticated():
            poll_data_qs = PollChoiceData.objects.filter(poll__pk=self.pk, 
                                                         user__pk=user.pk)
        elif poll_choice_data_id:
            poll_data_qs = PollChoiceData.objects.filter(id=poll_choice_data_id)
            
        if poll_data_qs and poll_data_qs.count():
            return poll_data_qs[0]
        else:
            return None
        
    def is_expired(self):
        """
        Check if the poll has expired. This is True if the status is 3
        or if the status is 1 and there is no expire date, or the expire
        date has not occured
        """
        if self.status == 2:
            return False
        elif self.status == 3:
            return True
        else:
            if self.expire_date is None:
                return False
            elif self.expire_date <= datetime.datetime.now():
                return True
    
    def vote(self, choice, user, poll_choice_data_id, ip):
        """
        Vote on a poll.
        
        Does all the checks for duplication
        
        :param choice: The id, or :class:`PollChoice` voted
        :type choice:  int or :class:`PollChoice`
        :param user:   The user who voted.
        :type user:    A Django ``User`` instance
        """
        if not self.user_can_vote(user, poll_choice_data_id, ip):
            raise AlreadyVoted()
        
        if self.is_expired():
            raise PollExpired()
        
        try:
            if isinstance(choice, PollChoice):
                selected_choice = choice
            else:
                selected_choice = PollChoice.objects.get(pk=choice)
        except PollChoice.DoesNotExist:
            raise Http404("Selected choice does not exist")
        
        poll_choice_data = PollChoiceData()
        poll_choice_data.poll = self
        poll_choice_data.choice = selected_choice
        if user and user.is_authenticated():
            poll_choice_data.user = user
        if ip:
            # if they had an IP store it
            poll_choice_data.ip = ip
        poll_choice_data.save()
        
        selected_choice.votes += 1
        selected_choice.save()
        self.total_votes += 1
        self.save()
        
        return poll_choice_data

class PollChoice(models.Model):
    """
    Choices for polls. Choices are referenced by their own unique id for voting.
    """
    poll = models.ForeignKey(Poll)
    choice = models.CharField(max_length=255)
    votes = models.IntegerField(editable=False, default=0)
    order = models.IntegerField(default=1)
    
    def percentage(self):
        """
        The percentage of the total votes in the poll that choce this option
        """
        total = self.poll.total_votes
        if total == 0 or self.votes == 0:
            return 0
        return int((float(self.votes) / float(total)) * 100)
    
    def __unicode__(self):
        return self.choice
        
    class Meta:
        ordering = ['order',]
        
        
class PollChoiceData(models.Model):
    """
    A User's vote on a poll
    """
    choice = models.ForeignKey(PollChoice)
    user = models.ForeignKey(User, null=True, blank=True)
    poll = models.ForeignKey(Poll, related_name="votes")
    ip = models.CharField(max_length=50, null=True, blank=True)
    class Meta:
        unique_together = ('choice', 'user')
    