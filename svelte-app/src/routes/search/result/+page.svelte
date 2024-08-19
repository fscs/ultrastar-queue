<script>
    import {onMount} from "svelte";
    import SongTable from "$lib/SongTable.svelte";
    import {goto} from "$app/navigation";
    import songs from "./+page.svelte";

    let a_songs;

    onMount(async () => {
        a_songs = songs
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
    {#each a_songs as song}
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