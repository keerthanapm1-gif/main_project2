from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from .models import Property, Wishlist, PropertyReview, Inquiry, Lease, PaymentSplit, TaxReport, SavedSearch, RecentlyViewed
from .forms import UserRegistrationForm, PropertyReviewForm, InquiryForm
from .recommendation_service import RecommendationEngine

def home(request):
    latest_properties = Property.objects.order_by('-created_at')[:6]
    total_properties = Property.objects.count()
    # City stats for popular cities section
    city_stats = Property.objects.values('city').annotate(count=Count('id')).order_by('-count')[:8]
    for_sale_count = Property.objects.filter(status='available').count()
    rented_count = Property.objects.filter(status='rented').count()
    # Trending: top 4 most viewed properties
    trending_properties = Property.objects.order_by('-view_count')[:4]
    
    # Personalized Recommendations
    recommendation_engine = RecommendationEngine(request.user)
    recommended_properties = recommendation_engine.get_recommendations(limit=6)

    wishlisted_property_ids = []
    if request.user.is_authenticated:
        wishlisted_property_ids = list(Wishlist.objects.filter(user=request.user).values_list('property_id', flat=True))

    context = {
        'properties': latest_properties,
        'total_properties': total_properties,
        'city_stats': city_stats,
        'for_sale_count': for_sale_count,
        'rented_count': rented_count,
        'trending_properties': trending_properties,
        'recommended_properties': recommended_properties,
        'wishlisted_property_ids': wishlisted_property_ids,
    }
    return render(request, 'home.html', context)

def properties_list(request):
    property_list = Property.objects.all().order_by('-created_at')
    
    # 1. Text Search (City or Title)
    query = request.GET.get('q')
    if query:
        property_list = property_list.filter(city__icontains=query) | property_list.filter(title__icontains=query)
        
    # 2. Dropdown Filters
    prop_type = request.GET.get('type')
    if prop_type:
        property_list = property_list.filter(property_type=prop_type)
        
    status = request.GET.get('status')
    if status:
        property_list = property_list.filter(status=status)
        
    bhk = request.GET.get('bhk')
    if bhk:
        property_list = property_list.filter(bhk=bhk)
        
    # 3. Price Range Filters
    min_price = request.GET.get('min_price')
    if min_price and min_price.isdigit():
        property_list = property_list.filter(price__gte=min_price)
        
    max_price = request.GET.get('max_price')
    if max_price and max_price.isdigit():
        property_list = property_list.filter(price__lte=max_price)
        
    # 4. Amenities (Booleans)
    if 'has_parking' in request.GET:
        property_list = property_list.filter(has_parking=True)
    if 'has_lift' in request.GET:
        property_list = property_list.filter(has_lift=True)
    if 'has_power_backup' in request.GET:
        property_list = property_list.filter(has_power_backup=True)
    if 'free_vehicle_facility' in request.GET:
        property_list = property_list.filter(free_vehicle_facility=True)

    # 5. New Field Filters
    furnished = request.GET.get('furnished')
    if furnished:
        property_list = property_list.filter(furnished_status=furnished)
        
    facing = request.GET.get('facing')
    if facing:
        property_list = property_list.filter(facing=facing)

    # 5. Sorting
    sort_by = request.GET.get('sort')
    if sort_by == 'price_low':
        property_list = property_list.order_by('price')
    elif sort_by == 'price_high':
        property_list = property_list.order_by('-price')
    elif sort_by == 'popular':
        property_list = property_list.order_by('-view_count')
    elif sort_by == 'oldest':
        property_list = property_list.order_by('created_at')
    else:
        property_list = property_list.order_by('-created_at') # Default newest

    paginator = Paginator(property_list, 10) # 10 properties per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    wishlisted_property_ids = []
    if request.user.is_authenticated:
        wishlisted_property_ids = list(Wishlist.objects.filter(user=request.user).values_list('property_id', flat=True))

    context = {
        'page_obj': page_obj, 
        'query': query,
        'current_filters': request.GET,
        'wishlisted_property_ids': wishlisted_property_ids,
    }
    return render(request, 'properties.html', context)

