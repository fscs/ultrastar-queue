export const intToDateStr = (seconds) => {
    let date = new Date(0, 0, 0, 0, 0, seconds)
    let min = date.getMinutes() < 10 ? `0${date.getMinutes()}` : `${date.getMinutes()}`
    let sec = date.getSeconds() < 10 ? `0${date.getSeconds()}` : `${date.getSeconds()}`
    return `${date.getHours()}:${min}:${sec}`
}