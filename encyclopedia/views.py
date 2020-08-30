from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.files.storage import default_storage

from . import util
import re, random
import markdown2


class SearchForm(forms.Form):
    """Search form"""
    title = forms.CharField(label='Search Encyclopedia')
    

class NewPage(forms.Form):
    """New page form"""
    title = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'Title'}))
    content = forms.CharField(label='', widget=forms.Textarea(attrs={'placeholder': 'Content...'}))


class EditPage(forms.Form):
    """Edit page form"""
    content = forms.CharField(label='', widget=forms.Textarea)


def index(request):
    """Show all entries"""
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            if util.get_entry(title):
                return HttpResponseRedirect(reverse('wiki:entry_page', args=(title,)))
            else:
                return HttpResponseRedirect(reverse('wiki:search', args=(title,)))
        else:
            form = SearchForm()

    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        'form': SearchForm()
    })


def entry_page(request, title):
    """Show title page data"""
    data = None
    if util.get_entry(title):
        data = markdown2.markdown(util.get_entry(title), extras=["footnotes"])
        return render(request, 'encyclopedia/entry-page.html', {
            'data': data,
            'form': SearchForm(),
            'entry_title': title
        })
    else:
        return render(request, 'encyclopedia/entry-page.html', {
            'data': data,
            'form': SearchForm(),
            'entry_title': title
        })


def search(request, title):
    """Search matching title"""
    _, filenames = default_storage.listdir("entries")
    entries = list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md") and title in filename.lower()))
                
    if entries:
        return render(request, 'encyclopedia/search.html', {
            'entries': entries,
            'form': SearchForm(),
            'title': title
        })
    else:
        return render(request, 'encyclopedia/entry-page.html', {
            'data': None,
            'form': SearchForm(),
            'entry_title': title
        })


def new_page(request):
    """Create new page"""
    if request.method == 'POST':
        form = NewPage(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            if util.get_entry(title):
                return render(request, 'encyclopedia/error.html', {
                    'form': SearchForm()
                })
            else:
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse('wiki:entry_page', args=(title,)))
        else:
            form = NewPage()

    return render(request, 'encyclopedia/new-page.html', {
        'form': SearchForm(),
        'new_page': NewPage(),
    })

def edit(request, title):
    """Edit page"""
    default_data = {'content': util.get_entry(title)}

    if request.method == 'POST':
        form = EditPage(request.POST)
        if form.is_valid():
            entry_title = title
            content = form.cleaned_data['content']
            util.save_entry(entry_title, content)
            return HttpResponseRedirect(reverse('wiki:entry_page', args=(title,)))
        else:
            form = EditPage(default_data)

    return render(request, 'encyclopedia/edit.html', {
        'form': SearchForm(),
        'edit_form': EditPage(default_data),
        'entry_title': title
    })


def random_page(request):
    """Redirect to random entries page"""
    entries = util.list_entries()
    random_title = random.choice(entries)
    return HttpResponseRedirect(reverse('wiki:entry_page', args=(random_title,)))
