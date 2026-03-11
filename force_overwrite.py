import os

def overwrite_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Overwrote {path}")

home_content = """{% extends 'base.html' %}
{% load static %}

{% block content %}
<section class="hero">
    <div class="hero-content">
        <div class="hero-tabs">
            <div class="hero-tab active" data-status="available">Buy</div>
            <div class="hero-tab" data-status="rented">Rent</div>
            <div class="hero-tab" data-status="commercial">Commercial</div>
        </div>
        <h1>Discover Your Perfect Home in India</h1>
        <p>Explore our premium collection of luxury apartments, spacious villas, and modern independent houses.</p>
        <form action="{% url 'properties' %}" method="GET" class="search-bar" id="hero-search-form">
            <input type="hidden" name="status" id="search-status" value="available">
            <input type="text" name="q" placeholder="Search by city or property name..." required>
            <button type="submit" class="btn btn-primary">Search</button>
        </form>
    </div>
</section>

<!-- Stats Banner -->
<section class="stats-banner">
    <div class="stat-item">
        <span class="stat-number">{{ total_properties|add:"500" }}+</span>
        <span class="stat-label">Properties Listed</span>
    </div>
    <div style="width: 1px; height: 40px; background: #e2e8f0;"></div>
    <div class="stat-item">
        <span class="stat-number">10K+</span>
        <span class="stat-label">Happy Clients</span>
    </div>
    <div style="width: 1px; height: 40px; background: #e2e8f0;"></div>
    <div class="stat-item">
        <span class="stat-number">{% if total_properties > 10 %}{{ total_properties|add:"-5" }}{% else %}25{% endif %}+</span>
        <span class="stat-label">Verified Listings Added Today</span>
    </div>
</section>

<section class="container" style="margin-top: 5rem;">
    <!-- Browse by Category -->
    <div style="margin-bottom: 4rem;">
        <h2 style="text-align: center; margin-bottom: 2rem;">Browse by Category</h2>
        <div class="category-grid">
            <a href="{% url 'properties' %}?type=apartment" class="category-tile">
                <i class="ph-fill ph-buildings category-icon"></i>
                <span style="font-weight: 600;">Apartments</span>
            </a>
            <a href="{% url 'properties' %}?type=house" class="category-tile">
                <i class="ph-fill ph-house category-icon"></i>
                <span style="font-weight: 600;">Villas/Houses</span>
            </a>
            <a href="{% url 'properties' %}?type=plot" class="category-tile">
                <i class="ph-fill ph-map-trifold category-icon"></i>
                <span style="font-weight: 600;">Plots</span>
            </a>
            <a href="{% url 'properties' %}?type=commercial" class="category-tile">
                <i class="ph-fill ph-factory category-icon"></i>
                <span style="font-weight: 600;">Commercial</span>
            </a>
            <a href="{% url 'properties' %}?type=pg" class="category-tile">
                <i class="ph-fill ph-users-three category-icon"></i>
                <span style="font-weight: 600;">PG/Co-living</span>
            </a>
        </div>
    </div>

    <!-- Latest Properties -->
    <div style="text-align: center; margin-bottom: 3rem;">
        <span style="color: var(--primary-color); font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">Featured</span>
        <h2>Latest Premium Properties</h2>
    </div>

    <div class="property-grid">
        {% for property in properties %}
        <a href="{% url 'property_detail' property.id %}" style="text-decoration:none; color:inherit;">
            <div class="property-card">
                <div class="property-img">
                    <div class="property-badge" style="background: var(--primary-color);">{{ property.get_status_display }}</div>
                    {% if property.image %}
                    <img src="{{ property.image.url }}" alt="{{ property.title }}">
                    {% else %}
                    <img src="https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80" alt="Placeholder">
                    {% endif %}
                </div>
                <div class="property-content">
                    <div class="property-price">₹ {{ property.price }}</div>
                    <h3 class="property-title">{{ property.title }}</h3>
                    <div class="property-address"><i class="ph-fill ph-map-pin"></i> {{ property.city }}, {{ property.state }}</div>
                    <div class="property-features">
                        <span class="feature"><i class="ph-fill ph-bed"></i> {{ property.bhk }} BHK</span>
                        <span class="feature"><i class="ph-fill ph-square-logo"></i> {{ property.sqft }} Sq.Ft.</span>
                    </div>
                </div>
            </div>
        </a>
        {% endfor %}
    </div>

    <!-- Popular Cities -->
    <div style="margin-top: 6rem; background: #fff; padding: 3rem; border-radius: 20px; border: 1px solid var(--border-color);">
        <h2 style="margin-bottom: 2rem; display: flex; align-items: center; gap: 0.75rem;">
            <i class="ph-fill ph-map-pin-line" style="color: var(--primary-color);"></i> Popular Cities
        </h2>
        <div class="city-grid">
            {% for city in city_stats %}
            <a href="{% url 'properties' %}?q={{ city.city }}" class="city-card">
                <img src="https://images.unsplash.com/photo-1570160897040-30430ade2218?auto=format&fit=crop&w=150&q=80" alt="{{ city.city }}" class="city-img">
                <div style="font-weight: 600; color: var(--text-main);">{{ city.city }}</div>
                <div style="font-size: 0.8rem; color: var(--text-muted);">{{ city.count }} Properties</div>
            </a>
            {% empty %}
            <p>Add properties to see city-wise insights.</p>
            {% endfor %}
        </div>
    </div>
</section>

<script>
    document.querySelectorAll('.hero-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.hero-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById('search-status').value = tab.dataset.status;
        });
    });
</script>
{% endblock %}
"""

