<script>
    import {SongStore} from "../song-store.js"
    import {onMount} from "svelte"
    import {goto} from "$app/navigation";

    onMount(async () => {
        if (!$SongStore.length) {
            const endpoint = "http://localhost:8000/songs/"
            const response = await fetch(endpoint)
            const data = await response.json()
            SongStore.set(data)
        }
    });
</script>

<table class="table  table-striped">
    <thead>
        <tr>
            <th scope="col">Title</th>
            <th scope="col">Artist</th>
            <th scope="col">Duration</th>
        </tr>
    </thead>
    <tbody>
        {#each $SongStore as song}
            <tr>
                <th scope="row"><a href="{song.id}">{song.title}</a></th>
                <th>{song.artist}</th>
                <th>{song.audio_duration}</th>
                <th><button type="button" class="btn btn-primary" on:click={() => goto(song.id+"/add")}>Add</button></th>
            </tr>
        {/each}
    </tbody>
</table>