// Main app functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize elements
    const photoBtn = document.querySelector('.photo-btn');
    const manualBtn = document.querySelector('.manual-btn');
    const entryForm = document.querySelector('.entry-form');
    const resultsSection = document.querySelector('.results');
    const addIngredientBtn = document.querySelector('.add-ingredient-btn');
    const calculateBtn = document.querySelector('.calculate-btn');
    const shareBtn = document.querySelector('.share-btn');

    // Initially hide results
    resultsSection.classList.add('hidden');

    // Photo upload functionality
    photoBtn.addEventListener('click', () => {
        createPhotoUploadModal();
    });

    // Manual entry functionality
    manualBtn.addEventListener('click', () => {
        entryForm.classList.remove('hidden');
        resultsSection.classList.add('hidden');
    });

    // Add ingredient row
    addIngredientBtn.addEventListener('click', addIngredientRow);

    // Calculate button
    calculateBtn.addEventListener('click', calculateNutrition);

    // Share button
    shareBtn.addEventListener('click', shareResults);
});

// Photo upload modal
function createPhotoUploadModal() {
    const modal = document.createElement('div');
    modal.className = 'upload-modal';
    
    modal.innerHTML = `
        <div class="modal-content">
            <span class="close-btn">&times;</span>
            <h2>Upload Food Photo 📸</h2>
            <div class="upload-options">
                <label class="upload-btn">
                    <input type="file" accept="image/*" capture="environment">
                    <span>Take Photo 📸</span>
                </label>
                <label class="upload-btn">
                    <input type="file" accept="image/*">
                    <span>Choose from Gallery 🖼️</span>
                </label>
            </div>
            <div class="preview-container hidden">
                <img id="imagePreview" src="" alt="Preview">
                <button class="analyze-btn">Analyze Food 🔍</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Close button functionality
    const closeBtn = modal.querySelector('.close-btn');
    closeBtn.onclick = () => {
        modal.remove();
    };

    // Handle file inputs
    const fileInputs = modal.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.onchange = handleFileSelect;
    });
}

// Handle file selection
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        const previewContainer = document.querySelector('.preview-container');
        const imagePreview = document.getElementById('imagePreview');
        const analyzeBtn = document.querySelector('.analyze-btn');

        reader.onload = function(e) {
            imagePreview.src = e.target.result;
            previewContainer.classList.remove('hidden');
            
            // Add click event to analyze button
            analyzeBtn.onclick = () => analyzeImage(file);
        };

        reader.readAsDataURL(file);
    }
}

// Analyze image
async function analyzeImage(file) {
    try {
        const formData = new FormData();
        formData.append('image', file);

        // Show loading state
        showLoading();

        // Replace with your actual API endpoint
        const response = await fetch('/api/analyze-image', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        
        // Hide loading state
        hideLoading();

        // Display results
        displayResults(data);
        
        // Close modal
        document.querySelector('.upload-modal').remove();

    } catch (error) {
        console.error('Error analyzing image:', error);
        hideLoading();
        showError('Failed to analyze image. Please try again.');
    }
}

// Add ingredient row
function addIngredientRow() {
    const ingredientsList = document.querySelector('.ingredients-list');
    const newRow = document.createElement('div');
    newRow.className = 'ingredient-row';
    newRow.innerHTML = `
        <input type="text" placeholder="Ingredient" class="ingredient-input">
        <input type="text" placeholder="Amount" class="amount-input">
        <button class="delete-btn">❌</button>
    `;

    // Add delete functionality
    newRow.querySelector('.delete-btn').onclick = () => newRow.remove();

    ingredientsList.appendChild(newRow);
}

// Calculate nutrition
async function calculateNutrition() {
    const mealName = document.querySelector('.meal-input').value;
    const ingredients = [];
    
    // Collect ingredients
    document.querySelectorAll('.ingredient-row').forEach(row => {
        const ingredient = row.querySelector('.ingredient-input').value;
        const amount = row.querySelector('.amount-input').value;
        if (ingredient && amount) {
            ingredients.push({ ingredient, amount });
        }
    });

    if (!mealName || ingredients.length === 0) {
        showError('Please fill in all fields');
        return;
    }

    try {
        showLoading();

        // Replace with your actual API endpoint
        const response = await fetch('/api/calculate-nutrition', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                mealName,
                ingredients
            })
        });

        const data = await response.json();
        hideLoading();
        displayResults(data);

    } catch (error) {
        console.error('Error calculating nutrition:', error);
        hideLoading();
        showError('Failed to calculate nutrition. Please try again.');
    }
}

// Display results
function displayResults(data) {
    const resultsSection = document.querySelector('.results');
    const mealName = resultsSection.querySelector('.meal-name');
    const servingSize = resultsSection.querySelector('.serving-size');
    
    // Update meal details
    mealName.textContent = data.mealName;
    servingSize.textContent = `Serving Size: ${data.servingSize}g`;

    // Update nutrition facts
    const nutritionFacts = resultsSection.querySelectorAll('.nutrient-row .value');
    nutritionFacts[0].textContent = `${data.calories} kcal`;
    nutritionFacts[1].textContent = `${data.carbs}g`;
    nutritionFacts[2].textContent = `${data.protein}g`;
    nutritionFacts[3].textContent = `${data.fat}g`;
    nutritionFacts[4].textContent = `${data.fiber}g`;

    // Show results section
    document.querySelector('.entry-form').classList.add('hidden');
    resultsSection.classList.remove('hidden');
}

// Share results
function shareResults() {
    // Implement sharing functionality
    // This could be social media sharing, saving to PDF, etc.
    alert('Sharing functionality coming soon!');
}

// Utility functions
function showLoading() {
    // Create and show loading spinner
    const loader = document.createElement('div');
    loader.className = 'loader';
    loader.innerHTML = `
        <div class="loader-content">
            <div class="spinner"></div>
            <p>Analyzing... 🔍</p>
        </div>
    `;
    document.body.appendChild(loader);
}

function hideLoading() {
    const loader = document.querySelector('.loader');
    if (loader) loader.remove();
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    
    document.body.appendChild(errorDiv);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 3000);
}