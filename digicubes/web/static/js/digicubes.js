
DigiCubes = {}

DigiCubes.token = null;

/**
 * Login to the digicube server. If successfull, it will return
 * a bearer token for authorization.
 * 
 * @param {string} login 
 * @param {string} password 
 */
DigiCubes.login = async function(login='root', password='digicubes') {
    
    data = {
        login : login,
        password : password
    }

    const response = await fetch('/login/', {
        method: 'POST',
        mode: 'same-origin',
        cache: 'default',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
        },
        redirect: 'follow',
        referrer: 'no-referrer',
        body: JSON.stringify(data),
    });
    if (response.status == 200) {
        const json = await response.json();
        DigiCubes.token = json.bearer_token;
        return json.bearer_token;
    } else {
        throw new Error("response.text");
    }
}

DigiCubes.getUsers = async function() {
    if (DigiCubes.token == null) throw new Error("User not authorized");
    const response = await fetch('/users/', {
        method: 'GET',
        mode: 'same-origin',
        cache: 'default',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + DigiCubes.token,
        },
        redirect: 'follow',
        referrer: 'no-referrer'
    });
    if (response.status == 200) {
        return await response.json();
    } else {
        throw new Error(response.text);
    }
}