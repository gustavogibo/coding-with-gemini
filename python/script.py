from bs4 import BeautifulSoup
import json
import os
import html
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def create_recipe_card(recipe):
    """Creates the HTML for a single recipe card."""
    
    # Sanitize data to prevent HTML injection issues
    name = html.escape(recipe.get('name', 'No Name'))
    description = html.escape(recipe.get('description', 'No description available.'))
    image_url = html.escape(recipe.get('image_url', ''))
    recipe_url = html.escape(recipe.get('recipe_url', '#'))

    return f"""
                <div class="col">
                    <div class="card h-100">
                        <img src="{image_url}" class="card-img-top" alt="{name}" style="height: 200px; object-fit: cover;">
                        <div class="card-body">
                            <a href="{recipe_url}" class="stretched-link" target="_blank" rel="noopener noreferrer"></a>
                            <h5 class="card-title">{name}</h5>
                            <p class="card-text">{description}</p>
                        </div>
                    </div>
                </div>"""

def generate_html_file(recipes, output_path):
    """Generates the full index.html file from a list of recipes."""

    # Generate all recipe card HTML strings
    recipe_cards_html = "\n".join([create_recipe_card(recipe) for recipe in recipes])

    # Define the HTML template
    html_template = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Melhores comidas brasileiras</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" integrity="sha512-DTOQO9RWCH3ppGqcWaEA1BIZOC6xxalwEsw9c2QQeAIftl+Vegovlnee1c9QX4TctnWMn13TZye+giMm8e2LwA==" crossorigin="anonymous" referrerpolicy="no-referrer" />
    <link rel="stylesheet" href="style.css">
    <style>
        #backToTopBtn {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            display: none; /* Hidden by default */
            z-index: 1030; /* Ensure it's above other content */
        }}
    </style>
</head>
<body>
    <header>
        <nav class="navbar navbar-expand-lg bg-body-tertiary">
            <div class="container">
                <a class="navbar-brand" href="#">Melhores receitas salgadas do <b>Brasil</b></a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarSupportedContent">
                    <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                        <li class="nav-item"><a class="nav-link active" aria-current="page" href="#">Home</a></li>
                        <li class="nav-item"><a class="nav-link" href="#">Sobre</a></li>
                        <li class="nav-item"><a class="nav-link" href="#">Links uteis</a></li>
                        <li class="nav-item"><a class="nav-link" href="#">Contato</a></li>
                    </ul>
                    <form class="d-flex" role="search">
                        <input class="form-control me-2" type="search" placeholder="Pesquisar receita..." aria-label="Search">
                        <button class="btn btn-outline-success" type="submit">Buscar</button>
                        <button class="btn btn-outline-secondary ms-2" type="button" id="resetBtn">Limpar</button>
                    </form>
                </div>
            </div>
        </nav>
    </header>
    <main class="container mt-5">
        <section>
            <h2 class="mb-5 text-center section-title">Comidas</h2>
            <div id="noResultsMessage" class="alert alert-warning text-center p-4" role="alert" style="display: none;">
                <img src="https://media.tenor.com/eB2zEVY6CNgAAAAM/broken-egg.gif" alt="Ovo quebrado caindo no chão" width="150" class="mb-3 rounded">
                <h4 class="alert-heading">Oops! A busca quebrou.</h4>
                <p>Não encontramos nenhuma receita com esses termos. Que tal tentar de novo?</p>
            </div>
            <div class="row row-cols-1 row-cols-md-2 row-cols-lg-4 g-4">
                {recipe_cards_html}
            </div>
            <div class="d-flex justify-content-center mt-5">
                <button class="btn btn-success btn-lg" id="loadMoreBtn">Carregar Mais Receitas</button>
            </div>
        </section>
    </main>
    <a href="#" id="backToTopBtn" class="btn btn-success btn-lg" role="button" title="Voltar ao topo"><i class="fas fa-arrow-up"></i></a>
    <footer class="bg-dark text-white pt-5 pb-4 mt-5">
        <div class="container text-center text-md-start">
            <div class="row text-center text-md-start">
                <div class="col-md-3 col-lg-3 col-xl-3 mx-auto mt-3">
                    <h5 class="text-uppercase mb-4 fw-bold text-success">Melhores Receitas</h5>
                    <p>Aqui você encontra as melhores receitas de comidas salgadas da culinária brasileira. Explore, cozinhe e delicie-se!</p>
                </div>
                <div class="col-md-2 col-lg-2 col-xl-2 mx-auto mt-3 footer-links">
                    <h5 class="text-uppercase mb-4 fw-bold text-success">Links</h5>
                    <p><a href="#" class="text-white text-decoration-none">Home</a></p>
                    <p><a href="#" class="text-white text-decoration-none">Sobre</a></p>
                    <p><a href="#" class="text-white text-decoration-none">Receitas</a></p>
                    <p><a href="#" class="text-white text-decoration-none">Contato</a></p>
                </div>
                <div class="col-md-4 col-lg-3 col-xl-3 mx-auto mt-3">
                    <h5 class="text-uppercase mb-4 fw-bold text-success">Siga-nos</h5>
                    <a href="#" class="btn btn-outline-light btn-floating m-1" role="button"><i class="fab fa-facebook-f"></i></a>
                    <a href="#" class="btn btn-outline-light btn-floating m-1" role="button"><i class="fab fa-twitter"></i></a>
                    <a href="#" class="btn btn-outline-light btn-floating m-1" role="button"><i class="fab fa-instagram"></i></a>
                    <a href="#" class="btn btn-outline-light btn-floating m-1" role="button"><i class="fab fa-youtube"></i></a>
                </div>
            </div>
            <hr class="mb-4">
            <div class="row align-items-center">
                <div class="col-md-7 col-lg-8"><p class="m-0">&copy; 2024 - Desenvolvido por Alura. Todos os direitos reservados.</p></div>
            </div>
        </div>
    </footer>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
    <script src="https://unpkg.com/isotope-layout@3/dist/isotope.pkgd.min.js"></script>
    <script src="https://unpkg.com/imagesloaded@5/imagesloaded.pkgd.min.js"></script>
    <script src="js/script.js"></script>
