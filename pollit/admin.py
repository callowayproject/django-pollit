from django.contrib import admin
from models import Poll, PollType, PollChoice, PollChoiceData

class ChoiceInline(admin.TabularInline):
    model = PollChoice
    extra = 5

class PollAdmin(admin.ModelAdmin):
    list_display = ('question', 'status', 'pub_date', 'expire_date', 'show_types')
    list_filter = ('types', 'status',)
    prepopulated_fields = {"slug": ("question",)}
    search_fields = ['question',]
    
    inlines = [ChoiceInline, ]
    
    def show_types(self, obj):
        return ', '.join([t.name for t in obj.types.all()])
        

admin.site.register(Poll, PollAdmin)
admin.site.register(PollType)
#admin.site.register(PollChoice)
#admin.site.register(PollChoiceData)