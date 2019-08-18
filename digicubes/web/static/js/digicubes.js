DigiCubes = {}

DigiCubes.token = null;

/**
 * Login to the digicube server. If successfull, it will return
 * a bearer token for authorization.
 * 
 * @param {string} login 
 * @param {string} password 
 */
DigiCubes.login = async function(login = 'root', password = 'digicubes') {
    data = {
        login: login,
        password: password
    }
    const response = await fetch('/account/login/', {
        method: 'GET',
        mode: 'same-origin',
        cache: 'default',
        credentials: 'include',
        headers: {},
        redirect: 'follow',
        referrer: 'no-referrer',
    });
    if (response.status == 200) {
        const json = await response.json();
        DigiCubes.token = json.bearer_token;
        return json.bearer_token;
    }

    if (response.status == 404) {
        throw new Error("Authorization failed")
    }

    throw new Error("Server error");
}

DigiCubes.getUsers = async function(token) {
    const response = await fetch('/account/users/', {
        method: 'GET',
        mode: 'same-origin',
        cache: 'default',
        credentials: 'include',
        headers: {
            'Authorization': 'Bearer ' + token,
        },
        redirect: 'follow',
        referrer: 'no-referrer'
    });
    if (response.status == 200) {
        return response.text();
    } else {
        throw new Error(response.text);
    }
}