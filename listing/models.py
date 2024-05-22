import os 
from collections import defaultdict
from django.db import models
from django.db.models import Q
# from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

from account.models import User, Profile
from core.models import Extensions, TimeStampedModel
from .classification import do_mix_and_match


class Category(Extensions):
    MAIN_CAT_CHOICES = [
        ("top", "Top"),
        ("bottom", "Bottom"),
        ("footwear", "Footwear"),
    ]

    name = models.CharField(
        choices=MAIN_CAT_CHOICES,
        verbose_name="Category Name",
        max_length=255,
        unique=True,
    )
    slug = models.SlugField(max_length=100, null=True, blank=True)
    image = models.ImageField(verbose_name="Main Category Cover Image", upload_to="images/", null=True, blank=True)

    class Meta:
        verbose_name = "Main Category"
        verbose_name_plural = "Main Categories"

    def __str__(self):
        return self.slug


def subcat_image_upload_path(instance, filename):
    # Get the filename and extension
    base_filename, file_extension = os.path.splitext(filename)
    # Generate the new filename
    new_filename = f"{instance.main_category}/{base_filename}{file_extension}"
    # Return the upload path
    return os.path.join("categories", new_filename)


class SubCategory(Extensions):
    GENDER_CHOICES = [
        ("men", "Men"),
        ("women", "Women"),
        ("others", "Others")
    ]
    name = models.CharField(verbose_name="Sub-category Name", max_length=155)
    main_category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    slug = models.SlugField(max_length=155, null=True, blank=True)
    image = models.ImageField(verbose_name="Category Cover Image", upload_to=subcat_image_upload_path, null=True, blank=True)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=25, null=True, blank=True)

    class Meta:
        verbose_name = "Sub-category"
        verbose_name_plural = "Sub-categories"

    def __str__(self):
        return f"{self.gender} - {self.main_category} - {self.slug}"


class Size(TimeStampedModel):
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    size = models.CharField(max_length=50)

    class Meta:
        unique_together = ('category', 'size')

    def __str__(self):
        return f"{self.category} - {self.size}"


class ListingManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def filter_listings(self, sort, color_filter, size_filter, condition_filter):
        qs = self.get_queryset().filter(is_sold=False)
        if sort:
            sort = int(sort)
            if sort == 1:
                qs = qs.order_by('-price')
            elif sort == 2:
                qs = qs.order_by('price')
            elif sort == 3:
                qs = qs.order_by('-created')
        if color_filter:
            pass
        if size_filter:
            pass
        if condition_filter:
            pass
        return qs

    def get_listings(self):
        return self.get_queryset().filter(is_sold=False)


