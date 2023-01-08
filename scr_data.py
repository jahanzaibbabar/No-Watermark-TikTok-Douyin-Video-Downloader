import re
import os
import random
import aiohttp
import platform
import asyncio
import traceback
import configparser

from typing import Union
from tenacity import *


class Scraper:
   
    def __init__(self):
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.66"
        }
        self.douyin_cookies = {
            'Cookie': 'msToken=tsQyL2_m4XgtIij2GZfyu8XNXBfTGELdreF1jeIJTyktxMqf5MMIna8m1bv7zYz4pGLinNP2TvISbrzvFubLR8khwmAVLfImoWo3Ecnl_956MgOK9kOBdwM=; odin_tt=6db0a7d68fd2147ddaf4db0b911551e472d698d7b84a64a24cf07c49bdc5594b2fb7a42fd125332977218dd517a36ec3c658f84cebc6f806032eff34b36909607d5452f0f9d898810c369cd75fd5fb15; ttwid=1%7CfhiqLOzu_UksmD8_muF_TNvFyV909d0cw8CSRsmnbr0%7C1662368529%7C048a4e969ec3570e84a5faa3518aa7e16332cfc7fbcb789780135d33a34d94d2'
        }
        self.tiktok_api_headers = {
            'User-Agent': 'com.ss.android.ugc.trill/494+Mozilla/5.0+(Linux;+Android+12;+2112123G+Build/SKQ1.211006.001;+wv)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Version/4.0+Chrome/107.0.5304.105+Mobile+Safari/537.36'
        }
    
        if os.path.exists('config.ini'):
            self.config = configparser.ConfigParser()
            self.config.read('config.ini', encoding='utf-8')
        
            if self.config['Scraper']['Proxy_switch'] == 'True':
            
                if self.config['Scraper']['Use_different_protocols'] == 'False':
                    self.proxies = {
                        'all': self.config['Scraper']['All']
                    }
                else:
                    self.proxies = {
                        'http': self.config['Scraper']['Http_proxy'],
                        'https': self.config['Scraper']['Https_proxy'],
                    }
            else:
                self.proxies = None
    
        else:
            self.proxies = None
    
        if platform.system() == 'Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


    @staticmethod
    def get_url(text: str) -> Union[str, None]:
        try:
        
            url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        
            if len(url) > 0:
                return url[0]
        except Exception as e:
        
            return None


    @retry(stop=stop_after_attempt(3), wait=wait_random(min=1, max=2))
    async def convert_share_urls(self, url: str) -> Union[str, None]:
           
        url = self.get_url(url)
    
        if url is None:
        
            return None
    
        if 'douyin' in url:
    
            if 'v.douyin' in url:
            
            
                url = re.compile(r'(https://v.douyin.com/)\w+', re.I).match(url).group()
            
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, headers=self.headers, proxy=self.proxies, allow_redirects=False,
                                               timeout=10) as response:
                            if response.status == 302:
                                url = response.headers['Location'].split('?')[0] if '?' in response.headers[
                                    'Location'] else \
                                    response.headers['Location']
                            
                                return url
                except Exception as e:
                
                
                    return None
            else:
            
                return url
    
        elif 'tiktok' in url:
    
            if '@' in url:
            
                return url
            else:
            
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, headers=self.headers, proxy=self.proxies, allow_redirects=False,
                                               timeout=10) as response:
                            if response.status == 301:
                                url = response.headers['Location'].split('?')[0] if '?' in response.headers[
                                    'Location'] else \
                                    response.headers['Location']
                            
                                return url
                except Exception as e:
                
                
                    return None


    async def get_douyin_video_id(self, original_url: str) -> Union[str, None]:
       
        try:
            video_url = await self.convert_share_urls(original_url)
        
        
            if '/video/' in video_url:
                key = re.findall('/video/(\d+)?', video_url)[0]
            
                return key
        
            elif 'discover?' in video_url:
                key = re.findall('modal_id=(\d+)', video_url)[0]
            
                return key
        
            elif 'live.douyin' in video_url:
            
                key = video_url.replace('https://live.douyin.com/', '')
            
                return key
        
            elif 'note' in video_url:
            
                key = re.findall('/note/(\d+)?', video_url)[0]
            
                return key
        except Exception as e:
        
            return None


    @retry(stop=stop_after_attempt(3), wait=wait_random(min=1, max=2))
    async def get_douyin_video_data(self, video_id: str) -> Union[dict, None]:

    
        try:
        
            api_url = f"https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={video_id}"
        
        
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, headers=self.headers, proxy=self.proxies, timeout=10) as response:
                    response = await response.json()
                
                    video_data = response['item_list'][0]
                
                
                    return video_data
        except Exception as e:
        
            return None


    @retry(stop=stop_after_attempt(3), wait=wait_random(min=1, max=2))
    async def get_douyin_live_video_data(self, web_rid: str) -> Union[dict, None]:
    
        try:
        
            api_url = f"https://live.douyin.com/webcast/web/enter/?aid=6383&web_rid={web_rid}"
        
        
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, headers=self.douyin_cookies, proxy=self.proxies, timeout=10) as response:
                    response = await response.json()
                
                    # data = orjson.loads(response.text)
                
                    # video_data = data['data']
                    video_data = ''
                
                
                    return video_data
        except Exception as e:
        
            return None

    async def get_tiktok_video_id(self, original_url: str) -> Union[str, None]:
        try:
        
            original_url = await self.convert_share_urls(original_url)
        
            if '.html' in original_url:
                video_id = original_url.replace('.html', '')
            elif '/video/' in original_url:
                video_id = re.findall('/video/(\d+)', original_url)[0]
            elif '/v/' in original_url:
                video_id = re.findall('/v/(\d+)', original_url)[0]
        
        
            return video_id
        except Exception as e:
        
            return None

    @retry(stop=stop_after_attempt(3), wait=wait_random(min=1, max=2))
    async def get_tiktok_video_data(self, video_id: str) -> Union[dict, None]:
    
        try:
        
            api_url = f'https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/feed/?aweme_id={video_id}&iid=6165993682518218889&device_id={random.randint(10*10*10, 9*10**10)}&aid=1180'
        
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, headers=self.tiktok_api_headers, proxy=self.proxies, timeout=10) as response:
                    response = await response.json()
                    video_data = response['aweme_list'][0]
                
                    return video_data
        except Exception as e:
        
            return None


    async def hybrid_parsing(self, video_url: str) -> dict:
    
        if 'douyin' in video_url:
            url_platform = 'douyin' 
        elif  'tiktok' in video_url:
            url_platform =  'tiktok'
        else:
            return "invalid_url"
    
    
    
        video_id = await self.get_douyin_video_id(
            video_url) if url_platform == 'douyin' else await self.get_tiktok_video_id(
            video_url)
        if video_id:
        
        
        
            data = await self.get_douyin_video_data(
                video_id) if url_platform == 'douyin' else await self.get_tiktok_video_data(
                video_id)
            if data:
            
                url_type_code = data['aweme_type']
    
                url_type_code_dict = {
                
                    2: 'image',
                    4: 'video',
                
                    0: 'video',
                    51: 'video',
                    55: 'video',
                    58: 'video',
                    61: 'video',
                    150: 'image'
                }
            
            
            
            
                url_type = url_type_code_dict.get(url_type_code, 'video')
            
            



                result_data = {
                    'status': 'success',
                    
                    'type': url_type,
                    'platform': url_platform,
                    'aweme_id': video_id,
                    'official_api_url':
                        {
                            "User-Agent": self.headers["User-Agent"],
                            "api_url": f"https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={video_id}"
                        } if url_platform == 'douyin'
                        else
                        {
                            "User-Agent": self.tiktok_api_headers["User-Agent"],
                            "api_url": f'https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/feed/?aweme_id={video_id}&iid=6165993682518218889&device_id={random.randint(10*10*10, 9*10**10)}&aid=1180'
                        },
                    'desc': data.get("desc"),
                    'create_time': data.get("create_time"),
                    'author': data.get("author"),
                    'music': data.get("music"),
                    'statistics': data.get("statistics"),
                    'cover_data': {
                        'cover': data.get("video").get("cover"),
                        'origin_cover': data.get("video").get("origin_cover"),
                        'dynamic_cover': data.get("video").get("dynamic_cover")
                    },
                    'hashtags': data.get('text_extra'),
                }
            
                api_data = None
            
                try:
                
                    if url_platform == 'douyin':
                    
                        if url_type == 'video':
                        
                        
                            uri = data['video']['play_addr']['uri']
                            wm_video_url = data['video']['play_addr']['url_list'][0]
                            wm_video_url_HQ = f"https://aweme.snssdk.com/aweme/v1/playwm/?video_id={uri}&radio=1080p&line=0"
                            nwm_video_url = wm_video_url.replace('playwm', 'play')
                            nwm_video_url_HQ = f"https://aweme.snssdk.com/aweme/v1/play/?video_id={uri}&ratio=1080p&line=0"
                            api_data = {
                                'video_data':
                                    {
                                        'wm_video_url': wm_video_url,
                                        'wm_video_url_HQ': wm_video_url_HQ,
                                        'nwm_video_url': nwm_video_url,
                                        'nwm_video_url_HQ': nwm_video_url_HQ
                                    }
                            }
                    
                        elif url_type == 'image':
                        
                        
                            no_watermark_image_list = []
                        
                            watermark_image_list = []
                        
                            for i in data['images']:
                                no_watermark_image_list.append(i['url_list'][0])
                                watermark_image_list.append(i['download_url_list'][0])
                            api_data = {
                                'image_data':
                                    {
                                        'no_watermark_image_list': no_watermark_image_list,
                                        'watermark_image_list': watermark_image_list
                                    }
                            }
                
                    elif url_platform == 'tiktok':
                    
                        if url_type == 'video':
                        
                        
                            wm_video = data['video']['download_addr']['url_list'][0]
                            api_data = {
                                'video_data':
                                    {
                                        'wm_video_url': wm_video,
                                        'wm_video_url_HQ': wm_video,
                                        'nwm_video_url': data['video']['play_addr']['url_list'][0],
                                        'nwm_video_url_HQ': data['video']['bit_rate'][0]['play_addr']['url_list'][0]
                                    }
                            }
                    
                        elif url_type == 'image':
                        
                        
                            no_watermark_image_list = []
                        
                            watermark_image_list = []
                            for i in data['image_post_info']['images']:
                                no_watermark_image_list.append(i['display_image']['url_list'][0])
                                watermark_image_list.append(i['owner_watermark_image']['url_list'][0])
                            api_data = {
                                'image_data':
                                    {
                                        'no_watermark_image_list': no_watermark_image_list,
                                        'watermark_image_list': watermark_image_list
                                    }
                            }
                
                    result_data.update(api_data)
                
                
                    return result_data
                except Exception as e:
                    traceback.print_exc()
                
                    return {'status': 'failed', 'message': 'Data processing failed!'}
            else:
            
                return {'status': 'failed',
                        'message': 'Return data is empty and cannot be processed!'}
        else:
        
            return {'status': 'failed', 'message': 'Failed to get video ID!'}



    @staticmethod
    def hybrid_parsing_minimal(data: dict) -> dict:
    
        if data['status'] == 'success':
            result = {
                'status': 'success',
                'message': data.get('message'),
                'platform': data.get('platform'),
                'type': data.get('type'),
                'desc': data.get('desc'),
                'wm_video_url': data['video_data']['wm_video_url'] if data['type'] == 'video' else None,
                'wm_video_url_HQ': data['video_data']['wm_video_url_HQ'] if data['type'] == 'video' else None,
                'nwm_video_url': data['video_data']['nwm_video_url'] if data['type'] == 'video' else None,
                'nwm_video_url_HQ': data['video_data']['nwm_video_url_HQ'] if data['type'] == 'video' else None,
                'no_watermark_image_list': data['image_data']['no_watermark_image_list'] if data[
                                                                                                'type'] == 'image' else None,
                'watermark_image_list': data['image_data']['watermark_image_list'] if data['type'] == 'image' else None
            }
            return result
        else:
            return data


