import os 
import google.generativeai as genai
import PIL.Image

GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY'] = 'AIzaSyCxoBIdN1YZhcyXjMQgRr69vQEs-HKgxUo'
genai.configure(api_key=GOOGLE_API_KEY)


def recommend(img):
    img = PIL.Image.open(img)
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content(["Write in json 5 other pieces of clothings that can go well with img, with the structure like this\
        {\
            \"category\": ""\
            \"colour\":""\
            \"description\": ["", "", ""]\
        }\
    \
    some info:\
    categories can be the following only:\
    tshirt, button up shirt, shirts and blouses, tank top, jackets and coats, jeans, pants, shorts, dress, skirt, polo tshirt\
    tops are: tshirt, button shirt, shirts and blouses, tank top, jackets and coats, polo shirt\
    bottoms are: jeans, pants, shorts, joggers, skirt, dress\
    for footwear, let category be footwear.\
    make sure your suggestion will not be the same category as the input. so if the input is a top, dont give another top, but bottoms\
    description is just an array (no size limit) of keywords. make sure that each description in the description array is one word only.\
    ", img], stream=True)

    response.resolve()
    json_response = response.text
    # print(json_response)

    return json_response


# E.G insert call to mix_and_match function here
# mix_and_match('images/white-tshirt-test_PHjiqRH.jpg')