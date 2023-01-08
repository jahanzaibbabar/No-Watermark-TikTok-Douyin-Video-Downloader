import requests
import json


key = '575cf421f4msh13bd5368757ea94p15bf25jsnee4e3a81de1e'

def get_user_uid(username):
    url = f"https://tokapi-mobile-version.p.rapidapi.com/v1/user/username/{username}"

    headers = {
    	"X-RapidAPI-Key": key,
    	"X-RapidAPI-Host": "tokapi-mobile-version.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers)

    p = response.text
    p = json.loads(p)
    try:
        return p["uid"]
    except:
        return False


def get_videos(user_uid, counter):
    url = f"https://tokapi-mobile-version.p.rapidapi.com/v1/post/user/{user_uid}/posts"

    querystring = {"count":counter}

    headers = {
    	"X-RapidAPI-Key": "575cf421f4msh13bd5368757ea94p15bf25jsnee4e3a81de1e",
    	"X-RapidAPI-Host": "tokapi-mobile-version.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    p = response.text
    p = json.loads(p)
    p = p['aweme_list']
    holder_list = []
    for item in p:
        # xxx = item['share_url'].split(".htm")[0]
        holder_list.append(item['share_url'])
    return holder_list


def get_video_id(links, username):
    addresses = []
    for link in links:
        link_ = link.split('.html')[0]
        link_ = str(link)
        video_id = link_.split('v/')[1]
        
        addr = f'https://www.tiktok.com/oembed?url=https://www.tiktok.com/@{username}/video/{str(video_id)}'
        # addr = f'https://www.tiktok.com/@{username}/video/{str(video_id)}'
        # print(addr)
        addresses.append(addr)
    # return addresses
    
    try:
        addresses_new = addresses[-16:]

    except:
        addresses_new = addresses
    
    embed_list = []
    for addr in addresses_new: 
        req = requests.request('GET', url=addr)
        req = json.loads(req.text)
        embed_list.append(req['html'])
    
    return embed_list