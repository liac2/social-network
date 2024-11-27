from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django import forms

from . import util

class SearchPage(forms.Form):
    search = forms.CharField()

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(), "form": SearchPage(), "heading": "All Pages"
    })


def search(request): 
    # Search for page
    if request.method == "POST":
        search = SearchPage(request.POST)

        if search.is_valid():
            page = search.cleaned_data["search"]
            content = util.get_entry(page)

            # If found: visit page
            if content != None:
                return render(request, "encyclopedia/page.html", {
                    "title": page, "content": content
                })

            # Else: show page titles with have query as substring 
            else: 
                return render(request, "encyclopedia/index.html", {
                    "entries": , "form": SearchPage(), "heading": "Page not Found", "message": "Similar Pages" 
                })
            
        # If search invalid: error
        else:
            return render(request, "encyclopedia/error.html", {
                "entries": , "form": SearchPage(), "heading": "Page not Found", "message": "Similar Pages" 
            })

    else:
        return
    
    


# Only for using wiki/ url
def wiki(request):
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
        "title": title, "content": data
    })
    

        

