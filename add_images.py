import os
import django
import requests
from django.core.files.base import ContentFile
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_core.settings')
django.setup()

from properties_app.models import Property

IMAGE_URLS = [
    "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1000&q=80", # luxury house
    "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1000&q=80", # modern mansion
    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1000&q=80", # property interior
    "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1000&q=80", # cozy room
    "https://images.unsplash.com/photo-1600607687931-5781eb815bfa?auto=format&fit=crop&w=1000&q=80", # premium interior
    "https://images.unsplash.com/photo-1600566753086-00f18efc2294?auto=format&fit=crop&w=1000&q=80", # contemporary living
    "https://images.unsplash.com/photo-1583608205776-bfd35f0d9f83?auto=format&fit=crop&w=1000&q=80", # nice house exterior
    "https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&w=1000&q=80", # kitchen interior
    "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&w=1000&q=80", # beautiful house setting
    "https://images.unsplash.com/photo-1502672260266-1c1e52b1f41b?auto=format&fit=crop&w=1000&q=80", # apartment
]

def run():
    print("Downloading images...")
    images = []
    for i, url in enumerate(IMAGE_URLS):
        print(f"Downloading image {i+1}/{len(IMAGE_URLS)}...")
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                images.append((f"prop_img_{i}.jpg", response.content))
        except Exception as e:
            print(f"Failed to download {url}: {e}")

    if not images:
        print("No images downloaded. Exiting.")
        return

    properties = Property.objects.all()
    count = properties.count()
    print(f"Found {count} properties to update.")
    
    updated = 0
    for prop in properties:
        # If it already has an image, maybe we just overwrite or skip.
        # But user wants attractive photos for ALL properties.
        img_name, img_content = random.choice(images)
        prop.image.save(f"{prop.id}_{img_name}", ContentFile(img_content), save=True)
        updated += 1
        if updated % 50 == 0:
            print(f"Updated {updated}/{count} properties...")

    print("Successfully added attractive photos to all properties.")

if __name__ == "__main__":
    run()
