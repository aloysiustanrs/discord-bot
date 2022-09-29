import requests

def respond():

    random_anime = requests.get('https://api.jikan.moe/v4/random/anime').json()['data']


    image =  random_anime['images']['jpg']['image_url']
    title = random_anime['title']
    description = random_anime['synopsis'] if random_anime['synopsis'] else '-'
    episodes = random_anime['episodes']
    all_genres = [genre['name'] for genre in random_anime['genres']] + [genre['name'] for genre in random_anime['explicit_genres']]
    all_genres = ', '.join(all_genres) if all_genres else '-'
    studios = ', '.join([studio['name'] for studio in random_anime['studios']]) if random_anime['studios'] else '-'
    duration = random_anime['duration']
    link = random_anime['url']

    ret = f"Title: {title} \n\nDescription: {description} \n\nEpisodes: {episodes} \n\nGenres: {all_genres} \n\nStudio: {studios} \n\nDuration: {duration} \n\nLink: {link} \n\n{image} "

    return(ret)
