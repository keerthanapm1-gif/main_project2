import random
import decimal
from django.core.management.base import BaseCommand
from properties_app.models import Property, Facility

class Command(BaseCommand):
    help = 'Seeds the database with additional 300 realistic property listings across India'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to seed properties...'))

        cities = [
            {'city': 'Mumbai', 'state': 'Maharashtra', 'pincode': '400001', 'lat': 18.9220, 'lng': 72.8347},
            {'city': 'Delhi', 'state': 'Delhi', 'pincode': '110001', 'lat': 28.6139, 'lng': 77.2090},
            {'city': 'Bangalore', 'state': 'Karnataka', 'pincode': '560001', 'lat': 12.9716, 'lng': 77.5946},
            {'city': 'Chennai', 'state': 'Tamil Nadu', 'pincode': '600001', 'lat': 13.0827, 'lng': 80.2707},
            {'city': 'Pune', 'state': 'Maharashtra', 'pincode': '411001', 'lat': 18.5204, 'lng': 73.8567},
            {'city': 'Hyderabad', 'state': 'Telangana', 'pincode': '500001', 'lat': 17.3850, 'lng': 78.4867},
            {'city': 'Kolkata', 'state': 'West Bengal', 'pincode': '700001', 'lat': 22.5726, 'lng': 88.3639},
            {'city': 'Ahmedabad', 'state': 'Gujarat', 'pincode': '380001', 'lat': 23.0225, 'lng': 72.5714},
            {'city': 'Surat', 'state': 'Gujarat', 'pincode': '395001', 'lat': 21.1702, 'lng': 72.8311},
            {'city': 'Jaipur', 'state': 'Rajasthan', 'pincode': '302001', 'lat': 26.9124, 'lng': 75.7873},
            {'city': 'Lucknow', 'state': 'Uttar Pradesh', 'pincode': '226001', 'lat': 26.8467, 'lng': 80.9462},
            {'city': 'Kanpur', 'state': 'Uttar Pradesh', 'pincode': '208001', 'lat': 26.4499, 'lng': 80.3319},
            {'city': 'Nagpur', 'state': 'Maharashtra', 'pincode': '440001', 'lat': 21.1458, 'lng': 79.0882},
            {'city': 'Indore', 'state': 'Madhya Pradesh', 'pincode': '452001', 'lat': 22.7196, 'lng': 75.8577},
            {'city': 'Bhopal', 'state': 'Madhya Pradesh', 'pincode': '462001', 'lat': 23.2599, 'lng': 77.4126},
            {'city': 'Patna', 'state': 'Bihar', 'pincode': '800001', 'lat': 25.5941, 'lng': 85.1376},
            {'city': 'Kochi', 'state': 'Kerala', 'pincode': '682001', 'lat': 9.9312, 'lng': 76.2673},
            {'city': 'Chandigarh', 'state': 'Chandigarh', 'pincode': '160001', 'lat': 30.7333, 'lng': 76.7794},
            {'city': 'Mysore', 'state': 'Karnataka', 'pincode': '570001', 'lat': 12.2958, 'lng': 76.6394},
            {'city': 'Mandya', 'state': 'Karnataka', 'pincode': '571401', 'lat': 12.5218, 'lng': 76.8951},
        ]
        
        property_types = ['Apartment', 'Villa', 'Independent House', 'Penthouse', 'Plot', 'Commercial Space']
        adjectives = ['Luxury', 'Spacious', 'Modern', 'Elegant', 'Cozy', 'Premium', 'Beautiful', 'Affordable', 'Newly Built', 'Furnished']
        
        facilities_pool = ['Hospital', 'International School', 'Supermarket', 'Metro Station', 'Park', 'Gym', 'Mall', 'Bus Stop', 'Airport', 'Railway Station']
        
        names = ['Rajesh Kumar', 'Priya Sharma', 'Amit Patel', 'Sneha Gupta', 'Vikram Singh', 'Ananya Desai', 'Rahul Reddy', 'Neha Singh', 'Karan Johar', 'Aarti Chabria']
        
        properties_to_create = []
        for i in range(300):
            city_data = random.choice(cities)
            bhk = random.choice([1, 2, 3, 4])
            prop_type = random.choice(property_types)
            adj = random.choice(adjectives)
            
            title = f"{adj} {bhk} BHK {prop_type} in {city_data['city']}"
            description = f"A beautiful {bhk} BHK {prop_type} located in the heart of {city_data['city']}. Features spacious rooms, excellent ventilation, and premium fittings. Perfect for a modern family or business."
            
            # Price between 15 Lakhs to 10 Crores
            price_lakhs = random.randint(15, 1000)
            price = decimal.Decimal(price_lakhs * 100000)
            
            sqft = bhk * random.randint(400, 600) + random.randint(100, 400)
            if prop_type == 'Plot' or prop_type == 'Commercial Space':
                bhk = 1 # Fallback
                sqft = random.randint(1000, 5000)
            
            # slight jitter to coordinates
            lat = decimal.Decimal(city_data['lat']) + decimal.Decimal(random.uniform(-0.1, 0.1))
            lng = decimal.Decimal(city_data['lng']) + decimal.Decimal(random.uniform(-0.1, 0.1))
            
            # random status
            status = random.choice(['available', 'available', 'available', 'sold', 'rented'])
            
            prop = Property(
                title=title,
                description=description,
                price=price,
                bhk=bhk,
                sqft=sqft,
                address=f"{random.randint(1, 150)}, {random.choice(['Main Road', 'Cross', 'Avenue', 'Street'])}, {city_data['city']}",
                city=city_data['city'],
                state=city_data['state'],
                pincode=city_data['pincode'],
                latitude=lat,
                longitude=lng,
                seller_name=random.choice(names),
                seller_phone=f"+91 98{random.randint(10000000, 99999999)}",
                seller_email=f"seller{i+random.randint(100, 999)}@example.com",
                property_type=prop_type.lower().replace(' ', '_'),
                status=status,
                has_lift=random.choice([True, False, True]),
                has_parking=random.choice([True, True, False]),
                has_power_backup=random.choice([True, False]),
                free_vehicle_facility=random.choice([True, False])
            )
            
            # map property types back to choices in model
            if prop.property_type not in [c[0] for c in Property.PROPERTY_TYPE_CHOICES]:
                if 'house' in prop.property_type or 'villa' in prop.property_type:
                    prop.property_type = 'house'
                elif 'apartment' in prop.property_type or 'penthouse' in prop.property_type:
                    prop.property_type = 'apartment'
                elif 'plot' in prop.property_type:
                    prop.property_type = 'plot'
                elif 'commercial' in prop.property_type:
                    prop.property_type = 'commercial'
                else:
                    prop.property_type = 'house'
            
            properties_to_create.append(prop)
        
        # Bulk create properties
        created_properties = Property.objects.bulk_create(properties_to_create)
        self.stdout.write(self.style.SUCCESS('Successfully created 300 properties.'))
        
        # Add facilities only to the newly created properties
        facilities_to_create = []
        for prop in created_properties:
            num_facilities = random.randint(3, 6)
            facs = random.sample(facilities_pool, num_facilities)
            for fac in facs:
                dist = decimal.Decimal(random.uniform(0.5, 8.0)).quantize(decimal.Decimal('0.00'))
                facilities_to_create.append(Facility(property=prop, name=fac, distance_km=dist))
        
        Facility.objects.bulk_create(facilities_to_create)
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(facilities_to_create)} facilities for the new properties.'))
