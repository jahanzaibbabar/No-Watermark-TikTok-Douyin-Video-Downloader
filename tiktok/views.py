from django.shortcuts import render
from .helpers import get_user_uid, get_videos, get_video_id
from django.core.paginator import Paginator
import os
import re
import time
import requests
import unicodedata
from flask import jsonify, make_response
import uuid
from werkzeug.urls import url_quote
from django.http import HttpResponse
from scr_data import Scraper
from scr_data import *
import asyncio
import urllib.request


# Create your views here.
def home(request):
    if request.method == 'POST':
        username = request.POST.get('text_username')
        username = username.lower()
        try:
            user_uid = get_user_uid(username)
            paginator = Paginator(get_video_id(get_videos(user_uid, 16), username), 15)
            # paginator = Paginator(get_video_id(get_videos(user_uid, 16), username), 15)
            page_obj = paginator.get_page(1)
            context = {
                'videos': page_obj,
                'username': username
            }
            # paginator = Paginator(contact_list, 25)
            # print('no error so far')
    
            return render(request, 'home.html', context)
        except:
            context = {
                'msg_': 'Username not found. Please insert username again.'
            }
            return render(request, 'home.html', context)
    else:
        try:
            page_number = request.GET.get('page')
            username = request.GET.get('username')
            user_uid = get_user_uid(username)
            paginator = Paginator(get_video_id(
                get_videos(user_uid, int(page_number)*15), username), 14)
            
            page_obj = paginator.get_page(1)
            context = {
                'videos': page_obj,
                'username': username
            }
        except:
            context = {

            }

        return render(request, 'home.html', context)
    
    
def tiktok_downloader(request):
    return render(request, 'save-video.html', {'disp':'none'})
    
    
def show_video(request):
    try:
        headers = {
        'user-agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.66'
    }
    
        api = Scraper()
        
        content = request.GET.get('text_video_url', '')
        
        if content == '':
            return jsonify(status='failed', reason='url value cannot be empty')

            
        data = asyncio.run(api.hybrid_parsing(content))
        if data == "invalid_url":
            return render(request, 'save-video.html', {'disp':'none'})
            
        video_url = data.get('video_data').get('nwm_video_url_HQ')
        
        if content == u or content == u2 :
            video_url = res_u
            
        res = requests.get(video_url, headers=headers)
        f = open("xaller.mp4", 'bw')
        f.write(res.content)
        f.close()

        return render(request, 'save-video.html', {'video_url' : video_url, 'original_url' : content, 'disp':'block' })
            

    except Exception as e:
        response = HttpResponse(str(e))
        return  response 
        
        

def download_video(request):
    ## Downloading
    headers = {
        'user-agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.66'
    }
    
  
    video_url = request.GET.get('video_url', '')
    video_mp4 = requests.get(video_url, headers).content
    
    filen = str(uuid.uuid4().hex) + '.mp4'
    
 
    response = HttpResponse(video_mp4)
    response['Content-Type'] = "application/force-download"
    response['Content-Disposition'] = f"inline; filename=" + str(filen)
    
    return response
    
        
        

def handle_not_found(request,exception):
    return render(request,'404.html')

    
    
    
    
    
