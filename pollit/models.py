import datetime
from django.db import models

from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.db.models import permalink
from django.conf import settings
from django.http import Http404

POLL_STATUS = (
    (1, 'Controlled By Expire Date'),
    (2, 'Open'),
    (3, 'Closed')
)
POLL_COMMENT_STATUS = (
    (1, 'Disabled'),
    (2, 'Show Only'),
    (3, 'Enabled'),
    (4, 'Allowed'),
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
    def get_latest_polls(self, count=10):
        queryset = super(PollManager, self).get_query_set()
        polls = queryset.filter(
            sites__pk__in=[settings.SITE_ID,], 
            status__in=[1,2],
            pub_date__lt=datetime.datetime.now()).order_by('-pub_date')
            
        poll_list = []
        for poll in polls:
            if poll.status == 1 and poll.expire_date:
                if poll.expire_date > datetime.datetime.now():
                    poll_list.append(poll)
            elif poll.status == 2:
                poll_list.append(poll)
                
        return poll_list[:count]
    
    def update_total_votes(self):
        """
        Just in case the total_votes field in the Poll model isn't or wasn't
        getting updated properly, this function will recalculate it by summing
        the choice totals.
        """
        sql = """UPDATE pollit_poll SET total_votes = v.votes
            FROM (SELECT poll_id, SUM(votes) FROM pollit_pollchoice 
            GROUP BY poll_id) v WHERE pollit_poll.id = v.poll_id"""
        from django.db import connection, transaction
        cursor = connection.cursor()
        cursor.execute(sql)
        transaction.commit_unless_managed()


class Poll(models.Model):
    question = models.CharField(max_length=255)
    slug = models.SlugField()
    pub_date = models.DateTimeField(auto_now_add=True)
    sites = models.ManyToManyField(Site, 
        null=True, 
        blank=True, 
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
        print self.pub_date.year, self.pub_date.month, self.pub_date.day
        return ('pollit_detail', None, {
                'year': self.pub_date.year,
                'month': self.pub_date.strftime('%b').lower(),
                'day': self.pub_date.day,
                'slug': self.slug })
    
    @permalink
    def get_absolute_results_url(self):
        return ('pollit_results', None, {
                'year': self.pub_date.year,
                'month': self.pub_date.month,
                'day': self.pub_date.day,
                'slug': self.slug })
    
    @permalink
    def get_absolute_comments_url(self):
        return ('pollit_results', None, {
                'year': self.pub_date.year,
                'month': self.pub_date.month,
                'day': self.pub_date.day,
                'slug': self.slug })
    
    def user_can_vote(self, user):
        if not user.is_authenticated():
            return False
        try:
            PollChoiceData.objects.get(poll__pk=self.pk, user__pk=user.pk)
            return False
        except PollChoiceData.DoesNotExist:
            return True
    
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
    
    def vote(self, choice, user):
        """
        Vote on a poll.
        
        Does all the checks for duplication
        
        :param choice: The id, or :class:`PollChoice` voted
        :type choice:  int or :class:`PollChoice`
        :param user:   The user who voted.
        :type user:    A Django ``User`` instance
        """
        if not self.user_can_vote(user):
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
        
        PollChoiceData.objects.create(
            poll=self, 
            choice=selected_choice, 
            user=user)
        
        selected_choice.votes += 1
        selected_choice.save()
        self.total_votes += 1
        self.save()


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
    user = models.ForeignKey(User)
    poll = models.ForeignKey(Poll, related_name="votes")
    
    class Meta:
        unique_together = ('choice', 'user')
    