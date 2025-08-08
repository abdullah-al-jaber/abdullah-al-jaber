// ==UserScript==
// @name         Dynamic Loader
// @description  Dynamically Load user agents effortlessly
// @namespace    http://tampermonkey.net/
// @version      1.0
// @author       Abdullah Al Jaber
// @match        *://*/*
// @run-at       document-idle
// ==/UserScript==

const web_socket_check = async (web_socket_url: string): Promise<boolean> => {
  let promise = new Promise<boolean>((resolve) => {
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
    const json = await fetch("")
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    const data = await response.json();

    let all_ports = Object.keys(data).map(Number);
    let working_ports: number[] = [];
    for (let port of all_ports) {
      const web_socket_url = `ws://localhost:${port}/`;
      if (await check_web_socket(web_socket_url)) working_ports.push(port);
    }
    if (working_ports.length > 1) throw new Error("Multiple working ports found !");

    const html_url = data[working_ports[0]];
    if (!html_url) throw new Error("No HTML URL found for the working port!");

    const html = await fetch(html_url);
    if (!html.ok) throw new Error(`Failed to fetch HTML: ${html.statusText}`);

    const holder = document.createElement("div");
    holder.innerHTML = await html.text();

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

    document.body.appendChild(body);

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