def property_detail(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    
    # Increment view count
    prop.view_count += 1
    # Save only the view_count field to prevent triggering price history loops accidentally
    prop.save(update_fields=['view_count'])
    
    # Wishlist status
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, property=prop).exists()
        # Record recently viewed
        RecentlyViewed.objects.update_or_create(
            user=request.user, 
            property=prop
        )
        
    review_form = PropertyReviewForm()
    reviews = prop.reviews.all().order_by('-created_at')
    
    # Phase 5: AI Recommendations (Heuristic based on city/bhk)
    recommended_properties = Property.objects.filter(
        Q(city__iexact=prop.city) | Q(bhk=prop.bhk)
    ).exclude(id=prop.id).order_by('?')[:3]

    from django.contrib.auth.models import User
    seller_user = User.objects.filter(email=prop.seller_email).first()

    video_room_name = None
    if request.user.is_authenticated and seller_user and seller_user != request.user:
        min_id = min(request.user.id, seller_user.id)
        max_id = max(request.user.id, seller_user.id)
        video_room_name = f"{min_id}_{max_id}"

    context = {
        'property': prop,
        'in_wishlist': in_wishlist,
        'review_form': review_form,
        'reviews': reviews,
        'recommended_properties': recommended_properties,
        'seller_user': seller_user,
        'video_room_name': video_room_name,
    }
    
    return render(request, 'property_detail.html', context)

def about(request):
    return render(request, 'about.html')

def contact_us(request):
    if request.method == 'POST':
        form = InquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            if request.user.is_authenticated:
                inquiry.user = request.user
            inquiry.save()
            messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
            return redirect('contact_us')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = InquiryForm()
    
    return render(request, 'contact_us.html', {'form': form})

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Save the selected role
            role = form.cleaned_data.get('role', 'user')
            user.profile.role = role
            user.profile.save()
            
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_user(request):
    logout(request)
    messages.info(request, 'You have successfully logged out.')
    return redirect('home')

@login_required
def toggle_wishlist(request, property_id):
    if request.method == 'POST':
        prop = get_object_or_404(Property, pk=property_id)
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, property=prop)
        if not created:
            wishlist_item.delete()
            return JsonResponse({'status': 'removed'})
        return JsonResponse({'status': 'added'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('property')
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def add_review(request, property_id):
    prop = get_object_or_404(Property, pk=property_id)
    if request.method == 'POST':
        form = PropertyReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.property = prop
            review.user = request.user
            review.save()
            messages.success(request, 'Review added successfully!')
        else:
            messages.error(request, 'Error adding review.')
    return redirect('property_detail', pk=property_id)

def contact_seller(request, property_id):
    prop = get_object_or_404(Property, pk=property_id)
    if request.method == 'POST':
        form = InquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.property = prop
            if request.user.is_authenticated:
                inquiry.user = request.user
            inquiry.save()
            
            if inquiry.inquiry_type == 'whatsapp':
                text = f"Hi, I am interested in your property: {prop.title}. My name is {inquiry.name}."
                import urllib.parse
                encoded_text = urllib.parse.quote(text)
                whatsapp_url = f"https://wa.me/{prop.seller_phone}?text={encoded_text}"
                return redirect(whatsapp_url)
            else:
                messages.success(request, 'Inquiry sent successfully! The seller will contact you soon.')
                return redirect('property_detail', pk=property_id)
        else:
            messages.error(request, 'Please correct the errors in the form.')
    return redirect('property_detail', pk=property_id)


import json
from .models import ChatMessage
from django.contrib.auth.models import User

@login_required
def chat_list(request):
    sent_messages = ChatMessage.objects.filter(sender=request.user)
    received_messages = ChatMessage.objects.filter(receiver=request.user)
    
    users_chatted_with = set()
    for msg in sent_messages:
        users_chatted_with.add(msg.receiver)
    for msg in received_messages:
        users_chatted_with.add(msg.sender)
        
    context = {
        'users_chatted_with': users_chatted_with
    }
    return render(request, 'chat_list.html', context)

@login_required
def chat_detail(request, user_id):
    other_user = get_object_or_404(User, pk=user_id)
    
    messages = ChatMessage.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).order_by('timestamp')
    
    ChatMessage.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)
    
    # Generate a unique video room name
    min_id = min(request.user.id, other_user.id)
    max_id = max(request.user.id, other_user.id)
    video_room_name = f"{min_id}_{max_id}"
    
    context = {
        'other_user': other_user,
        'chat_messages': messages,
        'video_room_name': video_room_name,
    }
    return render(request, 'chat_detail.html', context)

