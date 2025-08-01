// Wait for DOMContentLoaded to make sure elements exist

// Store numeric limits for price and size from server-provided globals
var minPrice = window.catalogueVars.minPrice;
var maxPrice = window.catalogueVars.maxPrice;
var minPriceStart = window.catalogueVars.minPriceStart;
var maxPriceStart = window.catalogueVars.maxPriceStart;
var minSize = window.catalogueVars.minSize;
var maxSize = window.catalogueVars.maxSize;
var minSizeStart = window.catalogueVars.minSizeStart;
var maxSizeStart = window.catalogueVars.maxSizeStart;

document.addEventListener("DOMContentLoaded", function () {
    // Price slider setup
    var priceSlider = document.getElementById('price-slider');
    noUiSlider.create(priceSlider, {
        start: [window.minPriceStart, window.maxPriceStart],
        connect: true,
        step: 1,
        range: {
            'min': window.minPrice,
            'max': window.maxPrice
        },
        tooltips: [true, true],
        format: {
            to: function (value) { return "$" + Math.round(value); },
            from: function (value) { return Number(String(value).replace('$', '')); }
        }
    });

    // Size slider setup
    var sizeSlider = document.getElementById('size-slider');
    noUiSlider.create(sizeSlider, {
        start: [window.minSizeStart, window.maxSizeStart],
        connect: true,
        step: 0.1,
        range: {
            'min': window.minSize,
            'max': window.maxSize
        },
        tooltips: [true, true],
        format: {
            to: function (value) {
                // Show one decimal place and append GB unit
                return (Math.round(value * 10) / 10) + ' GB';
            },
            from: function (value) {
                return Number(String(value).replace(' GB', ''));
            }
        }
    });

    // Grab inputs and labels
    const minPriceInput = document.getElementById('min-price');
    const maxPriceInput = document.getElementById('max-price');
    const priceRangeLabel = document.getElementById('price-range-label');
    const minSizeInput = document.getElementById('min-size');
    const maxSizeInput = document.getElementById('max-size');
    const sizeRangeLabel = document.getElementById('size-range-label');
    const filterForm = document.getElementById('filter-form');
    const gamesList = document.getElementById('games-list');

    // When the price slider is moved, update hidden fields and label and fetch results
    priceSlider.noUiSlider.on('update', function () {
        // Remove the $ symbol and update hidden inputs
        minPriceInput.value = Math.round(priceSlider.noUiSlider.get()[0].replace('$', ''));
        maxPriceInput.value = Math.round(priceSlider.noUiSlider.get()[1].replace('$', ''));
        priceRangeLabel.textContent = priceSlider.noUiSlider.get().join(' - ');
        // AJAX update as you slide
        fetchGames();
    });

    // When the size slider is moved, update hidden fields and label and fetch results
    sizeSlider.noUiSlider.on('update', function () {
        const val0 = sizeSlider.noUiSlider.get()[0];
        const val1 = sizeSlider.noUiSlider.get()[1];
        // Strip the ' GB' text and parse as float with one decimal
        minSizeInput.value = parseFloat(val0.replace(' GB', ''));
        maxSizeInput.value = parseFloat(val1.replace(' GB', ''));
        sizeRangeLabel.textContent = sizeSlider.noUiSlider.get().join(' - ');
        fetchGames();
    });

    // Set initial labels in case not updated yet
    priceRangeLabel.textContent = "$" + window.minPriceStart + " - $" + window.maxPriceStart;
    sizeRangeLabel.textContent = window.minSizeStart + " GB - " + window.maxSizeStart + " GB";

    function fetchGames() {
        const formData = new FormData(filterForm);
        const params = new URLSearchParams();
        for (const [key, value] of formData.entries()) {
            if (value !== '' && value != null) params.append(key, value);
        }
        // Add all checked genres explicitly (because unchecked checkboxes are not included)
        filterForm.querySelectorAll('input[name="genres"]:checked').forEach(cb => {
            params.append('genres', cb.value);
        });
        // Perform AJAX request to update games list
        fetch("/catalogue?" + params.toString(), {
            headers: { "X-Requested-With": "XMLHttpRequest" }
        })
            .then(response => response.text())
            .then(html => {
                gamesList.innerHTML = html;
            });
    }

    // Listen for filter changes (except slider updates, which we handle separately above)
    filterForm.addEventListener('input', function (e) {
        // Only trigger for checkboxes and search box, not the sliders
        if (!e.target.closest('#price-slider') && !e.target.closest('#size-slider')) {
            fetchGames();
        }
    });
    // When checkboxes change (for example when clicking on a label), fetch results
    filterForm.addEventListener('change', fetchGames);
    // Prevent full form submit
    filterForm.addEventListener('submit', function (e) { e.preventDefault(); });
});
