from django.shortcuts import render, redirect
import bcrypt
from .models import *
from .forms import *

# Create your views here.


def index(request):
    return render(request, "index.html")




#customer
# -artwork info
# -write review
# -artist bio

def artwork_info(request ,artwork_id):
    if 'uid' in request.session:
        this_user = Account.objects.get( id = request.session['uid'])
        if this_user.is_customer:
            this_user=Customer.objects.get(account_id =request.session['uid'])# if we want to access customer OR artist model we use account_id =
        else:
            this_user = Artist.objects.get(account_id = request.session['uid'])
    else:
        return redirect('/') # this_customer=null #if login>true,use "this_cus"else:redirect to login if need

    context = {
        "this_user" : this_user,
        "reviews" : Artwork.objects.get(id=artwork_id).reviews.all(),
        "this_artwork" : Artwork.objects.get(id=artwork_id),
    }
    return render(request ,'view_art.html',context)

# check quantity in html ,if not should be here
def buy_artwork(request,artwork_id):
    if request.session['login'] == True :
        this_customer=Customer.objects.get(id=request.session['uid'])
        this_artwork=Artwork.objects.get(id=artwork_id)
        if this_artwork.quantity >= request.POST['quantity']:
            context = {
                'this_customer' : this_customer,
                'this_artwork' : this_artwork
            }
            return render(request, "check_out.html",context)
        else: #soldout 
            return redirect(f'/artwork_info/{artwork_id}')
    else:
        return redirect('/login_reg') #missing complete purchase
    


def check_out(request,artwork_id,customer_id):
    #     this_artwork.quantity=this_artwork.quantity-request.POST['quantity']#will moved into "checkout"
    #     this_customer.purchases.add(this_artwork)
    #     return render(request, "completed_purchases.html")#will replaced with ckeckout page
    # else:
    #     return redirect(f'/artwork_info/{artwork_id}')
    return


# submit btn for review valid for logged-in +iscustomer+artwork in purchases
# could add rating with review
def add_review(request,artwork_id):
    this_customer=Customer.objects.get(id=request.session['uid'])
    this_artwork=Artwork.objects.get(id=artwork_id)
    the_review_txt=request.POST['review']
    this_review=Review.objects.create(review_txt=the_review_txt,artwork=this_artwork,customer=this_customer)
    this_artwork.reviews.add(this_review)
    return redirect(f'/artwork_info/{artwork_id}')

def show_artist_profile(request,artist_id):
    if 'uid' in request.session:
        this_user = Account.objects.get( id = request.session['uid'])
        if this_user.is_customer:
            this_user=Customer.objects.get(account_id =request.session['uid'])# if we want to access customer OR artist model we use account_id =
        else:
            this_user = Artist.objects.get(account_id = request.session['uid'])
    else:
        return redirect('/') 

    context = {
        "this_artist": Artist.objects.get(account_id=artist_id),
        "this_user": this_user,
        
    }
    return render(request, "artist_profile.html", context)
    # #####





def login_reg(request):
    return render(request, "login_page.html")


def process_reg(request):

    fname = request.POST['first_name']
    lname = request.POST['last_name']
    email = request.POST['email']
    new_pass = bcrypt.hashpw(
        request.POST['password'].encode(), bcrypt.gensalt()).decode()
    if(request.POST['account_type'] == 'customer'):
        new_user = Account.objects.create(
            first_name=fname, last_name=lname, email=email, password=new_pass, is_customer=True)
        this_user = Customer.objects.create(account=new_user)

    else:
        new_user = Account.objects.create(
            first_name=fname, last_name=lname, email=email, password=new_pass, is_artist=True)
        this_user = Artist.objects.create(account=new_user)
    request.session['uid'] = this_user.account_id
    request.session['login']=True
    return redirect('/sucsess')


def sucsess(request):
    this_account = Account.objects.get(id=request.session['uid'])
    if this_account.is_artist:
        this_account = Artist.objects.get(account_id=request.session['uid'])
        context = {
            "this_user": Artist.objects.get(account_id=request.session['uid']),
        }
        return render(request, "artist_dashboard_1.html", context)
    else:  
        this_account = Customer.objects.get(account_id=request.session['uid'])
        context = {
            "this_user": this_account,
        }
        return render(request, "index.html", context)# should be gallery


def login(request):

    logged_user = Account.objects.get(email=request.POST['email'])
    if bcrypt.checkpw(request.POST['pass'].encode(), logged_user.password.encode()):
        request.session['uid'] = logged_user.id
        request.session['login']=True #NEW
        return redirect('/sucsess')


def add_item(request):
    context = {
        "this_user": Artist.objects.get(account_id=request.session['uid']),
    }
    return render(request, "add_item_1.html", context)


def create_art(request):
    art_titel = request.POST['title']
    art_desc = request.POST['Description']
    art_q = request.POST['quantity']
    art_size = request.POST['size']
    art_price = request.POST['price']
    this_artist = Artist.objects.get(account_id=request.session['uid'])
    this_art = Artwork.objects.create(title=art_titel, description=art_desc, quantity=art_q,
                                      size=art_size, price=art_price, artist=this_artist)
    return redirect(f'/add_item_img/{this_art.id}')


def add_item_img(request, id):
    this_artwork = Artwork.objects.get(id=id)
    form = ArtworkImageForm()
    context = {
        'this_artwork': this_artwork,
        'this_user': Artist.objects.get(account_id=request.session['uid']),
        'form': form,
    }
    return render(request, "add_item_img.html", context)


def create_item_img(request, id):
    this_artwork = Artwork.objects.get(id=id)
    this_artist = Artist.objects.get(account_id=request.session['uid'])
    form = ArtworkImageForm(request.POST, request.FILES)
    if form.is_valid():
        this_image = form.save(commit=False)
        this_image.name = f'{this_artwork.title} image'
        this_image.alt_text = f'this image added by {this_artist.account.first_name} for {this_artwork.title}'
        this_image.artwork = this_artwork
        this_image.save()
        form.save()
        print(this_image.image.url)
    return redirect('/sucsess')

def logout(request):
    request.session.flush()
    return redirect("/")
