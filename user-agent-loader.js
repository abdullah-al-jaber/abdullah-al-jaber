"use strict";
// ==UserScript==
// @name         User Agent Loader
// @description  Load user agents effortlessly
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
    try {
        let promise = new Promise((resolve, reject) => {
            const web_socket = new WebSocket(web_socket_url);
            web_socket.onopen = () => resolve(web_socket);
            web_socket.onerror = () => reject(new Error("Web Socket connection failed !"));
        });
        let web_socket = await promise;
        web_socket.close();
        return true;
    }
    catch {
        return false;
    }
};
const load = async (user_agent) => {
    const html = await custom_fetch(user_agent.html_url);
    const user_agent_holder = document.createElement("div");
    user_agent_holder.id = "user_agent_holder";
    const shadow = user_agent_holder.attachShadow({ mode: "open" });
    const head = user_agent_holder.querySelector("div#head");
    const body = user_agent_holder.querySelector("div#body");
    if (!head || !body)
        throw new Error("Invalid HTML structure: Missing head or body");
    const link_tags = Array.from(head.querySelectorAll("link"));
    for (const link_tag of link_tags) {
        shadow.append(link_tag.cloneNode());
    }
    shadow.innerHTML += body.innerHTML;
    const script_tags = head.querySelectorAll("script");
    script_tags.forEach((old_tag) => {
        const new_tag = document.createElement("script");
        new_tag.src = old_tag.src;
        shadow.appendChild(new_tag);
    });
};
const user_agent_loader = async () => {
    try {
        const user_agents_json = await custom_fetch("https://abdullah-al-jaber.github.io/abdullah-al-jaber/user-agents.json");
        const user_agents = JSON.parse(user_agents_json);
        if (!user_agents || typeof user_agents !== "object")
            throw new Error("Invalid user agents JSON format");
        for (const [user_agent_name, user_agent] of Object.entries(user_agents)) {
            if (!(await web_socket_check(user_agent.web_socket_url)))
                delete user_agents[user_agent_name];
        }
        if (Object.keys(user_agents).length != 1)
            throw new Error("No user agent found!");
        const [[user_agent_name, user_agent]] = Object.entries(user_agents);
        const tag_element = document.createElement("div");
        [tag_element.id, tag_element.innerText] = ["tag_element", user_agent_name];
        const tag_element_style = {
            position: "fixed",
            top: "100%",
            left: "100%",
            zIndex: "9999",
            transform: "translate(-100% -100%)",
            padding: "5px",
            fontFamily: "monospace",
            fontSize: "10px",
            letterSpacing: "2px",
            whiteSpace: "nowrap",
            backgroundColor: "#404040",
            color: "#f0f0f0",
        };
        Object.assign(tag_element.style, tag_element_style);
        document.body.append(tag_element);
        await load(user_agent);
        console.log("MAIN PROCESS SUCCESS");
    }
    catch (error) {
        console.log("MAIN PROCESS FAILURE");
    }
};
if (window.top == window.self) {
    if (document.readyState === "loading")
        document.addEventListener("DOMContentLoaded", user_agent_loader);
    else
        user_agent_loader();
}
