import os
import django
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "real_estate_core.settings")
django.setup()

from properties_app.models import Property, Facility

print("Adding facilities and free vehicle status to properties...")

properties = Property.objects.all()

facility_types = [
    ("City Hospital", 0.5, 5.0),
    ("Supermarket", 0.1, 3.0),
    ("International School", 0.5, 4.0),
    ("Metro Station", 1.0, 8.0),
    ("Bus Stop", 0.2, 2.5),
    ("Public Park", 0.1, 2.0),
    ("Shopping Mall", 2.0, 10.0),
    ("Railway Station", 3.0, 15.0)
]

facilities_to_create = []
updated_count = 0

for prop in properties:
    prop.free_vehicle_facility = True
    
    # Check if they already have facilities so we don't duplicate too many times
    if prop.facilities.count() == 0:
        # Pick 3 to 5 random facilities
        num_facilities = random.randint(3, 5)
        chosen_facilities = random.sample(facility_types, num_facilities)
        
        for f_name, min_dist, max_dist in chosen_facilities:
            dist = round(random.uniform(min_dist, max_dist), 1)
            facilities_to_create.append(Facility(property=prop, name=f_name, distance_km=dist))
            
    updated_count += 1

# Bulk update free_vehicle_facility
Property.objects.bulk_update(properties, ['free_vehicle_facility'])

# Bulk create facilities
if facilities_to_create:
    Facility.objects.bulk_create(facilities_to_create)

print(f"Updated {updated_count} properties with free vehicle facility = True.")
print(f"Added {len(facilities_to_create)} new facilities.")
print("Database update complete.")
