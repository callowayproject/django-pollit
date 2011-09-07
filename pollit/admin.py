"""The ModelAdmin definitions for creating and editing polls in the admin"""
from django.contrib import admin
from pollit.models import Poll, PollChoice

class ChoiceInline(admin.TabularInline):
    """The inline choices for the poll"""
    model = PollChoice
    extra = 5

class PollAdmin(admin.ModelAdmin):
    """The Poll Admin, with choices inline"""
    list_display = ('question', 'status', 'total_votes', 'pub_date', 'expire_date')
    list_filter = ('status', 'multiple_choice', 'comment_status', 'anonymous')
    prepopulated_fields = {"slug": ("question",)}
    search_fields = ['question',]
    
    inlines = [ChoiceInline, ]

admin.site.register(Poll, PollAdmin)
