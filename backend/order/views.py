from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Order
from .serializers import OrderSerializer
from rest_framework.response import Response
from django.db.models import Q


class OrderListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        queryset = Order.objects.filter(Q(buyer=user_id) | Q(seller=user_id))
        return queryset

    def perform_create(self, serializer):
        serializer.save(buyer=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class OrderRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        order = serializer.instance
        if order.status == Order.COMPLETED_STATE:
            order.listing.is_sold = True
            order.listing.save()
        serializer.save()