@login_required
def send_message(request):
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver_id')
        message_text = request.POST.get('message')
        
        if not receiver_id or not message_text:
            return JsonResponse({'error': 'Missing data'}, status=400)
            
        receiver = get_object_or_404(User, pk=receiver_id)
        
        msg = ChatMessage.objects.create(
            sender=request.user,
            receiver=receiver,
            message=message_text
        )
        
        return JsonResponse({
            'status': 'success',
            'message': msg.message,
            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'sender_id': msg.sender.id,
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def fetch_messages(request, user_id):
    other_user = get_object_or_404(User, pk=user_id)
    last_timestamp = request.GET.get('last_timestamp')
    
    messages_query = ChatMessage.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    )
    
    if last_timestamp:
        pass # Note: In production you would filter, but for simplicitly we return unread messages
        messages_query = messages_query.filter(is_read=False, receiver=request.user)
            
    messages_query = messages_query.order_by('timestamp')
    
    messages_data = []
    for msg in messages_query:
        if last_timestamp and msg.is_read: # skip if we are just fetching unread and this one is read (simplification)
            pass
        messages_data.append({
            'message': msg.message,
            'timestamp': msg.timestamp.isoformat(),
            'sender_id': msg.sender.id,
            'is_read': msg.is_read
        })
        
    ChatMessage.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)
    
    return JsonResponse({'messages': messages_data})

@login_required
def video_call_room(request, room_name):
    # Pass user details to the template to join the room
    context = {
        'room_name': room_name,
        'user_name': request.user.username,
        'user_email': request.user.email,
    }
    return render(request, 'video_call.html', context)

@login_required
def video_call_property(request, property_id):
    prop = get_object_or_404(Property, id=property_id)
    from django.contrib.auth.models import User
    seller_user = User.objects.filter(email=prop.seller_email).first()
    
    if not seller_user or seller_user == request.user:
        messages.error(request, "Cannot initiate video call with this seller.")
        return redirect('property_detail', pk=property_id)
        
    min_id = min(request.user.id, seller_user.id)
    max_id = max(request.user.id, seller_user.id)
    room_name = f"{min_id}_{max_id}"
    
    return redirect('video_call_room', room_name=room_name)

import re
from django.db.models import Q

def chatbot_api(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '').lower().strip()
        
        # 1. Price Query Extraction (e.g., "under 50 lakhs", "below 1 crore")
        price_limit = None
        # Pattern to match "under/below/less than <number> lakhs/crores"
        price_match = re.search(r'(?:under|below|less than|within|budget of)\s*(?:rs\.?|inr)?\s*([\d\.]+)\s*(lakh|crore|cr|l|k)?', user_message)
        
        if price_match:
            try:
                value = float(price_match.group(1))
                unit = price_match.group(2)
                if unit in ['lakh', 'l']:
                    price_limit = value * 100000
                elif unit in ['crore', 'cr']:
                    price_limit = value * 10000000
                elif unit == 'k':
                    price_limit = value * 1000
                else:
                    # Assume lakhs if it's a small number, otherwise raw
                    if value < 500:
                        price_limit = value * 100000
                    else:
                        price_limit = value
            except:
                pass

        # 2. BHK Extraction (e.g., "2bhk", "3 bhk")
        bhk_count = None
        bhk_match = re.search(r'(\d)\s*bhk', user_message)
        if bhk_match:
            bhk_count = int(bhk_match.group(1))

        # 3. City Extraction
        # Get all unique cities from database to match against the query
        known_cities = list(Property.objects.values_list('city', flat=True).distinct())
        target_city = None
        for city in known_cities:
            if city.lower() in user_message:
                target_city = city
                break
        
        # If no city match found in DB, look for common city keywords as fallback
        if not target_city:
            common_cities = ['mumbai', 'delhi', 'bangalore', 'chennai', 'pune', 'hyderabad', 'kolkata', 'gurgaon', 'noida']
            for city in common_cities:
                if city in user_message:
                    target_city = city
                    break

        # 4. Location/IT Park Query Extraction
        it_park_query = False
        if 'it park' in user_message or 'tech park' in user_message or 'office' in user_message or 'work' in user_message:
            it_park_query = True

        # 3. Formulate Database Query
        properties = Property.objects.filter(status='available')
        triggered_query = False
        
        if price_limit:
            properties = properties.filter(price__lte=price_limit)
            triggered_query = True
        
        if bhk_count:
            properties = properties.filter(bhk=bhk_count)
            triggered_query = True
            
        if target_city:
            properties = properties.filter(city__icontains=target_city)
            triggered_query = True
        
        if it_park_query:
            # Search in title, description, address, or near facilities
            properties = properties.filter(
                Q(description__icontains='IT Park') | 
                Q(address__icontains='IT Park') |
                Q(city__icontains='IT Park') |
                Q(facilities__name__icontains='IT Park')
            ).distinct()
            triggered_query = True
        
        # Handle "best" or "top" keywords
        is_best = 'best' in user_message or 'top' in user_message or 'good' in user_message
        if is_best:
            triggered_query = True

        # Generate Response
        if triggered_query:
            recommended = properties.order_by('-view_count')[:3]
            if recommended.exists():
                response_text = f"I found {properties.count()} properties matching your request. Here are the top picks:"
                props_data = []
                for p in recommended:
                    props_data.append({
                        'id': p.id,
                        'title': p.title,
                        'price': f"₹{int(p.price):,}",
                        'city': p.city,
                        'bhk': p.bhk,
                        'property_type': p.get_property_type_display(),
                        'status': p.get_status_display(),
                        'image': p.image.url if p.image else None,
                        'url': f"/properties/{p.id}/"
                    })
                return JsonResponse({
                    'response': response_text,
                    'properties': props_data
                })
            else:
                response_text = "I couldn't find any properties matching those exact criteria. Try adjusting your budget or location!"
        
        # 4. General Fallback Logic
        if 'hello' in user_message or 'hi' in user_message:
            response = "Hello! Welcome to Luxia Real Estate. How can I help you today? Try asking for houses under a budget or near IT parks!"
        elif 'price' in user_message or 'cost' in user_message:
            response = "Property prices vary by location. For example, you can ask 'Best house under 60 lakhs'!"
        elif 'location' in user_message or 'city' in user_message:
            response = "We have properties across India! Try searching for a specific city or ask about areas near IT parks."
        elif 'contact' in user_message or 'seller' in user_message:
            response = "You can contact sellers directly from property pages. Just look for the 'Chat with Seller' button."
        elif 'rent' in user_message:
            response = "Yes, we list many rental properties. Use the 'Status' filter on our properties page to see what's available."
        else:
            response = "I'm the Luxia Assistant. I can help you find homes by budget (e.g., 'under 50 lakhs') or near IT parks. How can I assist you?"
            
        return JsonResponse({'response': response})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def price_estimator(request):
    """Render the price estimation UI"""
    return render(request, 'price_estimator.html')

