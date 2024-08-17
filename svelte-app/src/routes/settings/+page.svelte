<script>
    let checked = true //let checked = fetch(localhost:8000/is_blocked)

    $: {
        console.log(checked)
        setBlockAddingSong()
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
        <input class="form-check-input" type="checkbox" role="switch" id="flexSwitchCheckChecked" bind:checked>
        <label class="form-check-label" for="flexSwitchCheckChecked">Checked switch checkbox input</label>
    </div>
    <div class="mb-3">
        <label for="customRange3" class="form-label">Example range</label>
        <input type="range" class="form-range" min="1" max="3" step="1.0" id="customRange3" on:change={setMaxTimesSongCanBeSung()}>
    </div>
    <button type="submit" class="btn btn-primary" on:click={setBlockAddingSong}>Submit</button>
</form>

<div class="modal modal-sheet position-static d-block bg-body-secondary p-4 py-md-5" tabindex="-1" role="dialog"
     id="modalChoice">
    <div class="modal-dialog" role="document">
        <div class="modal-content rounded-3 shadow">
            <div class="modal-body p-4 text-center">
                <h5 class="mb-0">Enable this setting?</h5>
                <p class="mb-0">You can always change your mind in your account settings.</p>
            </div>
            <div class="modal-footer flex-nowrap p-0">
                <button type="button"
                        class="btn btn-lg btn-link fs-6 text-decoration-none col-6 py-3 m-0 rounded-0 border-end">
                    <strong>Yes, enable</strong></button>
                <button type="button" class="btn btn-lg btn-link fs-6 text-decoration-none col-6 py-3 m-0 rounded-0"
                        data-bs-dismiss="modal">No thanks
                </button>
            </div>
        </div>
    </div>
</div>