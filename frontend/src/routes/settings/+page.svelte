<script>
    import {onMount} from "svelte";
    import {deleteSettingValue, getSettingValue, setSettingValue} from "$lib/settings_funcs.js";
    import {User} from "../../stores.js";
    import {
        clearProcessedEntriesURL,
        clearQueueURL,
        getMaxTimesSongCanBeSungURL,
        getQueueIsOpenURL,
        getTimeBetweenSameSongURL,
        getTimeBetweenSongSubmissionsURL,
        setMaxTimesSongCanBeSungURL,
        setQueueIsOpenURL,
        setTimeBetweenSameSongURL,
        setTimeBetweenSongSubmissionsURL
    } from "$lib/backend_routes.js";

    let popupClearQueue = false;
    let popupClearProcessedEntries = false;

    $: isAdmin = $User === null ? false : $User.is_admin
    export let queueIsOpen;
    export let timeBetweenSameSong;
    export let hoursBetweenSameSong
    export let minutesBetweenSameSong
    export let secondsBetweenSameSong


    export let maxTimesSongCanBeSung;

    export let timeBetweenSongSubmissions;
    export let hoursBetweenSongSubmissions = 0;
    export let minutesBetweenSongSubmissions = 0;
    export let secondsBetweenSongSubmissions = 0;

    onMount(async () => {
        queueIsOpen = await getSettingValue(new URL(getQueueIsOpenURL));

        timeBetweenSameSong = await getSettingValue(new URL(getTimeBetweenSameSongURL));
        timeBetweenSameSong = new Date(0, 0, 0, 0, 0, timeBetweenSameSong)
        hoursBetweenSameSong = timeBetweenSameSong.getHours()
        minutesBetweenSameSong = timeBetweenSameSong.getMinutes()
        secondsBetweenSameSong = timeBetweenSameSong.getSeconds()

        maxTimesSongCanBeSung = await getSettingValue(new URL(getMaxTimesSongCanBeSungURL))

        timeBetweenSongSubmissions = await getSettingValue(new URL(getTimeBetweenSongSubmissionsURL));
        timeBetweenSongSubmissions = new Date(0, 0, 0, 0, 0, timeBetweenSongSubmissions)
        hoursBetweenSongSubmissions = timeBetweenSongSubmissions.getHours()
        minutesBetweenSongSubmissions = timeBetweenSongSubmissions.getMinutes()
        secondsBetweenSongSubmissions = timeBetweenSongSubmissions.getSeconds()
    });

    const setQueueIsOpen = () => {
        const endpoint = new URL(setQueueIsOpenURL)
        endpoint.searchParams.set("open_queue", queueIsOpen)
        setSettingValue(endpoint);
    }

    const setTimeBetweenSameSong = () => {
        const endpoint = new URL(setTimeBetweenSameSongURL)
        endpoint.searchParams.set("seconds", secondsBetweenSameSong)
        endpoint.searchParams.set("minutes", minutesBetweenSameSong)
        endpoint.searchParams.set("hours", hoursBetweenSameSong)
        setSettingValue(endpoint)
    }

    const setMaxTimesSongCanBeSung = () => {
        const endpoint = new URL(setMaxTimesSongCanBeSungURL)
        endpoint.searchParams.set("max_times", maxTimesSongCanBeSung)
        setSettingValue(endpoint)
    }

    const setTimeBetweenSubmittingSongs = () => {
        const endpoint = new URL(setTimeBetweenSongSubmissionsURL)
        endpoint.searchParams.set("seconds", secondsBetweenSongSubmissions)
        endpoint.searchParams.set("minutes", minutesBetweenSongSubmissions)
        endpoint.searchParams.set("hours", hoursBetweenSongSubmissions)
        setSettingValue(endpoint)
    }

    const clearQueue = () => {
        const endpoint = new URL(clearQueueURL)
        deleteSettingValue(endpoint)
    }

    const clearProcessedEntries = () => {
        const endpoint = new URL(clearProcessedEntriesURL)
        deleteSettingValue(endpoint)
    }

</script>

