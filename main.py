import os
import time
import requests
from threading import Thread


class VkGroupParser:
    def __init__(self):
        # getting data from files
        with open('./in/vk_group_ids.txt', 'r', encoding='utf-8') as file:
            self.group_ids = [x for x in file.read().split('\n') if x]
        with open('./in/vk_token.txt', 'r', encoding='utf-8') as file:
            self.token = file.read().split('\n')[0]

        self.videos_names = []
        self.videos_links = []

        self.threads_count = 10
        self.counts_of_videos_pages = 10

    def parse(self, owner_id):
        # parse vk.com wall
        self.links = []
        print(f'parsing group {owner_id}')
        wall = requests.get('https://api.vk.com/method/wall.get', params={'access_token': self.token,
                                                                          'v': '5.103',
                                                                          'owner_id': owner_id,
                                                                          }).json()
        ct = wall['response']['count'] // 100 + 1
        print(wall['response']['count'])
        offset = 0
        count = 100
        for x in range(ct)[:self.counts_of_videos_pages]:
            print(f"{x} of {ct}")
            wall = requests.get('https://api.vk.com/method/wall.get', params={'access_token': self.token,
                                                                              'v': '5.103',
                                                                              'owner_id': owner_id,
                                                                              'count': count,
                                                                              'offset': offset
                                                                              }).json()

            for x in wall['response']['items']:
                try:
                    for y in x['attachments']:
                        video = y['video']

                        video_id = str(video['id'])
                        video_owner_id = str(video['owner_id'])
                        video_get = requests.get('https://api.vk.com/method/video.get',
                                                 params={'access_token': self.token,
                                                         'v': '5.103',
                                                         'owner_id': video_owner_id,
                                                         'videos': video_owner_id + '_' + video_id
                                                         }).json()

                        try:
                            video_link = list(video_get['response']['items'][0]['files'].values())[-2]
                        except:
                            break
                        video_name = video_link.split('/')[-1].split('?')[0].replace('.', '_')
                        self.videos_links.append(video_link)
                        self.videos_names.append(video_name)
                        # attach_path = self.video_saver(video_link, video_name)
                except:
                    pass
            offset += 100

    def video_saver(self, url, local_filename):
        try:
            os.mkdir('out')
        except:
            pass
        if not local_filename:
            return False
        video_path = 'out\\' + local_filename + '.mp4'
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(video_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return video_path

    def download(self):
        # download videos
        try:
            os.mkdir('out')
        except:
            pass
        for thread_num in range(self.threads_count):
            thread_links = self.videos_links[thread_num::self.threads_count]
            thread_names = self.videos_names[thread_num::self.threads_count]
            Thread(target=self.downloading_thread, args=(thread_links, thread_names)).start()
            time.sleep(0.1)

    def downloading_thread(self, links, names):
        for x in links:
            print(f'downloading {links.index(x)} in {len(links)}')
            if not links:
                return False
            video_path = 'out\\' + names[links.index(x)] + '.mp4'
            with requests.get(x, stream=True) as r:
                r.raise_for_status()
                with open(video_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

    def run(self):
        for group_id in self.group_ids:
            self.parse(group_id)
            print(f'downloading {group_id}')
            self.download()


if __name__ == '__main__':
    bot = VkGroupParser()
    bot.run()