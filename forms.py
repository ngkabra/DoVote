from django import forms
from django.template.defaultfilters import striptags

from models import Item, Topic

class ItemForm(forms.ModelForm):
    topic = forms.ModelChoiceField(queryset=Topic.objects.all(),
                                   widget=forms.HiddenInput())

    def clean_title(self):
        return striptags(self.cleaned_data['title'])

    def clean_description(self):
        '''Remove html tags from description.

        For security. Would have liked to allow some simpler tags
        like strong, ul, li, etc. But that involves using a 
        full blown html parser etc. Maybe this is a TODO.
        '''
        return striptags(self.cleaned_data['description'])

    class Meta:
        model = Item

class TopicForm(forms.ModelForm):
    def clean_title(self):
        return striptags(self.cleaned_data['title'])

    def clean_description(self):
        return striptags(self.cleaned_data['description'])

    class Meta:
        model = Topic
        exclude = ('created', 'closed')

