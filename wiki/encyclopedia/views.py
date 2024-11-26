from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def search(request):
    
    # Use id_token for post form 
    """https://cs50.harvard.edu/web/2020/notes/3/#forms:~:text=the%20bank%E2%80%99s%20website!-,To,-solve%20this%20problem"""
    # Search for page
    # If found: visit page
    # Else: show page titles with have query as substring 
    pass


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
    

        

