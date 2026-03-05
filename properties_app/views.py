from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Property, Wishlist, PropertyReview, Inquiry
from .forms import UserRegistrationForm, PropertyReviewForm, InquiryForm

def home(request):
    latest_properties = Property.objects.order_by('-created_at')[:6]
    return render(request, 'home.html', {'properties': latest_properties})

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
    
    context = {
        'page_obj': page_obj, 
        'query': query,
        'current_filters': request.GET
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

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
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

from django.db.models import Q
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

def chatbot_api(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '').lower()
        
        # Simple rule-based logic
        if 'hello' in user_message or 'hi' in user_message:
            response = "Hello! Welcome to Luxia Real Estate. How can I help you today?"
        elif 'price' in user_message or 'cost' in user_message:
            response = "Property prices vary by location and type. You can use the price filter on our Properties page to find homes within your budget."
        elif 'location' in user_message or 'city' in user_message:
            response = "We have properties across India! Try searching for your desired city on the Properties page."
        elif 'contact' in user_message or 'seller' in user_message:
            response = "You can contact a seller directly from the property detail page by clicking 'Send Inquiry' or 'Chat with Seller' if you're logged in."
        elif 'rent' in user_message:
            response = "Yes, we have properties for rent. Just filter by 'Rented' or search for your needs on the Properties page."
        else:
            response = "I'm a simple bot, so I might not understand everything. Feel free to browse our properties or contact support at contact@luxia.in."
            
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
