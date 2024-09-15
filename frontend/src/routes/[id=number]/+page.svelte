<script>
    import {SongStore} from "../../stores.js";
    import {onMount} from "svelte";
    import {goto} from "$app/navigation";
    import {getSongByIdURL} from "$lib/backend_routes.js";

    export let data;
    let song;

    onMount(async () => {
        if ($SongStore.length) {
            song = $SongStore.find(song => song.id === parseInt(data.id))
        } else {
            const url = `${getSongByIdURL}/${data.id}/`
            const endpoint = new URL(url)
            let response = await fetch(endpoint)
            if (response.status === 200) {
                song = await response.json()
            } else {
                song = null;
            }
        }

    })
</script>
{#if song}
    <h1>{song.title}</h1>
    <p>{song.artist}</p>
    <p>{song.lyrics}</p>
    <button type="button" class="btn btn-primary" on:click={() => goto(song.id+"/add")}>Add</button>
{/if}