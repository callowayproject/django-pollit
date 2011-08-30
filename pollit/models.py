"""
The data models for polls, choices and votes
"""
import datetime

from django.db import models
from django.contrib.auth.models import User
from django.db.models import permalink
from django.utils.translation import ugettext as _

from pollit import settings as pollit_settings

class UserCannotVote(Exception):
    """
    The user must be Authenticated
    """
    pass

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
        Return the latest <count> polls, optionally including the 
        expired polls
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
        
        polls = queryset.filter(*args, **params).order_by('-pub_date')
        
        return polls[:count]
    
    @staticmethod
    def update_total_votes():
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
    The model for a poll. 
    """
    question = models.CharField(_("Question"), max_length=255)
    slug = models.SlugField(_("Slug"))
    pub_date = models.DateTimeField(_("Publish Date"))
    status = models.PositiveIntegerField(_("Status"), 
        choices=pollit_settings.STATUS_CHOICES)
    expire_date = models.DateTimeField(_("Expire Date"), blank=True,
        null=True)
    total_votes = models.IntegerField(_("Total Votes"), editable=False, 
        default=0)
    anonymous = models.BooleanField(_("Anonymous Voting"), 
        default=pollit_settings.ANONYMOUS_VOTING)
    multiple_choice = models.BooleanField(_("Multiple Choice"), default=False)
    comment_status = models.IntegerField(_('Comments Status'), 
        choices=pollit_settings.COMMENT_STATUS_CHOICES)
    
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
    
    def user_can_vote(self, user):
        """
        Make sure the user is able to vote: Logged in and hasn't voted or
        ANONYMOUS_VOTING is set to True
        """
        # If poll allows anonymous, user can vote
        if self.anonymous:
            return True
            
        # If no anonymous voting is allowed, make sure user is authenticated.
        if not user.is_authenticated():
            return False
            
        try:
            # User has already voted
            PollChoiceData.objects.get(poll__pk=self.pk, user__pk=user.pk)
            return False
        except PollChoiceData.DoesNotExist:
            return True
    
    def is_expired(self):
        """
        Check if the poll has expired. Two settings can dictate which 
        status to look for when determining if the poll is expired:
        
            EXPIRE_CHOICE - if the poll status is this setting, 
                poll is expired
            
            EXPIRED_BY_DATE_CHOICE - if the poll status is this setting, the 
                poll's expire date will be used to determine if its expored
                
                expire_date can be null, therefore the poll will never expire
                if status is EXPIRED_BY_DATE_CHOICE
        """
        if self.status == pollit_settings.EXPIRED_CHOICE:
            return True
        elif self.status == pollit_settings.EXPIRED_BY_DATE_CHOICE:
            if not self.expire_date:
                return False
            elif self.expire_date <= datetime.datetime.now():
                return True
        return False
    
    def vote(self, choice, user=None):
        """
        Vote on a poll.
        
        Does all the checks for duplication
        
        :param choice: The id, or :class:`PollChoice` voted
        :type choice:  int or :class:`PollChoice`
        :param user:   The user who voted (Optional).
        :type user:    A Django ``User`` instance
        """
        
        if not self.user_can_vote(user):
            raise UserCannotVote()
        
        if self.is_expired():
            raise PollExpired()
        
        if isinstance(choice, PollChoice):
            selected_choice = choice
        else:
            raise Exception, "choice argument must be a `PollChoice` instance"

        
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
    Choices for polls.
    """
    poll = models.ForeignKey(Poll, verbose_name=_("Poll"))
    choice = models.CharField(_("Choice"), max_length=255)
    votes = models.IntegerField(_("Votes"), editable=False, default=0)
    order = models.IntegerField(_("Order"), default=1)
    
    def percentage(self):
        """
        The percentage of the total votes in the poll
        """
        total = self.poll.total_votes
        if total == 0 or self.votes == 0:
            return 0
        return int((float(self.votes) / float(total)) * 100)
    
    def __unicode__(self):
        return "%s - %s" % (self.poll.question, self.choice)
        
    class Meta:
        ordering = ['order',]
        
        
class PollChoiceData(models.Model):
    """
    A User's vote on a poll
    """
    choice = models.ForeignKey(PollChoice, verbose_name=_("Choice"))
    user = models.ForeignKey(User, null=True, blank=True, 
        verbose_name=_("User"))
    poll = models.ForeignKey(Poll, related_name="votes", 
        verbose_name=_("Poll"))
    
    