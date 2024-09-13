<script>
    import {ErrorAlertStore, QueueStore, SuccessAlertStore, User} from "../../stores.js";
    import {onMount} from "svelte";

    import SongTable from "$lib/SongTable.svelte";
    import {goto} from "$app/navigation";
    import {checkSongInQueueByIndexURL, getQueueURL} from "$lib/backend_routes.js";

    $: isAdmin = $User === null ? false : $User.is_admin

    onMount(async () => {
        const endpoint = new URL(getQueueURL)
        const response = await fetch(endpoint)
        const queue = await response.json()
        QueueStore.set(queue)
    });

    const handleCheck = (index) => {
        const endpoint = new URL(checkSongInQueueByIndexURL)
        endpoint.searchParams.set("index", index)
        fetch(endpoint, {method: "PUT", credentials: "include"})
            .then(response => {
                if (response.ok) {
                    return response.json()
                } else {
                    return Promise.reject(response)
                }
            })
            .then((json) => {
                console.log(json)
                SuccessAlertStore.update(prev => [...prev, json["message"]])
            })
            .catch((response) => {
                response.json().then((json) => {
                    ErrorAlertStore.update(prev => [...prev, json["detail"]])
                })
            });
    }

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
    </tr>
    </thead>
    <tbody>
    {#each $QueueStore as song_in_queue, index}
        <tr>
            <th><a href="{song_in_queue.song.id}">{song_in_queue.song.title}</a></th>
            <th>{song_in_queue.song.artist}</th>
            <th>{intToDateStr(song_in_queue.song.audio_duration)}</th>
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

<div>
    <button class="button" on:click={() => goto("/processed-songs")}>Show recent Songs</button>
</div>