properties_content = """{% extends 'base.html' %}
{% load static %}
{% load humanize %}

{% block title %}Properties | Luxia Real Estate{% endblock %}

{% block content %}
<div class="container" style="padding-top: 3rem;">
    <div class="properties-layout">
        <!-- Left Sidebar Filters -->
        <aside class="filters-sidebar">
            <h3 style="margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.5rem;">
                <i class="ph ph-sliders"></i> Filters
            </h3>

            <form action="" method="GET" id="filter-form">
                <!-- Search Query -->
                <div class="filter-group">
                    <label style="font-weight: 600; display: block; margin-bottom: 0.5rem;">Search</label>
                    <input type="text" name="q" value="{{ query|default:'' }}" class="form-input" placeholder="City or title...">
                </div>

                <!-- BHK Filter -->
                <div class="filter-group">
                    <label style="font-weight: 600; display: block; margin-bottom: 0.75rem;">BHK Type</label>
                    <div class="chip-group">
                        <label class="filter-chip {% if request.GET.bhk == '1' %}active{% endif %}">
                            <input type="radio" name="bhk" value="1" style="display:none;" {% if request.GET.bhk == '1' %}checked{% endif %}> 1 BHK
                        </label>
                        <label class="filter-chip {% if request.GET.bhk == '2' %}active{% endif %}">
                            <input type="radio" name="bhk" value="2" style="display:none;" {% if request.GET.bhk == '2' %}checked{% endif %}> 2 BHK
                        </label>
                        <label class="filter-chip {% if request.GET.bhk == '3' %}active{% endif %}">
                            <input type="radio" name="bhk" value="3" style="display:none;" {% if request.GET.bhk == '3' %}checked{% endif %}> 3 BHK
                        </label>
                    </div>
                </div>

                <!-- Price Range -->
                <div class="filter-group">
                    <label style="font-weight: 600; display: block; margin-bottom: 0.75rem;">Price Range</label>
                    <div style="display: flex; gap: 0.5rem; align-items: center;">
                        <input type="number" name="min_price" value="{{ request.GET.min_price }}" class="form-input" placeholder="Min" style="padding: 0.5rem;">
                        <span>-</span>
                        <input type="number" name="max_price" value="{{ request.GET.max_price }}" class="form-input" placeholder="Max" style="padding: 0.5rem;">
                    </div>
                </div>

                <!-- Amenities -->
                <div class="filter-group">
                    <label style="font-weight: 600; display: block; margin-bottom: 0.75rem;">Amenities</label>
                    <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                        <label style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.9rem; cursor: pointer;">
                            <input type="checkbox" name="has_parking" {% if 'has_parking' in request.GET %}checked{% endif %}> Parking
                        </label>
                        <label style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.9rem; cursor: pointer;">
                            <input type="checkbox" name="has_lift" {% if 'has_lift' in request.GET %}checked{% endif %}> Lift
                        </label>
                        <label style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.9rem; cursor: pointer;">
                            <input type="checkbox" name="has_power_backup" {% if 'has_power_backup' in request.GET %}checked{% endif %}> Power Backup
                        </label>
                    </div>
                </div>

                <div style="display: flex; gap: 0.5rem;">
                    <button type="submit" class="btn btn-primary" style="flex: 1; padding: 0.5rem;">Apply</button>
                    <a href="{% url 'properties' %}" class="btn btn-secondary" style="padding: 0.5rem; display: flex; align-items: center; justify-content: center;" title="Clear">
                        <i class="ph ph-trash"></i>
                    </a>
                </div>
            </form>
        </aside>

        <!-- Main Content Area -->
        <main>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
                <h1 style="font-size: 1.75rem; margin: 0;">{{ page_obj.paginator.count }} Properties Found</h1>
                <select class="form-input" style="width: auto;" onchange="location.href='?'+new URLSearchParams(Object.assign(Object.fromEntries(new URLSearchParams(location.search)), {sort: this.value})).toString()">
                    <option value="newest" {% if request.GET.sort == 'newest' %}selected{% endif %}>Newest First</option>
                    <option value="price_low" {% if request.GET.sort == 'price_low' %}selected{% endif %}>Price: Low to High</option>
                    <option value="price_high" {% if request.GET.sort == 'price_high' %}selected{% endif %}>Price: High to Low</option>
                    <option value="popular" {% if request.GET.sort == 'popular' %}selected{% endif %}>Most Viewed</option>
                </select>
            </div>

            <div class="property-grid" style="margin-top: 0; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));">
                {% for property in page_obj %}
                <div class="property-card" data-id="{{ property.id }}">
                    <a href="{% url 'property_detail' property.id %}" style="text-decoration:none; color:inherit;">
                        <div class="property-img">
                            <div class="property-badge">{{ property.get_status_display }}</div>
                            {% if property.image %}
                            <img src="{{ property.image.url }}" alt="{{ property.title }}">
                            {% else %}
                            <img src="https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80" alt="Placeholder">
                            {% endif %}
                        </div>
                        <div class="property-content">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                <div class="property-price">₹ {{ property.price|intcomma }}</div>
                                <label style="display:flex; align-items:center; gap:0.25rem; font-size:0.75rem; color:var(--text-muted); cursor:pointer;" onclick="event.preventDefault(); toggleCompare('{{ property.id }}', '{{ property.title }}')">
                                    <input type="checkbox" class="compare-check" data-id="{{ property.id }}" data-title="{{ property.title }}"> Compare
                                </label>
                            </div>
                            <h3 class="property-title" style="font-size: 1.125rem;">{{ property.title }}</h3>
                            <div class="property-address"><i class="ph-fill ph-map-pin"></i> {{ property.city }}, {{ property.state }}</div>
                            <div class="property-features">
                                <span class="feature"><i class="ph-fill ph-bed"></i> {{ property.bhk }} BHK</span>
                                <span class="feature"><i class="ph-fill ph-square-logo"></i> {{ property.sqft }} sqft</span>
                            </div>
                        </div>
                    </a>
                </div>
                {% empty %}
                <div style="grid-column: 1 / -1; text-align: center; padding: 5rem 0;">
                    <i class="ph ph-magnifying-glass" style="font-size: 4rem; color: #cbd5e1; margin-bottom: 1rem;"></i>
                    <h3>No properties match your current filters.</h3>
                    <a href="{% url 'properties' %}" style="color: var(--primary-color);">Clear all filters</a>
                </div>
                {% endfor %}
            </div>

            {% if page_obj.has_other_pages %}
            <div class="pagination">
                {% if page_obj.has_previous %}
                <a href="?page={{ page_obj.previous_page_number }}{% for key, value in request.GET.items %}{% if key != 'page' %}&{{ key }}={{ value }}{% endif %}{% endfor %}" class="page-link"><i class="ph ph-caret-left"></i></a>
                {% endif %}
                <span class="page-link active">{{ page_obj.number }}</span>
                {% if page_obj.has_next %}
                <a href="?page={{ page_obj.next_page_number }}{% for key, value in request.GET.items %}{% if key != 'page' %}&{{ key }}={{ value }}{% endif %}{% endfor %}" class="page-link"><i class="ph ph-caret-right"></i></a>
                {% endif %}
            </div>
            {% endif %}
        </main>
    </div>
</div>

<script>
    // Handle chip-style radio buttons
    document.querySelectorAll('.filter-chip input').forEach(radio => {
        radio.addEventListener('change', () => {
            document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
            radio.parentElement.classList.add('active');
        });
    });
</script>
{% endblock %}
"""

if __name__ == "__main__":
    overwrite_file('templates/home.html', home_content)
    overwrite_file('templates/properties.html', properties_content)