def api_estimate_price(request):
    """Handle AJAX requests for price estimation based on heuristics."""
    if request.method == 'GET':
        city = request.GET.get('city', '').strip()
        bhk = request.GET.get('bhk')
        area = request.GET.get('area')
        
        if not city or not bhk or not area:
            return JsonResponse({'error': 'Missing parameters'}, status=400)
            
        try:
            bhk = int(bhk)
            area = float(area)
        except ValueError:
            return JsonResponse({'error': 'Invalid parameters'}, status=400)
            
        # AI heuristic: find average price per sqft for similar properties in the database
        similar_properties = Property.objects.filter(city__icontains=city, bhk=bhk)
        
        if similar_properties.exists():
            total_price = sum(p.price for p in similar_properties)
            total_area = sum(p.sqft for p in similar_properties)
            if total_area > 0:
                avg_price_per_sqft = float(total_price) / float(total_area)
            else:
                avg_price_per_sqft = 8000 # default fallback
        else:
            # Fallback mock average rates if no properties match perfectly
            fallback_rates = {
                'mumbai': 25000,
                'delhi': 15000,
                'bangalore': 10000,
                'chennai': 8000,
                'pune': 7500,
            }
            # lower city string to match generic keys
            city_low = city.lower()
            avg_price_per_sqft = fallback_rates.get(city_low, 5000)
            # check subsets
            for k, v in fallback_rates.items():
                if k in city_low:
                    avg_price_per_sqft = v
                    break
        
        # Calculate estimated price
        estimated_price = avg_price_per_sqft * area
        
        # Format as INR string
        import locale
        try:
            locale.setlocale(locale.LC_ALL, 'en_IN.UTF-8')
            formatted_price = locale.currency(estimated_price, grouping=True, symbol=True)
        except locale.Error:
            formatted_price = f"₹ {estimated_price:,.2f}"
            
        # Fetch similar properties around this price point (+/- 20%)
        min_price = estimated_price * 0.8
        max_price = estimated_price * 1.2
        
        sim_props_qs = Property.objects.filter(
            city__icontains=city,
            price__gte=min_price,
            price__lte=max_price
        ).order_by('?')[:3]
        
        sim_props_data = []
        for p in sim_props_qs:
            try:
                formatted_p_price = locale.currency(p.price, grouping=True, symbol=True)
            except:
                formatted_p_price = f"₹ {p.price:,.2f}"
                
            sim_props_data.append({
                'id': p.id,
                'title': p.title,
                'city': p.city,
                'price': float(p.price),
                'formatted_price': formatted_p_price,
                'bhk': p.bhk,
                'image_url': p.image.url if p.image else '',
                'property_type': p.property_type,
                'status': p.status,
            })
            
        return JsonResponse({
            'estimated_price': formatted_price,
            'raw_value': estimated_price,
            'avg_psf': avg_price_per_sqft,
            'confidence': 'High' if similar_properties.exists() else 'Medium',
            'similar_properties': sim_props_data
        })
        
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def lease_generation(request, property_id):
    prop = get_object_or_404(Property, pk=property_id)
    
    from datetime import date, timedelta
    today = date.today()
    next_year = today.replace(year=today.year + 1)
    
    lease, created = Lease.objects.get_or_create(
        property=prop,
        tenant=request.user,
        defaults={
            'start_date': today,
            'end_date': next_year,
            'rent_amount': prop.price,
            'deposit_amount': prop.price * 2, # Example 2 months rent
            'clauses': '1. Standard strict adherence to local real estate tenancy laws.\n2. Tenant must notify landlord 30 days before vacating.\n3. Automatic rent collection enabled via escrow.'
        }
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'sign':
            lease.is_signed = True
            lease.save()
            messages.success(request, 'Lease digitally signed successfully.')
            return redirect('lease_generation', property_id=property_id)
            
    return render(request, 'lease_generation.html', {'property': prop, 'lease': lease})

@login_required
def payment_splitter(request, property_id):
    prop = get_object_or_404(Property, pk=property_id)
    leases = Lease.objects.filter(property=prop)
    payments = PaymentSplit.objects.filter(lease__in=leases).order_by('-payment_date')
    return render(request, 'payment_splitter.html', {'property': prop, 'leases': leases, 'payments': payments})

@login_required
def mock_payment_gateway(request):
    if request.method == 'POST':
        property_id = request.POST.get('property_id')
        lease_id = request.POST.get('lease_id')
        amount = request.POST.get('amount')
        is_deposit_str = request.POST.get('is_deposit', 'false')
        is_deposit = is_deposit_str == 'true'

        context = {
            'property_id': property_id,
            'lease_id': lease_id,
            'amount': amount,
            'is_deposit_str': is_deposit_str,
            'is_deposit': is_deposit,
        }
        return render(request, 'payment_gateway.html', context)
    return redirect('home')

@login_required
def process_online_payment(request):
    if request.method == 'POST':
        property_id = request.POST.get('property_id')
        lease_id = request.POST.get('lease_id')
        amount = request.POST.get('amount')
        is_deposit = request.POST.get('is_deposit') == 'true'

        if lease_id and amount:
            lease = get_object_or_404(Lease, pk=lease_id)
            PaymentSplit.objects.create(
                lease=lease,
                amount_paid=amount,
                is_deposit=is_deposit,
                status='released' if not is_deposit else 'escrow' # Online payment is considered processed
            )
            messages.success(request, 'Secure Online Payment was successful.')
            return redirect('payment_splitter', property_id=property_id)

    return redirect('home')

# ─── EMI Calculator ────────────────────────────────────────────
def emi_calculator(request):
    return render(request, 'emi_calculator.html')

# ─── Property Comparison ───────────────────────────────────────
def compare_properties(request):
    ids_param = request.GET.get('ids', '')
    ids = [i.strip() for i in ids_param.split(',') if i.strip().isdigit()]
    properties = Property.objects.filter(pk__in=ids[:3])  # Max 3
    return render(request, 'compare.html', {'properties': properties})

# ─── Post a Property ───────────────────────────────────────────
from .decorators import role_required

@login_required
@role_required(['admin', 'agent', 'user'])
def post_property(request):
    if request.method == 'POST':
        try:
            prop = Property(
                title=request.POST.get('title'),
                description=request.POST.get('description'),
                property_type=request.POST.get('property_type', 'apartment'),
                status=request.POST.get('status', 'available'),
                price=request.POST.get('price'),
                bhk=request.POST.get('bhk', 2),
                sqft=request.POST.get('sqft'),
                address=request.POST.get('address'),
                city=request.POST.get('city'),
                state=request.POST.get('state'),
                pincode=request.POST.get('pincode'),
                seller_name=request.user.get_full_name() or request.user.username,
                seller_phone=request.POST.get('seller_phone', ''),
                seller_email=request.user.email,
                survey_number=request.POST.get('survey_number', ''),
                has_parking='has_parking' in request.POST,
                has_lift='has_lift' in request.POST,
                has_power_backup='has_power_backup' in request.POST,
                free_vehicle_facility='free_vehicle_facility' in request.POST,
                offers=request.POST.get('offers', ''),
            )
            if 'image' in request.FILES:
                prop.image = request.FILES['image']
            prop.save()
            messages.success(request, 'Your property has been listed successfully!')
            return redirect('property_detail', pk=prop.pk)
        except Exception as e:
            messages.error(request, f'Error listing property: {e}')
    return render(request, 'post_property.html')


# ─── Map View ───────────────────────────────────────────────────
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on the Earth
    using the Haversine formula. Returns distance in kilometers.
    """
    R = 6371.0  # Earth radius in KM
    
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi / 2)**2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def map_view(request):
    """Render an interactive Leaflet map with all properties that have coordinates."""
    all_properties = Property.objects.all()
    properties_json = []
    
    # Track min/max for normalization
    prices = [float(p.price) for p in all_properties if p.price]
    min_price = min(prices) if prices else 0
    max_price = max(prices) if prices else 100000000

    for p in all_properties:
        lat = float(p.latitude) if p.latitude else None
        lng = float(p.longitude) if p.longitude else None
        if lat is None or lng is None:
            continue
        properties_json.append({
            'id': p.id,
            'title': p.title,
            'city': p.city,
            'price': float(p.price),
            'bhk': p.bhk,
            'sqft': p.sqft,
            'property_type': p.get_property_type_display(),
            'status': p.get_status_display(),
            'lat': lat,
            'lng': lng,
            'image_url': p.image.url if p.image else '',
        })
    import json as _json
    context = {
        'properties_json': _json.dumps(properties_json),
        'total_on_map': len(properties_json),
        'total_properties': all_properties.count(),
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'map_view.html', context)

def api_nearby_properties(request):
    """
    API endpoint to fetch properties within a given radius of a point.
    Expects GET params: lat, lng, radius (in KM, optional, default 10)
    """
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    radius = request.GET.get('radius', 10) # default 10km
    
    if not lat or not lng:
        return JsonResponse({'error': 'Missing lat or lng parameters'}, status=400)
    
    try:
        lat = float(lat)
        lng = float(lng)
        radius = float(radius)
    except ValueError:
        return JsonResponse({'error': 'Invalid lat, lng or radius parameters'}, status=400)
    
    all_props = Property.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    nearby_props = []
    
    for p in all_props:
        dist = calculate_distance(lat, lng, float(p.latitude), float(p.longitude))
        if dist <= radius:
            nearby_props.append({
                'id': p.id,
                'title': p.title,
                'price': float(p.price),
                'formatted_price': f"₹{int(p.price):,}",
                'city': p.city,
                'bhk': p.bhk,
                'sqft': p.sqft,
                'image_url': p.image.url if p.image else '',
                'distance': round(dist, 2),
                'property_type': p.get_property_type_display(),
                'url': f"/property/{p.id}/"
            })
            
    # Sort by distance
    nearby_props.sort(key=lambda x: x['distance'])
    
    return JsonResponse({
        'center': {'lat': lat, 'lng': lng},
        'radius': radius,
        'count': len(nearby_props),
        'properties': nearby_props[:10] # return top 10
    })




# ─── Seller Profile ─────────────────────────────────────────────
def seller_profile(request, seller_email):
    """Show all properties listed by a specific seller."""
    listings = Property.objects.filter(seller_email__iexact=seller_email).order_by('-created_at')
    if not listings.exists():
        messages.error(request, 'No listings found for this seller.')
        return redirect('home')
    seller_name = listings.first().seller_name
    seller_phone = listings.first().seller_phone
    avg_price = listings.aggregate(Avg('price'))['price__avg']
    context = {
        'seller_email': seller_email,
        'seller_name': seller_name,
        'seller_phone': seller_phone,
        'listings': listings,
        'total_listings': listings.count(),
        'avg_price': avg_price,
    }
    return render(request, 'seller_profile.html', context)


# ─── Save Search / Property Alerts ──────────────────────────────
@login_required
def save_search(request):
    """Save current search filters as a saved search for the user."""
    if request.method == 'POST':
        q = request.POST.get('q', '').strip()
        city = request.POST.get('city', '').strip()
        property_type = request.POST.get('property_type', '').strip()
        bhk = request.POST.get('bhk', None)
        min_price = request.POST.get('min_price', None)
        max_price = request.POST.get('max_price', None)

        if bhk and not bhk.isdigit():
            bhk = None
        if min_price and not min_price.replace('.', '', 1).isdigit():
            min_price = None
        if max_price and not max_price.replace('.', '', 1).isdigit():
            max_price = None

        SavedSearch.objects.create(
            user=request.user,
            query=q or None,
            city=city or None,
            property_type=property_type or None,
            bhk=bhk or None,
            min_price=min_price or None,
            max_price=max_price or None,
        )
        messages.success(request, '✅ Search saved! You can access it from your Saved Searches.')
    return redirect(request.POST.get('next', 'saved_searches'))


@login_required
def saved_searches(request):
    """Show the user's list of saved search alerts."""
    if request.method == 'POST' and request.POST.get('delete_id'):
        delete_id = request.POST.get('delete_id')
        SavedSearch.objects.filter(pk=delete_id, user=request.user).delete()
        messages.success(request, 'Saved search deleted.')
        return redirect('saved_searches')

    searches = SavedSearch.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'saved_searches.html', {'searches': searches})


