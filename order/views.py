from django.db.models import Q
from rest_framework import generics, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from listing.models import Listing
from .models import Order
from .serializers import ReadOrderSerializer, WriteOrderSerializer
from .permissions import IsOrderByBuyerSellerOrAdmin, IsOrderPending


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    permission_classes = [IsOrderByBuyerSellerOrAdmin]

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return WriteOrderSerializer
        else:
            return ReadOrderSerializer

    def get_queryset(self):
        res = super().get_queryset()
        user = self.request.user
        return res.filter(buyer=user)

    def get_permissions(self):
        if self.action in ("update", "partial_update"):
            self.permission_classes += [IsOrderPending]

        return super().get_permissions()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sales_orders(request):
    user = request.user

    try:
        sales_orders = Order.objects.filter(listing__seller=user)
        serializer = ReadOrderSerializer(sales_orders, many=True)
        return Response(serializer.data)
    except Exception as e:
        raise Response({'error': str(e)}, status=500)
