import json
import os
import sys
from pathlib import Path
from urllib.parse import urljoin
import glob
import pystac
import time
import requests

print("======================================")
workingdir = Path(__file__).parent.absolute()

stacCatalogdata = workingdir.parent / "testdata" / "stacCatalog" / "TREE STRESS COLLECTION"
catalog_file = "/app/testdata/stacCatalog/TREE STRESS COLLECTION/catalog.json"
# catalog_file = "/Users/revanth/PycharmProjects/stac-fastapi-pgstac/testdata/stacCatalog/TREE STRESS COLLECTION/catalog.json"


app_host = sys.argv[1]
# app_host  = "http://0.0.0.0:8080"

if not app_host:
    raise Exception("You must include full path/port to stac instance")


def post_or_put(url: str, data: dict):
    """Post or put data to url."""
    r = requests.post(url, json=data)
    if r.status_code == 409:
        new_url = url + f"/{data['id']}"
        # Exists, so update
        r = requests.put(new_url, json=data)
        # Unchanged may throw a 404
        if not r.status_code == 404:
            r.raise_for_status()
    else:
        r.raise_for_status()


def load_collection(collection_data: dict, app_host: str):
    # Post or update the collection to the STAC API
    print(urljoin(app_host, "/collections"))
    post_or_put(urljoin(app_host, "/collections"), collection_data)


def load_feature(feature_data: dict, app_host: str, collection_id: str):
    # Post or update the collection to the STAC API
    print("==============LOAD FEATURE TRIGGERED =================")
    print(f"collection_data['id]' = {collection_id}")
    post_or_put(urljoin(app_host, f"collections/{collection_id}/items"), feature_data)


# Function to recursively ingest collections and their items
def ingest_catalog(catalog_file):

    catalog = pystac.Catalog.from_file(catalog_file)

    # Recursively ingest sub-collections
    for provider_collection in catalog.get_children():
        # Update links to point to the API endpoints instead of static JSON files
        APP_HOST = "http://0.0.0.0:8082"

        # PART-1
        # for link in provider_collection.links:
        #     if link.rel == "child":
        #         child_id = link.target.split('/')[-2]
        #         # link.target = f"{APP_HOST}/collections/{child_id}"
        #         print(link.target)
        #
        # load_collection(provider_collection.to_dict(), app_host)
        # print(f"Loaded Provider collection: {provider_collection.id}")

        # PART-2
        for cell_collection in provider_collection.get_children():
            # Update links to point to the API endpoints instead of static JSON files
            for link in cell_collection.links:
                if link.rel == "child":
                    child_id = link.target.split('/')[-2]
                    # link.target = f"{APP_HOST}/collections/{child_id}"
            load_collection(cell_collection.to_dict(), app_host)
            print(f"Loaded Cell collection: {cell_collection.id}")


            for item in cell_collection.get_all_items():
                load_feature(item.to_dict(), app_host, cell_collection.id)
                print(f"Loaded Feature item: {item.id}")




if __name__ == "__main__":
    ingest_catalog(catalog_file)
