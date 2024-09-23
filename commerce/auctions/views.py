from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import User, Bid, Listing, Comment, Watchlist, Closedbid, Alllisting
from datetime import datetime

# Views
def index(request):
    items = Listing.objects.all()
    watched_items = Watchlist.objects.filter(user=request.user.username)
    watchcount = len(watched_items)
    return render(request, "auctions/index.html",{
        "items": items,
        "watchcount": watchcount
    })

def categories(request):
    items = Listing.objects.raw("SELECT * FROM auctions_listing GROUP BY category")
    watched_items = Watchlist.objects.filter(user=request.user.username)
    watchcount = len(watched_items)
    return render(request,"auctions/categpage.html",{
        "items": items,
        "watchcount": watchcount
    })

def category(request, category):
    catitems = Listing.objects.filter(category=category)
    watched_items = Watchlist.objects.filter(user=request.user.username)
    watchcount = len(watched_items)
    return render(request,"auctions/category.html",{
        "items": catitems,
        "cat": category,
        "watchcount": watchcount
    })

def create(request):
    watched_items = Watchlist.objects.filter(user=request.user.username)
    watchcount = len(watched_items)
    return render(request,"auctions/create.html",{
        "watchcount": watchcount
    })

def submit(request):
    if request.method == "POST":
        listtable = Listing()
        now = datetime.now()
        dt = now.strftime(" %d %B %Y %X ")
        listtable.owner = request.user.username
        listtable.title = request.POST.get('title')
        listtable.description = request.POST.get('description')
        listtable.price = request.POST.get('price')
        listtable.category = request.POST.get('category')
        if request.POST.get('link'):
            listtable.link = request.POST.get('link')
        else :
            listtable.link = "https://wallpaperaccess.com/full/1605486.jpg"
        listtable.time = dt
        listtable.save()
        all = Alllisting()
        items = Listing.objects.all()
        for item in items:
            all.listingid = item.id
            all.title = item.title
            all.description = item.description
            all.link = item.link
            all.save()

        return redirect('index')
    else:
        return redirect('index')


def listingpage(request, id):
    item = Listing.objects.get(id=id)
    comments = Comment.objects.filter(listingid=id)
    if request.user.username:
        try:
            Watchlist.objects.get(user=request.user.username,listingid=id)
            added = True
        except:
            added = False
        listing = Listing.objects.get(id=id)
        if listing.owner == request.user.username :
            owner = True
        else:
            owner = False
    else:
        added = False
        owner = False
    watched_listings = Watchlist.objects.filter(user=request.user.username)
    watchcount = len(watched_listings)
    return render(request,"auctions/listingpage.html",{
        "item": item,
        "error": request.COOKIES.get('error'),
        "errorgreen": request.COOKIES.get('errorgreen'),
        "comments": comments,
        "added": added,
        "owner": owner,
        "watchcount": watchcount
    })

def bidsubmit(request, listingid):
    current_bid = Listing.objects.get(id=listingid)
    current_bid = current_bid.price
    if request.method == "POST":
        user_bid = int(request.POST.get("bid"))
        if user_bid > current_bid:
            listing_items = Listing.objects.get(id=listingid)
            listing_items.price = user_bid
            listing_items.save()
            if Bid.objects.filter(id=listingid):
                bidrow = Bid.objects.filter(id=listingid)
                bidrow.delete()
            bidtable = Bid()
            bidtable.user=request.user.username
            bidtable.title = listing_items.title
            bidtable.listingid = listingid
            bidtable.bid = user_bid
            bidtable.save()

            response = redirect('listingpage',id=listingid)
            response.set_cookie('errorgreen','Bid successful!',max_age=3)
            return response
        else :
            response = redirect('listingpage',id=listingid)
            response.set_cookie('error','Bid should be greater than current price',max_age=3)
            return response
    else:
        return redirect('index')


def cmntsubmit(request, listingid):
    if request.method == "POST":
        now = datetime.now()
        date = now.strftime(" %d %B %Y %X ")
        comment = Comment()
        comment.comment = request.POST.get('comment')
        comment.user = request.user.username
        comment.time = date
        comment.listingid = listingid
        comment.save()
        return redirect('listingpage',id=listingid)
    else:
        return redirect('index')

def addwatchlist(request, listingid):
    if request.user.username:
        watched_listings = Watchlist()
        watched_listings.user = request.user.username
        watched_listings.listingid = listingid
        watched_listings.save()
        return redirect('listingpage',id=listingid)
    else:
        return redirect('index')


def removewatchlist(request, listingid):
    if request.user.username:
        watched_listings = Watchlist.objects.get(user=request.user.username,listingid=listingid)
        watched_listings.delete()
        return redirect('listingpage',id=listingid)
    else:
        return redirect('index')

def watchlistpage(request, username):
    if request.user.username:
        try:
            watched_listings = Watchlist.objects.filter(user=username)
            items = []
            for item in watched_listings:
                items.append(Listing.objects.filter(id=item.listingid))
            
            watched_listings = Watchlist.objects.filter(user=request.user.username)
            watchcount = len(watched_listings)
            return render(request,"auctions/watchlistpage.html",{
                "items": items,
                "watchcount": watchcount
            })
        except:
            watched_listings = Watchlist.objects.filter(user=request.user.username)
            watchcount = len(watched_listings)
            return render(request,"auctions/watchlistpage.html",{
                "items": None,
                "watchcount": watchcount
            })
    else:
        return redirect('index')

def closebid(request, listingid):
    if request.user.username:
        try:
            listingrow = Listing.objects.get(id=listingid)
        except:
            return redirect('index')
        cb = Closedbid()
        title = listingrow.title
        cb.owner = listingrow.owner
        cb.listingid = listingid
        try:
            bidrow = Bid.objects.get(listingid=listingid,bid=listingrow.price)
            cb.winner = bidrow.user
            cb.winprice = bidrow.bid
            cb.save()
            bidrow.delete()
        except:
            cb.winner = listingrow.owner
            cb.winprice = listingrow.price
            cb.save()
        if Watchlist.objects.filter(listingid=listingid):
            watchrow = Watchlist.objects.filter(listingid=listingid)
            watchrow.delete()
        c_row = Comment.objects.filter(listingid=listingid)
        c_row.delete()
        b_row = Bid.objects.filter(listingid=listingid)
        b_row.delete()
        try:
            cblist=Closedbid.objects.get(listingid=listingid)
        except:
            cb.owner = listingrow.owner
            cb.winner = listingrow.owner
            cb.listingid = listingid
            cb.winprice = listingrow.price
            cb.save()
            cblist=Closedbid.objects.get(listingid=listingid)
        listingrow.delete()
        watched_listings = Watchlist.objects.filter(user=request.user.username)
        watchcount = len(watched_listings)

        return render(request,"auctions/winningpage.html",{
            "cb": cblist,
            "title": title,
            "watchcount": watchcount
        })   

    else:
        return redirect('index')     

def mywinnings(request):
    if request.user.username:
        items = []
        wonitems = Closedbid.objects.filter(winner=request.user.username)
        for item in wonitems:
            items.append(Alllisting.objects.filter(listingid=item.listingid))
        
        watched_listings = Watchlist.objects.filter(user=request.user.username)
        watchcount = len(watched_listings)
        return render(request,'auctions/mywinnings.html',{
            "items": items,
            "watchcount": watchcount,
            "wonitems": wonitems
        })
    else:
        return redirect('index')


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