# ─── Loan Eligibility Calculator ────────────────────────────────
def loan_eligibility(request):
    """Render the home loan eligibility calculator."""
    result = None
    if request.method == 'POST':
        try:
            monthly_salary = float(request.POST.get('monthly_salary', 0))
            tenure_years = int(request.POST.get('tenure_years', 20))
            interest_rate = float(request.POST.get('interest_rate', 8.5))
            down_payment_pct = float(request.POST.get('down_payment_pct', 20))

            # Max EMI banks allow = 40-50% of net monthly income
            max_emi = monthly_salary * 0.45

            # Calculate max loan using EMI formula: P = EMI * [(1+r)^n - 1] / [r * (1+r)^n]
            r = interest_rate / 12 / 100  # monthly rate
            n = tenure_years * 12  # months
            if r > 0:
                max_loan = max_emi * ((1 + r) ** n - 1) / (r * (1 + r) ** n)
            else:
                max_loan = max_emi * n

            # Total property value they can afford (loan + down payment)
            down_payment_decimal = down_payment_pct / 100
            affordable_property = max_loan / (1 - down_payment_decimal) if down_payment_pct < 100 else max_loan

            # Actual EMI for max loan
            if r > 0:
                emi = max_loan * r * (1 + r) ** n / ((1 + r) ** n - 1)
            else:
                emi = max_loan / n

            result = {
                'max_loan': round(max_loan),
                'max_emi': round(max_emi),
                'actual_emi': round(emi),
                'affordable_property': round(affordable_property),
                'down_payment': round(affordable_property * down_payment_decimal),
                'tenure_years': tenure_years,
                'interest_rate': interest_rate,
            }
        except Exception as e:
            messages.error(request, f'Calculation error: {e}')

    return render(request, 'loan_eligibility.html', {'result': result})

