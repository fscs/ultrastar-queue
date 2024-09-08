<script>
    import {ErrorAlertStore, SuccessAlertStore, User} from "../stores.js";
    import {goto} from "$app/navigation";
    import {loginURL} from "./backend_routes.js";

    let username = "";
    let password = "";

    const login = () => {
        let form_data = new FormData()
        form_data.append('username', username)
        form_data.append('password', password)
        fetch(loginURL, {
            method: "POST",
            credentials: "include",
            //headers: {
            //    "Accept": "application/json",
            //    "Content-Type": "application/x-www-form-urlencoded"
            //},
            body: form_data
        })
            .then(response => {
                if (response.ok) {
                    return response.json()
                } else {
                    return Promise.reject(response)
                }
            })
            .then((data) => {
                User.update(val => val = {...data})
                SuccessAlertStore.update(prev => [...prev, data["message"]])
                goto("/")
            })
            .catch((response) => {
                response.json().then((json) => {
                    ErrorAlertStore.update(prev => [...prev, json["detail"]])
                })
            });


    }

</script>

<div class="container col-xl-10 col-xxl-8 px-4 py-5">
    <div class="row align-items-center g-lg-5 py-5">

        <div class="col-md-10 mx-auto col-lg-5">
            <form class="p-4 p-md-5 border rounded-3 bg-body-tertiary" on:submit|preventDefault={login}>
                <div class="form-floating mb-3">
                    <input bind:value={username} class="form-control" id="username" placeholder="bestUsername"
                           required type="text">
                    <label for="username">Username</label>
                </div>
                <div class="form-floating mb-3">
                    <input bind:value={password} class="form-control" id="password" placeholder="Password"
                           required type="password">
                    <label for="password">Password</label>
                </div>
                <button class="w-100 btn btn-lg btn-primary" type="submit">Sign in</button>
            </form>
        </div>
    </div>
</div>
