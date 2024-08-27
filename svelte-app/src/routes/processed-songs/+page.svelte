<script>
    import {ProcessedSongsStore} from "../../stores.js";
    import {onMount} from "svelte";
    import SongTable from "$lib/SongTable.svelte";

    onMount(async () => {
        const endpoint = "http://localhost:8000/queue/processed-songs"
        const response = await fetch(endpoint)
        const processedSongs = await response.json()
        ProcessedSongsStore.set(processedSongs)
    });

</script>

<SongTable>

    <thead>
    <slot id="tablehead"></slot>
    <tr>
        <th scope="col">Title</th>
        <th scope="col">Artist</th>
        <th scope="col">Duration</th>
        <th scope="col">Sung at</th>
    </tr>
    </thead>
    <tbody>
    {#each $ProcessedSongsStore as processedSong}
        <tr>
            <th><a href="{processedSong.song.id}">{processedSong.song.title}</a></th>
            <th>{processedSong.song.artist}</th>
            <th>{processedSong.song.audio_duration}</th>
            <th>{processedSong.processed_at}</th>
        </tr>
    {/each}
    </tbody>

</SongTable>
