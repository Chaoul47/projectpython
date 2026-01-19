const keyInput = document.getElementById("key");
const messageInput = document.getElementById("message");
const encryptButton = document.getElementById("encrypt");
const encryptStatus = document.getElementById("encrypt-status");
const encryptResult = document.getElementById("encrypt-result");
const decryptButton = document.getElementById("decrypt");
const decryptStatus = document.getElementById("decrypt-status");
const decryptResult = document.getElementById("decrypt-result");
const messageIdInput = document.getElementById("message-id");
const refreshButton = document.getElementById("refresh");
const messagesList = document.getElementById("messages");
const generateKeyButton = document.getElementById("generate-key");

function base64UrlEncode(bytes) {
  let binary = "";
  bytes.forEach((value) => {
    binary += String.fromCharCode(value);
  });
  const base64 = btoa(binary);
  return base64.replaceAll("+", "-").replaceAll("/", "_");
}

function setStatus(element, message, isError = false) {
  element.textContent = message;
  element.classList.toggle("error", isError);
}

async function refreshMessages() {
  const response = await fetch("/api/messages");
  const data = await response.json();
  messagesList.innerHTML = "";
  data.messages.forEach((message) => {
    const item = document.createElement("li");
    item.textContent = `#${message.id} — ${message.created_at}`;
    messagesList.appendChild(item);
  });
}

generateKeyButton.addEventListener("click", () => {
  const bytes = new Uint8Array(32);
  window.crypto.getRandomValues(bytes);
  keyInput.value = base64UrlEncode(bytes);
});

encryptButton.addEventListener("click", async () => {
  setStatus(encryptStatus, "");
  encryptResult.textContent = "";

  const message = messageInput.value.trim();
  const key = keyInput.value.trim();

  const response = await fetch("/api/encrypt", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, key }),
  });

  const data = await response.json();
  if (!response.ok) {
    setStatus(encryptStatus, data.error || "Unable to encrypt message.", true);
    return;
  }

  setStatus(encryptStatus, "Message encrypted and stored.");
  encryptResult.textContent = `Message ID: ${data.id}`;
  messageInput.value = "";
  await refreshMessages();
});

decryptButton.addEventListener("click", async () => {
  setStatus(decryptStatus, "");
  decryptResult.textContent = "";

  const key = keyInput.value.trim();
  const id = messageIdInput.value.trim();

  const response = await fetch("/api/decrypt", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id, key }),
  });

  const data = await response.json();
  if (!response.ok) {
    setStatus(decryptStatus, data.error || "Unable to decrypt message.", true);
    return;
  }

  setStatus(decryptStatus, `Decrypted (created ${data.created_at}).`);
  decryptResult.textContent = data.message;
});

refreshButton.addEventListener("click", async () => {
  await refreshMessages();
});

refreshMessages();
