from django.db import models
from account.models import User, Address
from core.models import Extensions
from listing.models import Listing
from django.utils import timezone

from django.db import models
from django.utils import timezone

class Order(models.Model):  # I removed "Extensions" because its definition wasn't provided
    PENDING_STATE = "Pending"
    COMPLETED_STATE = "Completed"
    ACCEPTED_STATE = "Accepted"
    REJECTED_STATE = "Rejected"

    ORDER_CHOICES = (
        (PENDING_STATE, "Pending"),
        (COMPLETED_STATE, "Completed"),
        (ACCEPTED_STATE, "Accepted"),
        (REJECTED_STATE, "Rejected"),
    )

    order_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    buyer = models.ForeignKey(User, related_name="orders_placed", on_delete=models.CASCADE, null=True, blank=True)
    seller = models.ForeignKey(User, related_name="orders_received", on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=50, choices=ORDER_CHOICES, default=PENDING_STATE)
    listing = models.ForeignKey(Listing, related_name="listing_order", on_delete=models.CASCADE, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    address = models.ForeignKey(Address, related_name="order_address", on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super(Order, self).save(*args, **kwargs)
        if not self.order_number:
            self.order_number = f"ORD{self.id}"
            super(Order, self).save(*args, **kwargs)

    @staticmethod
    def create_order(buyer, seller, listing, address, is_paid=False):
        order = Order()
        order.buyer = buyer
        order.seller = seller
        order.listing = listing
        order.address = address
        order.is_paid = is_paid
        order.save()
        return order

    def __str__(self):
        return str(self.order_number)



# Function to mark listing as sold when an order is accepted
def mark_listing_as_sold(sender, instance, **kwargs):
    if instance.status == Order.ACCEPTED_STATE:
        instance.listing.is_sold = True
        instance.listing.save()

# Connect the signal
from django.db.models.signals import post_save
post_save.connect(mark_listing_as_sold, sender=Order)
