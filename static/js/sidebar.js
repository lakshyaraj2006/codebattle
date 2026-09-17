/**
 * CodeBattle - Mobile Navigation Sidebar Drawer & Search Overlay Controller
 */
(function () {
    function initSidebar() {
        const toggleBtn = document.getElementById('sidebar-toggle-btn');
        const closeBtn = document.getElementById('sidebar-close-btn');
        const sidebar = document.getElementById('mobile-sidebar');
        const backdrop = document.getElementById('sidebar-backdrop');

        if (!toggleBtn || !sidebar || !backdrop) return;

        function openSidebar() {
            sidebar.classList.remove('translate-x-full');
            sidebar.classList.add('translate-x-0');
            backdrop.classList.remove('opacity-0', 'pointer-events-none');
            backdrop.classList.add('opacity-100', 'pointer-events-auto');
            toggleBtn.setAttribute('aria-expanded', 'true');
            document.body.classList.add('overflow-hidden');
        }

        function closeSidebar() {
            sidebar.classList.add('translate-x-full');
            sidebar.classList.remove('translate-x-0');
            backdrop.classList.add('opacity-0', 'pointer-events-none');
            backdrop.classList.remove('opacity-100', 'pointer-events-auto');
            toggleBtn.setAttribute('aria-expanded', 'false');
            document.body.classList.remove('overflow-hidden');
        }

        toggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const isOpen = sidebar.classList.contains('translate-x-0');
            if (isOpen) {
                closeSidebar();
            } else {
                openSidebar();
            }
        });

        if (closeBtn) {
            closeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                closeSidebar();
            });
        }

        backdrop.addEventListener('click', () => {
            closeSidebar();
        });

        // Close on Escape key press
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && sidebar.classList.contains('translate-x-0')) {
                closeSidebar();
            }
        });

        // Close sidebar when clicking links inside the sidebar
        const sidebarLinks = sidebar.querySelectorAll('a');
        sidebarLinks.forEach(link => {
            link.addEventListener('click', () => {
                closeSidebar();
            });
        });

        // Close sidebar if window is resized above mobile breakpoint (md: 768px)
        window.addEventListener('resize', () => {
            if (window.innerWidth >= 768 && sidebar.classList.contains('translate-x-0')) {
                closeSidebar();
            }
        });
    }

    function initMobileSearch() {
        const searchToggleBtn = document.getElementById('mobile-search-toggle-btn');
        const searchCloseBtn = document.getElementById('navbar-mobile-search-close-btn');
        const searchOverlay = document.getElementById('navbar-mobile-search-overlay');
        const searchInput = document.getElementById('navbar-mobile-search-input');
        const autocompleteResults = document.getElementById('navbar-mobile-autocomplete-results');

        if (!searchToggleBtn || !searchOverlay) return;

        function openSearch() {
            searchOverlay.classList.remove('hidden');
            if (searchInput) {
                searchInput.focus();
            }
        }

        function closeSearch() {
            searchOverlay.classList.add('hidden');
            if (autocompleteResults) {
                autocompleteResults.classList.add('hidden');
                autocompleteResults.innerHTML = '';
            }
        }

        searchToggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            openSearch();
        });

        if (searchCloseBtn) {
            searchCloseBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                closeSearch();
            });
        }

        // Close on Escape key press
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !searchOverlay.classList.contains('hidden')) {
                closeSearch();
            }
        });

        // Close search if resized to desktop
        window.addEventListener('resize', () => {
            if (window.innerWidth >= 768 && !searchOverlay.classList.contains('hidden')) {
                closeSearch();
            }
        });
    }

    function init() {
        initSidebar();
        initMobileSearch();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
