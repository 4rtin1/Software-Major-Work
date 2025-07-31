// Wait for DOMContentLoaded to make sure elements exist
var minPrice = window.catalogueVars.minPrice;
var maxPrice = window.catalogueVars.maxPrice;
var minPriceStart = window.catalogueVars.minPriceStart;
var maxPriceStart = window.catalogueVars.maxPriceStart;


document.addEventListener("DOMContentLoaded", function () {
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

    const minPriceInput = document.getElementById('min-price');
    const maxPriceInput = document.getElementById('max-price');
    const priceRangeLabel = document.getElementById('price-range-label');
    const filterForm = document.getElementById('filter-form');
    const gamesList = document.getElementById('games-list');

    priceSlider.noUiSlider.on('update', function (values, handle) {
        minPriceInput.value = Math.round(priceSlider.noUiSlider.get()[0].replace('$', ''));
        maxPriceInput.value = Math.round(priceSlider.noUiSlider.get()[1].replace('$', ''));
        priceRangeLabel.textContent = priceSlider.noUiSlider.get().join(' - ');
        // AJAX update as you slide
        fetchGames();
    });

    // Set initial label in case not updated yet
    priceRangeLabel.textContent = "$" + window.minPriceStart + " - $" + window.maxPriceStart;

    function fetchGames() {
        const formData = new FormData(filterForm);
        const params = new URLSearchParams();
        for (const [key, value] of formData.entries()) {
            if (value) params.append(key, value);
        }
        // Add all checked genres
        filterForm.querySelectorAll('input[name="genres"]:checked').forEach(cb => {
            params.append('genres', cb.value);
        });

        fetch("/catalogue?" + params.toString(), {
            headers: { "X-Requested-With": "XMLHttpRequest" }
        })
            .then(response => response.text())
            .then(html => {
                gamesList.innerHTML = html;
            });
    }

    // Listen for filter changes (except slider, which is handled above)
    filterForm.addEventListener('input', function (e) {
        // Only trigger for checkboxes and search box, not the slider
        if (!e.target.closest('#price-slider')) {
            fetchGames();
        }
    });
    filterForm.addEventListener('change', fetchGames);
    filterForm.addEventListener('submit', function (e) { e.preventDefault(); });
});
