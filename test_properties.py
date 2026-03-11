from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from properties_app.models import Property

def run_test():
    client = Client(SERVER_NAME='localhost')
    # Create test users
    seller, _ = User.objects.get_or_create(username='seller_test', email='seller@test.com')
    buyer, _ = User.objects.get_or_create(username='buyer_test', email='buyer@test.com')
    
    # Create test property
    prop, _ = Property.objects.get_or_create(
        title='Test Video Call Property',
        seller_email='seller@test.com',
        price=1000000,
        sqft=1000,
        city='Mumbai',
        state='MH',
        pincode='400001'
    )
    
    try:
        # Test unauthenticated access (redirects to login due to @login_required in video_call_property)
        # The property page should not have video_call_property
        response = client.get(reverse('properties'))
        html = response.content.decode()
        assert 'video_call_property' not in html, "Unauthenticated user should not see video call button"
        
        # Login as buyer
        client.force_login(buyer)
        
        # Test authenticated access to properties list
        response = client.get(reverse('properties') + '?q=Test Video Call Property')
        html = response.content.decode()
        assert 'video_call_property' in html, "Authenticated user should see video call button"
        
        # Test the redirect view
        response = client.get(reverse('video_call_property', args=[prop.id]))
        # should be a redirect to video_call_room
        assert response.status_code == 302, f"Expected 302 redirect, got {response.status_code}"
        
        expected_room_name = f"{min(buyer.id, seller.id)}_{max(buyer.id, seller.id)}"
        expected_url = reverse('video_call_room', args=[expected_room_name])
        assert response.url == expected_url, f"Expected redirect to {expected_url}, got {response.url}"
        
        print("All tests passed successfully!")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("TEST FAILED WITH EXCEPTION")


run_test()
