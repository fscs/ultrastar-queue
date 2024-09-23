<script>
    import {ProcessedQueueEntriesStore} from "../../stores.js";
    import {onMount} from "svelte";
    import SongTable from "$lib/SongTable.svelte";
    import {getProcessedEntriesURL} from "$lib/backend_routes.js";

    onMount(async () => {
        const endpoint = new URL(getProcessedEntriesURL)
        const response = await fetch(endpoint)
        const entries = await response.json()
        ProcessedQueueEntriesStore.set(entries)
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
        <th scope="col">Singer</th>
        <th scope="col">Sung at</th>
    </tr>
    </thead>
    <tbody>
    {#each $ProcessedQueueEntriesStore as entry}
        <tr>
            <th><a href="{entry.song.id}">{entry.song.title}</a></th>
            <th>{entry.song.artist}</th>
            <th>{intToDateStr(entry.song.audio_duration)}</th>
            <th>{entry.singer}</th>
            <th>{entry.processed_at}</th>
        </tr>
    {/each}
    </tbody>

</SongTable>
