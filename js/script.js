// Custom JavaScript file
console.log("Custom script.js v3 loaded successfully.");

document.addEventListener('DOMContentLoaded', function() {
    const cardContainer = document.querySelector('.row.g-4');

    // --- State Management ---
    const searchForm = document.querySelector('form[role="search"]');
    const searchInput = searchForm.querySelector('input[type="search"]');
    const resetBtn = document.getElementById('resetBtn');
    const noResultsMessage = document.getElementById('noResultsMessage');
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    const itemsPerLoad = 12;
    let visibleItemCount = itemsPerLoad;
    const allCards = Array.from(cardContainer.children);

    let iso; // Isotope instance

    function initializeIsotope() {
        // Initialize Isotope. It will automatically perform the first layout.
        iso = new Isotope(cardContainer, {
            itemSelector: '.col',
            layoutMode: 'masonry',
            transitionDuration: '0.5s',
            stagger: 30,
            hiddenStyle: {
                opacity: 0,
                transform: 'translateY(50px)'
            },
            visibleStyle: {
                opacity: 1,
                transform: 'translateY(0)'
            },
            filter: function(item) {
                const index = allCards.indexOf(item);
                const searchTerm = searchInput.value.toLowerCase().trim();
                const title = item.querySelector('.card-title').textContent.toLowerCase();
                const text = item.querySelector('.card-text').textContent.toLowerCase();
                const searchMatch = searchTerm === '' || title.includes(searchTerm) || text.includes(searchTerm);
                const withinLimit = index < visibleItemCount;
                return searchMatch && withinLimit;
            }
        });
        console.log("Isotope initialized and layout complete.");
    }

    function filterCards() {
        if (!iso) return; // Don't do anything if Isotope isn't ready
        iso.arrange(); // Just tell Isotope to re-apply its filter

        // Use a timeout to update buttons after the animation has started
        setTimeout(function() {
            // Show or hide the "no results" message
            if (iso.filteredItems.length === 0 && searchInput.value.trim() !== '') {
                noResultsMessage.style.display = 'block';
            } else {
                noResultsMessage.style.display = 'none';
            }

            // Manually find all cards that match the search term, ignoring the "load more" limit.
            const searchTerm = searchInput.value.toLowerCase().trim();
            const totalMatchingCards = allCards.filter(item => {
                if (searchTerm === '') return true; // All cards match an empty search
                const title = item.querySelector('.card-title').textContent.toLowerCase();
                const text = item.querySelector('.card-text').textContent.toLowerCase();
                return title.includes(searchTerm) || text.includes(searchTerm);
            });

            // Show or hide the "Load More" button
            if (visibleItemCount >= totalMatchingCards.length) {
                loadMoreBtn.style.display = 'none';
            } else {
                loadMoreBtn.style.display = 'block';
            }
        }, 500); // Corresponds to the transition duration
    }

    // Use imagesLoaded to trigger the first layout calculation
    imagesLoaded(cardContainer).on('done', function() {
        console.log('All images loaded. Trimming text and initializing Isotope.');

        // --- Dynamic Text Trimming ---
        // This should run AFTER images are loaded but BEFORE Isotope initializes.
        // Trim descriptions
        const descriptionLimit = 95;
        const descriptionElements = document.querySelectorAll('.card-text');
        descriptionElements.forEach(cardText => {
            const originalText = cardText.textContent;
            if (originalText.length > descriptionLimit) {
                cardText.textContent = originalText.substring(0, descriptionLimit).trim() + '...';
            }
        });

        // Trim titles
        const titleLimit = 25;
        const titleElements = document.querySelectorAll('.card-title');
        titleElements.forEach(cardTitle => {
            const originalTitle = cardTitle.textContent;
            if (originalTitle.length > titleLimit) {
                cardTitle.textContent = originalTitle.substring(0, titleLimit).trim() + '...';
            }
        });

        initializeIsotope();
    });

    function resetSearch() {
        searchInput.value = '';
        visibleItemCount = itemsPerLoad; // Reset visible count
        filterCards();
    }

    searchForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent page reload on form submission
        visibleItemCount = itemsPerLoad; // Reset to first page on new search
        filterCards();
    });

    resetBtn.addEventListener('click', function() {
        resetSearch();
    });

    loadMoreBtn.addEventListener('click', function() {
        visibleItemCount += itemsPerLoad;
        filterCards();
    });

    // Debounce function to limit how often a function can run.
    function debounce(func, wait, immediate) {
        var timeout;
        return function() {
            var context = this, args = arguments;
            var later = function() {
                timeout = null;
                if (!immediate) func.apply(context, args);
            };
            var callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func.apply(context, args);
        };
    };

    window.addEventListener('resize', debounce(() => {
        if (iso) {
            iso.layout();
        }
    }, 150));

    // --- "Back to Top" Button Logic ---
    const backToTopBtn = document.getElementById('backToTopBtn');

    if (backToTopBtn) {
        // Show or hide the button based on scroll position
        window.onscroll = function() {
            if (document.body.scrollTop > 300 || document.documentElement.scrollTop > 300) {
                backToTopBtn.style.display = "block";
            } else {
                backToTopBtn.style.display = "none";
            }
        };

        // Smoothly scroll to top on click
        backToTopBtn.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
});