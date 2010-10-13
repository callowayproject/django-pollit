"""Request handling code for pollit"""
import datetime
from django.conf import settings
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from models import Poll, PollChoiceData, PollExpired

MULTIPLE_SITES = getattr(settings, 'POLLIT_MULTIPLE_SITES', False)

def index(request, count=10, template_name="pollit/index.html"):
    """
    Returns the latest polls, default is 10
    """
    polls = Poll.objects.get_latest_polls(count=count, include_expired=True)
    
    return render_to_response(template_name,
                              {'poll_list': polls},
                              context_instance=RequestContext(request))

def detail_old(request, year, month, slug, template_name="pollit/detail.html"):
    """A backwards-compatible way to handle the old urls"""
    return detail(request, year, month, None, slug, template_name)

def detail(request, year, month, day, slug, template_name="pollit/detail.html"):
    """
    Display the basic voting page. If the user has voted or is not authenticated
    They cannot vote.
    """
    params = {
        'pub_date__year': year,
        'pub_date__month': datetime.datetime.strptime(month, '%b').month,
        'slug': slug,
    }
    
    if MULTIPLE_SITES:
        params['sites__pk'] = settings.SITE_ID
    if day is not None:
        params['pub_date__day'] = day
    
    try:
        poll = Poll.objects.get(**params)
    except Poll.DoesNotExist, Poll.MultipleItemsReturned:
        raise Http404
    
    errors = []
    poll_choice = None
    if request.user.is_authenticated():
        try:
            poll_choice = PollChoiceData.objects.get(
                poll__pk=poll.pk, 
                user__pk=request.user.pk)
        except PollChoiceData.DoesNotExist:
            pass
        
    
    # If user is logged in and has not voted
    if 'choice' in request.POST and request.user.is_authenticated():
        try:
            if not poll_choice:
                poll.vote(request.POST['choice'], request.user)
                return HttpResponseRedirect(poll.get_absolute_results_url())
        except PollExpired:
            errors.append('The poll has expired.')
        
    return render_to_response(template_name,
                              {'poll': poll,
                               'has_voted': (poll_choice is not None),
                               'user_choice': poll_choice,
                               'errors': errors},
                              context_instance=RequestContext(request))

def results_old(request, year, month, slug, template_name="pollit/results.html"):
    """A backwards-compatible way to handle the old urls"""
    return results(request, year, month, None, slug, template_name)

def results(request, year, month, day, slug, template_name="pollit/results.html"):
    """
    A simple view to show the results on a seperate url
    """
    params = {
        'pub_date__year': year,
        'pub_date__month': datetime.datetime.strptime(month, '%b').month,
        'slug': slug,
    }
    
    if MULTIPLE_SITES:
        params['sites__pk'] = settings.SITE_ID
    if day is not None:
        params['pub_date__day'] = day
    
    try:
        poll = Poll.objects.get(**params)
    except:
        raise Http404
    
    poll_choice = None
    if request.user.is_authenticated():
        try:
            poll_choice = PollChoiceData.objects.get(
                choice__poll__pk=poll.pk, 
                user=request.user.pk)
        except PollChoiceData.DoesNotExist:
            pass
    
    return render_to_response(template_name,
                              {'poll': poll,
                              'has_voted': poll_choice is not None,
                              'user_choice': poll_choice},
                              context_instance=RequestContext(request))
    
    
