<script>
    import {onMount} from "svelte";
    import {QueueStore} from "../../queue-store.js";
    import SongTable from "$lib/SongTable.svelte";

    let isAdmin = true;

    onMount(async () => {
        const endpoint = "http://localhost:8000/queue/"
        const response = await fetch(endpoint)
        const queue = await response.json()
        QueueStore.set(queue)
    });

    function handleCheck(index) {
        console.log(index)
        const endpoint = `http://localhost:8000/queue/check-song-by-index?index=${index}`
        fetch(endpoint, {method: "PUT", credentials: "include"})
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
    </tr>
    </thead>
    <tbody>
    {#each $QueueStore as song_in_queue, index}
        <tr>
            <th><a href="{song_in_queue.song.id}">{song_in_queue.song.title}</a></th>
            <th>{song_in_queue.song.artist}</th>
            <th>{song_in_queue.song.audio_duration}</th>
            <th>{song_in_queue.singer}</th>
            {#if isAdmin}
                <th>
                    <button type="button" class="btn btn-primary" on:click={() => handleCheck(index)}>Check</button>
                </th>
            {/if}
        </tr>
    {/each}
    </tbody>

</SongTable>