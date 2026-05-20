// Nexus Market Core Client Actions

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initSearchSuggestions();
    updateCartCount();
});

// ==========================================
// 1. Dark/Light Theme Handler
// ==========================================
function initTheme() {
    const themeToggleBtn = document.getElementById('theme-toggle');
    if (!themeToggleBtn) return;
    
    // Check local storage or system preference
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
        document.body.classList.add('dark-theme');
        updateThemeIcon('dark');
    } else {
        document.body.classList.remove('dark-theme');
        updateThemeIcon('light');
    }
    
    themeToggleBtn.addEventListener('click', () => {
        const isDark = document.body.classList.contains('dark-theme');
        if (isDark) {
            document.body.classList.remove('dark-theme');
            localStorage.setItem('theme', 'light');
            updateThemeIcon('light');
        } else {
            document.body.classList.add('dark-theme');
            localStorage.setItem('theme', 'dark');
            updateThemeIcon('dark');
        }
    });
}

function updateThemeIcon(theme) {
    const icon = document.querySelector('#theme-toggle i');
    if (!icon) return;
    if (theme === 'dark') {
        icon.className = 'fas fa-sun'; // Sun icon for switching back to light
    } else {
        icon.className = 'fas fa-moon'; // Moon icon for switching to dark
    }
}

// ==========================================
// 2. Intelligent Search Suggestions (Debounced)
// ==========================================
function initSearchSuggestions() {
    const searchInput = document.getElementById('search-input');
    const suggestionsBox = document.getElementById('suggestions-box');
    if (!searchInput || !suggestionsBox) return;
    
    let debounceTimer;
    
    searchInput.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        const query = searchInput.value.trim();
        
        if (query.length < 2) {
            suggestionsBox.style.display = 'none';
            return;
        }
        
        debounceTimer = setTimeout(() => {
            fetch(`/api/search/suggestions?q=${encodeURIComponent(query)}`)
                .then(res => res.json())
                .then(data => {
                    renderSuggestions(data);
                })
                .catch(err => console.error("Suggestions fetch error:", err));
        }, 300); // 300ms debounce
    });
    
    // Hide dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (e.target !== searchInput && e.target !== suggestionsBox) {
            suggestionsBox.style.display = 'none';
        }
    });
    
    // Helper to render suggestions
    function renderSuggestions(list) {
        if (!list || list.length === 0) {
            suggestionsBox.style.display = 'none';
            return;
        }
        
        suggestionsBox.innerHTML = '';
        list.forEach(item => {
            const div = document.createElement('div');
            div.className = 'suggestion-item';
            div.textContent = item;
            
            div.addEventListener('click', () => {
                searchInput.value = item;
                suggestionsBox.style.display = 'none';
                // Trigger form submit
                searchInput.closest('form').submit();
            });
            suggestionsBox.appendChild(div);
        });
        suggestionsBox.style.display = 'block';
    }
}

// ==========================================
// 3. Dynamic Cart Count AJAX Update
// ==========================================
function updateCartCount() {
    const badge = document.getElementById('cart-badge');
    if (!badge) return;
    
    fetch('/api/cart/count')
        .then(res => res.json())
        .then(data => {
            if (data.count > 0) {
                badge.textContent = data.count;
                badge.style.display = 'inline-block';
            } else {
                badge.style.display = 'none';
            }
        })
        .catch(err => console.warn("Cart count sync skipped. User may not be logged in."));
}
