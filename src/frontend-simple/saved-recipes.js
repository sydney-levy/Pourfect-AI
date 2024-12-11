document.addEventListener('scroll', () => {
    const header = document.querySelector('.header');
    if (window.scrollY > 50) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});

// Load saved recipes from localStorage
document.addEventListener('DOMContentLoaded', () => {
    const savedRecipesList = document.getElementById('savedRecipesList');
    const savedRecipes = JSON.parse(localStorage.getItem('savedResponses')) || [];
    
    // Function to render recipes
    const renderRecipes = () => {
        savedRecipesList.innerHTML = ''; 
        if (savedRecipes.length === 0) {
            savedRecipesList.innerHTML = '<li>No recipes saved yet. Start chatting with Pourfect AI and discover your favorite recipes!</li>';
        } else {
            savedRecipes.forEach((recipe, index) => {
                const recipeTitle = extractRecipeTitle(recipe.content); 
                const recipeItem = document.createElement('li');
                recipeItem.innerHTML = `
                    <div class="recipe-card">
                        <div class="recipe-header">
                            <h3>${recipeTitle}</h3>
                            <button class="delete-btn" data-index="${index}" aria-label="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                        <div class="recipe-content">
                            ${recipe.content
                                .split('\n')
                                .map(paragraph => `<p>${paragraph}</p>`)
                                .join('')}
                        </div>
                    </div>
                `;
                savedRecipesList.appendChild(recipeItem);
            });
    
            // Event listeners for all delete buttons
            document.querySelectorAll('.delete-btn').forEach(button => {
                button.addEventListener('click', (event) => {
                    const recipeIndex = event.target.closest('.delete-btn').getAttribute('data-index');
                    removeRecipe(recipeIndex);
                });
            });
        }
    };

    // Function to remove a recipe if needed
    const removeRecipe = (index) => {
        savedRecipes.splice(index, 1);
        localStorage.setItem('savedResponses', JSON.stringify(savedRecipes));
        renderRecipes();
    };

    renderRecipes(); 
});

const extractRecipeTitle = (content) => {
    // Regex to find bolded lines for a title in saved recipes
    const boldTitleMatch = content.match(/\*\*(.+?)\*\*/);
    if (boldTitleMatch) {
        return boldTitleMatch[1].trim();
    }

    const firstLine = content.split('\n')[0].trim();
    if (firstLine && firstLine.length > 3 && !firstLine.startsWith('*')) {
        return firstLine;
    }

    return generateFunName();
};