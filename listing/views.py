# from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.db.models import Q


from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.views import APIView

from .models import (Listing,
                     Category,
                     SubCategory,
                     ListingImage,
                     Preference,
                     Size,
                     SubCategoryClassification)
from .serializers import (ReadListingSerializer,
                          WriteListingSerializer,
                          CategorySerializer,
                          SubCategorySerializer,
                          PreferenceSerializer,
                          SizeSerializer,
                          SubCategoryClassificationSerializer)

# to remove
from django.db.models import Prefetch


'''
API to get all listings by gender or by sub-category of given gender
'''
@api_view(['GET'])
def get_all_listings_by_gender(request, sub_category_gender=None, main_category_slug=None, sub_category_slug=None):
    # test
    print(sub_category_gender)
    if main_category_slug and sub_category_slug and sub_category_gender:
        try:
            main_category = get_object_or_404(
                Category,
                slug=main_category_slug
            )
            print(main_category)
            sub_category = get_object_or_404(
                SubCategory,
                main_category=main_category,
                slug=sub_category_slug,
                gender=sub_category_gender,
                )
            print(sub_category)
            listings = Listing.objects.filter(
                category=sub_category,
                is_sold=False
            ).order_by('-created')

            serializer = ReadListingSerializer(listings, many=True, context={'request': request})

            # debug
            # print(serializer.data)
            print('hello')

            return Response(serializer.data)
        except Exception as e:
            raise e
    elif not main_category_slug and not sub_category_slug and sub_category_gender:
        try:
            sub_categories = SubCategory.objects.filter(gender=sub_category_gender)
            listings_by_gender = []
            for sub_category in sub_categories:
                listings = Listing.objects.filter(
                    category=sub_category,
                    is_sold=False
                ).order_by('-created')
                listings_by_gender.extend(listings)

            # Debug: Inspect queryset
            for listing in listings:
                print(f"Listing: {listing.title}")
                for listing_image in listing.listing_image.all():  # Use 'listing_image' instead of 'listing_image_set'
                    print(f"- Image: {listing_image.image}")

            serializer = ReadListingSerializer(listings_by_gender, many=True, context={'request': request})

            # debug
            print('whats up')
            print(serializer.data)

            return Response(serializer.data)
        except Exception as e:
            raise e


@api_view(['GET'])
@permission_classes([AllowAny])
def get_listing_details(request, listing_pk):
    try:
        listing = Listing.objects.get(
            pk=listing_pk
            )
    except Exception as e:
        raise e

    serializer = ReadListingSerializer(listing)
    print("Listing details: ", serializer.data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_similar_listings(request, listing_pk):
    try:
        listing = get_object_or_404(Listing, id=listing_pk)
        similar_listings = listing.get_related_listings(limit=6)
        similar_listings_serializd = ReadListingSerializer(
            similar_listings, many=True, context={'request': request})
    except Exception as e:
        raise e
    return Response(similar_listings_serializd.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_mixnmatch_listings(request, listing_pk):
    try:
        listing = get_object_or_404(Listing, id=listing_pk)
        print(listing)
        mixnmatch_listings_serializd = ReadListingSerializer(
            listing.get_recommended_listings(), many=True, context={'request': request})
    except Exception as e:
        raise e
    return Response(mixnmatch_listings_serializd.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_listing_image(request):
    if request.method == 'POST':
        serializer = SubCategoryClassificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_listing_image(request, pk):
    try:
        subcategory_classification = SubCategoryClassification.objects.get(pk=pk)
    except SubCategoryClassification.DoesNotExist:
        return Response({'error': 'SubCategoryClassification not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method in ['PUT', 'PATCH']:
        serializer = SubCategoryClassificationSerializer(subcategory_classification, data=request.data, partial=(request.method == 'PATCH'))

        if serializer.is_valid():
            # updated_instance = serializer.update(subcategory_classification, serializer.validated_data)
            # return Response(SubCategoryClassificationSerializer(updated_instance).data, status=status.HTTP_200_OK)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

'''
GET Request to show extracted category once photo is uploaded
'''
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_extracted_subcategory(request):
    pass


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_listing(request):
    serializer = WriteListingSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(seller=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_listing(request, pk):
    try:
        listing = Listing.objects.get(pk=pk)
    except Listing.DoesNotExist:
        return Response({"error": "Listing not found"}, status=status.HTTP_404_NOT_FOUND)

    if listing.seller != request.user:
        return Response({"error": "You do not have permission to edit this listing"}, status=status.HTTP_403_FORBIDDEN)

    serializer = WriteListingSerializer(listing, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_sizes_for_category(request, main_category_slug):
    try:
        main_category = Category.objects.get(slug=main_category_slug)
    except Category.DoesNotExist:
        return Response({"detail": "Main category not found."}, status=404)

    sizes = Size.objects.filter(category=main_category)
    serializer = SizeSerializer(sizes, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_sub_categories(request, sub_category_gender=None):
    if sub_category_gender:
        sub_categories = SubCategory.objects.filter(gender=sub_category_gender)
    serializer = SubCategorySerializer(sub_categories, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_main_categories(request):
    category_types = Category.objects.all()
    serializer = CategorySerializer(category_types, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def search(request):
    '''
            if keyword:
            qs = qs.filter(
                Q(tag_list__title__icontains=keyword) |
                Q(title__icontains=keyword)
            ).distinct()
    '''
    if 'keyword' in request.GET:
        keyword = request.GET.get('keyword', '')

        if keyword:
            listings = Listing.objects.filter(
                # __icontains looks for keyword value in description TextField
                # Q object works as a query function together with various operators
                Q(description__icontains=keyword),
                Q(title__icontains=keyword),
            ).order_by('-created')
            listings_count = listings.count()

        serializer = ReadListingSerializer(listings)
        return Response({
            'listings': serializer.data,
            'listings_count': listings_count
        })


@permission_classes([IsAuthenticated])
class PreferenceView(APIView):
    def get(self, request):
        try:
            preference = Preference.objects.get(user_profile=request.user.profile)
        except Preference.DoesNotExist:
            return Response({"detail": "Preference not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PreferenceSerializer(preference)
        return Response(serializer.data)

    def post(self, request):
        serializer = PreferenceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_profile=request.user.profile)
            # Set user_profile.has_preference to True
            request.user.profile.has_preference = True
            request.user.profile.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            preference = Preference.objects.get(user_profile=request.user.profile)
        except Preference.DoesNotExist:
            return Response({"detail": "Preference not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PreferenceSerializer(preference, data=request.data)
        if serializer.is_valid():
            serializer.save()
            # Set user_profile.has_preference to True
            request.user.profile.has_preference = True
            request.user.profile.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

