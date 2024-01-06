var baseUrl = new URL(window.location.href);
baseUrl = `${baseUrl.protocol}//${baseUrl.hostname}:${baseUrl.port}`;
var cart_count = 0;
var productData = [
    {
        "id": 1,
        "url": "../static/images/mangoes.jpg",
        "product-title": "Mangoes",
        "product-description": "Enjoy the sweet, tropical delight of our fresh mangoes. Bursting with juicy goodness, each bite takes you on a journey to sun-kissed orchards.",
        "product-price": "Rs. 100/- per kg",
        "quantity": 0
    },
    {
        "id": 2,
        "url": "../static/images/Carrot.jpg",
        "product-title": "Carrots",
        "product-description": "Crisp and versatile, our carrots are nature's snack. From salads to smoothies, these vibrant veggies add a healthy crunch to your meals.",
        "product-price": "Rs. 150/- per kg",
        "quantity": 0
    },
    {
        "id": 3,
        "url": "../static/images/Carrot.jpg",
        "product-title": "Carrots",
        "product-description": "Crisp and versatile, our carrots are nature's snack. From salads to smoothies, these vibrant veggies add a healthy crunch to your meals.",
        "product-price": "Rs. 150/- per kg",
        "quantity": 0
    },
    {
        "id": 4,
        "url": "../static/images/Carrot.jpg",
        "product-title": "Carrots",
        "product-description": "Crisp and versatile, our carrots are nature's snack. From salads to smoothies, these vibrant veggies add a healthy crunch to your meals.",
        "product-price": "Rs. 150/- per kg",
        "quantity": 0
    }
];

$(document).ready(function() {
    var products = $("#products");
    productData.forEach((product) => {
        products.append(
            `<div class="product-card">
                    <img src="${product.url}" alt="product-image" class="product-image">
                    <h2 class="product-title">${product["product-title"]}</h2>
                    <p class="product-description">${product["product-description"]}</p>
                    <p class="product-price">${product["product-price"]}</p>
                    <button class="add-to-cart-btn" onclick="add_to_cart(this)" type="button">Add to Cart</button>
                    <input type="hidden" name="product_id" class="product_id" value="${product['id']}">
            </div>`
        );
    });
    $(".add-to-cart-btn").click(function() {
        $("#lblCartCount").html(++cart_count);
    });
});

function add_to_cart(obj) {
    var product_id = obj.parentElement.querySelector(".product_id").value;
    var product_title = obj.parentElement.querySelector(".product-title").textContent;
    var product_price = obj.parentElement.querySelector(".product-price").textContent;
    var curr_product_quantity = 1;
    productData.forEach((product) => {
        if(product.id == product_id) {
            product.quantity += 1;
            curr_product_quantity = product.quantity;
        }
    });

    if(($("#modal_add_cart_content").children().length == 1) || ($("#myModal_add_to_cart #modal_add_cart_content .modal-content[data-id='" + product_id + "']").length == 0) ) {
        console.log("here");
        $("#myModal_add_to_cart #modal_add_cart_content").append(
            `<div class="modal-content" class="product_id_${product_id}" data-id="${product_id}">
                <div class="modal-header">
                    <h5 class="modal-title">${product_title}</h5>
                </div>
                <div class="modal-body">
                    <p>${product_price}</p>
                    <input type="number" name="quantity" class="quantity" value="${curr_product_quantity}">
                </div>
                <input type="hidden" name="product_id" class="product_id" value="${product_id}">
            </div>`
        );
    }
    if ( $("#myModal_add_to_cart #modal_add_cart_content .modal-content[data-id='" + product_id + "']")) {
        // update current product quantity input field
        $("#myModal_add_to_cart #modal_add_cart_content .modal-content[data-id='" + product_id + "'] .modal-body .quantity").val(curr_product_quantity);
    } 
}


$(document).on("click", "#add_to_cart", function() {
    if ($("#myModal_add_to_cart").hasClass("hide")) {
        $("#myModal_add_to_cart").removeClass("hide");
        $("#myModal_add_to_cart").addClass("show");
    }
});

$(document).on("click", ".modal-close", function() {
    if ($("#myModal_add_to_cart").hasClass("show")) {
        $("#myModal_add_to_cart").removeClass("show");
        $("#myModal_add_to_cart").addClass("hide");
    }
});


$(document).on("click", "#checkout", function() {
    var checkout_data = [];
    for(let i=0; i<productData.length; i++) {
        if(productData[i].quantity > 0) {
            checkout_data.push({
                "product_id": productData[i].id,
                "product_title": productData[i]["product-title"],
                "product_price": productData[i]["product-price"],
                "product_url": productData[i].url,       
                "quantity": productData[i].quantity
            });
        }
    }
    console.log({checkout_data});
    axios({
        method: "POST",
        url: baseUrl + "/checkout",
        data: {
            "data": checkout_data
        }
    }).then((response) => {
        console.log(response);
        document.write(response.data);
    }).catch((error) => {
        console.log(error);
    });
});


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
