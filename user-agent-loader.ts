// ==UserScript==
// @name         User Agent Loader
// @description  Load user agents effortlessly
// @namespace    http://tampermonkey.net/
// @version      1.0
// @author       Abdullah Al Jaber
// @match        *://*/*
// @run-at       document-idle
// ==/UserScript==

type user_agent = {
  html_url: string;
  web_socket_url: string;
};

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

const user_agent_load = async (user_agent: user_agent): Promise<void> => {
  const html = await custom_fetch(user_agent.html_url);

  const user_agent_element = document.createElement("div");
  user_agent_element.id = "user_agent_element";

  const shadow = user_agent_element.attachShadow({ mode: "open" });

  const head = user_agent_element.querySelector("div#head");
  const body = user_agent_element.querySelector("div#body");

  if (!head || !body) throw new Error("Invalid HTML structure: Missing head or body");

  const link_tags = Array.from(head.querySelectorAll("link"));
  for (const link_tag of link_tags) {
    shadow.append(link_tag);
  }

  shadow.innerHTML += body.innerHTML;

  const script_tags = head.querySelectorAll("script");
  script_tags.forEach((old_tag) => {
    const new_tag = document.createElement("script");
    new_tag.src = old_tag.src;
    shadow.append(new_tag);
  });
};

const user_agent_loader = async () => {
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
    [tag_element.id, tag_element.innerText] = ["user_agent_tag", user_agent_name];
    const tag_element_style: Partial<CSSStyleDeclaration> = {
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

    await user_agent_load(user_agent);

    console.log("MAIN PROCESS SUCCESS");
  } catch (error) {
    console.log("MAIN PROCESS FAILURE");
    console.error(error);
  }
};

if (window.top == window.self) {
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", user_agent_loader);
  else user_agent_loader();
}
