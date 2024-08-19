<script>
    let checked = true //let checked = fetch(localhost:8000/is_adding_blocked) über page.server load
    let max_times = 1;

    $: {
        console.log(checked)
        setBlockAddingSong()
    }

    $: {
        console.log(max_times)
         setMaxTimesSongCanBeSung()
    }
    function setTimeBetween() {

    }

    let setBlockAddingSong = () => {
        console.log("{checked}")
    }

    function setMaxTimesSongCanBeSung() {

    }
</script>


<form>
    <div class="mb-3 form-check form-switch">
        <input bind:checked class="form-check-input" id="flexSwitchCheckChecked" role="switch" type="checkbox">
        <label class="form-check-label" for="flexSwitchCheckChecked">Checked switch checkbox input</label>
    </div>

    <div class="mb-3">
        <input type="number" bind:value={max_times} min="1" />
        <label class="form-label" for="customRange3">Example range</label>
        <input bind:value={max_times} class="form-range" id="customRange3" max="3" min="1" step="1.0"
               type="range">
    </div>
    <button class="btn btn-primary" on:click={setBlockAddingSong} type="submit">Submit</button>
</form>

<div class="modal modal-sheet position-static d-block bg-body-secondary p-4 py-md-5" id="modalChoice" role="dialog"
     tabindex="-1">
    <div class="modal-dialog" role="document">
        <div class="modal-content rounded-3 shadow">
            <div class="modal-body p-4 text-center">
                <h5 class="mb-0">Enable this setting?</h5>
                <p class="mb-0">You can always change your mind in your account settings.</p>
            </div>
            <div class="modal-footer flex-nowrap p-0">
                <button class="btn btn-lg btn-link fs-6 text-decoration-none col-6 py-3 m-0 rounded-0 border-end"
                        type="button">
                    <strong>Yes, enable</strong></button>
                <button class="btn btn-lg btn-link fs-6 text-decoration-none col-6 py-3 m-0 rounded-0" data-bs-dismiss="modal"
                        type="button">No thanks
                </button>
            </div>
        </div>
    </div>
</div>