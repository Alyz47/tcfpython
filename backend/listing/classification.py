import json

from ml_model.category_classification import predict
from ml_model.mix_and_match import recommend

from django.db.models import Q


def do_category_classification(listing_image):
    labels = {'Button_Up_Shirt': 'Button Up Shirt',
              'T_Shirt': 'T-shirt',
              'Polo_Shirt': 'Polo Shirt',
              'Shirts_And_Blouse': 'Blouse',
              'Tank_Top': 'Tank Top',
              'Jackets_And_Coats': 'Jackets And Coats',
              'Dress': 'Dress',
              'Skirt': 'Skirt',
              'Jeans': 'Jeans',
              'Pants': 'Pants',
              'Shorts': 'Shorts',
              'background': ''}
    extracted_res = {}
    is_extracted = True
    extracted_categories = predict(listing_image)
    print(f"Extraction Results: {extracted_categories}")

    if extracted_categories['detected_objects']:
        for obj in extracted_categories['detected_objects']:
            label = obj['label']
            confidence = obj['confidence']
            extracted_res[label] = confidence
    else:
        label = 'background'
        confidence = 0.0
        extracted_res[label] = confidence
        is_extracted = False
        print("No prediction returned from YOLOv8")

    if is_extracted:
        highest_conf_label = max(zip(
            extracted_res.values(),
            extracted_res.keys()))[1]
        # Get the sub-category with highest confidence score
        # Dict that contains sub-category naming that matches our db
        sub_category_extracted = labels[highest_conf_label]
        selected_subcat_score = extracted_res[highest_conf_label]
        results = {'label': sub_category_extracted, 'score': selected_subcat_score}
    else:
        sub_category_extracted = labels[next(iter(extracted_res.keys()))]
        selected_subcat_score = extracted_res[next(iter(extracted_res.keys()))]
        results = {'label': sub_category_extracted, 'score': selected_subcat_score}

    return results


def do_mix_and_match(listing_image, pk):
    from .models import Listing

    sub_categories_list = ['button up shirt', 't-shirt', 'polo shirt', 'blouse',
                           'tank top', 'jackets and coats', 'dress', 'skirt',
                           'jeans', 'pants', 'shorts', 'footwear']
    colors_list = ['white', 'black', 'beige', 'red', 'blue', 'green',
                   'yellow', 'orange', 'purple', 'pink', 'brown', 'grey',
                   'silver', 'gold', 'multi']
    mix_and_match_list = []

    # try:
    #     recommendations = recommend(listing_image)
    # except Exception as e:
    #     print(f"Error in recommend function: {e}")
    recommendations_json = recommend(listing_image)
    recommendations_parsed = json.loads(recommendations_json)
    print(recommendations_parsed)
    print(type(recommendations_parsed))
    for rec in recommendations_parsed:
        print("Entered For Loop in do_mix_and_match")
        print(rec)
        try:
            category = rec['category']
            color = rec['colour']
            print(f"rec cat: {category}, rec color: {color}")
            if category in sub_categories_list and color in colors_list:
                descriptions = rec['description']

                print(f"ENTER IF STATEMENT SUCCESS! category: {category}, color: {color}, descriptions: {descriptions}")

                category_query = Q(category__name__icontains=category)
                color_query = Q(color__icontains=color)
                description_query = Q(description__icontains=descriptions[0])

                for desc in descriptions[1:]:
                    description_query |= Q(description__icontains=desc)

                rec_query = category_query & color_query & description_query
                print(f"Query for mix n match: {rec_query}")
                mix_and_match = Listing.objects.filter(rec_query).distinct().exclude(id=pk)
                mix_and_match = list(mix_and_match)
                mix_and_match_list.extend(mix_and_match)
        except KeyError as e:
            print(f"KeyError: {e} in recommendation {rec}")
        except Exception as e:
            print(f"Unexpected error: {e} in recommendation {rec}")

    mix_and_match_qs = Listing.objects.filter(id__in=[listing.id for listing in mix_and_match_list])

    return mix_and_match_qs
