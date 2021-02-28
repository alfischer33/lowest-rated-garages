from django.shortcuts import render
from django.http import HttpRequest
import requests
import pandas as pd


# Create your views here.
def index(request):

    #build request_df
    headers = {'Authorization':'Bearer nyEwhmVUy_rfbVFFOgvSUQJNGy9ufqalrmO_cC0x1l96BYfh4VMufgaK8jImIUrRM7l5geysxXzkCoR52FdQ3H0G5YneEnPhP0yacGak-KepPkcvQY5D8LwXXps6YHYx'}

    location = request.GET.get('location')
    if location == None:
        location = 'San Francisco'

    min_reviews = request.GET.get('min_reviews')
    if min_reviews == None:
        min_reviews = 0

    url = f'https://api.yelp.com/v3/businesses/search?categories=parking&location={location}'

    offset=0
    request_json = requests.get(f'https://api.yelp.com/v3/businesses/search?offset={offset}&limit=50&categories=parking&location={location}', headers=headers).json()

    def get_lot_df(offset, location):
        request_json = requests.get(f'https://api.yelp.com/v3/businesses/search?offset={offset}&limit=50&categories=parking&location={location}', headers=headers).json()
        request_df = pd.DataFrame(request_json['businesses'])
        return request_df

    request_df = pd.DataFrame(request_json['businesses'])
    while offset < request_json['total']:
        offset = offset+50
        print(offset)
        request_df = request_df.append(get_lot_df(offset=offset, location=location))

    #build df with relevant info
    df = pd.DataFrame()
    df['address'] = request_df['location'].apply(lambda x: ", ".join(x['display_address']))
    df['name'] = request_df['name']
    df['image'] = request_df['image_url']
    df['star_rating'] = request_df['rating']
    df['review_count'] = request_df['review_count']
    df['link'] = request_df['url']
    df['score'] = request_df.apply(lambda x: (x.review_count * x.rating)/(x.review_count + 1), axis=1)
    df = df.sort_values('score')
    df = df[df['review_count']>int(min_reviews)]

    lots = [df.iloc[i] for i in range(len(df))]

    context={'lots':lots, "location":location}

    return render(request, 'parkingdata/index.html',context)