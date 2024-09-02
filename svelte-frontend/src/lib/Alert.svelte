<script>
    import {ErrorAlertStore, SuccessAlertStore} from "../stores.js";

    function handleSuccessClick() {
        SuccessAlertStore.update(prev => {
            let [a, ...rest] = prev
            return rest
        })
    }

    function handleErrorClick() {
        ErrorAlertStore.update(prev => {
            let [a, ...rest] = prev
            return rest
        })
    }

</script>

{#each $SuccessAlertStore as successMessage}
    <div class="alert alert-success" role="alert">
        {successMessage}
        <button on:click={handleSuccessClick}>
            <span aria-hidden="true">&times;</span>
        </button>
    </div>
{/each}
{#each $ErrorAlertStore as errorMessage}
    <div class="alert alert-danger" role="alert">
        {errorMessage}
        <button on:click={handleErrorClick}>
            <span aria-hidden="true">&times;</span>
        </button>
    </div>
{/each}
