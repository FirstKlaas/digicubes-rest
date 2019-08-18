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

DigiCubes.getUserTable = async function(offset = null, count = null) {
    url = new URL('/account/panel/usertable/', window.location)
    if (offset != null) {
        url.searchParams.append('offset', offset)
        console.log(`Adding offset=${ offset } to query parameter.`)
    }
    if (count != null) {
        url.searchParams.append('count', count)
        console.log(`Adding count=${ count } to query parameter.`)
    }
    console.log(url)

    const response = await fetch(url, {
        method: 'GET',
        mode: 'same-origin',
        cache: 'default',
        credentials: 'include',
        redirect: 'follow',
        referrer: 'no-referrer'
    });
    if (response.status == 200) {
        return response.text();
    } else {
        console.log(response)
        throw new Error(response.statusText);
    }
}