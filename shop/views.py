from django.shortcuts import render
from django.http import HttpResponse
from .models import product,Contact,Order,OrderUpdate
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
import requests
import razorpay
client = razorpay.Client(auth=("rzp_test_ZCYa51jvvnD7cK", "eQuTjlBDoSDBbmVyoMTBNaAL"))



# Create your views here.
def index(request):


    # products=product.objects.all()
    # n=len(products)
    # nslides= n//4+ceil(n/4-n//4)
    # params={ 'product':products, 'no-of-slides':nslides , 'range': range(1,nslides)}
    # allprods=[[products,nslides,range(1,nslides)],
    #           [products,nslides,range(1,nslides)]]
    allprods=[]
    catprods=product.objects.values('category','id')
    cats={item['category'] for item in catprods}
    for cat in cats:
        prod=product.objects.filter(category=cat)
        n=len(prod)
        nslides= n//4+ceil(n/4-n//4)
        allprods.append([prod,nslides,range(1,nslides)])

    params={'allprods':allprods}

    return render(request,'shop/index.html',params)

def searchMatch(query, item):
    if query in item.product_name.lower() or query in item.product_desc.lower() or query in item.category.lower() or query in item.subcategory.lower():
        return True
    else:
        return False

def search(request):
    query=request.GET.get('search')
    allprods = []
    catprods = product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = product.objects.filter(category=cat)
        prod=[item for item in prodtemp if searchMatch(query,item)]
        n = len(prod)
        nslides = n // 4 + ceil(n / 4 - n // 4)
        if n!=0:
            allprods.append([prod, nslides, range(1, nslides)])

    params = {'allprods': allprods, 'msg':''}
    if len(allprods)==0 or len(query)<3:
        params={'msg': 'Please enter relavant search query for results'}
    return render(request, 'shop/search.html', params)

def about(request):
    return render(request,'shop/about.html')

def contact(request):
    if request.method=="POST":
        thank=True
        name=request.POST.get('name','')
        email=request.POST.get('email','')
        phone=request.POST.get('phone','')
        desc=request.POST.get('desc','')
        contact=Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        return render(request, 'shop/contact.html',{'thank':thank})
    return render(request, 'shop/contact.html')

def tracker(request):
    if request.method=="POST":
        orderId=request.POST.get('orderId','')
        email=request.POST.get('email','')

        try:
            order=Order.objects.filter(order_id=orderId, email=email)

            if len(order)>0:
                update=OrderUpdate.objects.filter(order_id=orderId)
                updates=[]
                for item in update:
                    updates.append({'text':item.update_desc, 'time': item.timestamp})
                response=json.dumps([updates,order[0].items_json], default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{}')
        except Exception as e:
            return HttpResponse('{}')

    return render(request, 'shop/tracker.html')

def productView(request,myid):
    prod=product.objects.filter(id=myid)
    return render(request, 'shop/prodview.html',{'product':prod[0]})

# @login_required
def checkout(request):
    if request.method=="POST":
        itemsJson=request.POST.get('itemsJson','')
        amount=request.POST.get('amount','')
        name=request.POST.get('name','')
        email=request.POST.get('email','')
        address=request.POST.get('address1','') + " " + request.POST.get('address2','')
        city=request.POST.get('city','')
        state=request.POST.get('state','')
        zip_code=request.POST.get('zip_code','')
        phone = request.POST.get('phone', '')

        if amount=='0':
            return render(request, 'shop/checkout.html')

        thank = "1"
        order=Order(items_json=itemsJson, name=name, email=email,address=address, city=city, state=state, zip_code=zip_code , phone=phone,amount=amount)
        order.save()

        update=OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()

        id1 =order.order_id

        # request razorpay to transfer amount to your account
        order_currency = 'INR'
        callback_url="http://127.0.0.1:8000/shop/handlerequest/"
        notes = {'Shipping address': address}
        order_amount = int(amount) * 100
        razorpay_order=client.order.create(dict(amount=order_amount, currency=order_currency, notes=notes, receipt=str(id1), payment_capture='0'))
        order.razorpay_order_id= razorpay_order['id']
        order.save()

        return render(request, 'shop/checkout.html',{'thank':thank, 'id':id1, 'amount':order_amount,
                'order':order, 'order_id':razorpay_order['id'], 'razorpay_merchant_id': "rzp_test_ZCYa51jvvnD7cK", 'callback_url':callback_url})

    return render(request, 'shop/checkout.html')

#
#
@csrf_exempt
def handlerequest(request):
    # paytm send you post request here, exempt from csrf token
    if request.method=='POST':
        try:
            payment_id = request.POST.get('razorpay_payment_id','')
            order_id = request.POST.get('razorpay_order_id','')
            signature = request.POST.get('razorpay_signature','')

            params_dict = {
                'razorpay_order_id' : order_id,
                'razorpay_payment_id' : payment_id,
                'razorpay_signature' : signature
            }
            try:
                order_db = Order.objects.get(razorpay_order_id = order_id)
            except:
                return HttpResponse("Error : 505 Not Found ")
            order_db.razorpay_payment_id = payment_id
            order_db.razorpay_signature = signature
            order_db.save()

            result = client.utility.verify_payment_signature(params_dict)
            if result==None:
                amount = order_db.amount*100
                try:
                    client.payment.capture(payment_id,amount,{"currency": "INR"})
                    return render(request, "shop/success.html",{'id':order_db.order_id})
                except:
                    return render(request, "shop/failure.html")
            else:
                return render(request, "shop/failure.html")
        except:
            return HttpResponse("Error : 505 Not Found")