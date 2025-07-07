import os
import json

from scrapers.leetcode_scraper import process_leetcode
from scrapers.codeforces_scraper import process_codeforces
from utils.normalizer import process_aggregation_of_data

def build_user_profile(leetcode_handle, codeforces_handle, user_name,group_name):
    leetcode_data = process_leetcode(leetcode_handle)
    codeforces_data = process_codeforces(codeforces_handle)
    aggregated = process_aggregation_of_data(leetcode_data, codeforces_data)

    user = {
        "username": user_name.capitalize(),
        "groupname": group_name.capitalize(),
        "data" :{
            "platforms": {
                "leetcode": leetcode_data,
                "codeforces": codeforces_data
            },
            "aggregated_data": aggregated
        }
    }

    return user  