from httpx import get
import os
from selectolax.parser import HTMLParser
import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s"
                    )

def get_img_tags_for(term=None):
    url = f"https://unsplash.com/s/photos/{term}"
    resp = get(url)
    
    if resp.status_code != 200:
        raise Exception("Error getting response")
    
    tree = HTMLParser(resp.text)
    imgs = tree.css("figure a img")
    return imgs

def img_filter_out(url: str, keywords: list) -> bool:
    return not any(keyword in url for keyword in keywords)

def get_high_res_img_url(img_node):
    srcset = img_node.attrs.get("srcset")
    if srcset:
        srcset_list = srcset.split(",")
        url_res = [src.split(" ") for src in srcset_list if img_filter_out(src, ['plus', 'profile', 'premium'])]
        if url_res:
            return url_res[0][0].split("?")[0]
    
    # Fallback to src attribute if srcset is not present
    src = img_node.attrs.get("src")
    if src and img_filter_out(src, ['plus', 'profile', 'premium']):
        return src.split("?")[0]
    
    return None

def save_images(img_urls, dest_dir="images", tag=""):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    for url in img_urls:
        try:
            resp = get(url)
            resp.raise_for_status()  # Check if request was successful
            logging.info(f"Downloading {url}...")
            
            file_name = url.split("/")[-1].split("?")[0]  # Extract filename and remove query params
            file_name = f"{tag}{file_name}"  # Add tag to filename
            
            # Extract and append file extension from URL if available
            if '.' not in file_name:
                file_name += ".jpeg"
            
            with open(os.path.join(dest_dir, file_name), "wb") as f:
                f.write(resp.content)
            logging.info(f"Saved {file_name}, with size {round(len(resp.content)/1024/1024,2)} MB.")
        
        except Exception as e:
            print(f"Failed to download {url}. Reason: {e}")

if __name__ == '__main__':
    search_tag = "mountain"
    dest_dir = "mountains"
    
    img_nodes = get_img_tags_for(search_tag)
    all_img_urls = [get_high_res_img_url(i) for i in img_nodes]
    img_urls = [u for u in all_img_urls if u]
    
    save_images(img_urls, dest_dir, search_tag)
