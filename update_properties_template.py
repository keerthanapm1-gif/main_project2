import re

path = 'templates/properties.html'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the LAST endblock position (the one closing content)
endblock_idx = -1
for i in range(len(lines) - 1, -1, -1):
    if re.search(r'\{%\s*endblock\s*%\}', lines[i]):
        endblock_idx = i
        print(f"Found endblock at line {i+1}: {lines[i].strip()}")
        break

if endblock_idx != -1:
    # Search backwards from endblock for the script tag
    script_start_idx = -1
    for i in range(endblock_idx - 1, -1, -1):
        stripped = lines[i].strip()
        if stripped:
            print(f"Checking line {i+1}: {stripped[:30]}")
        if re.search(r'<script>', lines[i]):
            script_start_idx = i
            print(f"Found script at line {i+1}")
            break
    
    if script_start_idx != -1:
        comparison_bar_html = """
<!-- Comparison Bar (Sticky Bottom) -->
<div id="comparison-bar" style="position: fixed; bottom: 0; left: 0; right: 0; background: white; border-top: 1px solid var(--border-color); box-shadow: 0 -10px 15px -3px rgba(0,0,0,0.1); padding: 1rem; display: none; z-index: 1000; animation: slideUp 0.3s ease-out;">
    <div class="container" style="display: flex; justify-content: space-between; align-items: center;">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="background: var(--primary-color); color: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700;" id="compare-count">0</div>
            <div>
                <h4 style="margin: 0; font-size: 1rem;">Properties selected for comparison</h4>
                <p style="margin: 0; font-size: 0.85rem; color: var(--text-muted);" id="compare-titles">None</p>
            </div>
        </div>
        <div style="display: flex; gap: 1rem;">
            <button onclick="clearComparison()" class="btn btn-secondary" style="padding: 0.5rem 1rem;">Clear All</button>
            <a href="#" id="compare-link" class="btn btn-primary" style="padding: 0.5rem 1.5rem;">Compare Now</a>
        </div>
    </div>
</div>

<style>
    @keyframes slideUp {
        from { transform: translateY(100%); }
        to { transform: translateY(0); }
    }
    .filter-chip.active {
        background: var(--primary-color);
        color: white;
        border-color: var(--primary-color);
    }
</style>

<script>
    // Handle chip-style radio buttons
    document.querySelectorAll('.filter-chip input').forEach(radio => {
        radio.addEventListener('change', () => {
            document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
            radio.parentElement.classList.add('active');
        });
    });

    let selectedProperties = JSON.parse(localStorage.getItem('compare_ids')) || [];

    function updateComparisonBar() {
        const bar = document.getElementById('comparison-bar');
        const count = document.getElementById('compare-count');
        const titles = document.getElementById('compare-titles');
        const link = document.getElementById('compare-link');

        if (selectedProperties.length > 0) {
            bar.style.display = 'block';
            count.innerText = selectedProperties.length;
            
            // Get titles from checkboxes on the current page for display
            let titlesList = [];
            selectedProperties.forEach(id => {
                const cb = document.querySelector(`.compare-check[data-id="${id}"]`);
                if (cb) titlesList.push(cb.dataset.title);
            });
            
            if (titlesList.length > 0) {
                titles.innerText = titlesList.join(', ');
            } else {
                titles.innerText = selectedProperties.length + ' active selections';
            }

            link.href = `{% url 'compare_properties' %}?ids=${selectedProperties.join(',')}`;
        } else {
            bar.style.display = 'none';
        }

        // Sync checkboxes
        document.querySelectorAll('.compare-check').forEach(cb => {
            cb.checked = selectedProperties.includes(cb.dataset.id.toString());
        });
    }

    window.toggleCompare = function(id, title) {
        id = id.toString();
        const index = selectedProperties.indexOf(id);
        if (index > -1) {
            selectedProperties.splice(index, 1);
        } else {
            if (selectedProperties.length >= 3) {
                alert('You can compare up to 3 properties at a time.');
                return;
            }
            selectedProperties.push(id);
        }
        localStorage.setItem('compare_ids', JSON.stringify(selectedProperties));
        updateComparisonBar();
    };

    window.clearComparison = function() {
        selectedProperties = [];
        localStorage.setItem('compare_ids', JSON.stringify(selectedProperties));
        updateComparisonBar();
    };

    // Initial load
    document.addEventListener('DOMContentLoaded', updateComparisonBar);
</script>
"""
        # Replace script block with our new content
        new_lines = lines[:script_start_idx] + [comparison_bar_html, '\n'] + lines[endblock_idx:]
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print('Successfully updated properties.html')
    else:
        print('Could not find script tag')
else:
    print('Could not find endblock tag')
