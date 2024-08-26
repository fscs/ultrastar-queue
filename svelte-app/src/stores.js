import {writable} from "svelte/store";


export const QueueStore = writable([])

export const SongStore = writable([])

export const ErrorAlertStore = writable([])

export const SuccessAlertStore = writable([])

export const User = writable(null);

export const SearchResultStore = writable([])