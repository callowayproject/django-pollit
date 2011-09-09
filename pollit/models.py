"""
The data models for polls, choices and votes
"""
import datetime

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.db.models import permalink
from django.utils.translation import ugettext as _

from pollit import settings as pollit_settings

class UserCannotVote(Exception):
    """
    The user must be Authenticated
    """
    pass

class PollClosed(Exception):
    """
    The poll has closed
    """
    pass
    
class TooManyChoicesSelected(Exception):
    """
    User has selected too many choices
    """
    pass

class PollManager(models.Manager):
    """
    Adds some basic utility functions for the Poll objects as a whole
    """
        
    def get_latest_polls(self, count=10, include_all=False):
        """
        Return the latest <count> polls, optionally including the 
        expired polls
        """
        queryset = super(PollManager, self).get_query_set()
        
        eargs, params = [], {}
        if not include_all:
            # Make sure the poll is not set to STATUS_CLOSED_CHOICE and
            # that the poll is not expired
            eargs = [
                Q(status=pollit_settings.STATUS_CLOSED_CHOICE) |
                Q(status=pollit_settings.STATUS_EXPIRED_BY_DATE_CHOICE,
                    expire_date__isnull=False,
                    expire_date__lte=datetime.datetime.now())
            ]
            # Ensure the published date is before or equal to now
            params = {
                'pub_date__lte': datetime.datetime.now(),
            }
            
        polls = queryset.filter(**params).exclude(*eargs).order_by('-pub_date')
        
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
    pub_date = models.DateTimeField(_("Publish Date"), 
        default=datetime.datetime.now)
    status = models.PositiveIntegerField(_("Status"), 
        choices=pollit_settings.STATUS_CHOICES, 
        default=pollit_settings.STATUS_ACTIVE_CHOICE)
    expire_date = models.DateTimeField(_("Expire Date"), blank=True,
        null=True)
    total_votes = models.IntegerField(_("Total Votes"), editable=False, 
        default=0)
    anonymous = models.BooleanField(_("Anonymous Voting"), 
        default=False)
    multiple_choice = models.BooleanField(_("Multiple Choice"), default=False)
    multiple_choice_limit = models.PositiveIntegerField(
        _("Mutliple Choice Limit"), default=0)
    comment_status = models.IntegerField(_('Comments Status'), null=True, 
        blank=True, choices=pollit_settings.COMMENT_STATUS_CHOICES)
    
    objects = PollManager()
    
    class Meta:
        ordering = ('-pub_date',)
    
    def __unicode__(self):
        return self.question
    
    def add_choice(self, choice):
        """
        Add a choice to the poll
        """
        if not isinstance(choice, str):
            raise ValueError, "choice must be a string."
            
        self.pollchoice_set.create(choice=choice)
        
    def add_choices(self, choices):
        """
        Add multiple choices to the poll
        """
        for choice in choices:
            self.add_choice(choice)
    
    @staticmethod
    def get_active_status_choices():
        """
        Retrieve all status choices that can make the poll active
        """
        return [s for s, v in pollit_settings.STATUS_CHOICES if s not in [
            pollit_settings.STATUS_EXPIRED_BY_DATE_CHOICE, 
            pollit_settings.STATUS_CLOSED_CHOICE]]
            
            
    def _get_url(self, name):
        """ Given a name, returns the arguments needed for getting urls """
        return (name, None, {
            'year': self.pub_date.year,
            'month': self.pub_date.strftime('%b').lower(),
            'day': self.pub_date.day,
            'slug': self.slug })
        
    @permalink
    def get_absolute_url(self):
        """ The absolute url for this poll """
        return self._get_url('pollit_detail')
    
    @permalink
    def get_absolute_results_url(self):
        """ The absolute url for the results of this poll """
        return self._get_url('pollit_results')
        
    @permalink
    def get_absolute_comments_url(self):
        """ The absolute url for comments of this poll """
        return self._get_url('pollit_comments')
    
    def user_can_vote(self, user):
        """ Make sure the user is able to vote """
        # If poll is anonymous, user can vote.
        if self.anonymous:
            return True
            
        # If no anonymous voting is allowed, make sure user is authenticated.
        if not user or not user.is_authenticated():
            return False
            
        polldata = self.votes.filter(user__pk=user.pk)
            
        # If no votes were found for user, return True
        if not len(polldata):
            return True 
        # If there is a length and multiple choice is allowed, return True
        elif self.multiple_choice:
            return True
            
        # TODO: check for limited choice selection
        
        # Default return
        return False
    
    def is_closed(self):
        """
        Check if the poll has expired. Two settings can dictate which 
        status to look for when determining if the poll is expired:
        
            STATUS_CLOSED_CHOICE - if the poll status is this setting, 
                poll is expired
            
            STATUS_EXPIRED_BY_DATE_CHOICE - if the poll status is this 
                setting, the poll's expire date will be used to determine 
                if its expored
        """
        if self.status == pollit_settings.STATUS_CLOSED_CHOICE:
            return True
        elif self.status == pollit_settings.STATUS_EXPIRED_BY_DATE_CHOICE:
            if not self.expire_date:
                return False
            elif self.expire_date <= datetime.datetime.now():
                return True
        return False
    
    def vote(self, choice, user=None):
        """ Vote on a poll. """
        
        if not self.user_can_vote(user):
            raise UserCannotVote
        
        if self.is_closed():
            raise PollClosed
        
        if isinstance(choice, PollChoice):
            selected_choice = choice
        else:
            raise ValueError, "choice argument must be a `PollChoice` instance"

        # Create the poll choice data
        self.votes.create(
            choice=selected_choice, 
            user=user)
        
        # Increament the totals
        selected_choice.votes += 1
        selected_choice.save()
        self.total_votes += 1
        self.save()


class PollChoice(models.Model):
    """ Choices for polls. """
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
    A User's choice on a poll, user can be null (for anonymous polls)
    """
    choice = models.ForeignKey(PollChoice, verbose_name=_("Choice"))
    user = models.ForeignKey(User, null=True, blank=True, 
        verbose_name=_("User"))
    poll = models.ForeignKey(Poll, related_name="votes", 
        verbose_name=_("Poll"))
    
        