</body>
</html>"""

    # Write the final HTML to the file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    print(f"Successfully generated {output_path} with {len(recipes)} recipes.")

def scrape_receiteria():
    """
    Scrapes recipe data from receiteria.com.br using Selenium with Firefox.

    This function fetches the main category page, and for each recipe,
    extracts the title, image, and description.

    Returns:
        list: A list of dictionaries, where each dictionary represents a recipe.
              Returns an empty list if the initial request fails.
    """    
    category_url = "https://www.receiteria.com.br/receitas-de-salgadinhos/"

    print(f"Fetching recipe list from: {category_url}")
    
    # Setup Firefox options for Selenium
    ff_options = Options()
    # Add a preference to disable the notification pop-up
    ff_options.set_preference("dom.webnotifications.enabled", False)
    # Attempt to hide the fact that we are using a webdriver
    ff_options.set_preference("dom.webdriver.enabled", False)
    ff_options.add_argument("--disable-blink-features=AutomationControlled")
    # Comment out the next line to see the browser window for debugging
    ff_options.add_argument("--headless")

    # Use a try...finally block to ensure the browser is closed
    driver = None
    try:
        # Initialize the Firefox driver
        # webdriver-manager will download/manage geckodriver automatically
        driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=ff_options)

        # Get the main category page
        print("Navigating to category page...")
        driver.get(category_url)

        # Add a small fixed delay to allow animations to complete
        print("Waiting for page to settle...")
        time.sleep(5)

        # --- DEBUG STEP: Save the page source to a file ---
        print("Saving current page source to debug.html for inspection...")
        with open("debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

        # --- Handle Cookie Consent Banner ---
        try:
            # Wait for the cookie banner button to be present in the DOM
            cookie_button_wait = WebDriverWait(driver, 10)
            cookie_button = cookie_button_wait.until(EC.presence_of_element_located((By.ID, "cn-accept-cookie")))
            print("Cookie consent banner found. Clicking 'OK'.")
            # Use a JavaScript click, which can be more reliable
            driver.execute_script("arguments[0].click();", cookie_button)
        except Exception as e:
            # If the banner doesn't appear or another error occurs, just print a message and continue.
            print("Cookie consent banner not found or could not be clicked. Continuing...")

        # Use an explicit wait for the recipe list to be present
        print("Waiting for recipe cards to load...")
        wait = WebDriverWait(driver, 15) # Wait up to 15 seconds
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.receita")))
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find all recipe cards in the listing
        recipe_cards = soup.select('div.receita')
        
        if not recipe_cards:
            print("No recipe cards found. The site may have blocked the request or changed its structure.")
            return []

        print(f"Found {len(recipe_cards)} recipes. Scraping details...")
        
        recipes_data = []
        for card in recipe_cards:
            # Find elements and check if they exist before getting data
            name_element = card.select_one('div.recipe-head h3')
            description_element = card.select_one('div.info p')
            image_element = card.select_one('div.hover-zoom img')
            link_element = card.select_one('div.hover-zoom a')

            # If any essential part is missing, skip this card.
            # This is common for ad blocks styled like recipe cards.
            if not all([name_element, image_element]):
                print("Skipping a card that is not a valid recipe (likely an ad).")
                continue

            name = name_element.get_text(strip=True)
            # Description can sometimes be missing, so provide a default.
            description = description_element.get_text(strip=True) if description_element else "No description available."
            image_url = image_element['src']
            recipe_url = link_element['href'] if link_element else "#"

            recipes_data.append({
                'name': name,
                'description': description,
                'image_url': image_url,
                'recipe_url': recipe_url
            })

        return recipes_data

    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        return []
    finally:
        if driver:
            driver.quit() # Make sure to close the browser

if __name__ == "__main__":
    scraped_data = scrape_receiteria()
    if scraped_data:
        print("\nScraping finished successfully!")
        
        # --- Save JSON data ---
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(script_dir, 'recipe.json')

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(scraped_data, f, ensure_ascii=False, indent=4)
        
        print(f"Data for {len(scraped_data)} recipes saved to {json_path}")

        # --- Generate HTML file ---
        print("\nGenerating HTML file...")
        html_path = os.path.join(script_dir, '..', 'index.html') # Go up one directory for index.html
        try:
            generate_html_file(scraped_data, html_path)
        except Exception as e:
            print(f"An error occurred during HTML generation: {e}")
    else:
        print("\nScraping failed. HTML file was not generated.")