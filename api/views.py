from django.shortcuts import render
from django.db.models import Sum
from datetime import datetime
from .models import *
import json
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth import login, authenticate,logout
from .models import Bill



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
        billers = Biller.objects.all()
        return render(request,"home.html",{"items":items, "billers":billers})

def report_view(request):
    total_bill_sum = 0
    total_inventory_sum = 0
    bills = []
    inventory_sold = []
    billers = Biller.objects.all()

    if request.method == 'POST':
        date_input = request.POST.get('date_input')
        payment_mode = request.POST.get('payment_mode', '')
        biller_id = request.POST.get('biller', '')

        date_obj = datetime.strptime(date_input, "%Y-%m-%d")

        # Build the filter query
        bill_query = Bill.objects.filter(DateTime__date=date_obj)
        
        # Apply payment mode filter if provided
        if payment_mode:
            bill_query = bill_query.filter(mode_of_payment=payment_mode)
        
        # Apply biller filter if provided
        if biller_id:
            bill_query = bill_query.filter(biller_id=biller_id)

        bills = bill_query.annotate(total_sum=Sum('total'))
        total_bill_sum = bills.aggregate(Sum('total'))['total__sum'] or 0

        # Calculate inventory sold from filtered bills instead of using InventorySold directly
        # This ensures inventory sold matches the filtered bills
        inventory_dict = {}
        for bill in bills:
            # Handle both list format and dict with 'items' key format
            items_list = []
            if isinstance(bill.items, list):
                items_list = bill.items
            elif isinstance(bill.items, dict) and 'items' in bill.items:
                items_list = bill.items['items']
            
            for item in items_list:
                if isinstance(item, dict):
                    item_name = item.get('item_name', '')
                    quantity = item.get('quantity', 0)
                    price = item.get('item_price', 0)
                    
                    if item_name:
                        if item_name in inventory_dict:
                            inventory_dict[item_name]['quantity'] += quantity
                            inventory_dict[item_name]['total'] += price * quantity
                        else:
                            inventory_dict[item_name] = {
                                'name': item_name,
                                'quantity': quantity,
                                'price': price,
                                'total': price * quantity
                            }
        
        # Convert dict to list for template
        inventory_sold = list(inventory_dict.values())
        total_inventory_sum = sum(item['total'] for item in inventory_sold)

        for bill in bills:
            bill.DateTime = bill.DateTime.strftime("%Y-%m-%d")

    context = {
        'total_bill_sum': total_bill_sum,
        'total_inventory_sum': total_inventory_sum,
        'bills': bills,
        'inventory_sold': inventory_sold,
        'billers': billers,
        'selected_payment_mode': request.POST.get('payment_mode', '') if request.method == 'POST' else '',
        'selected_biller': request.POST.get('biller', '') if request.method == 'POST' else '',
        'selected_date': request.POST.get('date_input', '') if request.method == 'POST' else '',
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
                discount = body["discount"]
                payment_mode = body.get("payment_mode", "cash")  # Default to cash if not provided
                biller_id = body.get("biller_id", None)
                
                # Get or create default "admin" biller
                default_biller, created = Biller.objects.get_or_create(name="admin")
                
                # Set biller - use provided biller_id or default to "admin"
                biller = None
                if biller_id:
                    try:
                        biller = Biller.objects.get(id=biller_id)
                    except Biller.DoesNotExist:
                        biller = default_biller
                else:
                    biller = default_biller
                
                bill=Bill.objects.create(
                    customer_name=customer_name, 
                    customer_phone=customer_phone, 
                    items=items, 
                    total=total, 
                    discount=discount,
                    mode_of_payment=payment_mode,
                    biller=biller
                )
                bill.save()
                bill.calculate_total()
                return HttpResponse("Order Placed")
            except Exception as e:
                print(f"error: {e}")
                return HttpResponse("Error")
        else:
            return HttpResponse("Invalid Request")
    else:
        return redirect("/login")


def previous_bills(request):
    bills = []
    search_performed = False

    if request.method == 'POST':
        search_performed = True
        date_input = request.POST.get('date_input')
        customer_name = request.POST.get('customer_name')
        bill_id = request.POST.get('bill_id')

        # Build the query based on provided filters
        query = {}
        if date_input:
            date_obj = datetime.strptime(date_input, "%Y-%m-%d")
            query['DateTime__date'] = date_obj
        if customer_name:
            query['customer_name__icontains'] = customer_name
        if bill_id:
            # Assuming billId is the field name in your Bill model
            # If it's 'id' instead of 'billId', change this accordingly
            query['billId'] = bill_id

        # Get bills matching the query
        bills = Bill.objects.filter(**query).order_by('-DateTime')

    context = {
        'bills': bills,
        'search_performed': search_performed
    }

    return render(request, 'previous_bills.html', context)

def previous_bills_combined(request):
    bills = []
    search_performed = False

    if request.method == 'POST':
        search_performed = True
        date_input = request.POST.get('date_input')
        customer_name = request.POST.get('customer_name')
        bill_id = request.POST.get('bill_id')

        # Build the query based on provided filters
        query = {}
        if date_input:
            date_obj = datetime.strptime(date_input, "%Y-%m-%d")
            query['DateTime__date'] = date_obj
        if customer_name:
            query['customer_name__icontains'] = customer_name
        if bill_id:
            query['billId'] = bill_id

        # Get bills matching the query
        bills = Bill.objects.filter(**query).order_by('-DateTime')
    else:
        # Fetch the last bill if no search is performed
        last_bill = Bill.objects.order_by('-DateTime').first()
        bills = [last_bill] if last_bill else []

    context = {
        'bills': bills,
        'search_performed': search_performed
    }

    return render(request, 'previous_bills.html', context)