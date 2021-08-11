from django.db import models

# Create your models here.
class product(models.Model):
    product_id=models.AutoField
    product_name=models.CharField(max_length=20)
    product_desc=models.CharField(max_length=1000)
    pub_date=models.DateField()
    category=models.CharField(max_length=30,default="")
    subcategory=models.CharField(max_length=30,default="")
    price=models.IntegerField(default=0)
    image=models.ImageField(upload_to="shop/images",default="")

    def __str__(self):
        return self.product_name


class Contact(models.Model):
    product_id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=30)
    email=models.CharField(max_length=30)
    phone=models.CharField(max_length=30)
    desc=models.CharField(max_length=1000)


    def __str__(self):
        return self.name

class Order(models.Model):
    order_id=models.AutoField(primary_key=True)
    items_json=models.CharField(max_length=5000)
    amount=models.IntegerField(default=0)
    name=models.CharField(max_length=20)
    email=models.CharField(max_length=50)
    address=models.CharField(max_length=100)
    city=models.CharField(max_length=20)
    state=models.CharField(max_length=20)
    zip_code=models.CharField(max_length=10)
    phone=models.CharField(max_length=20,default='')
    razorpay_order_id = models.CharField(max_length=500,default='')
    razorpay_payment_id = models.CharField(max_length=500,default='')
    razorpay_signature = models.CharField(max_length=500,default='')

    def __str__(self):
        return self.name+"   ("+str(self.order_id)+")"


class OrderUpdate(models.Model):
    update_id=models.AutoField(primary_key=True)
    order_id = models.IntegerField(default="")
    update_desc= models.CharField(max_length=50)
    timestamp= models.DateField(auto_now_add=True)

    def __str__(self):
        return self.update_desc[0:10]+"..."
