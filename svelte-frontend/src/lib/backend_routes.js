const serverRoute = "http://localhost:8000"

const adminRoute = "/admin"
const queueRoute = "/queue"
const songsRoute = "/songs"
const authRoute = ""


// QUEUE
export const getQueueURL = new URL(`${serverRoute}${queueRoute}/`)
export const getProcessedSongsURL = new URL(`${serverRoute}${queueRoute}/processed-songs`)
export const addSongToQueueURL = new URL(`${serverRoute}${queueRoute}/add-song`)


// SONGS
export const getSongsURL = new URL(`${serverRoute}${songsRoute}/`)
export const getSongsByCriteriaURL = new URL(`${serverRoute}${songsRoute}/get-songs-by-criteria`)
export const getSongByIdURL = new URL(`${serverRoute}${songsRoute}`)


// AUTH
export const tokenURL = new URL(`${serverRoute}${authRoute}/token`)
export const loginURL = new URL(`${serverRoute}${authRoute}/login`)
export const logoutURL = new URL(`${serverRoute}${authRoute}/logout`)
export const getCurrentUserURL = new URL(`${serverRoute}${authRoute}/current-user`)


// ADMIN
export const addSongToQueueAsAdminURL = new URL(`${serverRoute}${adminRoute}/add-song-as-admin`)
export const checkFirstSongInQueueURL = new URL(`${serverRoute}${adminRoute}/check-first-song`)
export const removeSongFromQueueURL = new URL(`${serverRoute}${adminRoute}/remove-song`)
export const checkSongInQueueByIndexURL = new URL(`${serverRoute}${adminRoute}/check-song-by-index`)
export const getIsQueueOpenURL = new URL(`${serverRoute}${adminRoute}/get-is-queue-open`)
export const getTimeBetweenSameSongURL = new URL(`${serverRoute}${adminRoute}/get-time-between-same-song`)
export const getMaxTimesSongCanBeSungURL = new URL(`${serverRoute}${adminRoute}/get-max-times-song-can-be-sung`)
export const getTimeBetweenSubmittingSongsURL = new URL(`${serverRoute}${adminRoute}/get-time-between-submitting-songs`)
export const getBlockSubmittingSongsInTimeframeURL = new URL(`${serverRoute}${adminRoute}/get-block-submitting-songs-in-timeframe`)
export const setIsQueueOpenURL = new URL(`${serverRoute}${adminRoute}/set-is-queue-open`)
export const setTimeBetweenSameSongURL = new URL(`${serverRoute}${adminRoute}/set-time-between-same-song`)
export const setMaxTimesSongCanBeSungURL = new URL(`${serverRoute}${adminRoute}/set-max-times-song-can-be-sung`)
export const setTimeBetweenSubmittingSongsURL = new URL(`${serverRoute}${adminRoute}/set-time-between-submitting-songs`)
export const setBlockSubmittingSongsInTimeframeURL = new URL(`${serverRoute}${adminRoute}/set-block-submitting-songs-in-timeframe`)
export const clearQueueURL = new URL(`${serverRoute}${adminRoute}/clear-queue`)
export const clearProcessedSongsURL = new URL(`${serverRoute}${adminRoute}/clear-processed-songs`)
export const clearQueueServiceURL = new URL(`${serverRoute}${adminRoute}/clear-queue-service`)
export const createSongURL = new URL(`${serverRoute}${adminRoute}/create-song`)
