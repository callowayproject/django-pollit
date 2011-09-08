from pollit.models import Poll, PollChoice, PollChoiceData, PollClosed, UserCannotVote
from pollit import settings as pollit_settings
import datetime
from django.contrib.auth.models import User, AnonymousUser
from django.http import Http404

from django.test.client import Client
from django.test import TestCase

class TestPollit(TestCase):
    """Tests for Pollit"""
    def setUp(self):

        # Normal Poll
        self.poll = Poll.objects.create(
            question="How are you feeling?",
            pub_date=datetime.datetime.now(),
            slug='how-are-you-feeling',
        )
        
        # Mulitple Choice Poll (multiple choices for ONE poll)
        self.multi_poll = Poll.objects.create(
            question="How are you feeling?",
            pub_date=datetime.datetime.now(),
            slug='how-are-you-feeling2',
            multiple_choice=True)
            
        # Multiple Choice Poll
        self.anon_poll = Poll.objects.create(
            question="How are you feeling?",
            pub_date=datetime.datetime.now(),
            slug='how-are-you-feeling3',
            anonymous=True)

        # Multiple Choice Anonymous Poll
        self.multi_anon_poll = Poll.objects.create(
            question="How are you feeling?",
            pub_date=datetime.datetime.now(),
            slug='how-are-you-feeling4',
            anonymous=True,
            multiple_choice=True)
            
        self.user = User.objects.create_user('demouser','demo@example.com')
        self.anon_user = AnonymousUser()

    def testAddChoice(self):
        
        # Only strings are allowed
        self.assertRaises(ValueError, self.poll.add_choice, 3432)
        
        # Test adding a choice
        self.poll.add_choice("Good")
        self.assertEquals(len(self.poll.pollchoice_set.all()), 1)
        self.assertEquals(self.poll.pollchoice_set.all()[0].choice, "Good")
        
        # Test adding multiple choices at once
        self.poll.add_choices(["Bad", "So So"])
        self.assertEquals(len(self.poll.pollchoice_set.all()), 3)
        
    def testIsClosed(self):
        """
        Test a poll for expiration
        """
        # By Default he poll should be active
        self.assertEquals(self.poll.is_closed(), False)
        
        # Change the status to closed status
        self.poll.status = pollit_settings.STATUS_CLOSED_CHOICE
        self.assertEquals(self.poll.is_closed(), True)
        
        # Change the status to expire by date
        self.poll.status = pollit_settings.STATUS_EXPIRED_BY_DATE_CHOICE
        # If expire by date is used and no expire date is set, the
        # poll is not expired.
        self.assertEquals(self.poll.is_closed(), False)
        
        # Set the date to now, which should make this poll expired
        self.poll.expire_date = datetime.datetime.now()
        self.assertEquals(self.poll.is_closed(), True)
    
    def testGetLatestPoll(self):
        """
        Ensure get latest polls works correctly
        
        Polls with STATUS_CLOSED_CHOICE will not be returned by default
        Polls with DEFAULT_STATUS_EXPIRED_BY_DATE_CHOICE and its expire_date 
            set to before now will not be returned
        Supplying "include_closed" in get_latest_polls will will return all 
            polls
        """
        # We created 4 polls, make sure we get 4 active polls
        polls = Poll.objects.get_latest_polls()
        self.assertEquals(len(polls), 4)
        
        # Set a poll to be closed status, should result in only 3
        # polls returned by get_latest_polls
        self.poll.status = pollit_settings.STATUS_CLOSED_CHOICE
        self.poll.save()
        polls = Poll.objects.get_latest_polls()
        self.assertEquals(len(polls), 3)
        
        # Set a poll to be expired by date choice, but dont set the
        # expire date, this should result in 4 polls again.
        self.poll.status = pollit_settings.DEFAULT_STATUS_EXPIRED_BY_DATE_CHOICE
        self.poll.save()
        polls = Poll.objects.get_latest_polls()
        self.assertEquals(len(polls), 4)
        
        # Set a poll's expire date to ensure it is not returned.
        self.poll.expire_date = datetime.datetime.now()
        self.poll.save()
        polls = Poll.objects.get_latest_polls()
        self.assertEquals(len(polls), 3)
        
        # Set a poll's expire date ahead a day to ensure it does
        # still get returned
        self.poll.expire_date = datetime.timedelta(days=1) + datetime.datetime.now()
        self.poll.save()
        polls = Poll.objects.get_latest_polls()
        self.assertEquals(len(polls), 4)
        
        # Set another poll be to closed
        self.multi_poll.status = pollit_settings.STATUS_CLOSED_CHOICE
        self.multi_poll.save()
        
        # Make sure we get all polls when we ask for non active polls
        polls = Poll.objects.get_latest_polls(include_all=True)
        self.assertEquals(len(polls), 4)
        
        # Make sure the count we specify is the count we are returned
        self.poll.status = pollit_settings.STATUS_ACTIVE_CHOICE
        self.poll.save()
        self.multi_poll.status = pollit_settings.STATUS_ACTIVE_CHOICE
        self.multi_poll.save()
        
        polls = Poll.objects.get_latest_polls()
        self.assertEquals(len(polls), 4)
        polls = Poll.objects.get_latest_polls(count=2)
        self.assertEquals(len(polls), 2)
        
    def testUserCanVote(self):
        """
        Test to ensure a user can vote on all types of polls
        """
        # Normal poll
        self.assertEquals(self.poll.user_can_vote(self.user), True)
        
        # Anonymous poll
        self.assertEquals(self.anon_poll.user_can_vote(self.user), True)
        
        self.assertEquals(self.poll.user_can_vote(None), False)
        
        # Ensure a anonymous user cannot vote
        self.assertEquals(self.poll.user_can_vote(self.anon_user), False)
        
        # Ensure a anonymous user can vote on a anonymous poll
        self.assertEquals(self.anon_poll.user_can_vote(self.anon_user), True)

        # Ensure user cannot vote if they already voted
        self.poll.add_choice("Good")
        self.multi_poll.add_choice("Bad")
        self.multi_poll.add_choice("Ugly")
        PollChoiceData.objects.create(
            choice=self.poll.pollchoice_set.all()[0], 
            user=self.user,
            poll=self.poll)
            
        self.assertEquals(self.poll.user_can_vote(self.user), False)
        
        # Ensure that a user can vote mutliple times for a multi choice poll
        PollChoiceData.objects.create(
            choice=self.multi_poll.pollchoice_set.all()[0], 
            user=self.user,
            poll=self.multi_poll)
            
        self.assertEquals(self.multi_poll.user_can_vote(self.user), True)
        
    def testVote(self):
        """
        Test to ensure voting works
        """
        # Add some data
        self.poll.add_choice("Good")
        self.poll.add_choice("Bad")
        choice = self.poll.pollchoice_set.all()[0]
        
        # Make sure when passing ini None for the choice we get UserCannotVote
        self.assertRaises(UserCannotVote, self.poll.vote, None)
        
        # If user can vote but the choice is not a `PollChoice` instance, we
        # should get a ValueError
        self.assertRaises(ValueError, self.poll.vote, None, self.user)
        
        # Make sure we can UserCannotVote if no user is specified
        self.assertRaises(UserCannotVote, self.poll.vote, choice, None)
        
        # Make a valid vote
        self.poll.vote(choice, self.user)
        # Ensure that we now have 1 total vote and the same for the choice
        self.assertEquals(self.poll.total_votes, 1)
        self.assertEquals(choice.votes, 1)
        
        # Ensure the only poll data is the one we just created.
        choice_data = PollChoiceData.objects.get(poll=self.poll, 
            user=self.user, choice=choice)
        self.assertEquals(self.poll.votes.all()[0], choice_data)
        
        # Set a poll to be expired
        self.multi_poll.status = pollit_settings.DEFAULT_STATUS_EXPIRED_BY_DATE_CHOICE
        self.multi_poll.expire_date = datetime.datetime.now()
        self.multi_poll.save()
        
        # Ensure PollExpired is raise when we try to make a vote on an 
        # expired poll.
        self.assertRaises(PollClosed, self.multi_poll.vote, choice, self.user)
        
        # TODO: multiple choice submission
        
    def testIndexPage(self):
        c = Client()
        response = c.get("/polls/")
        
        # Ensure status 200 is returned
        self.assertEquals(response.status_code, 200)
        
        # Ensure we get back 4 items
        self.assertEquals(len(response.context['poll_list']), 4)
        
    def testDetailPage(self):
        c = Client()
        now = datetime.datetime.now()
        response = c.get(self.poll.get_absolute_url())
        
        # Ensure status 200 is returned
        self.assertEquals(response.status_code, 200)
        
        self.assertEquals(response.context['poll'], self.poll)
        
        response = c.get("/polls/2010/sep/8/blahblah/")
        
        self.assertEquals(response.status_code, 404)
        
        # TODO:
        # response = c.post(self.poll.get_absolute_url(), {'choice': 1})
        
    def testResultPage(self):
        c = Client()
        now = datetime.datetime.now()
        response = c.get(self.poll.get_absolute_results_url())
        
        # Ensure status 200 is returned
        self.assertEquals(response.status_code, 200)
        
        self.assertEquals(response.context['poll'], self.poll)
        
        # TODO: