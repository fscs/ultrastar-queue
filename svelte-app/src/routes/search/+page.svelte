<script>
    import {goto} from "$app/navigation";

    let title = "";
    let artist = "";
    export let songs;

    const handleSubmit = () => {
        const endpoint = `http://localhost:8000/songs/get-songs-by-criteria?title=${title}&artist=${artist}`
        const response = fetch(endpoint, {
            method: "GET",
            credentials: "include"
        })
            .then((response) => {
                if (response.status <= 299) return response.json()
            })
            .then((data) => {
                songs = data
                goto("search/result")
            })
    }
</script>

<form class="d-flex" role="search" on:submit|once={{handleSubmit}}>
    <div class="form-floating mb-3">
        <input type="text" class="form-control" id="title" placeholder="Title" bind:value={title}>
        <label for="title">Song Title</label>
    </div>
    <div class="form-floating mb-3">
        <input type="text" class="form-control" id="artist" placeholder="Artist" bind:value={artist}>
        <label for="artist">Artist</label>
    </div>
    <button class="w-100 btn btn-outline-success" type="submit">Search</button>
</form>