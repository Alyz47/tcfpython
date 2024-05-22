import tempfile

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Avg, Q
from rest_framework import serializers
from account.serializers import UserSerializer, SellerSerializer
from .classification import do_category_classification
from .models import (
    Listing,
    ListingImage,
    Category,
    SubCategoryClassification,
    SubCategory,
    Size,
    Preference,
    PreferredSubCategory,
    PreferredSize)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'image']


class SubCategorySerializer(serializers.ModelSerializer):
    main_category = CategorySerializer()

    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'slug', 'main_category', 'gender', 'image']


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'category', 'size']


class ListingImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = ListingImage
        fields = ['id', 'image', 'is_cover']


class ReadListingSerializer(serializers.ModelSerializer):
    listing_image = ListingImageSerializer(many=True)
    category = SubCategorySerializer()
    size = SizeSerializer()
    seller = SellerSerializer()

    class Meta:
        model = Listing
        fields = '__all__'


'''
Handles Category classification by YOLOv8
'''
class SubCategoryClassificationSerializer(serializers.ModelSerializer):
    uploaded_image = serializers.ImageField(write_only=True)
    delete_image = serializers.BooleanField(write_only=True, required=False, default=False)
    # listing = serializers.PrimaryKeyRelatedField(queryset=Listing.objects.all())

    class Meta:
        model = SubCategoryClassification
        fields = ['id', 'uploaded_image', 'delete_image', 'sub_category', 'score']

    def create(self, validated_data):
        image_file = validated_data.pop('uploaded_image')
        print(f"Uploaded Image: {image_file}")

        if image_file:
            try:
                image_path = self.handle_uploaded_image(image_file)
                extraction_results = do_category_classification(image_path)
                print(f"Classification Results: {extraction_results}")

                subcategory_extracted = extraction_results['label']
                score_extracted = extraction_results['score']
                subcategory_classification = SubCategoryClassification.objects.create(
                    uploaded_image=image_file,
                    sub_category=subcategory_extracted,
                    score=score_extracted
                )
                subcategory_classification.save()

                return subcategory_classification
            except Exception as e:
                raise e

    '''
    Update serializer function to handle deletion
    '''
    def update(self, instance, validated_data):
        delete_image = validated_data.get('delete_image', False)

        if delete_image and instance.uploaded_image:
            instance.uploaded_image.delete(save=False)
            instance.uploaded_image = None
            instance.sub_category = ''
            instance.score = None

        uploaded_new_image = validated_data.get('uploaded_image', None)
        if uploaded_new_image:
            if instance.uploaded_image:
                instance.uploaded_image.delete(save=False)
            image_path = self.handle_uploaded_image(uploaded_new_image)
            extraction_results = do_category_classification(image_path)
            # Debug
            print(f"Classification Results: {extraction_results}")

            subcategory_extracted = extraction_results['label']
            score_extracted = extraction_results['score']

            instance.uploaded_image = uploaded_new_image
            instance.sub_category = subcategory_extracted
            instance.score = score_extracted
        else:
            print(f"No new image uploaded for {instance}")

        instance.save()
        return instance

    def handle_uploaded_image(self, image_file):
        if isinstance(image_file, InMemoryUploadedFile):
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            for chunk in image_file.chunks():
                temp_file.write(chunk)
            temp_file.flush()
            return temp_file.name

        return image_file.path


