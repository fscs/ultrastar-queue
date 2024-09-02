<script>
    import {ErrorAlertStore, SuccessAlertStore, User} from "../stores.js";
    import {onMount} from "svelte";
    import {getCurrentUserURL, logoutURL} from "./backend_routes.js";

    $: isLoggedIn = $User !== null
    $: isAdmin = $User === null ? false : $User.is_admin

    const logout = () => {
        fetch(logoutURL, {
            method: "POST",
            credentials: "include",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
        })
            .then(response => {
                if (response.ok) {
                    return response.json()
                } else {
                    return Promise.reject(response)
                }
            })
            .then((data) => {
                console.log(data)
                User.update(val => val = null)
                SuccessAlertStore.update(prev => [...prev, data["message"]])
            })
            .catch((response) => {
                response.json().then((json) => {
                    ErrorAlertStore.update(prev => [...prev, json["detail"]])
                })
            });


    }

    onMount(async () => {
        if (!$User) {
            fetch(getCurrentUserURL, {
                method: "POST",
                credentials: "include",
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
            })
                .then(response => {
                    if (response.ok) {
                        return response.json()
                    } else if (response.status === 401) {
                        return Promise.resolve({"user": false})
                    } else {
                        return Promise.reject(response)
                    }
                })
                .then((data) => {
                    if (data["user"] === true) {
                        User.update(val => val = {...data})
                    }
                })
                .catch((response) => {
                    response.json().then((json) => {
                        ErrorAlertStore.update(prev => [...prev, json["detail"]])
                    })
                });
        }
    })

</script>
<nav class="navbar navbar-expand-md navbar-dark fixed-top bg-dark">
    <div class="container-fluid">
        <a class="navbar-brand" href="/">Home</a>
        <button aria-controls="navbarCollapse" aria-expanded="false" aria-label="Toggle navigation"
                class="navbar-toggler"
                data-bs-target="#navbarCollapse" data-bs-toggle="collapse" type="button">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarCollapse">
            <ul class="navbar-nav me-auto mb-2 mb-md-0">
                <li class="nav-item">
                    <a aria-current="page" class="nav-link active" href="/queue">Queue</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="/search">Search</a>
                </li>
                {#if isAdmin}
                    <li class="nav-item">
                        <a class="nav-link" href="/settings">Settings</a>
                    </li>
                {/if}
            </ul>
            <div class="d-flex">
                {#if isLoggedIn}
                    <button type="button" class="btn btn-outline-success me-2" on:click={() => logout()}>Logout</button>
                {:else}
                    <a class="btn btn-outline-success me-2" href="/login">Login</a>
                {/if}
            </div>
        </div>
    </div>
</nav>