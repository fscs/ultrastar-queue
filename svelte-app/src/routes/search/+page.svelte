<script>
    import {goto} from "$app/navigation";
    import {ErrorAlertStore, SearchResultStore} from "../../stores.js";

    let title = "";
    let artist = "";

    const handleSubmit = () => {
        let endpoint = `http://localhost:8000/songs/get-songs-by-criteria?`
        if (title !== "") {
            endpoint += `title=${title}&`
        }
        if (artist !== "") {
            endpoint += `artist=${artist}`
        }
        fetch(endpoint, {
            method: "GET",
            credentials: "include"
        })
            .then(response => {
                if (response.ok) {
                    return response.json()
                } else {
                    return Promise.reject(response)
                }
            })
            .then((data) => {
                SearchResultStore.set(data)
                goto("/search/result")
            })
            .catch((response) => {
                response.json().then((json) => {
                    ErrorAlertStore.update(prev => [...prev, json["detail"]])
                })
            });

    }
</script>

<form class="d-flex" on:submit={handleSubmit} role="search">
    <div class="form-floating mb-3">
        <input bind:value={title} class="form-control" id="title" placeholder="Title" type="text">
        <label for="title">Song Title</label>
    </div>
    <div class="form-floating mb-3">
        <input bind:value={artist} class="form-control" id="artist" placeholder="Artist" type="text">
        <label for="artist">Artist</label>
    </div>
    <button class="w-100 btn btn-outline-success" type="submit">Search</button>
</form>