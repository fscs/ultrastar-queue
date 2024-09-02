import {ErrorAlertStore, SuccessAlertStore} from "../stores.js";

export const getSettingValue = (endpoint) => {

    return fetch(endpoint, {
        method: "GET",
        credentials: "include"
    })
        .then(response => {
            if (response.ok) {
                return response.json()
            } else {
                return Promise.reject(response)
            }
        })
        .catch((response) => {
            response.json().then((json) => {
                ErrorAlertStore.update(prev => [...prev, json["detail"]])
            })
        });

}

export const setSettingValue = (endpoint) => {

    fetch(endpoint, {
        method: "PUT",
        credentials: "include"
    })
        .then(response => {
            if (response.ok) {
                response.json().then((json) => {
                    SuccessAlertStore.update(prev => [...prev, json["message"]])
                })
            } else {
                return Promise.reject(response)
            }
        })
        .catch((response) => {
            response.json().then((json) => {
                ErrorAlertStore.update(prev => [...prev, json["detail"]])
            })
        });

}

export const deleteSettingValue = (endpoint) => {

    fetch(endpoint, {
        method: "DELETE",
        credentials: "include"
    })
        .then(response => {
            if (response.ok) {
                response.json().then((json) => {
                    SuccessAlertStore.update(prev => [...prev, json["message"]])
                })
            } else {
                return Promise.reject(response)
            }
        })
        .catch((response) => {
            response.json().then((json) => {
                ErrorAlertStore.update(prev => [...prev, json["detail"]])
            })
        });

}