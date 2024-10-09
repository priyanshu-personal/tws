from django.db import models
from django.utils.timezone import now  # For DateTime field
from django.db.models import JSONField  # Import JSONField for structured data storage
from django.utils import timezone
import pytz

def currentDate():
    indian_timezone = pytz.timezone("Asia/Kolkata")
    now_in_india = timezone.now().astimezone(indian_timezone)
    return now_in_india.strftime("%Y-%m-%d")
def currentTime():
    indian_timezone = pytz.timezone("Asia/Kolkata")
    now_in_india = timezone.now().astimezone(indian_timezone)
    return now_in_india.strftime("%H:%M:%S")

def get_indian_time():
    indian_timezone = pytz.timezone("Asia/Kolkata")
    return timezone.now().astimezone(indian_timezone)

class Category(models.Model):
    name = models.CharField(null=False, max_length=100)
    def __str__(self):
        return self.name


class Item(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(null=False, max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)

    def __str__(self):
        return f'{self.category} {self.name}'

class InventorySold(models.Model):
    name = models.CharField(null=False, max_length=100)
    quantity = models.IntegerField(null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    date = models.CharField(null=False, max_length=100)

    def __str__(self):
        return f'{self.name}'

class Bill(models.Model):
    billId = models.AutoField(primary_key=True)  # Auto-increment primary key
    DateTime = models.DateTimeField(default=get_indian_time) # Auto-create DateTime when bill is created
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Decimal for precise totals
    customer_name = models.CharField(max_length=50)
    customer_phone = models.CharField(max_length=50)
    date = models.CharField(max_length=50, default=currentDate())
    time = models.CharField(max_length=50, default=currentTime())

    # Store items and their details in JSONField
    items = JSONField(default=dict)

    def __str__(self):
        return f'{self.customer_name}'

    # Method to add items to the bill
    def add_item(self, item, quantity):
        # Check if the item is already in the items field
        if 'items' not in self.items:
            self.items['items'] = []

        self.items['items'].append({
            'item_id': item.id,
            'item_name': item.name,
            'item_price': float(item.price),
            'quantity': quantity
        })
        self.save()

    def calculate_total(self):
        print(get_indian_time(),"priyans")
        for bill_item in self.items:
            try:
                soldInventory = InventorySold.objects.filter(name=bill_item['item_name'], date=currentDate()).first()
                if soldInventory:
                    soldInventory.quantity += bill_item['quantity']
                    soldInventory.total += bill_item['item_price'] * bill_item['quantity']
                    soldInventory.save()
                else:
                    soldInventory = InventorySold(name=bill_item['item_name'], quantity=bill_item['quantity'], price=bill_item['item_price'], total=bill_item['item_price'] * bill_item['quantity'], date=currentDate())
                    soldInventory.save()
            except Exception as e:
                print(e)
        return True
