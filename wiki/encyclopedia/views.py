from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.core.files import File
from django.urls import reverse
import markdown2
import random

from . import util

class NewEntryForm(forms.Form):
    title = forms.CharField(label='', widget=forms.TextInput(attrs={
        'class' : 'col-sm-6', 
        'placeholder' : 'Title', 
        'autocomplete' : 'off', 
        'style' : 'margin: 5px; padding: 5px; position: relative; left: -15px;'
    }))
    content = forms.CharField(label='', widget=forms.Textarea(attrs={
        'class' : 'col-sm-11 h-50', 
        'placeholder' : 'Entry', 
        'autocomplete' : 'off', 
        'style' : 'margin: 5px; padding: 5px; position: relative; left: -15px;'
    }))


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, entry):
    if util.get_entry(entry) != None:
        return util.render_entry(request, entry)
    else:
        return render(request, "encyclopedia/error.html", {
            "title": entry,
            "exists": False
        })

def random_entry(request):
    entries = util.list_entries()
    random_entry = random.choice(entries)
    return redirect(f'wiki/{random_entry}')

def new_page(request):
    if request.method == "GET":
        return render(request, "encyclopedia/new.html", {
            "form": NewEntryForm()
        })
    elif request.method == "POST":
        form = NewEntryForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            try:
                f = open(f"entries/{title}.md", "x")
            except FileExistsError:
                return render(request, "encyclopedia/error.html", {
                    "title": title,
                    "exists": True
                })
            f.write(form.cleaned_data["content"])
            f.close()
            return HttpResponseRedirect(f"wiki/{title}")
        else:
            return render(request, "encyclopedia/new.html", {
            "form": NewEntryForm()
            })

def edit(request, entry):
    if request.method == "GET":
        return render(request, "encyclopedia/edit.html", {
            "entry": util.get_entry(entry), 
            "title": entry
        })
    elif request.method == "POST":
        new_entry = request.POST.get('entry')
        f = open(f"entries/{entry}.md", "w")
        f.write(new_entry)
        f.close()
        return HttpResponseRedirect(f"/wiki/{entry}")

def search(request):
    value = request.GET.get('q', '')
    if (util.get_entry(value) is not None):
        return HttpResponseRedirect(reverse("entry", kwargs={'entry' : value}))
    else:
        subStringEntries = []
        for entry in util.list_entries():
            if value.upper() in entry.upper():
                subStringEntries.append(entry)
        return render(request, "encyclopedia/index.html", {
            "entries" : subStringEntries,
            "search" : True,
            "value" : value
        })