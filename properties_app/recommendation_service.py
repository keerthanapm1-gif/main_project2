from django.db.models import Q, Avg
from .models import Property, Wishlist, SavedSearch, RecentlyViewed, PropertyReview

class RecommendationEngine:
    """
    Personalized Property Recommendation Engine.
    Uses a scoring heuristic based on:
    - Search history (SavedSearch)
    - Wishlist items
    - Recently viewed properties
    - User preferences (BHK, City, Property Type)
    - Budget (Average price of interactions)
    """

    def __init__(self, user):
        self.user = user

    def get_recommendations(self, limit=6):
        if not self.user.is_authenticated:
            # For anonymous users, return trending/top-rated properties
            return Property.objects.order_by('-view_count')[:limit]

        # 1. Gather User Preferences and Behavior
        user_searches = SavedSearch.objects.filter(user=self.user)
        user_wishlist = Wishlist.objects.filter(user=self.user).select_related('property')
        user_recent = RecentlyViewed.objects.filter(user=self.user).select_related('property')
        
        # Extract preferred cities, types, and BHKs
        preferred_cities = set(user_searches.values_list('city', flat=True)) | \
                           set(user_wishlist.values_list('property__city', flat=True)) | \
                           set(user_recent.values_list('property__city', flat=True))
        preferred_cities = {c for c in preferred_cities if c}

        preferred_types = set(user_searches.values_list('property_type', flat=True)) | \
                          set(user_wishlist.values_list('property__property_type', flat=True))
        preferred_types = {t for t in preferred_types if t}

        preferred_bhks = set(user_searches.values_list('bhk', flat=True)) | \
                         set(user_wishlist.values_list('property__bhk', flat=True))
        preferred_bhks = {b for b in preferred_bhks if b}

        # Estimate Budget based on wishlist and searches
        avg_wishlist_price = user_wishlist.aggregate(Avg('property__price'))['property__price__avg']
        search_max_prices = [s.max_price for s in user_searches if s.max_price]
        estimated_budget = avg_wishlist_price
        if search_max_prices:
            estimated_budget = sum(search_max_prices) / len(search_max_prices)
        
        # 2. Query Potential Properties (Exclude already wishlisted/recently seen to focus on new discovery)
        exclude_ids = set(user_wishlist.values_list('property_id', flat=True)) | \
                      set(user_recent.values_list('property_id', flat=True))
        
        all_properties = Property.objects.exclude(id__in=exclude_ids)

        # 3. Calculate Scores
        scored_properties = []
        for prop in all_properties[:100]: # Limit processing for performance
            score = 0
            
            # City Match (+50)
            if prop.city in preferred_cities:
                score += 50
            
            # Type Match (+30)
            if prop.property_type in preferred_types:
                score += 30
            
            # BHK Match (+30)
            if prop.bhk in preferred_bhks:
                score += 30
            
            # Budget Match (+40 or +20)
            if estimated_budget:
                diff = abs(float(prop.price) - float(estimated_budget))
                if diff <= float(estimated_budget) * 0.1: # Within 10%
                    score += 40
                elif diff <= float(estimated_budget) * 0.25: # Within 25%
                    score += 20
            
            # Popularity Bonus (+10-20)
            if prop.view_count > 100:
                score += 20
            elif prop.view_count > 20:
                score += 10
            
            # Freshness Bonus (+15 for new properties)
            import datetime
            from django.utils import timezone
            if prop.created_at > timezone.now() - datetime.timedelta(days=7):
                score += 15

            scored_properties.append((prop, score))

        # 4. Sort and Return Top Recommendations
        scored_properties.sort(key=lambda x: x[1], reverse=True)
        recommendations = [item[0] for item in scored_properties[:limit]]
        
        # If not enough recommendations, pad with trending ones
        if len(recommendations) < limit:
            remaining = limit - len(recommendations)
            trending = Property.objects.exclude(id__in=[p.id for p in recommendations]).order_by('-view_count')[:remaining]
            recommendations.extend(list(trending))

        return recommendations
