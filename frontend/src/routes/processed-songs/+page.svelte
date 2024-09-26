<script>
    import {ProcessedQueueEntriesStore} from "../../stores.js";
    import {onMount} from "svelte";
    import SongTable from "$lib/SongTable.svelte";
    import {getProcessedEntriesURL} from "$lib/backend_routes.js";
    import {intToDateStr} from "$lib/custom_utils.js";

    onMount(async () => {
        const endpoint = new URL(getProcessedEntriesURL)
        const response = await fetch(endpoint)
        const entries = await response.json()
        ProcessedQueueEntriesStore.set(entries)
    });

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
            {#if entry.song.audio_duration}
                <td>{intToDateStr(entry.song.audio_duration)}</td>
            {:else}
                <td>Not provided</td>
            {/if}
            <th>{entry.singer}</th>
            <th>{entry.processed_at}</th>
        </tr>
    {/each}
    </tbody>

</SongTable>
