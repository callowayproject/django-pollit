import datetime
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.safestring import mark_safe
from django.views.decorators.cache import cache_page
from django.utils.dates import MONTHS_3_REV

from models import Poll, PollChoice, PollChoiceData, PollType

def index(request, count=10, template_name="pollit/index.html"):
    """
    Returns the latest polls, default is 10
    """
    polls = Poll.objects.get_latest_polls(count=count)
    
    return render_to_response(template_name,
                              {'poll_list': polls},
                              context_instance=RequestContext(request))
                              
def detail(request, year, month, slug, template_name="pollit/detail.html"):
    try:
        poll = Poll.objects.get(
            pub_date__year=year, 
            pub_date__month=MONTHS_3_REV[month],
            slug=slug,
            sites__pk__in=[settings.SITE_ID,])
    except:
        raise Http404
        
    if request.user.is_authenticated():
        try:
            PollChoiceData.objects.get(choice__poll__pk=poll.pk, user=request.user.pk)
            has_voted = True
        except:
            has_voted = False
    else:
        has_voted = False
        
    if has_voted:
        return HttpResponseRedirect("%sresults/" % poll.get_absolute_url())
    # If user is logged in and has not voted
    if request.POST.items() and request.user.is_authenticated() and not has_voted:
        try:
            selected_choice = PollChoice.objects.get(pk=request.POST['choice'])
        except PollChoice.DoesNotExist:
            return HttpResponseRedirect(poll.get_absolute_url())
            
        selected_choice.votes += 1
        selected_choice.save()
        
        PollChoiceData.objects.create(choice=selected_choice, user=request.user)
        return HttpResponseRedirect("%sresults/" % poll.get_absolute_url()) 
    
    return render_to_response(template_name,
                              {'poll': poll,
                               'has_voted': has_voted},
                              context_instance=RequestContext(request))
                              
def results(request, year, month, slug, template_name="pollit/results.html"):
    """
    A simple view to show the results on a seperate url
    """
    try:
        poll = Poll.objects.get(
            pub_date__year=year, 
            pub_date__month=MONTHS_3_REV[month],
            slug=slug,
            sites__pk__in=[settings.SITE_ID,])
    except:
        raise Http404
        
    return render_to_response(template_name,
                              {'poll': poll},
                              context_instance=RequestContext(request))
    
    
