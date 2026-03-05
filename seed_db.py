import os
import django
import random
import urllib.request
from tempfile import NamedTemporaryFile

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "real_estate_core.settings")
django.setup()

from django.contrib.auth.models import User
from properties_app.models import Property
from django.core.files import File

# Create dummy user
admin_user, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com'})
if not admin_user.password:
    admin_user.set_password('admin@123')
    admin_user.save()

print("Clearing database...")
Property.objects.all().delete()

cities = [
    ('Bangalore', 'Karnataka', 12.9716, 77.5946, 5000, 15000),
    ('Mysore', 'Karnataka', 12.2958, 76.6394, 3000, 8000),
    ('Mandya', 'Karnataka', 12.5218, 76.8951, 2000, 5000),
]

property_types = ['house', 'apartment', 'plot', 'commercial', 'pg']
property_status = ['available', 'sold', 'rented']
titles = [
    "Luxury {} in {}",
    "Modern {} in prime {}",
    "Spacious {} setup in {}",
    "Budget-friendly {} in {}",
    "Premium {} available in {}"
]
descriptions = [
    "Exceptional property featuring open layouts, great natural light, and modern amenities.",
    "Located in a prime neighborhood with excellent access to public transit and local markets.",
    "Perfect for families looking for a peaceful environment with beautifully landscaped surroundings.",
    "A stunning investment opportunity. High yield potential and great community features."
]

print("Downloading 5 base images to reuse...")
image_files = []
# Using some placeholder architecture seeds
urls = [
    "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1448630360428-65456885c650?auto=format&fit=crop&w=800&q=80"
]

for i, url in enumerate(urls):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req)
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(res.read())
        img_temp.flush()
        image_files.append((f"house_{i}.jpg", img_temp))
    except Exception as e:
        print(f"Failed to download image {i}: {e}")

print("Generating 220 properties...")
for i in range(220):
    city_data = random.choice(cities)
    city_name, state_name, base_lat, base_lon, min_p, max_p = city_data
    
    p_type = random.choice(property_types)
    bhk = random.randint(1, 5) if p_type in ['house', 'apartment'] else 0
    sqft = random.randint(500, 5000)
    
    # Calculate price based on city avg per sqft
    price_per_sqft = random.uniform(min_p, max_p)
    price = int(sqft * price_per_sqft)
    
    # Slight coordinate variation for map pins
    lat = base_lat + random.uniform(-0.05, 0.05)
    lon = base_lon + random.uniform(-0.05, 0.05)
    
    prop = Property(
        seller_name="Admin User",
        seller_email="admin@example.com",
        seller_phone="+919876543210",
        title=random.choice(titles).format(p_type.capitalize(), city_name),
        description=random.choice(descriptions),
        property_type=p_type,
        status=random.choice(property_status),
        price=price,
        bhk=bhk,
        sqft=sqft,
        address=f"Phase {random.randint(1,5)}, Near Landmark",
        city=city_name,
        state=state_name,
        pincode=f"{random.randint(560000, 570000)}",
        latitude=lat,
        longitude=lon,
        has_parking=random.choice([True, False]),
        has_lift=random.choice([True, False]),
        has_power_backup=random.choice([True, False])
    )
    
    # Save image randomly from our 5 downloaded templates
    if image_files:
        img_name, img_temp = random.choice(image_files)
        # We need to save the model first so image field applies to the id correctly? Or we can just save with image.
        prop.image.save(f"prop_{i}_{img_name}", File(img_temp), save=False)
        
    prop.save()
    if (i+1) % 20 == 0:
        print(f"Created {i+1} properties...")

print("Seed complete.")
