from typing import Any, Mapping
from django.forms.renderers import BaseRenderer
from django.forms.utils import ErrorList
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django import forms
from random import randrange
from markdown2 import markdown

from . import util

class SearchPage(forms.Form):
    search = forms.CharField()

class NewPage(forms.Form):
    title = forms.CharField(label="Enter a title")
    content = forms.CharField(widget=forms.Textarea, label="Enter content")

class EditPage(forms.Form):
    content = forms.CharField(widget=forms.Textarea)
        

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(), "form": SearchPage(), "heading": "All Pages"
    })

# Visiting a random page
def random(request):
    if request.method == "GET":
        pages = util.list_entries()
        length = len(pages)
        if length == 0:
            return render(request, "encyclopedia/error.html", {
                "error": "No pages exist" 
            })
        index = randrange(0, length)
        page = pages[index]
        if ".md" in page:
            return render(request, "encyclopedia/error.html", {
                "error": "Not appropriate url" 
            })
        return HttpResponseRedirect(reverse('wiki:wiki') + page)




# Creating new wiki page
def new(request):
    if request.method == "POST":
        data = NewPage(request.POST)

        if data.is_valid():
            title = data.cleaned_data["title"]
            content = data.cleaned_data["content"]
            if util.get_entry(title) != None:
                return render(request, "encyclopedia/error.html", {
                    "error": "Page already exists" 
                })
            util.save_entry(title=title, content=content)
            return HttpResponseRedirect(reverse('wiki:wiki') + title)

        # If search invalid: let user try again
        else:
            return render(request, "encyclopedia/new.html", {
                "form": SearchPage(),"new_page_form": data, "heading": "Create new page"
            })

    # Handle GET
    else:
        return render(request, "encyclopedia/new.html", {
            "form": SearchPage() ,"new_page_form": NewPage(), "heading": "Create new page"
        })

def search(request): 
    # Search for page
    if request.method == "POST":
        search = SearchPage(request.POST)

        # If valid input
        if search.is_valid():
            title = search.cleaned_data["search"]
            content = util.get_entry(title)

            # If found: visit page
            if content != None:
                content = markdown(content)
                return render(request, "encyclopedia/page.html", {
                    "title": title, "form": SearchPage(), "content": content
                })

            # Else: show page titles with have query as substring 
            else: 
                pages = util.list_entries()
                results = []
                for page in pages:
                    if title in page:
                        results.append(page)
                return render(request, "encyclopedia/index.html", {
                    "entries": results, "form": search, "heading": "Page not Found", "message": "Similar Pages" 
                })
            
        # If search invalid: let user try again
        else:
            return render(request, "encyclopedia/index.html", {
                "entries": util.list_entries(), "form": search, "heading": "All Pages", "message": "" 
            })

    # If GET
    else:
        return
    
    


# Only for using wiki/ url
def wiki(request):
    pass 


# Edits a page
def edit(request, title):
    if request.method == "POST":
        form = EditPage(request.POST)
        print(form)
        if form.is_valid():
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse('wiki:wiki') + title)

        # If search invalid: let user try again
        else:
            return render(request, "encyclopedia/edit.html", {
                "title": title, "form": SearchPage(), "textarea_form": form
            })
    
    # Handle GET 
    else:
        data = util.get_entry(title)

        # If entry not found: error
        if data == None:
            return render(request, "encyclopedia/error.html", {
                    "error": "Page not found" 
            })
        
        # Render edit.html
        return render(request, "encyclopedia/edit.html", {
            "title": title, "form": SearchPage(), "textarea_form": EditPage(initial={"content": data})
        })


def page(request, title):

    # render page of title
    data = util.get_entry(title)

    # If entry not found: error
    if data == None:
        return render(request, "encyclopedia/error.html", {
                "error": "Page not found" 
        })
    data = markdown(data)
    
    # set <title> to the var title 
    return render(request, "encyclopedia/page.html", {
        "title": title, "form": SearchPage(), "content": data
    })
    

        

