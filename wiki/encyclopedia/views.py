from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django import forms

from . import util

class SearchPage(forms.Form):
    search = forms.CharField()

class NewPage(forms.Form):
    title = forms.CharField(label="Enter a title")
    content = forms.CharField(widget=forms.Textarea, label="Enter content")

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(), "form": SearchPage(), "heading": "All Pages"
    })


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
    pass

def page(request, title):

    # render page of title
    data = util.get_entry(title)

    # If entry not found: error
    if data == None:
        return render(request, "encyclopedia/error.html", {
                "error": "Page not found" 
        })
    
    # set <title> to the var title 
    return render(request, "encyclopedia/page.html", {
        "title": title, "form": SearchPage(), "content": data
    })
    

        

