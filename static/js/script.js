let baseUrl = new URL(window.location.href);
baseUrl = `${baseUrl.protocol}//${baseUrl.hostname}:${baseUrl.port}`;
let cart_count = 0;

$(document).ready(function() {
    var products = $("#products");
    var productData = [
        {
            "url": "../static/images/mangoes.jpg",
            "product-title": "Mangoes",
            "product-description": "Enjoy the sweet, tropical delight of our fresh mangoes. Bursting with juicy goodness, each bite takes you on a journey to sun-kissed orchards.",
            "product-price": "Rs. 100/- per kg",
        },
        {
            "url": "../static/images/Carrot.jpg",
            "product-title": "Carrots",
            "product-description": "Crisp and versatile, our carrots are nature's snack. From salads to smoothies, these vibrant veggies add a healthy crunch to your meals.",
            "product-price": "Rs. 150/- per kg",
        },
        {
            "url": "../static/images/Carrot.jpg",
            "product-title": "Carrots",
            "product-description": "Crisp and versatile, our carrots are nature's snack. From salads to smoothies, these vibrant veggies add a healthy crunch to your meals.",
            "product-price": "Rs. 150/- per kg",
        },
        {
            "url": "../static/images/Carrot.jpg",
            "product-title": "Carrots",
            "product-description": "Crisp and versatile, our carrots are nature's snack. From salads to smoothies, these vibrant veggies add a healthy crunch to your meals.",
            "product-price": "Rs. 150/- per kg",
        }
    ];
    productData.forEach((product) => {
        products.append(
            `<div class="product-card">
                    <img src="${product.url}" alt="product-image" class="product-image">
                    <h2 class="product-title">${product["product-title"]}</h2>
                    <p class="product-description">${product["product-description"]}</p>
                    <p class="product-price">${product["product-price"]}</p>
                    <button class="add-to-cart-btn" onclick="add_to_cart(this)" type="button">Add to Cart</button>
            </div>`
        );
    });
    $(".add-to-cart-btn").click(function() {
        $("#lblCartCount").html(++cart_count);
    });
});

function add_to_cart(obj) {
    console.log(obj.parentElement.querySelector(".product-title").textContent);
    console.log(obj.parentElement.querySelector(".product-price").textContent);
}

document.getElementById('searchInput').addEventListener('keyup', function() {
    const searchTerm = this.value.toLowerCase();
    const productCards = document.querySelectorAll('.product-card');
    
    productCards.forEach(card => {
        const title = card.querySelector('.product-title').textContent.toLowerCase();
        if (title.includes(searchTerm)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
});

// onclick for signup button
function signup() {
    window.location.href = "/signup";
}

// onclick for login button
function login() {
    window.location.href = "/login";
}

$("#signup_form #submit").click(async function(event) {
    event.preventDefault();
    var data = $("#signup_form").serializeArray();
    console.log({data});
    data = {
        "data": data
    }
    await axios({
        method: "POST",
        url: baseUrl + "/signup_farmer",
        data: data
    }).then((response) => {
        console.log(response);
        if (response.data.success) {
            if(response.data.category == "farmer") {
                window.location.href = "/login";
            }
        } else {
            alert(response.data.message);
        }
    }).catch((error) => {
        console.log(error);
    });
})

$("#farmer_login #submit").click(async function(event) {
    event.preventDefault();
    var data = $("#farmer_login").serializeArray();
    data = {
        "data": data
    }
    console.log(data);
    resp = await axios({
        method: "POST",
        url: baseUrl + "/login",
        data: data
    })
    console.log(resp);
    if(!resp.data.success) {
        alert(resp.data.message);
        $("#farmer_login").trigger("reset");
    } else {
        window.location.href = "/";
    }
});
