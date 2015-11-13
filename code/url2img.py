import urllib.request
import os


def url2img(folder_name, img_name, img_url):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    full_name = folder_name + '/' + img_name + ".jpg"
    try:
        print(full_name)
    except:
        print("the actor name is unprintable")
    urllib.request.urlretrieve(img_url, full_name)

