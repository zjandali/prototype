# -*- coding: utf-8 -*-

### Needs to be run in a torch env

from m3inference import M3Inference,M3Twitter,preprocess,get_lang
import regex as re
import urllib.request
import os
from db import db, user_collection



def tranform_profile_m3(id_, url_raw, path):
    url = re.sub("_normal","",url_raw)
    try:
        urllib.request.urlretrieve(url, f"{path}/{id_}.jpg")
        preprocess.resize_img(f"{path}/{id_}.jpg", f"{path}/{id_}(2).jpg",force=True)
        return True
    except:
        print(url, "url not found! break!")
        return False

def prepare_json_m3(user, path="static/tag_m3"):
    id_ = user["userID"]
    url = user["profile_image_url"]
    img = tranform_profile_m3(id_, url, path)

    pre_json = {
        "description": user["description"],
        "id": id_,
        'lang': get_lang(user["description"]),
        "name": user["name"],
        "screen_name": user["screenName"]
    }
    if img:
        pre_json["img_path"] =  f"{path}/{id_}(2).jpg"
    
    return pre_json, img


def clear_space(path):
    for file in os.listdir(path):
        if file.endswith(".jpg"):
            os.remove(f"{path}/{file}")

def update_m3(pred_list, collection):
    for (id_, value) in pred_list:
        collection.update_one(
            {"userID": id_},
            { "$set": {"org": value["org"]["is-org"]}}
        )

def predict_m3(users, path="static/tag_m3", batch_size=100, collection=db[user_collection]):
    multiple = len(users) // 100 + 1
    for i in range(1,multiple+1):
        print(f"Multiple: {i}")
        clear_space(path)
        text_based_json = []
        img_based_json = []
        for j in range((i-1)*batch_size,i*batch_size):
            if j < len(users):
                user = users[j]
                pre_json, img = prepare_json_m3(user, path)
                if img:
                    img_based_json.append(pre_json)
                else:
                    text_based_json.append(pre_json)
            else:
                break
                print(f"Jump in the index of {j}")
        if len(img_based_json):
            m3_img = M3Inference()
            pred = m3_img.infer(img_based_json)
            pred_list = list(zip(pred.keys(), pred.values()))
            update_m3(pred_list, collection)
        if len(text_based_json):
            m3_text = M3Inference(use_full_model=False)
            pred2 = m3_text.infer(text_based_json)
            pred_list2 = list(zip(pred2.keys(), pred2.values()))
            update_m3(pred_list2, collection)




users = db[user_collection].find(
  				{"org":{"$exists": False}}
		)
users = [user for user in users]
predict_m3(users, path="/content/pics", batch_size=100)