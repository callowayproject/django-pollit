from pollit.models import Poll, PollChoice, PollChoiceData, AlreadyVoted, PollExpired
import datetime
from django.contrib.auth.models import User
from django.http import Http404

from django.test import TestCase

class TestPollit(TestCase):
    """Tests for Pollit"""
    def setUp(self):

        self.poll = Poll.objects.create(
            question="How are you feeling?",
            pub_date=datetime.datetime.now(),
            slug='how-are-you-feeling',
        )
        self.poll.save()

        self.poll.pollchoice_set.create(choice="Yes")
        self.poll.pollchoice_set.create(choice="No")
        self.poll.pollchoice_set.create(choice="What")

        self.user = User.objects.create_user('demouser','demo@example.com')

    def testVoting(self):
        """
        Test the basic Poll.vote method
        """
        selected_choice_id = self.poll.pollchoice_set.all()[1].id
        self.poll.vote(selected_choice_id, self.user)
        self.assertEquals(self.poll.total_votes, 1)
        
        for choice in self.poll.pollchoice_set.all():
            if choice.id == selected_choice_id:
                self.assertEquals(choice.votes, 1)
            else:
                self.assertEquals(choice.votes, 0)
    
    def testVoteOnlyOnce(self):
        """
        Test that a user can only vote once
        """
        selected_choice_id = self.poll.pollchoice_set.all()[1].id
        self.poll.vote(selected_choice_id, self.user)
        selected_choice_id = self.poll.pollchoice_set.all()[0].id
        self.assertRaises(AlreadyVoted, self.poll.vote, selected_choice_id, self.user)
    
    
    def testPollExpired(self):
        """
        The poll is expired if the status is 3 or
        if the status is 2 and IF there is an expire_date, it has not occurred.
        """
        # default is 2, which is always valid
        selected_choice_id = self.poll.pollchoice_set.all()[0].id
        self.poll.vote(selected_choice_id, self.user)
        
        #status 3 is invald (closed)
        self.poll.status = 3
        self.poll.save()
        user = User.objects.create_user('demouser4','demo4@example.com')
        self.assertRaises(PollExpired, self.poll.vote, selected_choice_id, user)
        
        # status 1, but no expire date is valid
        self.poll.status = 1
        self.poll.save()
        user2 = User.objects.create_user('demouser2','demo2@example.com')
        self.poll.vote(selected_choice_id, user2)
        
        # status 1, and now has an expire_date
        self.poll.expire_date = datetime.datetime.now()
        self.poll.save()
        user3 = User.objects.create_user('demouser3','demo3@example.com')
        selected_choice_id = self.poll.pollchoice_set.all()[0].id
        self.assertRaises(PollExpired, self.poll.vote, selected_choice_id, user3)
    
    
    def testGetLatestPoll(self):
        """
        Make sure the code querying for only non-exired polls works
        """
        # Default status is open
        polls = Poll.objects.get_latest_polls()
        self.assertEquals(len(polls), 1)
        
        # Set to expire by date, but have no start or end date is valid
        self.poll.status = 1
        self.poll.save()
        polls = Poll.objects.get_latest_polls()
        self.assertEquals(len(polls), 1)
        
        # Set to expire by date, has start but no end date is valid
        self.poll.pub_date = datetime.datetime(2010,1,1)
        self.poll.save()
        polls = Poll.objects.get_latest_polls()
        self.assertEquals(len(polls), 1)
        
        # Set to expire by date, but has start and end date, but not reached end
        self.poll.expire_date = datetime.datetime(2030,1,1)
        self.poll.save()
        polls = Poll.objects.get_latest_polls()
        self.assertEquals(len(polls), 1)
        
        # Set to expire by date, but has start and end date and past end is
        # not valid
        self.poll.expire_date = datetime.datetime(2010,1,2)
        self.poll.save()
        polls = Poll.objects.get_latest_polls()
        self.assertEquals(len(polls), 0)
        polls = Poll.objects.get_latest_polls(include_expired=True)
        self.assertEquals(len(polls), 1)
        
        # Set to expired
        self.poll.status = 3
        self.poll.save()
        polls = Poll.objects.get_latest_polls()
        self.assertEquals(len(polls), 0)
        polls = Poll.objects.get_latest_polls(include_expired=True)
        self.assertEquals(len(polls), 1)

        