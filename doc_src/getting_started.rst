===============
Getting Started
===============

Create your first poll
======================

::

    poll = Pollit.objects.create(question="How are you?")

    poll.add_choice(choice="Good")
    poll.add_choice(choice="Bad")
    poll.add_choice(choice="So So")

or::

    poll.add_choices(["Good", "Bad", "So So"])
    
By default this poll will be for registered users and they can only 
select one choice.

Configuration options
=====================

`Pollit` allows for a couple different types of polls:

Registered/Anonymous Users
--------------------------

* Registered users, one choices per user
* Registered users, multiple choices per user
* Registered users, limited multiple choices per user
* Anonymous users, one choice per user
* Anonymous users, multiple choices per user
* Anonymous users, limited multiple choices per user


.. note::

    Multiple choice means multiple selections for one poll, not multiple
    submissions per poll.
    
    Multiple Choice Poll Example:
        
        * User1 submits choice1 and choice2 for pollA
        * User1 has selected 2 choices for pollA
        * User1 cannot then submit a vote for pollA again
    
Expiration
----------

Any poll can have an expiration date if the status is set for date expiration.
By default this is status choice 1. (1 'Controlled By Expire Date'), this can 
be changed to a custom status as well. See :ref:`settings` for more 
information.

Anonymous Users
===============

The values for a anonymous user are simple, same as a registered user except 
that the `user` field is left null. The value will be stored in the user's 
cookies (if user's browser allows it), as well in order to determine if the 
user has already voted.

