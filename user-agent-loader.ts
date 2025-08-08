// ==UserScript==
// @name         User Agent Loader
// @description  Load user agents effortlessly
// @namespace    http://tampermonkey.net/
// @version      1.0
// @author       Abdullah Al Jaber
// @match        *://*/*
// @run-at       document-idle
// ==/UserScript==

const custom_fetch = async (url: string): Promise<string> => {
  let response = await fetch(url);
  if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
  return response.text();
};

const web_socket_check = async (web_socket_url: string): Promise<boolean> => {
  try {
    let promise = new Promise<WebSocket>((resolve, reject) => {
      const web_socket = new WebSocket(web_socket_url);
      web_socket.onopen = () => resolve(web_socket);
      web_socket.onerror = () => reject(new Error("Web Socket connection failed !"));
    });
    let web_socket = await promise;
    web_socket.close();
    return true;
  } catch {
    return false;
  }
};

type user_agent = {
  html_url: string;
  web_socket_url: string;
};

const dynamic_loader = async () => {
  try {
    const user_agents_json = await custom_fetch(
      "https://abdullah-al-jaber.github.io/abdullah-al-jaber/user-agents.json"
    );

    const user_agents = JSON.parse(user_agents_json) as Record<string, user_agent>;
    if (!user_agents || typeof user_agents !== "object") throw new Error("Invalid user agents JSON format");

    for (const [user_agent_name, user_agent] of Object.entries(user_agents)) {
      if (!(await web_socket_check(user_agent.web_socket_url))) delete user_agents[user_agent_name];
    }

    if (Object.keys(user_agents).length != 1) throw new Error("No user agent found!");
    const [[user_agent_name, user_agent]] = Object.entries(user_agents);

    const tag_element = document.createElement("div");
    [tag_element.id, tag_element.innerText] = ["tag_element", user_agent_name];
    const tag_element_style: Partial<CSSStyleDeclaration> = {};
    Object.assign(tag_element.style, tag_element_style);
    document.body.append(tag_element);

    const html = await custom_fetch(user_agent.html_url);

    const holder = document.createElement("div");
    holder.innerHTML = html;

    const head = holder.querySelector("div#head");
    const body = holder.querySelector("div#body");

    if (!head || !body) throw new Error("Invalid HTML structure: Missing head or body");

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
      } else {
        new_script.textContent = old_script.textContent;
      }
      document.body.appendChild(new_script);
    });

    console.log("MAIN PROCESS SUCCESS");
  } catch (error) {
    console.log("MAIN PROCESS FAILURE");
  }
};

if (window.top == window.self) {
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", dynamic_loader);
  else dynamic_loader();
}
