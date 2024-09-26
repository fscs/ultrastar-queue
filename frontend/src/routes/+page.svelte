<script>
    import {SongStore} from "../stores.js"
    import {onMount} from "svelte"
    import {goto} from "$app/navigation";
    import SongTable from "$lib/SongTable.svelte";
    import {getSongsURL} from "$lib/backend_routes.js";
    import {intToDateStr} from "$lib/custom_utils.js";


    onMount(async () => {
        if (!$SongStore.length) {
            const endpoint = new URL(getSongsURL)
            const response = await fetch(endpoint)
            const data = await response.json()
            SongStore.set(data)
        }
    });

</script>

<SongTable>

    <thead>
    <tr>
        <th scope="col">Title</th>
        <th scope="col">Artist</th>
        <th scope="col">Duration</th>
        <th scope="col"></th>
    </tr>
    </thead>
    <tbody>
    {#each $SongStore as song}
        <tr>
            <td><a href="{song.id}">{song.title}</a></td>
            <td>{song.artist}</td>
            {#if song.audio_duration}
                <td>{intToDateStr(song.audio_duration)}</td>
            {:else}
                <td>Not provided</td>
            {/if}
            <td>
                <button type="button" class="btn btn-primary" on:click={() => goto(song.id+"/add")}>Add</button>
            </td>
        </tr>
    {/each}
    </tbody>

</SongTable>