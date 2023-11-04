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