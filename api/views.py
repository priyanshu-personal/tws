from django.shortcuts import render
from django.db.models import Sum
from datetime import datetime
from .models import *
import json
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth import login, authenticate,logout



def home(request):
    if(request.session.has_key('loged')==False or request.session['loged']==False):
        if request.method=='POST':
            username=request.POST.get('userid')
            password=request.POST.get('password')

            user= authenticate(username=username,password=password)

            if user:
                if user.is_active:
                    login(request,user)
                    request.session['loged'] = True
                    request.session['username'] = username
                    return redirect("/")
                else:
                    return HttpResponse("Your account was inactive.")
            else:
                error1="Invalid login details supplied!"
                return render(request,'login.html',{'error1':error1})
        else:
            return render(request,'login.html')
    else:
        items = Item.objects.all()
        return render(request,"home.html",{"items":items})

def report_view(request):
    total_bill_sum = 0
    total_inventory_sum = 0
    bills = []
    inventory_sold = []

    if request.method == 'POST':
        date_input = request.POST.get('date_input')
        
        date_obj = datetime.strptime(date_input, "%Y-%m-%d")

        
        bills = Bill.objects.filter(DateTime__date=date_obj).annotate(total_sum=Sum('total'))
        total_bill_sum = bills.aggregate(Sum('total'))['total__sum'] or 0

       
        inventory_sold = InventorySold.objects.filter(date=date_input)
        total_inventory_sum = inventory_sold.aggregate(Sum('total'))['total__sum'] or 0

       
        for bill in bills:
            bill.DateTime = bill.DateTime.strftime("%Y-%m-%d")  

    context = {
        'total_bill_sum': total_bill_sum,
        'total_inventory_sum': total_inventory_sum,
        'bills': bills,
        'inventory_sold': inventory_sold,
    }

    return render(request, 'report.html', context)


def user_login(request):
    if(request.session.has_key('loged')==False or request.session['loged']==False):
        if request.method=='POST':
            username=request.POST.get('userid')
            password=request.POST.get('password')

            user= authenticate(username=username,password=password)

            if user:
                if user.is_active:
                    login(request,user)
                    request.session['loged'] = True
                    request.session['username'] = username
                    return redirect("/")
                else:
                    return HttpResponse("Your account was inactive.")
            else:
                error1="Invalid login details supplied!"
                return render(request,'login.html',{'error1':error1})
        else:
            return render(request,'login.html')
    else:
        return redirect("/")


def user_logout(request):
    logout(request)
    request.session['loged'] = False
    request.session['username'] =""
    return redirect('/login')


def bill(request):
    if(request.session.has_key('loged') and request.session['loged']==True):
        if(request.method=="POST"):
            try:
                body = request.body.decode("utf-8")
                body = json.loads(body)
                customer_name = body["customer_name"]
                customer_phone = body["customer_phone"]
                items = body["items"]
                total = body["total"]
                bill=Bill.objects.create(customer_name=customer_name, customer_phone=customer_phone, items=items, total=total)
                bill.save()
                bill.calculate_total()
                return HttpResponse("Order Placed")
            except:
                print("error")
                return HttpResponse("Error")
        else:
            return HttpResponse("Invalid Request")
    else:
        return redirect("/login")