<script>
    import {onMount} from "svelte";

    let queue = []

    onMount(async () => {
            const endpoint = "http://localhost:8000/queue/"
            const response = await fetch(endpoint)
            const data = await response.json()
            queue = data
        console.log(queue)
    });
</script>

<table class="table table-striped">
    <thead>
        <tr>
            <th>Title</th>
            <th>Artist</th>
            <th>Duration</th>
            <th>Singer</th>
        </tr>
    </thead>
    <tbody>
        {#each queue as song_in_queue}
            <tr>
                <th><a href="{song_in_queue.song.id}">{song_in_queue.song.title}</a></th>
                <th>{song_in_queue.song.artist}</th>
                <th>{song_in_queue.song.audio_duration}</th>
                <th>{song_in_queue.singer}</th>
            </tr>
        {/each}
    </tbody>
</table>