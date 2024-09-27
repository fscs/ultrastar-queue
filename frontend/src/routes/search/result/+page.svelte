<script>
    import SongTable from "$lib/SongTable.svelte";
    import {goto} from "$app/navigation";
    import {SearchResultStore} from "../../../stores.js";
    import {intToDateStr} from "$lib/custom_utils.js";
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
    {#each $SearchResultStore as song}
        <tr>
            <td><a href="{song.id}">{song.title}</a></td>
            <td>{song.artist}</td>
            {#if song.audio_duration}
                <td>{intToDateStr(song.audio_duration)}</td>
            {:else}
                <td>Not provided</td>
            {/if}
            <td>
                <button type="button" class="btn btn-primary" on:click={() => goto(`/${song.id}/add`)}>Add</button>
            </td>
        </tr>
    {/each}
    </tbody>
</SongTable>