class WriteListingSerializer(serializers.ModelSerializer):
    listing_image = ListingImageSerializer(many=True, read_only=True)
    listing_image_list = serializers.ListField(
        child=serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )
    # category = serializers.PrimaryKeyRelatedField(queryset=SubCategory.objects.all())

    class Meta:
        model = Listing
        fields = [
            'id', 'seller', 'listing_image', 'listing_image_list', 'title', 'gender', 'category', 'description', 'price',
            'size', 'condition', 'color', 'is_sold', 'is_manual'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        images = SubCategoryClassification.objects.all().values_list('uploaded_image', flat=True)
        data['listing_image_list'] = images
        return data

    def create(self, validated_data):
        gender = validated_data.pop('gender')
        subcategory_classifications = SubCategoryClassification.objects.all()

        sub_category_scores = subcategory_classifications.values('sub_category', 'score')
        # Group the results by 'sub_category' and compute the average score for each group
        average_scores_by_category = sub_category_scores.annotate(avg_score=Avg('score')).order_by('-avg_score')
        print("---------------Average Score by Category-------------------")
        print(average_scores_by_category)
        # Get the group with the highest average score
        highest_average_group = average_scores_by_category.first()
        highest_average_sub_category = highest_average_group['sub_category']
        highest_average_score = highest_average_group['avg_score']
        print(f"Subcat: {highest_average_sub_category} Score: {highest_average_score}")
        print(f"Subcat Data Type: {type(highest_average_sub_category)}")

        sub_category_extracted = SubCategory.objects.get(
            Q(name__iexact=highest_average_sub_category.strip()) & Q(gender__iexact=gender)
        )
        print(f"Sub-Category retrieved: {sub_category_extracted}")
        print(f"Data Type: {type(sub_category_extracted)}")
        listing = Listing.objects.create(**validated_data, gender=gender, category=sub_category_extracted)
        print(f"Listing created! {listing} {listing.title}")

        # Get uploaded images from SubCategoryClassification table and assign to listing_image_list
        uploaded_images = subcategory_classifications.values_list('uploaded_image', flat=True)
        uploaded_images_list = list(uploaded_images)

        if not uploaded_images:
            raise serializers.ValidationError("At least one image must be uploaded.")
        if len(uploaded_images) > 6:
            raise serializers.ValidationError("Maximum number of images allowed is 6.")

        for image in uploaded_images_list:
            ListingImage.objects.create(listing=listing, image=image)

        return listing

    def update(self, instance, validated_data):
        listing_images_list = validated_data.pop('listing_image_list', None)
        category_data = validated_data.pop('category', None)

        if category_data:
            instance.category = category_data

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if listing_images_list:
            # Clear existing images
            instance.listing_image.all().delete()
            
            for image in listing_images_list:
                ListingImage.objects.create(listing=instance, image=image)

        return instance


class PreferredSubCategorySerializer(serializers.ModelSerializer):
    sub_category = serializers.PrimaryKeyRelatedField(queryset=SubCategory.objects.all())

    class Meta:
        model = PreferredSubCategory
        fields = ['id', 'sub_category']


class PreferredSizeSerializer(serializers.ModelSerializer):
    size = serializers.PrimaryKeyRelatedField(queryset=Size.objects.all())

    class Meta:
        model = PreferredSize
        fields = ['id', 'size']


class PreferenceSerializer(serializers.ModelSerializer):
    preferred_subcategories = PreferredSubCategorySerializer(many=True)
    preferred_sizes = PreferredSizeSerializer(many=True)

    class Meta:
        model = Preference
        fields = ['user_profile', 'preferred_subcategories', 'preferred_sizes']

    def create(self, validated_data):
        preferred_subcategories_data = validated_data.pop('preferred_subcategories')
        preferred_sizes_data = validated_data.pop('preferred_sizes')
        profile = validated_data['user_profile']

        try:
            preference = Preference.objects.get(user_profile=profile)
            # If exists, update the existing Preference object
            self.update(preference, validated_data)
        except Preference.DoesNotExist:
            # If not, create a new Preference object
            preference = Preference.objects.create(**validated_data)

        # Clear old preferences
        preference.preferred_subcategories.all().delete()
        preference.preferred_sizes.all().delete()

        for subcategory_data in preferred_subcategories_data:
            sub_category_instance = subcategory_data['sub_category']
            PreferredSubCategory.objects.create(preference=preference, sub_category=sub_category_instance)

        for size_data in preferred_sizes_data:
            # size_instance = Size.objects.get(id=size_data['size'].id)
            size_instance = size_data['size']
            PreferredSize.objects.create(preference=preference, size=size_instance)

        profile.has_preference = bool(preferred_subcategories_data or preferred_sizes_data)
        profile.save()

        return preference

    def update(self, instance, validated_data):
        preferred_subcategories_data = validated_data.pop('preferred_subcategories')
        preferred_sizes_data = validated_data.pop('preferred_sizes')
        profile = instance.user_profile

        instance.preferred_subcategories.all().delete()
        instance.preferred_sizes.all().delete()

        for subcategory_data in preferred_subcategories_data:
            # PreferredSubCategory.objects.create(preference=instance, **subcategory_data)
            PreferredSubCategory.objects.create(preference=instance, sub_category=subcategory_data['sub_category'])

        for size_data in preferred_sizes_data:
            size_instance = Size.objects.get(id=size_data['size'].id)
            PreferredSize.objects.create(preference=instance, size=size_instance)

        profile.has_preference = bool(preferred_subcategories_data or preferred_sizes_data)
        profile.save()

        instance.save()
        return instance
