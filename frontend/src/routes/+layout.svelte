<script>
    import Navbar from "$lib/Navbar.svelte";
    import Alert from "$lib/Alert.svelte";
</script>


<Navbar/>

<main class="container">
    <div class="bg-body-tertiary p-5">
        <Alert/>
        <slot>
            <em>Something went wrong</em>
        </slot>
    </div>
</main>