class Listing(Extensions):
    GENDER_CHOICES = [
        ("men", "Men"),
        ("women", "Women"),
    ]

    CONDITION_CHOICES = [
        ("Heavily Used", "Heavily Used"),
        ("Well Used", "Well Used"),
        ("Lightly Used", "Lightly Used"),
        ("Like New", "Like New"),
        ("Brand New", "Brand New"),
    ]

    COLOR_CHOICES = [
        ('White', 'White'),
        ('Black', 'Black'),
        ('Beige', 'Beige'),
        ('Red', 'Red'),
        ('Blue', 'Blue'),
        ('Green', 'Green'),
        ('Yellow', 'Yellow'),
        ('Orange', 'Orange'),
        ('Purple', 'Purple'),
        ('Pink', 'Pink'),
        ('Brown', 'Brown'),
        ('Grey', 'Grey'),
        ('Silver', 'Silver'),
        ('Gold', 'Gold'),
        ('Multi', 'Multi'),
    ]
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=25, null=True, blank=True)
    category = models.ForeignKey(SubCategory,
                                 on_delete=models.CASCADE,
                                 null=True,
                                 blank=True
                                 )  # Stores extracted category from ML model
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    condition = models.CharField(choices=CONDITION_CHOICES, max_length=100)
    color = models.CharField(choices=COLOR_CHOICES, max_length=100)
    is_sold = models.BooleanField(default=False)
    is_manual = models.BooleanField(default=False)

    objects = ListingManager()

    class Meta:
        verbose_name = "Listing"
        verbose_name_plural = "Listings"

    def __str__(self):
        return str(self.pk)

    def get_related_listings(self, limit=None):
            title_split = self.title.split(' ')
            lookups = Q(title__icontains=title_split[0])

            for i in title_split[1:]:
                lookups |= Q(title__icontains=i)

            related_listings = Listing.objects.filter(
                lookups).distinct().exclude(id=self.id)
            
            # Limit the number of related listings if a limit is provided
            if limit is not None:
                related_listings = related_listings[:limit]

            print(f"Related Listings: {related_listings}")
            return related_listings

    def get_recommended_listings(self):
        listing_images = ListingImage.objects.filter(listing_id=self.id)
        subcat_classif_obj_list = []
        for listing_image in listing_images:
            listing_image_path = listing_image.image.name
            try:
                subcat_classif_obj = SubCategoryClassification.objects.get(
                    Q(uploaded_image__iexact=listing_image_path.strip()))
                subcat_classif_obj_list.append(subcat_classif_obj)
                print(f"Subcat and score list: {subcat_classif_obj_list}")
            except SubCategoryClassification.DoesNotExist:
                subcat_classif_obj = None

        subcat_scores = defaultdict(list)
        for obj in subcat_classif_obj_list:
            subcat_scores[obj.sub_category].append(obj.score)

        subcat_avg_scores = {}
        for subcat, scores in subcat_scores.items():
            average_score = sum(scores) / len(scores)
            subcat_avg_scores[subcat] = average_score

        highest_avg_subcat = max(subcat_avg_scores, key=subcat_avg_scores.get)
        highest_score_obj = SubCategoryClassification.objects.filter(
            sub_category=highest_avg_subcat).order_by('-score').first()

        print(f"Best Scored Image: {highest_score_obj}")

        results = do_mix_and_match(highest_score_obj.uploaded_image, self.id)
        print(f"Recommended Listings: {results}")
        return results


class ListingImage(Extensions):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="listing_image"
    )
    image = models.ImageField(
        verbose_name="image",
        upload_to="images/",
    )
    is_cover = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Listing Image"
        verbose_name_plural = "Listing Images"

    def __str__(self):
        return f"Listing Image -> Listing PK: {self.listing} Image: {self.image}"


class Feedback(Extensions):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.TextField()
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedbacks"

    def __str__(self):
        return str(self.rating)


class Preference(Extensions):
    user_profile = models.OneToOneField(Profile, on_delete=models.CASCADE)

    def __str__(self):
        # return f"{str(self.user_profile.user.username)} ---> {self.category} + {self.size}"
        return self.user_profile.user.username


class PreferredSubCategory(TimeStampedModel):
    preference = models.ForeignKey(
        Preference,
        related_name='preferred_subcategories',
        on_delete=models.CASCADE
        )
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Preferred Sub-Category"
        verbose_name_plural = "Preferred Sub-Categories"

    def __str__(self):
        return f"{self.preference} - {self.sub_category}"


class PreferredSize(TimeStampedModel):
    preference = models.ForeignKey(
        Preference,
        related_name='preferred_sizes',
        on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.preference} - {self.size}"


class SubCategoryClassification(Extensions):
    # listing_image = models.ForeignKey(ListingImage, on_delete=models.CASCADE)
    # listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    uploaded_image = models.ImageField(verbose_name="image", upload_to="images/")
    sub_category = models.CharField(max_length=155, default='', null=True, blank=True)
    score = models.DecimalField(decimal_places=5, max_digits=10, null=True, blank=True)

    def __str__(self):
        return f"{self.uploaded_image} -> {self.sub_category}"
