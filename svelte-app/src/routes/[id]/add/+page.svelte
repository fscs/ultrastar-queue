<script>

    import {goto} from "$app/navigation";
    export let singer = ""
export let data;

    export const handleSubmit = () => {

        const endpoint = ("http://localhost:8000/queue/add-song?requested_song_id="+data.id+"&singer="+singer)
        fetch(endpoint, {method: "GET"}).then(
            response => response.json())
        goto("/queue/")
    }

</script>

<form on:submit|once|preventDefault={handleSubmit}>
    <div class="col-md-4">
        <input type="text" class="form-control" placeholder="Enter name" bind:value={singer} required/>
    </div>
    <button class="submit">Submit</button>
</form>