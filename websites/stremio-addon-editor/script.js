const API = "https://api.strem.io/api/";
let authKey = null;

const post = (url, body) =>
  fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }).then((res) => res.json());

async function login(event) {
  event?.preventDefault();

  const email = document.querySelector("#email").value;
  const password = document.querySelector("#password").value;
  const addons = document.querySelector("#addons");

  const response = await post(API + "login", {
    type: "Login",
    email,
    password,
  });
  authKey = response?.result?.authKey;

  if (!authKey) return alert("Login & Load Addons Failed!");

  const addonsResponse = await post(API + "addonCollectionGet", {
    type: "AddonCollectionGet",
    authKey,
  });

  addons.value = JSON.stringify(addonsResponse.result.addons, null, 2);
}

async function save() {
  const addons = document.querySelector("#addons");
  if (!authKey) return alert("Please Login & Load Addons First!");

  let parsed;
  try {
    parsed = JSON.parse(addons.value);
  } catch {
    return alert("INVALID ADDON JSON!");
  }

  await post(API + "addonCollectionSet", {
    type: "AddonCollectionSet",
    authKey,
    addons: parsed,
  });

  alert("Successfully Saved to Stremio!");
  addons.value = "";
  authKey = null;
}
