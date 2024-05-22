from django.db import models
from account.models import User, Address
from core.models import Extensions
from listing.models import Listing
from django.utils import timezone

from django.db import models


class Order(Extensions):
    PENDING_STATE = "Pending"
    COMPLETED_STATE = "Completed"
    # ACCEPTED_STATE = "Accepted"
    # REJECTED_STATE = "Rejected"

    ORDER_CHOICES = (
        (PENDING_STATE, "Pending"),
        (COMPLETED_STATE, "Completed"),
        # (ACCEPTED_STATE, "Accepted"),
        # (REJECTED_STATE, "Rejected"),
    )

    # order_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    buyer = models.ForeignKey(User, related_name="orders_placed", on_delete=models.CASCADE, null=True, blank=True)
    listing = models.ForeignKey(Listing, related_name="listing_order", on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=50, choices=ORDER_CHOICES, default=PENDING_STATE)
    address = models.ForeignKey(Address, related_name="order_address", on_delete=models.CASCADE, null=True, blank=True)
    is_delivered = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return f"Order ID: {self.id} Buyer: {self.buyer.get_username}"
