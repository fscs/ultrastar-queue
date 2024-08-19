<script>
  import Navbar from "$lib/Navbar.svelte";
</script>


<Navbar />

<main class="container">
    <div class="bg-body-tertiary p-5">
        <slot />
    </div>
</main>