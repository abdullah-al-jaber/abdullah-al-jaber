document.addEventListener("DOMContentLoaded", () => {
  const API = "https://api.strem.io/api/";
  let authKey = null;

  const editor = CodeMirror(document.querySelector("#addons"), {
    value: "",
    mode: { name: "javascript", json: true },
    lineNumbers: true,
    lineWrapping: false,
    theme: "default",
  });

  const post = (url, body) =>
    fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then((response) => response.json());

  async function login(event) {
    event?.preventDefault();

    const email = document.querySelector("#email").value;
    const password = document.querySelector("#password").value;

    const response = await post(API + "login", {
      type: "Login",
      email,
      password,
    });
    authKey = response?.result?.authKey;

    if (!authKey) return window.window.alert("Login & Load Addons Failed!");

    const addonCollection = await post(API + "addonCollectionGet", {
      type: "AddonCollectionGet",
      authKey,
    });

    editor.setValue(JSON.stringify(addonCollection.result.addons, null, 2));
  }

  async function save() {
    try {
      if (!authKey) return window.alert("Please Login & Load Addons First!");
      let parsed_data = JSON.parse(editor.getValue());
      await post(API + "addonCollectionSet", {
        type: "AddonCollectionSet",
        authKey,
        addons: parsed_data,
      });
      window.alert("Successfully Saved to Stremio!");

      authKey = null;
      editor.setValue("");
    } catch {
      return window.alert("INVALID ADDON JSON!");
    }
  }
  window.login = login;
  window.save = save;
});
