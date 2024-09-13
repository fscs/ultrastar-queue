<script>
    import {ProcessedSongsStore} from "../../stores.js";
    import {onMount} from "svelte";
    import SongTable from "$lib/SongTable.svelte";
    import {getProcessedSongsURL} from "$lib/backend_routes.js";

    onMount(async () => {
        const endpoint = new URL(getProcessedSongsURL)
        const response = await fetch(endpoint)
        const processedSongs = await response.json()
        ProcessedSongsStore.set(processedSongs)
    });

    const intToDateStr = (int) => {
        let date = new Date(0, 0, 0, 0, 0, int)
        let min = date.getMinutes() < 10 ? `0${date.getMinutes()}` : `${date.getMinutes()}`
        let sec = date.getSeconds() < 10 ? `0${date.getSeconds()}` : `${date.getSeconds()}`
        return `${date.getHours()}:${min}:${sec}`
    }
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
            <th>{intToDateStr(processedSong.song.audio_duration)}</th>
            <th>{processedSong.processed_at}</th>
        </tr>
    {/each}
    </tbody>

</SongTable>
