/** @type {import('@sveltejs/kit').HandleFetch} */
export async function handleFetch({event, request, fetch}) {
    if (request.url.startsWith('http://localhost:8000/')) {
        request.headers.set('cookie', event.request.headers.get('cookie'));

    }
    if (request.url.startsWith('http://127.0.0.1:8000/')) {
        request.headers.set('cookie', event.request.headers.get('cookie'));

    }
    console.log(request.headers)
    return fetch(request);
}