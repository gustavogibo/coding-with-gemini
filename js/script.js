document.addEventListener('DOMContentLoaded', function () {
    const searchForm = document.querySelector('form[role="search"]');
    const searchInput = document.querySelector('input[type="search"]');
    const resultsContainer = document.querySelector('.row.g-4');
    const noResultsMessage = document.getElementById('noResultsMessage');
    const loadingSpinner = document.getElementById('loadingSpinner'); // Pega o spinner
    const resetBtn = document.getElementById('resetBtn');
    const navTriggers = document.querySelectorAll('.nav-trigger');
    const pageSections = document.querySelectorAll('.page-section');

    // --- Event Listeners ---
    searchForm.addEventListener('submit', function (event) {
        event.preventDefault();
        const query = searchInput.value.trim();

        if (query) {
            fetchRecipes(query);
        }
    });

    resetBtn.addEventListener('click', function() {
        searchInput.value = ''; // Clear the search input
        fetchRecipes(''); // Fetch the initial random recipes
    });

    navTriggers.forEach(trigger => {
        trigger.addEventListener('click', function(event) {
            event.preventDefault();
            const targetId = this.getAttribute('data-target');
            showSection(targetId);

            // Update active class in header
            document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('data-target') === targetId) {
                    link.classList.add('active');
                }
            });
        });
    });

    function showSection(sectionId) {
        pageSections.forEach(section => {
            section.style.display = section.id === sectionId ? 'block' : 'none';
        });
        window.scrollTo(0, 0); // Scroll to the top of the page on section change
    }


    async function fetchRecipes(query) {
        // 1. Prepara a UI para a busca
        loadingSpinner.style.display = 'block'; // Show the spinner
        resultsContainer.innerHTML = ''; // Limpa resultados antigos
        noResultsMessage.style.display = 'none'; // Esconde mensagem de erro

        try {
            // 2. Chama o back-end
            const response = await fetch(`http://127.0.0.1:5000/api/search?query=${query}`);
            
            if (!response.ok) {
                // Tenta ler a mensagem de erro do corpo da resposta do nosso back-end
                const errorData = await response.json().catch(() => null); // Avoid breaking if error response is not JSON
                throw new Error(errorData?.error || `Server error (status: ${response.status})`);
            }

            const recipes = await response.json();
            
            // 3. Exibe os resultados
            displayRecipes(recipes);

        } catch (error) {
            console.error('Error fetching recipes:', error.message);
            // Exibe a mensagem de erro específica que veio do back-end ou um erro genérico.
            noResultsMessage.innerHTML = `<p class="text-center text-danger">An error occurred while fetching: ${error.message}</p>
                                          <p class="text-center text-muted small">Please check your API key or daily usage limit.</p>`;
            noResultsMessage.style.display = 'block';
        } finally {
            // 4. Garante que o spinner seja escondido ao final
            loadingSpinner.style.display = 'none';
        }
    }

    function displayRecipes(recipes) {
        resultsContainer.innerHTML = ''; // Limpa novamente por segurança

        if (recipes.length === 0) {
            noResultsMessage.style.display = 'block';
            return;
        }

        recipes.forEach(recipe => {
            // A API Spoonacular retorna 'image', 'title', 'readyInMinutes' e 'sourceUrl'
            const cardHtml = `
                <div class="col">
                    <div class="card h-100">
                        <a href="${recipe.sourceUrl}" target="_blank" rel="noopener noreferrer" title="View recipe for ${recipe.title}">
                            <img src="${recipe.image}" class="card-img-top" alt="${recipe.title}" style="height: 200px; object-fit: cover;">
                        </a>
                        <div class="card-body d-flex flex-column pb-3">
                            <h5 class="card-title">${recipe.title}</h5>
                            <p class="card-text small">${
                                // Remove tags HTML do sumário e pega a primeira frase.
                                (recipe.summary || '').replace(/<[^>]*>?/gm, '').split('.')[0] + '.'
                            }</p>
                            <p class="card-text mt-auto"><i class="fa-regular fa-clock"></i> ${
                                recipe.readyInMinutes ? `Ready in ${recipe.readyInMinutes} minutes.` : 'Time not available.'
                            }</p>
                            <a href="${recipe.sourceUrl}" class="btn btn-success mt-auto" target="_blank" rel="noopener noreferrer">View Recipe</a>
                        </div>
                    </div>
                </div>
            `;
            resultsContainer.insertAdjacentHTML('beforeend', cardHtml);
        });
    }

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

    // Oculta o botão "Carregar Mais", pois a busca agora é dinâmica
    document.getElementById('loadMoreBtn').style.display = 'none';

    // --- Carga Inicial ---
    showSection('recipes-section'); // Ensure only the recipe section is visible on load
    fetchRecipes(''); // Chama a busca com uma query vazia para carregar as receitas padrão.
});