const API = "https://api.strem.io/api/";
let authKey = null;

const post = (url, body) =>
  fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }).then((r) => r.json());

async function login(event) {
  event?.preventDefault();
  const email = document.querySelector("input#email").value;
  const password = document.querySelector("input#password").value;
  const r = await post(API + "login", { type: "Login", email, password });
  authKey = r?.result?.authKey;
  if (!authKey) return window.alert("Login & Load Addons Failed !");

  const a = await post(API + "addonCollectionGet", {
    type: "AddonCollectionGet",
    authKey,
  });

  addons.value = JSON.stringify(a.result.addons, null, 2);
}

async function save() {
  if (!authKey) return window.alert("Please Login & Load Addons First !");
  let parsed;
  try {
    parsed = JSON.parse(addons.value);
  } catch {
    return window.alert("INVALID ADDON JSON !");
  }

  const r = await post(API + "addonCollectionSet", {
    type: "AddonCollectionSet",
    authKey,
    addons: parsed,
  });

  window.alert("Successfully Saved to Stremio !");
  await login();
}