res_u = "https://v16.tiktokcdn.com/e399bbba937117f1c69b2e00444b4fd7/6399027a/video/tos/alisg/tos-alisg-pve-0037c001/a16787ffc90644f7a8fa4b13655f812a/?a=1180&ch=0&cr=0&dr=0&lr=all&cd=0%7C0%7C0%7C0&cv=1&br=1776&bt=888&cs=0&ds=6&ft=KLrRMzm88No0PDyl~IMaQ95HheQ4JE.C0&mime_type=video_mp4&qs=0&rc=OzM1M2g5aDNnaTs2OTk3OUBpMzhvbmhscDhqeDMzZTczM0BgYzMuMDBgX2AxLWNgL181YSNsYWxrLy5gcy5fLS1fMTRzcw%3D%3D&l=2022121316533801021713503217417B02&btag=80000&cc=2"
u = "https://vm.tiktok.com/ZSJmdax66/"
u2 = "https://vm.tiktok.com/ZSJmdax66"

async def async_test(douyin_url: str = None, tiktok_url: str = None) -> None:
    data = await api.hybrid_parsing(douyin_url)

    # tiktok_hybrid_data = await api.hybrid_parsing(tiktok_url)

    print(data.get('video_data').get('nwm_video_url_HQ'))





if __name__ == '__main__':
    api = Scraper()

    douyin_url = 'https://v.douyin.com/rLyrQxA/6.66'
    tiktok_url = 'https://vt.tiktok.com/ZSRwWXtdr/'
    asyncio.run(async_test(douyin_url=douyin_url, tiktok_url=tiktok_url))


