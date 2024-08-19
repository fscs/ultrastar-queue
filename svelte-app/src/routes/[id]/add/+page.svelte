<script>

    import {goto} from "$app/navigation";
    import {onMount} from "svelte";

    export let singer = ""
    let name_field;
    export let data;

    onMount(async () => {
        name_field.focus()
    })

    export const handleSubmit = () => {

        const endpoint = (`http://localhost:8000/queue/add-song?requested_song_id=${data.id}&singer=${singer}`)
        fetch(endpoint, {method: "POST"})
            .then(response => response.json())
            .then(data => {
                QueueStore.update(prev => [...prev, data])
            })
        goto("/queue/")
    }


</script>

<form on:submit|once|preventDefault={handleSubmit}>
    <div class="col-md-4">
        <input bind:this={name_field} bind:value={singer} class="form-control" placeholder="Enter name" required
               type="text"/>
    </div>
    <button class="submit">Submit</button>
</form>