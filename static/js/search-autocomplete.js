/**
 * CodeBattle - Search Autocomplete & Realtime Search URL Sync
 */

function debounce(fn, delay = 250) {
    let timer = null;
    return function (...args) {
        clearTimeout(timer);
        timer = setTimeout(() => {
            fn.apply(this, args);
        }, delay);
    };
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function updateSearchUrlParam(query) {
    try {
        const isSearchPage = window.location.pathname.startsWith('/search');
        const url = new URL(isSearchPage ? window.location.pathname : '/search/', window.location.origin);
        const currentParams = new URLSearchParams(window.location.search);

        if (currentParams.has('category') && isSearchPage) {
            url.searchParams.set('category', currentParams.get('category'));
        }

        if (query && query.length > 0) {
            url.searchParams.set('q', query);
        } else {
            url.searchParams.delete('q');
        }

        window.history.replaceState({ q: query }, '', url.pathname + url.search);
    } catch (err) {
        console.error('Failed to update search URL param:', err);
    }
}

function setupSearchAutocomplete(inputId, resultsId, theme = 'dark', debounceDelay = 250) {
    const input = document.getElementById(inputId);
    const results = document.getElementById(resultsId);
    if (!input || !results) return;

    let activeIndex = -1;
    let abortController = null;

    const isDark = theme === 'dark';
    const headerClass = isDark ? 'text-gray-400 bg-gray-900/60' : 'text-gray-400 bg-gray-50';
    const hoverItemClass = isDark ? 'hover:bg-gray-700/70 focus:bg-gray-700/70 text-gray-100' : 'hover:bg-red-50/50 focus:bg-red-50/50 text-gray-900';
    const activeItemClass = isDark ? 'bg-gray-700/70' : 'bg-red-50/70';
    const subtextClass = isDark ? 'text-gray-400' : 'text-gray-500';
    const dividerClass = isDark ? 'border-gray-700/60' : 'border-gray-100';

    function closeDropdown() {
        results.classList.add('hidden');
        results.innerHTML = '';
        activeIndex = -1;
        if (abortController) {
            abortController.abort();
            abortController = null;
        }
    }

    function showLoading() {
        results.innerHTML = `
            <div class="py-3 px-4 flex items-center justify-center gap-2 text-xs ${subtextClass}">
                <svg class="animate-spin h-3.5 w-3.5 text-red-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Searching...</span>
            </div>
        `;
        results.classList.remove('hidden');
    }

    async function fetchSuggestions(query) {
        if (!query || query.trim().length === 0) {
            closeDropdown();
            return;
        }

        showLoading();

        if (abortController) {
            abortController.abort();
        }
        abortController = new AbortController();

        try {
            const response = await fetch(`/search/autocomplete/?q=${encodeURIComponent(query.trim())}`, {
                signal: abortController.signal
            });
            if (!response.ok) return;
            const data = await response.json();
            renderSuggestions(query.trim(), data);
        } catch (e) {
            if (e.name !== 'AbortError') {
                console.error('Autocomplete fetch error:', e);
                closeDropdown();
            }
        }
    }

    const debouncedFetch = debounce((q) => {
        fetchSuggestions(q);
    }, debounceDelay);

    function renderSuggestions(query, data) {
        const { events = [], users = [] } = data;

        if (events.length === 0 && users.length === 0) {
            results.innerHTML = `
                <div class="p-4 text-center text-xs ${subtextClass}">
                    No matching events or hackers found for "<strong class="${isDark ? 'text-gray-200' : 'text-gray-700'}">${escapeHtml(query)}</strong>"
                </div>
            `;
            results.classList.remove('hidden');
            return;
        }

        let html = '<div class="max-h-96 overflow-y-auto py-1">';

        // Events Section
        if (events.length > 0) {
            html += `
                <div class="px-3 py-1.5 text-[11px] font-bold uppercase tracking-wider ${headerClass} flex items-center gap-1.5">
                    <span class="icon icon-lightning w-3.5 h-3.5 text-red-500"></span>
                    Events (${events.length})
                </div>
            `;
            events.forEach(event => {
                const statusBadgeClass = event.status === 'Ongoing'
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    : (event.status === 'Upcoming' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' : 'bg-gray-500/10 text-gray-400 border border-gray-500/20');

                html += `
                    <a href="${event.url}" class="autocomplete-item flex items-center justify-between px-3.5 py-2.5 text-xs ${hoverItemClass} transition-colors border-b ${dividerClass} last:border-0">
                        <div class="flex items-center gap-2.5 min-w-0 pr-2">
                            <div class="w-7 h-7 rounded-lg ${isDark ? 'bg-gray-700' : 'bg-red-50'} flex items-center justify-center flex-shrink-0 text-red-500">
                                <span class="icon icon-calendar w-3.5 h-3.5"></span>
                            </div>
                            <div class="truncate">
                                <p class="font-semibold truncate ${isDark ? 'text-gray-100' : 'text-gray-900'}">${highlightMatch(event.name, query)}</p>
                                <p class="${subtextClass} text-[11px]">${event.participants_count} participant${event.participants_count === 1 ? '' : 's'}</p>
                            </div>
                        </div>
                        <span class="flex-shrink-0 px-2 py-0.5 rounded-full text-[10px] font-semibold ${statusBadgeClass}">${event.status}</span>
                    </a>
                `;
            });
        }

        // Community / Users Section
        if (users.length > 0) {
            html += `
                <div class="px-3 py-1.5 text-[11px] font-bold uppercase tracking-wider ${headerClass} flex items-center gap-1.5 ${events.length > 0 ? 'mt-1' : ''}">
                    <span class="icon icon-users w-3.5 h-3.5 text-red-500"></span>
                    Community (${users.length})
                </div>
            `;
            users.forEach(user => {
                html += `
                    <a href="${user.url}" class="autocomplete-item flex items-center gap-2.5 px-3.5 py-2.5 text-xs ${hoverItemClass} transition-colors border-b ${dividerClass} last:border-0">
                        <img src="${user.avatar}" alt="${user.username}" class="w-7 h-7 rounded-full object-cover ring-1 ${isDark ? 'ring-gray-700' : 'ring-gray-200'} flex-shrink-0">
                        <div class="truncate">
                            <p class="font-semibold truncate ${isDark ? 'text-gray-100' : 'text-gray-900'}">${highlightMatch(user.name, query)}</p>
                            <p class="${subtextClass} text-[11px]">@${highlightMatch(user.username, query)}</p>
                        </div>
                    </a>
                `;
            });
        }

        // Footer Link
        html += `
            </div>
            <div class="p-2.5 ${isDark ? 'bg-gray-900/50' : 'bg-gray-50'} border-t ${dividerClass} text-center">
                <a href="/search/?q=${encodeURIComponent(query)}" class="text-xs font-semibold text-red-500 hover:text-red-400 transition-colors inline-flex items-center gap-1">
                    <span>See all results for "<span class="underline">${escapeHtml(query)}</span>"</span>
                    <span class="icon icon-arrow-right w-3.5 h-3.5"></span>
                </a>
            </div>
        `;

        results.innerHTML = html;
        results.classList.remove('hidden');
        activeIndex = -1;
    }

    function highlightMatch(text, query) {
        if (!text || !query) return escapeHtml(text || '');
        const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const regex = new RegExp(`(${escapedQuery})`, 'gi');
        return escapeHtml(text).replace(regex, '<mark class="bg-red-500/30 text-red-300 rounded px-0.5">$1</mark>');
    }

    input.addEventListener('input', (e) => {
        const query = e.target.value;

        if (!query || query.trim().length === 0) {
            closeDropdown();
            return;
        }
        debouncedFetch(query);
    });

    input.addEventListener('focus', (e) => {
        if (e.target.value && e.target.value.trim().length > 0) {
            debouncedFetch(e.target.value);
        }
    });

    input.addEventListener('keydown', (e) => {
        if (results.classList.contains('hidden')) return;
        const items = results.querySelectorAll('.autocomplete-item');
        if (items.length === 0) return;

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            activeIndex = (activeIndex + 1) % items.length;
            updateItemHighlight(items);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            activeIndex = (activeIndex - 1 + items.length) % items.length;
            updateItemHighlight(items);
        } else if (e.key === 'Enter') {
            if (activeIndex >= 0 && items[activeIndex]) {
                e.preventDefault();
                items[activeIndex].click();
            }
        } else if (e.key === 'Escape') {
            closeDropdown();
        }
    });

    function updateItemHighlight(items) {
        items.forEach((item, idx) => {
            if (idx === activeIndex) {
                item.classList.add(activeItemClass);
                item.scrollIntoView({ block: 'nearest' });
            } else {
                item.classList.remove(activeItemClass);
            }
        });
    }

    document.addEventListener('click', (e) => {
        if (!input.contains(e.target) && !results.contains(e.target)) {
            closeDropdown();
        }
    });
}

function initMainSearchInput() {
    const mainInput = document.getElementById('main-search-input');
    const navbarInput = document.getElementById('navbar-search-input');
    const navbarMobileInput = document.getElementById('navbar-mobile-search-input');

    if (!mainInput) return;

    mainInput.addEventListener('input', (e) => {
        const val = e.target.value;
        updateSearchUrlParam(val);

        // Sync value to navbar search inputs in desktop & mobile
        if (navbarInput && navbarInput !== document.activeElement) {
            navbarInput.value = val;
        }
        if (navbarMobileInput && navbarMobileInput !== document.activeElement) {
            navbarMobileInput.value = val;
        }
    });

    // Also sync from navbar search input to search page input
    if (navbarInput) {
        navbarInput.addEventListener('input', (e) => {
            if (mainInput && mainInput !== document.activeElement) {
                mainInput.value = e.target.value;
            }
        });
    }
    if (navbarMobileInput) {
        navbarMobileInput.addEventListener('input', (e) => {
            if (mainInput && mainInput !== document.activeElement) {
                mainInput.value = e.target.value;
            }
        });
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Navbar search (desktop)
    setupSearchAutocomplete('navbar-search-input', 'navbar-autocomplete-results', 'dark', 250);
    // Navbar search (mobile overlay)
    setupSearchAutocomplete('navbar-mobile-search-input', 'navbar-mobile-autocomplete-results', 'dark', 250);
    // Search page input URL sync and cross-input value synchronization
    initMainSearchInput();
});
