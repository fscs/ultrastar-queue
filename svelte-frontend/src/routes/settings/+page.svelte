<script>
    import {onMount} from "svelte";
    import {deleteSettingValue, getSettingValue, setSettingValue} from "$lib/settings_funcs.js";
    import {User} from "../../stores.js";
    import {
        clearProcessedSongsURL,
        clearQueueURL,
        getIsQueueOpenURL,
        getMaxTimesSongCanBeSungURL,
        getTimeBetweenSameSongURL,
        getTimeBetweenSubmittingSongsURL,
        setIsQueueOpenURL,
        setMaxTimesSongCanBeSungURL,
        setTimeBetweenSameSongURL,
        setTimeBetweenSubmittingSongsURL
    } from "$lib/backend_routes.js";

    let popupClearQueue = false;
    let popupClearProcessedSongs = false;

    $: isAdmin = $User === null ? false : $User.is_admin
    export let queueIsOpen;
    export let timeBetweenSameSong;
    export let hoursBetweenSameSong
    export let minutesBetweenSameSong
    export let secondsBetweenSameSong


    export let maxTimesSongCanBeSung;

    export let timeBetweenSubmittingSongs;
    export let hoursBetweenSubmittingSongs = 0;
    export let minutesBetweenSubmittingSongs = 0;
    export let secondsBetweenSubmittingSongs = 0;

    onMount(async () => {
        queueIsOpen = await getSettingValue(getIsQueueOpenURL);
        timeBetweenSameSong = await getSettingValue(getTimeBetweenSameSongURL);
        timeBetweenSameSong = new Date(0, 0, 0, 0, 0, timeBetweenSameSong)
        hoursBetweenSameSong = timeBetweenSameSong.getHours()
        minutesBetweenSameSong = timeBetweenSameSong.getMinutes()
        secondsBetweenSameSong = timeBetweenSameSong.getSeconds()
        maxTimesSongCanBeSung = await getSettingValue(getMaxTimesSongCanBeSungURL)
        timeBetweenSubmittingSongs = await getSettingValue(getTimeBetweenSubmittingSongsURL);
        timeBetweenSubmittingSongs = new Date(0, 0, 0, 0, 0, timeBetweenSubmittingSongs)
        hoursBetweenSubmittingSongs = timeBetweenSubmittingSongs.getHours()
        minutesBetweenSubmittingSongs = timeBetweenSubmittingSongs.getMinutes()
        secondsBetweenSubmittingSongs = timeBetweenSubmittingSongs.getSeconds()
    });

    const setIsQueueOpen = () => {
        const endpoint = setIsQueueOpenURL
        endpoint.searchParams.set("open_queue", queueIsOpen)
        setSettingValue(endpoint);
    }

    const setTimeBetweenSameSong = () => {
        const endpoint = setTimeBetweenSameSongURL
        endpoint.searchParams.set("seconds", secondsBetweenSameSong)
        endpoint.searchParams.set("minutes", minutesBetweenSameSong)
        endpoint.searchParams.set("hours", hoursBetweenSameSong)
        setSettingValue(endpoint)
    }

    const setMaxTimesSongCanBeSung = () => {
        const endpoint = setMaxTimesSongCanBeSungURL
        endpoint.searchParams.set("max_times", maxTimesSongCanBeSung)
        setSettingValue(endpoint)
    }

    const setTimeBetweenSubmittingSongs = () => {
        const endpoint = setTimeBetweenSubmittingSongsURL
        endpoint.searchParams.set("seconds", secondsBetweenSubmittingSongs)
        endpoint.searchParams.set("minutes", minutesBetweenSubmittingSongs)
        endpoint.searchParams.set("hours", hoursBetweenSubmittingSongs)
        setSettingValue(endpoint)
    }

    const clearQueue = () => {
        deleteSettingValue(clearQueueURL)
    }

    const clearProcessedSongs = () => {
        deleteSettingValue(clearProcessedSongsURL)
    }

</script>

