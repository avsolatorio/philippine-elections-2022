import json
from pathlib import Path

import requests
import brotli
from joblib import Parallel, delayed

from headers import HEADERS


DATA_DIR = Path("__file__").parent / "data"
DATA_DIR.mkdir(exist_ok=True)

BASE_URL = "https://2022electionresults.comelec.gov.ph/data"

def get_region_url(uri):
    return f"{BASE_URL}/regions/{uri}.json"


def get_result_url(uri):
    return f"{BASE_URL}/results/{uri}.json"


def get_cache_data(url, use_cache=True):
    print(f"Getting data from {url}")

    url_path = Path(url)
    data_fname = Path(DATA_DIR, *url_path.as_posix().split("/")[-3:])
    data = None

    if use_cache:
        if data_fname.exists():
            data = json.loads(data_fname.read_text())

    if data is None:
        response = requests.get(url, headers=HEADERS)

        if response.status_code == 200:
            # data = json.loads(brotli.decompress(response.content))
            data = response.json()

            data_fname.parent.mkdir(parents=True, exist_ok=True)
            data_fname.write_text(json.dumps(data))
        else:
            if "AccessDenied" in response.text:
                print(f"AccessDenied: {url} - {response.status_code}")
                return
            else:
                raise Exception(f"Failed to fetch data from {url}. Received status code {response.status_code}")

    return data


def parallel_scrape_municipalities(c_data):
    log_region_data(c_data)  # city/municipality
    uri = c_data["url"]

    city_url = get_region_url(uri)
    city_data = get_cache_data(city_url)

    for _, b_data in city_data.get("srs", {}).items():
        log_region_data(b_data)  # barangay
        uri = b_data["url"]

        barangay_url = get_region_url(uri)
        barangay_data = get_cache_data(barangay_url)

        pps = barangay_data.get("pps", [])
        if len(barangay_data.get("srs")) == 0:
            for p in pps:
                vbs = p.get("vbs", [])
                for v in vbs:
                    result_url = get_result_url(v["url"])
                    get_cache_data(result_url)


def log_region_data(data):
    print(f'{data["can"]}\t{data["rn"]}')


if __name__ == "__main__":

    country_url = get_region_url("44/44021")
    country_data = get_cache_data(country_url)


    with Parallel(n_jobs=5) as parallel:
        for _, r_data in country_data.get("srs", {}).items():
            log_region_data(r_data)
            uri = r_data["url"]  # region

            region_url = get_region_url(uri)
            region_data = get_cache_data(region_url)

            for _, p_data in region_data.get("srs", {}).items():
                log_region_data(p_data)
                uri = p_data["url"]  # province

                province_url = get_region_url(uri)
                province_data = get_cache_data(province_url)

                parallel(delayed(parallel_scrape_municipalities)(c_data) for _, c_data in province_data.get("srs", {}).items())
