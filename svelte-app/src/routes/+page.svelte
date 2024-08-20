<script>
    import {SongStore} from "../stores.js"
    import {onMount} from "svelte"
    import {goto} from "$app/navigation";
    import SongTable from "$lib/SongTable.svelte";


    onMount(async () => {
        if (!$SongStore.length) {
            const endpoint = "http://localhost:8000/songs/"
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
            <td>{song.audio_duration}</td>
            <td>
                <button type="button" class="btn btn-primary" on:click={() => goto(song.id+"/add")}>Add</button>
            </td>
        </tr>
    {/each}
    </tbody>

</SongTable>