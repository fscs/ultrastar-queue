<script>
    import user from "../user";
    import {goto} from "$app/navigation";

    let username = "";
    let password = "";
    let currentError = null;

    const login = () => {
        const endpoint = "http://localhost:8000/token"
        let form_data = new FormData()
        form_data.append('username', username)
        form_data.append('password', password)
        fetch(endpoint, {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: form_data
        })
            .then((response) => {
                if (response.status <= 299) return response.json()
                if (response.status > 299) currentError = response.json()["detail"];
            })
            .then((data) => {
                if (data) user.update(val => val = {...data})
            })
            .catch((error) => {
                currentError = error;
                console.log("Error logging in: ", error)
            })

    }

</script>

<div class="container col-xl-10 col-xxl-8 px-4 py-5">
    <div class="row align-items-center g-lg-5 py-5">
        <div class="col-lg-7 text-center text-lg-start">
            <h1 class="display-4 fw-bold lh-1 text-body-emphasis mb-3">Vertically centered hero sign-up form</h1>
            <p class="col-lg-10 fs-4">Below is an example form built entirely with Bootstrap’s form controls. Each
                required form group has a validation state that can be triggered by attempting to submit the form
                without completing it.</p>
        </div>
        <div class="col-md-10 mx-auto col-lg-5">
            <form class="p-4 p-md-5 border rounded-3 bg-body-tertiary" on:submit|preventDefault={login}>
                <div class="form-floating mb-3">
                    <input type="text" class="form-control" id="username" placeholder="bestUsername" bind:value={username} required>
                    <label for="username">Username</label>
                </div>
                <div class="form-floating mb-3">
                    <input type="password" class="form-control" id="password" placeholder="Password" bind:value={password} required>
                    <label for="password">Password</label>
                </div>
                <button class="w-100 btn btn-lg btn-primary" type="submit">Sign in</button>
                <hr class="my-4">
                <small class="text-body-secondary">By clicking Sign up, you agree to the terms of use.</small>
            </form>
        </div>
    </div>
</div>
