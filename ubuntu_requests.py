import requests
import os
from urllib.parse import urlparse
import imghdr

def is_safe_to_download(url,content_type):
    #chaecks if url looks like an image
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    parsed_url=urlparse(url)
    url_path=parsed_url.path.lower()
    #checks if the url ends with an image extension
    is_image_url= any(url_path.endswith(ext) for ext in image_extensions)
    #check if content type is an image
    is_image_content= content_type.startswith('image/') if content_type else False
    return is_image_url or is_image_content

def verify_image_file(filepath):
    """Check if the downloaded file is actually an image"""
    try:
        # Use imghdr to detect the image type
        image_type = imghdr.what(filepath)
        if image_type:
            return True, image_type
        else:
            return False, "Not a recognized image format"
    except Exception as e:
        return False, f"Error verifying image: {e}"

def get_unique_filename(folder, filename):
    filepath=os.path.join(folder,filename)
    if not os.path.exists(filepath):
        return filename
    name, ext=os.path.splitext(filename)
    counter=1
    while True:
        new_filename=f"{name}_{counter}{ext}"
        if not os.path.exists(os.path.join(folder,new_filename)):
            return new_filename
        counter+=1

def download_image(url, download_folder):
    try:
        print(f"Fetching image: {url}")
        #creating a session
        session=requests.session()
        session.headers.update({'User-Agent':'Ubuntu Image Fetcher'})

        response=session.get(url, timeout=10, stream=True)
        response.raise_for_status() #raise exception for bad status codes
        #now check the content type
        content_type=response.headers.get('Content-Type','')
        if not is_safe_to_download(url,content_type):
            print(f"✗ Skipping non-image URL: {url}, Content-Type: {content_type}")
            return False
        #get the image data
        image_data=response.content
        #extract filename from url or generate one
        parsed_url=urlparse(url)
        filename=os.path.basename(parsed_url.path)

        if not filename:
            ext='.jpg' #default extension
            if content_type:
                content_map={
                    'image/jpeg':'.jpg',
                    'image/png':'.png',
                    'image/gif':'.gif',
                    'image/bmp':'.bmp',
                    'image/webp':'.webp'
                }
                ext=content_map.get(content_type.split(';')[0],'.jpg')
            filename=f"downloaded_image{ext}"
        
        # Make filename unique
        filename = get_unique_filename(download_folder, filename)
        
        #save the image
        filepath=os.path.join(download_folder,filename)
        with open(filepath, 'wb') as f:
            f.write(image_data)
        
        # VERIFY THIS IS ACTUALLY AN IMAGE FILE
        is_image, image_type = verify_image_file(filepath)
        if not is_image:
            print(f"❌ Security warning: {filename} is not a valid image file!")
            print(f"   Detected as: {image_type}")
            os.remove(filepath)  # Delete the non-image file
            print(f"   File has been deleted for security")
            return False

        print(f"✓ Successfully downloaded: {filename}")
        print(f"📁 Saved to: {filepath}")
        print(f"🖼️ Image type: {image_type}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Connection error for {url}: {e}")
        return False
    except Exception as e:
        print(f"✗ An error occurred for {url}: {e}")
        return False

def main():
    print("Welcome to the Ubuntu Image Fetcher")
    print("A tool for mindfully collecting images from the web\n")
    #make a download directory
    download_folder="Fetched_Images"
    os.makedirs(download_folder, exist_ok=True)

    # Get URL from user
    print("Please enter the image URL (one per line): ")
    print("Tip: Try these test URLs:")
    print("  - https://httpbin.org/image/jpeg (Test JPEG)")
    print("  - https://httpbin.org/image/png (Test PNG)")
    print("  - https://httpbin.org/image/webp (Test WebP)")
    
    urls=[]
    while True:
        url=input().strip()
        if not url:
            break
        urls.append(url)
    
    if not urls:
        print("No URLs provided. Exiting.")
        return
    
    successful = 0
    for url in urls:
        if download_image(url,download_folder):
            successful += 1
    
    print(f"\nDownload completed! {successful}/{len(urls)} images downloaded successfully.")

if __name__ == "__main__":
    main()