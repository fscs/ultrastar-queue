<script>
    import {SongStore} from "../../song-store.js";
    import {onMount} from "svelte";
    export let data;
    let song;

    onMount(async () => {
        if ($SongStore.length) {
            song = $SongStore.find(song => song.id === parseInt(data.id))
        } else {
            const endpoint = `http://localhost:8000/songs/${data.id}/`
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
    <p>{song.audio_duration}</p>
    <p>{song.lyrics}</p>
{/if}