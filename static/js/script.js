let baseUrl = new URL(window.location.href);
baseUrl = `${baseUrl.protocol}//${baseUrl.hostname}:${baseUrl.port}`;

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
        if (response.data.status == "success") {
            window.location.href = "/login";
        } else {
            alert(response.data.message);
        }
    }).catch((error) => {
        console.log(error);
    });
})