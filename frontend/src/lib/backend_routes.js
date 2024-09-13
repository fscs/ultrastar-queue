const serverRoute = "http://localhost:8000"

const adminRoute = "/admin"
const queueRoute = "/queue"
const songsRoute = "/songs"
const authRoute = ""


// QUEUE
export const getQueueURL = `${serverRoute}${queueRoute}/`
export const getProcessedSongsURL = `${serverRoute}${queueRoute}/processed-songs`
export const addSongToQueueURL = `${serverRoute}${queueRoute}/add-song`


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
export const addSongToQueueAsAdminURL = `${serverRoute}${adminRoute}/add-song-as-admin`
export const checkFirstSongInQueueURL = `${serverRoute}${adminRoute}/check-first-song`
export const removeSongFromQueueURL = `${serverRoute}${adminRoute}/remove-song`
export const checkSongInQueueByIndexURL = `${serverRoute}${adminRoute}/check-song-by-index`
export const getQueueIsOpenURL = `${serverRoute}${adminRoute}/get-queue-is-open`
export const getTimeBetweenSameSongURL = `${serverRoute}${adminRoute}/get-time-between-same-song`
export const getMaxTimesSongCanBeSungURL = `${serverRoute}${adminRoute}/get-max-times-song-can-be-sung`
export const getTimeBetweenSongSubmissionsURL = `${serverRoute}${adminRoute}/get-time-between-song-submissions`
export const setQueueIsOpenURL = `${serverRoute}${adminRoute}/set-queue-is-open`
export const setTimeBetweenSameSongURL = `${serverRoute}${adminRoute}/set-time-between-same-song`
export const setMaxTimesSongCanBeSungURL = `${serverRoute}${adminRoute}/set-max-times-song-can-be-sung`
export const setTimeBetweenSongSubmissionsURL = `${serverRoute}${adminRoute}/set-time-between-song-submissions`
export const clearQueueURL = `${serverRoute}${adminRoute}/clear-queue`
export const clearProcessedSongsURL = `${serverRoute}${adminRoute}/clear-processed-songs`
export const clearQueueServiceURL = `${serverRoute}${adminRoute}/clear-queue-service`
export const createSongURL = `${serverRoute}${adminRoute}/create-song`
