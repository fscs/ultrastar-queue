const serverRoute = "http://localhost:8000"

const adminRoute = "/admin"
const queueRoute = "/queue"
const songsRoute = "/songs"
const authRoute = ""


// QUEUE
export const getQueueURL = `${serverRoute}${queueRoute}/`
export const getProcessedEntriesURL = `${serverRoute}${queueRoute}/processed-entries`
export const addEntryToQueueURL = `${serverRoute}${queueRoute}/add-entry`


// SONGS
export const getSongsURL = `${serverRoute}${songsRoute}/`
export const getSongsByCriteriaURL = `${serverRoute}${songsRoute}/get-songs-by-criteria`
export const getSongByIdURL = `${serverRoute}${songsRoute}`


// AUTH
export const tokenURL = `${serverRoute}${authRoute}/token`
export const loginURL = `${serverRoute}${authRoute}/login`
export const logoutURL = `${serverRoute}${authRoute}/logout`
export const getCurrentUserURL = `${serverRoute}${authRoute}/current-user`


// ADMIN
export const addEntryToQueueAsAdminURL = `${serverRoute}${adminRoute}/add-entry-as-admin`
export const removeEntryFromQueueURL = `${serverRoute}${adminRoute}/remove-entry`
export const markEntryAtIndexAsProcessedURL = `${serverRoute}${adminRoute}/mark-entry-at-index-as-processed`
export const getQueueIsOpenURL = `${serverRoute}${adminRoute}/get-queue-is-open`
export const getTimeBetweenSameSongURL = `${serverRoute}${adminRoute}/get-time-between-same-song`
export const getMaxTimesSongCanBeSungURL = `${serverRoute}${adminRoute}/get-max-times-song-can-be-sung`
export const getTimeBetweenSongSubmissionsURL = `${serverRoute}${adminRoute}/get-time-between-song-submissions`
export const setQueueIsOpenURL = `${serverRoute}${adminRoute}/set-queue-is-open`
export const setTimeBetweenSameSongURL = `${serverRoute}${adminRoute}/set-time-between-same-song`
export const setMaxTimesSongCanBeSungURL = `${serverRoute}${adminRoute}/set-max-times-song-can-be-sung`
export const setTimeBetweenSongSubmissionsURL = `${serverRoute}${adminRoute}/set-time-between-song-submissions`
export const clearQueueURL = `${serverRoute}${adminRoute}/clear-queue`
export const clearProcessedEntriesURL = `${serverRoute}${adminRoute}/clear-processed-entries`
export const clearQueueServiceURL = `${serverRoute}${adminRoute}/clear-queue-service`