@login_required
def personalized_recommendations(request):
    """
    Dedicated page for personalized property suggestions.
    """
    engine = RecommendationEngine(request.user)
    recommendations = engine.get_recommendations(limit=12)
    
    wishlisted_property_ids = list(Wishlist.objects.filter(user=request.user).values_list('property_id', flat=True))
    
    context = {
        'recommended_properties': recommendations,
        'wishlisted_property_ids': wishlisted_property_ids,
    }
    return render(request, 'recommendations.html', context)

def location_intelligence(request):
    """Render the location intelligence UI"""
    return render(request, 'location_intelligence.html')

def api_location_intelligence(request):
    """Handle AJAX requests for price estimation based on location intelligence factors."""
    if request.method == 'GET':
        city = request.GET.get('city', '').strip()
        bhk = request.GET.get('bhk')
        area = request.GET.get('area')
        
        # New Factors
        schools = request.GET.get('schools', 0)
        hospitals = request.GET.get('hospitals', 0)
        metro_distance = request.GET.get('metro_distance', 5) # in km
        traffic_level = request.GET.get('traffic', 'medium')
        crime_rate = request.GET.get('crime', 'low')
        pollution = request.GET.get('pollution', 'moderate')
        
        if not city or not bhk or not area:
            return JsonResponse({'error': 'Missing parameters'}, status=400)
            
        try:
            bhk = int(bhk)
            area = float(area)
            schools = int(schools)
            hospitals = int(hospitals)
            metro_distance = float(metro_distance)
        except ValueError:
            return JsonResponse({'error': 'Invalid parameters'}, status=400)
            
        # Base price per sqft calculation
        similar_properties = Property.objects.filter(city__icontains=city, bhk=bhk)
        
        if similar_properties.exists():
            total_price = sum(p.price for p in similar_properties)
            total_area = sum(p.sqft for p in similar_properties)
            if total_area > 0:
                base_price_per_sqft = float(total_price) / float(total_area)
            else:
                base_price_per_sqft = 8000
        else:
            fallback_rates = {
                'mumbai': 25000,
                'delhi': 15000,
                'bangalore': 10000,
                'chennai': 8000,
                'pune': 7500,
            }
            city_low = city.lower()
            base_price_per_sqft = fallback_rates.get(city_low, 5000)
            for k, v in fallback_rates.items():
                if k in city_low:
                    base_price_per_sqft = v
                    break
        
        # Calculate base price
        base_price = base_price_per_sqft * area
        multiplier = 1.0
        
        # Apply multipliers for Location Intelligence
        # 1. Schools (Max +10%)
        multiplier += min(schools * 0.02, 0.10)
        
        # 2. Hospitals (Max +10%)
        multiplier += min(hospitals * 0.02, 0.10)
        
        # 3. Metro Distance (Closer = Better, Max +15%, Far = No change or slight decrease)
        if metro_distance <= 1.0:
            multiplier += 0.15
        elif metro_distance <= 3.0:
            multiplier += 0.05
        elif metro_distance > 10.0:
            multiplier -= 0.05
            
        # 4. Traffic Level
        if traffic_level == 'low':
            multiplier += 0.05
        elif traffic_level == 'high':
            multiplier -= 0.05
            
        # 5. Crime Rate
        if crime_rate == 'medium':
            multiplier -= 0.10
        elif crime_rate == 'high':
            multiplier -= 0.25
            
        # 6. Pollution Index
        if pollution == 'good':
            multiplier += 0.05
        elif pollution == 'poor':
            multiplier -= 0.10
        elif pollution == 'hazardous':
            multiplier -= 0.20
            
        # Final estimated price
        estimated_price = base_price * multiplier
        
        # Format price
        if estimated_price >= 10000000:
            formatted_price = f"₹ {estimated_price / 10000000:.2f} Cr"
        elif estimated_price >= 100000:
            formatted_price = f"₹ {estimated_price / 100000:.2f} Lac"
        else:
            formatted_price = f"₹ {estimated_price:,.0f}"
            
        return JsonResponse({
            'estimated_price': formatted_price,
            'base_price_formatted': f"₹ {base_price:,.0f}",
            'multiplier': f"{multiplier:.2f}x",
            'confidence': 'High' if similar_properties.count() >= 5 else ('Medium' if similar_properties.count() > 0 else 'Low')
        })

