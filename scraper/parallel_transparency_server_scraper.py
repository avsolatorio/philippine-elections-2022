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
                return {}
            else:
                raise Exception(f"Failed to fetch data from {url}. Received status code {response.status_code}")

    return data


def parallel_scrape_municipalities(c_data, r_name, p_name):
    c_name = get_data_name(c_data)
    log_data_name(r_name, p_name, c_name)

    uri = c_data["url"]  # city/municipality

    city_url = get_region_url(uri)
    city_data = get_cache_data(city_url)

    for _, b_data in city_data.get("srs", {}).items():
        b_name = get_data_name(b_data)
        log_data_name(r_name, p_name, c_name, b_name)

        uri = b_data["url"]  # barangay

        barangay_url = get_region_url(uri)
        barangay_data = get_cache_data(barangay_url)

        pps = barangay_data.get("pps", [])
        if len(barangay_data.get("srs")) == 0:
            for p in pps:
                vbs = p.get("vbs", [])
                for v in vbs:
                    result_url = get_result_url(v["url"])
                    get_cache_data(result_url)


def get_data_name(data):
    return f'{data["can"]}::{data["rn"]}'


def log_region_data(data):
    print(get_data_name(data))


def log_data_name(*args):
    print("\t".join(args))


if __name__ == "__main__":

    country_url = get_region_url("44/44021")
    country_data = get_cache_data(country_url)

    with Parallel(n_jobs=100) as parallel:
        for _, r_data in country_data.get("srs", {}).items():
            r_name = get_data_name(r_data)
            log_data_name(r_name)

            uri = r_data["url"]  # region

            region_url = get_region_url(uri)
            region_data = get_cache_data(region_url)

            for _, p_data in region_data.get("srs", {}).items():
                p_name = get_data_name(p_data)
                log_data_name(r_name, p_name)

                uri = p_data["url"]  # province

                province_url = get_region_url(uri)
                province_data = get_cache_data(province_url)

                parallel(delayed(parallel_scrape_municipalities)(c_data, r_name, p_name) for _, c_data in province_data.get("srs", {}).items())