{#if isAdmin}
    <form on:submit={setIsQueueOpen}>
        <div class="mb-3 form-check form-switch">
            <input bind:checked={queueIsOpen} class="form-check-input" id="flexSwitchCheckChecked" role="switch"
                   type="checkbox">
            <label class="form-check-label" for="flexSwitchCheckChecked">Open Queue</label>
        </div>
        <button class="btn btn-primary" type="submit">Save</button>
    </form>

    <form on:submit={setTimeBetweenSameSong}>
        <div class="mb-3">
            <p>Time between submitting the same song</p>
            <input bind:value={hoursBetweenSameSong} min="0" type="number"/>
            <label class="form-label" for="customRange3">Hours</label>
            <input bind:value={minutesBetweenSameSong} min="0" type="number"/>
            <label class="form-label" for="customRange3">Minutes</label>
            <input bind:value={secondsBetweenSameSong} min="0" type="number"/>
            <label class="form-label" for="customRange3">Seconds</label>
        </div>
        <button class="btn btn-primary" type="submit">Save</button>
    </form>

    <form on:submit={setMaxTimesSongCanBeSung}>
        <div class="mb-3">
            <input bind:value={maxTimesSongCanBeSung} min="1" type="number"/>
            <label class="form-label" for="customRange3">Max Times a song can be sung</label>
        </div>
        <button class="btn btn-primary" type="submit">Save</button>
    </form>

    <form on:submit={setTimeBetweenSubmittingSongs}>
        <div class="mb-3">
            <p>Time between submitting songs</p>
            <input bind:value={hoursBetweenSubmittingSongs} min="0" type="number"/>
            <label class="form-label" for="customRange3">Hours</label>
            <input bind:value={minutesBetweenSubmittingSongs} min="0" type="number"/>
            <label class="form-label" for="customRange3">Minutes</label>
            <input bind:value={secondsBetweenSubmittingSongs} min="0" type="number"/>
            <label class="form-label" for="customRange3">Seconds</label>
        </div>
        <button class="btn btn-primary" type="submit">Save</button>
    </form>

    <div>
        <button class="btn btn-primary" type="submit" on:click={() => popupClearQueue=true}>Clear Queue</button>
    </div>

    <div>
        <button class="btn btn-primary" type="submit" on:click={() => popupClearProcessedSongs=true}>Clear
            ProcessedSongs
        </button>
    </div>

    {#if popupClearQueue || popupClearProcessedSongs}
        <div class="modal modal-sheet position-flexible d-block bg-body-secondary p-4 py-md-5" id="modalChoice"
             role="dialog"
             tabindex="-1">
            <div class="modal-dialog" role="document">
                <div class="modal-content rounded-3 shadow">
                    <div class="modal-body p-4 text-center">
                        {#if popupClearQueue}
                            <h5 class="mb-0">Do you really want to clear the queue?</h5>
                        {:else if popupClearProcessedSongs}
                            <h5 class="mb-0">Do you really want to clear all the processed songs?</h5>
                        {/if}
                    </div>
                    <div class="modal-footer flex-nowrap p-0">
                        {#if popupClearQueue}
                            <button class="btn btn-lg btn-link fs-6 text-decoration-none col-6 py-3 m-0 rounded-0 border-end"
                                    type="button" on:click={() => {popupClearQueue=false; clearQueue();}}>
                                <strong>Yes, do it!</strong></button>
                            <button class="btn btn-lg btn-link fs-6 text-decoration-none col-6 py-3 m-0 rounded-0"
                                    data-bs-dismiss="modal"
                                    type="button" on:click={() => popupClearQueue=false}>No thanks
                            </button>
                        {:else if popupClearProcessedSongs}
                            <button class="btn btn-lg btn-link fs-6 text-decoration-none col-6 py-3 m-0 rounded-0 border-end"
                                    type="button"
                                    on:click={() => {popupClearProcessedSongs=false; clearProcessedSongs();}}>
                                <strong>Yes, do it!</strong></button>
                            <button class="btn btn-lg btn-link fs-6 text-decoration-none col-6 py-3 m-0 rounded-0"
                                    data-bs-dismiss="modal"
                                    type="button" on:click={() => popupClearProcessedSongs=false}>No thanks
                            </button>
                        {/if}
                    </div>
                </div>
            </div>
        </div>
    {/if}
{/if}