def smart_recommendation(request):
    """Render the Smart Recommendation Engine UI"""
    return render(request, 'smart_recommendation.html')

def api_smart_recommendation(request):
    """Handle AJAX requests for the smart recommendation engine."""
    if request.method == 'GET':
        budget = request.GET.get('budget')
        lifestyle = request.GET.get('lifestyle')
        family_size = request.GET.get('family_size')
        commute = request.GET.get('commute')

        if not budget or not lifestyle or not family_size or not commute:
            return JsonResponse({'error': 'Missing parameters'}, status=400)

        try:
            budget = float(budget)
            family_size = int(family_size)
            commute = float(commute)
        except ValueError:
            return JsonResponse({'error': 'Invalid parameters'}, status=400)

        # Base query
        properties = Property.objects.all()

        # 1. Budget Filter
        # Allowing properties up to the budget, and somewhat below.
        min_budget = budget * 0.5 # Example: properties not cheaper than 50% of budget
        properties = properties.filter(price__lte=budget, price__gte=min_budget)

        # 2. Family Size -> BHK Mapping
        if family_size == 1:
            properties = properties.filter(bhk__in=[1, 2])
        elif family_size == 2:
            properties = properties.filter(bhk__in=[2, 3])
        elif family_size >= 4:
            properties = properties.filter(bhk__gte=3)

        # 3. Lifestyle Mapping
        if lifestyle == 'student':
            properties = properties.filter(property_type__in=['pg', 'apartment'])
        elif lifestyle == 'luxury':
            properties = properties.filter(property_type__in=['house', 'apartment', 'villa']).filter(price__gte=budget*0.8)
        elif lifestyle == 'minimalist':
            properties = properties.filter(property_type='apartment', bhk__lte=2)
        elif lifestyle == 'family':
            properties = properties.filter(property_type__in=['house', 'apartment'], bhk__gte=2)

        # 4. Commute Distance
        # Since we don't have user's work location, we will sort or filter heuristically.
        # Let's say if commute < 5km, we assume they want city center properties (mock by sorting high price first as proxy for center)
        # We will just limit the results to a manageable number.
        if commute <= 5:
            properties = properties.order_by('-price')
        else:
            properties = properties.order_by('price')

        # Limit to top 12 recommendations
        recommendations = properties[:12]

        results = []
        for prop in recommendations:
            image_url = prop.image.url if prop.image else 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80'
            
            # Format price nicely
            price_val = float(prop.price)
            if price_val >= 10000000:
                formatted_price = f"₹ {price_val / 10000000:.2f} Cr"
            elif price_val >= 100000:
                formatted_price = f"₹ {price_val / 100000:.2f} Lac"
            else:
                formatted_price = f"₹ {price_val:,.0f}"

            results.append({
                'id': prop.id,
                'title': prop.title,
                'city': prop.city,
                'state': prop.state,
                'bhk': prop.bhk,
                'sqft': prop.sqft,
                'formatted_price': formatted_price,
                'property_type_display': prop.get_property_type_display(),
                'image_url': image_url
            })

        return JsonResponse({'recommendations': results})


