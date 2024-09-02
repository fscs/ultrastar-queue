<script>
    import {ErrorAlertStore, QueueStore, SuccessAlertStore, User} from "../../../stores.js";
    import {goto} from "$app/navigation";
    import {onMount} from "svelte";
    import {addSongToQueueAsAdminURL, addSongToQueueURL} from "$lib/backend_routes.js";

    export let singer = "";
    export let data;

    let name_field;

    $: isAdmin = $User === null ? false : $User.is_admin

    onMount(async () => {
        name_field.focus()
    })

    const handleSubmit = () => {

        const endpoint = addSongToQueueURL
        endpoint.searchParams.set("requested_song_id", data.id)
        endpoint.searchParams.set("singer", singer)
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

    const handleSubmitAsAdmin = () => {

        const endpoint = addSongToQueueAsAdminURL
        endpoint.searchParams.set("requested_song_id", data.id)
        endpoint.searchParams.set("singer", singer)
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
            .catch((response) => {
                response.json().then((json) => {
                    ErrorAlertStore.update(prev => [...prev, json["detail"]])
                })
            });

    }

</script>

{#if isAdmin}
    <form on:submit|preventDefault={handleSubmitAsAdmin}>
        <div class="col-md-4">
            <input bind:this={name_field} bind:value={singer} class="form-control" placeholder="Enter name" required
                   type="text"/>
        </div>
        <button class="submit">Submit</button>
    </form>
{:else}
    <form on:submit|preventDefault={handleSubmit}>
        <div class="col-md-4">
            <input bind:this={name_field} bind:value={singer} class="form-control" placeholder="Enter name" required
                   type="text"/>
        </div>
        <button class="submit">Submit</button>
    </form>
{/if}