<script>
    import {ErrorAlertStore, QueueStore, SuccessAlertStore, User} from "../../stores.js";
    import {onMount} from "svelte";

    import SongTable from "$lib/SongTable.svelte";
    import {goto} from "$app/navigation";
    import {markEntryAtIndexAsProcessedURL, getQueueURL} from "$lib/backend_routes.js";

    $: isAdmin = $User === null ? false : $User.is_admin

    onMount(async () => {
        const endpoint = new URL(getQueueURL)
        const response = await fetch(endpoint)
        const queue = await response.json()
        QueueStore.set(queue)
    });

    const handleCheck = (index) => {
        const endpoint = new URL(markEntryAtIndexAsProcessedURL)
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
                SuccessAlertStore.update(prev => [...prev, json["message"]])
                goto("/queue/reload")
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
    {#each $QueueStore as entry, index}
        <tr>
            <th><a href="{entry.song.id}">{entry.song.title}</a></th>
            <th>{entry.song.artist}</th>
            <th>{intToDateStr(entry.song.audio_duration)}</th>
            <th>{entry.singer}</th>
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