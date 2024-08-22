<script>
    import {ErrorAlertStore, QueueStore, SuccessAlertStore} from "../../../stores.js";
    import {goto} from "$app/navigation";
    import {onMount} from "svelte";

    export let singer = "";
    export let data;

    let name_field;

    onMount(async () => {
        name_field.focus()
    })

    export const handleSubmit = () => {

        const endpoint = (`http://localhost:8000/queue/add-song?requested_song_id=${data.id}&singer=${singer}`)
        fetch(endpoint, {
            method: "POST",
            credentials: "include"
        })
            .then(response => {
                if (response.ok) {
                    return response.json()
                } else {
                    return Promise.reject(response)
                }
            })
            .then(data => {
                QueueStore.update(prev => [...prev, data])
                SuccessAlertStore.update(prev => [...prev, "Song successfully added to queue!"])
                goto("/queue/")
            })
            .catch((response) => { // https://stackoverflow.com/a/67660773
                response.json().then((json) => {
                    ErrorAlertStore.update(prev => [...prev, json["detail"]])
                })
            });

    }

</script>

<form on:submit|once|preventDefault={handleSubmit}>
    <div class="col-md-4">
        <input bind:this={name_field} bind:value={singer} class="form-control" placeholder="Enter name" required
               type="text"/>
    </div>
    <button class="submit">Submit</button>
</form>