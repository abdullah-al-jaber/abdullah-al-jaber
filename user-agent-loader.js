"use strict";
// ==UserScript==
// @name         Dynamic Loader
// @description  Dynamically Load user agents effortlessly
// @namespace    http://tampermonkey.net/
// @version      1.0
// @author       Abdullah Al Jaber
// @match        *://*/*
// @run-at       document-idle
// ==/UserScript==
const custom_fetch = async (url) => {
    let response = await fetch(url);
    if (!response.ok)
        throw new Error(`HTTP error! status: ${response.status}`);
    return response.text();
};
const web_socket_check = async (web_socket_url) => {
    let promise = new Promise((resolve) => {
        const web_socket = new WebSocket(web_socket_url);
        web_socket.onopen = () => {
            web_socket.close();
            resolve(true);
        };
        web_socket.onerror = () => {
            resolve(false);
        };
    });
    return promise;
};
const dynamic_loader = async () => {
    try {
        const user_agents_json = await custom_fetch("https://abdullah-al-jaber.github.io/abdullah-al-jaber/user-agents.json");
        const user_agents = JSON.parse(user_agents_json);
        if (!user_agents || typeof user_agents !== "object")
            throw new Error("Invalid user agents JSON format");
        let web_socket_urls = Object.keys(user_agents);
        for (const web_socket_url of web_socket_urls) {
            if (typeof web_socket_url !== "string")
                continue;
            if (!(await web_socket_check(web_socket_url)))
                web_socket_urls = web_socket_urls.splice(web_socket_urls.indexOf(web_socket_url), 1);
        }
        if (web_socket_urls.length != 1)
            throw new Error("No Single WebSocket URLs found!");
        const web_socket_url = web_socket_urls[0];
        const html_url = user_agents[web_socket_url];
        const html = await custom_fetch(html_url);
        const holder = document.createElement("div");
        holder.innerHTML = html;
        const head = holder.querySelector("div#head");
        const body = holder.querySelector("div#body");
        if (!head || !body)
            throw new Error("Invalid HTML structure: Missing head or body");
        const links = head.querySelectorAll("link");
        links.forEach((old_link) => {
            const new_link = document.createElement("link");
            new_link.rel = old_link.rel;
            new_link.href = old_link.href;
            document.head.appendChild(new_link);
        });
        document.body.innerHTML += body.innerHTML;
        const scripts = holder.querySelectorAll("script");
        scripts.forEach((old_script) => {
            const new_script = document.createElement("script");
            if (old_script.src) {
                new_script.src = old_script.src;
            }
            else {
                new_script.textContent = old_script.textContent;
            }
            document.body.appendChild(new_script);
        });
        console.log("MAIN PROCESS SUCCESS");
    }
    catch (error) {
        console.log("MAIN PROCESS FAILURE");
    }
};
if (window.top == window.self) {
    if (document.readyState === "loading")
        document.addEventListener("DOMContentLoaded", dynamic_loader);
    else
        dynamic_loader();
}