{#if isAdmin}
    <form class="d-flex flex-column mt-3 mb-3" on:submit={setQueueIsOpen}>
        <div class="mb-3 form-check form-switch">
            <label class="form-check-label" for="flexSwitchCheckChecked">Open Queue</label>
            <input bind:checked={queueIsOpen} class="form-check-input" id="flexSwitchCheckChecked" role="switch"
                   type="checkbox">
        </div>
        <div class="mb-3">
            <button class="btn btn-primary" type="submit">Save</button>
        </div>
    </form>

    <hr>

    <form class="d-flex flex-column mb-3" on:submit={setTimeBetweenSameSong}>
        <div class="mb-3">
            <p>Time that has to pass before the same song can be sung again</p>
            <div>
                <input bind:value={hoursBetweenSameSong} min="0" type="number"/>
                <label class="form-label" for="customRange3">Hours</label>
                <input bind:value={minutesBetweenSameSong} min="0" type="number"/>
                <label class="form-label" for="customRange3">Minutes</label>
                <input bind:value={secondsBetweenSameSong} min="0" type="number"/>
                <label class="form-label" for="customRange3">Seconds</label>
            </div>
        </div>
        <div class="mb-3">
            <button class="btn btn-primary" type="submit">Save</button>
        </div>
    </form>

    <hr>

    <form class="d-flex flex-column mb-3" on:submit={setMaxTimesSongCanBeSung}>
        <div class="mb-3">
            <p>Max Times a song can be sung</p>
            <div>
                <input bind:value={maxTimesSongCanBeSung} min="1" type="number"/>
                <label class="form-label" for="customRange3">Times</label>
            </div>
        </div>
        <div class="mb-3">
            <button class="btn btn-primary" type="submit">Save</button>
        </div>
    </form>

    <hr>

    <form class="d-flex flex-column mb-3" on:submit={setTimeBetweenSubmittingSongs}>
        <div class="mb-3">
            <p>Time that has to pass before the same person can submit a song</p>
            <div>
                <input bind:value={hoursBetweenSongSubmissions} min="0" type="number"/>
                <label class="form-label" for="customRange3">Hours</label>
                <input bind:value={minutesBetweenSongSubmissions} min="0" type="number"/>
                <label class="form-label" for="customRange3">Minutes</label>
                <input bind:value={secondsBetweenSongSubmissions} min="0" type="number"/>
                <label class="form-label" for="customRange3">Seconds</label>
            </div>
        </div>
        <div class="mb-3">
            <button class="btn btn-primary" type="submit">Save</button>
        </div>
    </form>

    <hr>

    <div class="d-flex mt-3 mb-3">
        <button class="btn btn-primary" type="submit" on:click={() => popupClearQueue=true}>Clear Queue</button>
    </div>

    <hr>

    <div class="d-flex mt-3 mb-3">
        <button class="btn btn-primary" type="submit" on:click={() => popupClearProcessedEntries=true}>Clear
            Processed Songs
        </button>
    </div>

    {#if popupClearQueue || popupClearProcessedEntries}
        <div class="modal modal-sheet position-flexible d-block bg-body-secondary p-4 py-md-5" id="modalChoice"
             role="dialog"
             tabindex="-1">
            <div class="modal-dialog" role="document">
                <div class="modal-content rounded-3 shadow">
                    <div class="modal-body p-4 text-center">
                        {#if popupClearQueue}
                            <h5 class="mb-0">Do you really want to clear the queue?</h5>
                        {:else if popupClearProcessedEntries}
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
                        {:else if popupClearProcessedEntries}
                            <button class="btn btn-lg btn-link fs-6 text-decoration-none col-6 py-3 m-0 rounded-0 border-end"
                                    type="button"
                                    on:click={() => {popupClearProcessedEntries=false; clearProcessedEntries();}}>
                                <strong>Yes, do it!</strong></button>
                            <button class="btn btn-lg btn-link fs-6 text-decoration-none col-6 py-3 m-0 rounded-0"
                                    data-bs-dismiss="modal"
                                    type="button" on:click={() => popupClearProcessedEntries=false}>No thanks
                            </button>
                        {/if}
                    </div>
                </div>
            </div>
        </div>
    {/if}
{/if}
