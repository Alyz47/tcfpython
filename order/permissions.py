from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import BasePermission

from .models import Order


class IsOrderPending(BasePermission):
    message = "Updating or deleting closed order is not allowed."

    def has_object_permission(self, request, view, obj):
        if view.action in ("retrieve",):
            return True
        return obj.status == "P"


class IsOrderByBuyerSellerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated is True

    def has_object_permission(self, request, view, obj):
        return obj.buyer == request.user or obj.listing.seller == request.user or request.user.is_staff

