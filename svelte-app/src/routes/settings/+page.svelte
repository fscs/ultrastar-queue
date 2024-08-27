<script>
    import {onMount} from "svelte";
    import {getSettingValue, setSettingValue, deleteSettingValue} from "$lib/settings_funcs.js";
    import {User} from "../../stores.js";

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

    export let blockSubmittingSongsInTimeframe;

    onMount(async () => {
        queueIsOpen = await getSettingValue("/get-is-queue-open");
        timeBetweenSameSong = await getSettingValue("/get-time-between-same-song");
        timeBetweenSameSong = new Date(0, 0, 0, 0, 0, timeBetweenSameSong)
        hoursBetweenSameSong = timeBetweenSameSong.getHours()
        minutesBetweenSameSong = timeBetweenSameSong.getMinutes()
        secondsBetweenSameSong = timeBetweenSameSong.getSeconds()
        maxTimesSongCanBeSung = await getSettingValue("/get-max-times-song-can-be-sung")
        timeBetweenSubmittingSongs = await getSettingValue("/get-time-between-submitting-songs");
        timeBetweenSubmittingSongs = new Date(0, 0, 0, 0, 0, timeBetweenSubmittingSongs)
        hoursBetweenSubmittingSongs = timeBetweenSubmittingSongs.getHours()
        minutesBetweenSubmittingSongs = timeBetweenSubmittingSongs.getMinutes()
        secondsBetweenSubmittingSongs = timeBetweenSubmittingSongs.getSeconds()
        blockSubmittingSongsInTimeframe = await getSettingValue("/get-block-submitting-songs-in-timeframe");
    });

    const setQueueIsOpen = () => {
        setSettingValue(`/set-is-queue-open?open_queue=${queueIsOpen}`);
    }

    const setTimeBetweenSameSong = () => {
        setSettingValue(`/set-time-between-same-song` +
            `?seconds=${secondsBetweenSameSong}` +
            `&minutes=${minutesBetweenSameSong}` +
            `&hours=${hoursBetweenSameSong}`)
    }

    const setMaxTimesSongCanBeSung = () => {
        setSettingValue(`/set-max-times-song-can-be-sung?max_times=${maxTimesSongCanBeSung}`)
    }

    const setTimeBetweenSubmittingSongs = () => {

        setSettingValue(`/set-time-between-submitting-songs` +
            `?seconds=${secondsBetweenSubmittingSongs}` +
            `&minutes=${minutesBetweenSubmittingSongs}` +
            `&hours=${hoursBetweenSubmittingSongs}`)
    }

    const setBlockSubmittingSongsInTimeframe = () => {
        setSettingValue(`/set-block-submitting-songs-in-timeframe?block_submitting=${blockSubmittingSongsInTimeframe}`)
    }

    const clearQueue = () => {
        deleteSettingValue(`/clear-queue`)
    }

    const clearProcessedSongs = () => {
        deleteSettingValue(`/clear-processed-songs`)
    }

    //$: console.log(queueIsOpen)
    //$: console.log(timeBetweenSameSong)
    //$: console.log(maxTimesSongCanBeSung)
    //$: console.log(timeBetweenSubmittingSongs)
    //$: console.log(blockSubmittingSongsInTimeframe)

</script>

{#if isAdmin}
    <form on:submit={setQueueIsOpen}>
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

    <form on:submit={setBlockSubmittingSongsInTimeframe}>
        <div class="mb-3 form-check form-switch">
            <input bind:checked={blockSubmittingSongsInTimeframe} class="form-check-input" id="flexSwitchCheckChecked"
                   role="switch"
                   type="checkbox">
            <label class="form-check-label" for="flexSwitchCheckChecked">Block submitting songs in timeframe</label>
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