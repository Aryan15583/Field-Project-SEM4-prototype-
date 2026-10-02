// Passkeys in the browser: turn the server's JSON options into WebAuthn calls and the result back into JSON.
import { api } from "./api";

const toBytes = (b64url) => {
  const b64 = b64url.replace(/-/g, "+").replace(/_/g, "/") + "===".slice((b64url.length + 3) % 4);
  return Uint8Array.from(atob(b64), (c) => c.charCodeAt(0));
};
const toB64url = (buf) =>
  btoa(String.fromCharCode(...new Uint8Array(buf)))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");

export const passkeysSupported = () => typeof window !== "undefined" && !!window.PublicKeyCredential && !!navigator.credentials;

function creationOptions(o) {
  if (PublicKeyCredential.parseCreationOptionsFromJSON) return PublicKeyCredential.parseCreationOptionsFromJSON(o);
  return {
    ...o,
    challenge: toBytes(o.challenge),
    user: { ...o.user, id: toBytes(o.user.id) },
    excludeCredentials: (o.excludeCredentials || []).map((c) => ({ ...c, id: toBytes(c.id) })),
  };
}

function requestOptions(o) {
  if (PublicKeyCredential.parseRequestOptionsFromJSON) return PublicKeyCredential.parseRequestOptionsFromJSON(o);
  return { ...o, challenge: toBytes(o.challenge), allowCredentials: (o.allowCredentials || []).map((c) => ({ ...c, id: toBytes(c.id) })) };
}

function credentialJSON(cred) {
  if (typeof cred.toJSON === "function") return cred.toJSON();
  const r = cred.response;
  const response = { clientDataJSON: toB64url(r.clientDataJSON) };
  if (r.attestationObject) {
    response.attestationObject = toB64url(r.attestationObject);
    response.transports = r.getTransports ? r.getTransports() : [];
  } else {
    response.authenticatorData = toB64url(r.authenticatorData);
    response.signature = toB64url(r.signature);
    if (r.userHandle) response.userHandle = toB64url(r.userHandle);
  }
  return { id: cred.id, rawId: toB64url(cred.rawId), type: cred.type, response, clientExtensionResults: cred.getClientExtensionResults?.() || {} };
}

/** "Cancelled" (the person closed the dialog) is not an error worth showing. */
export const cancelled = (e) => e?.name === "NotAllowedError" || e?.name === "AbortError";

/** A friendly default name like "Chrome on Windows". */
export function deviceName() {
  const ua = navigator.userAgent;
  const os = /iPhone|iPad/.test(ua) ? "iPhone" : /Android/.test(ua) ? "Android" : /Mac/.test(ua) ? "Mac" : /Windows/.test(ua) ? "Windows" : /Linux/.test(ua) ? "Linux" : "this device";
  const browser = /Edg\//.test(ua) ? "Edge" : /Firefox\//.test(ua) ? "Firefox" : /Chrome\//.test(ua) ? "Chrome" : /Safari\//.test(ua) ? "Safari" : "Browser";
  return `${browser} on ${os}`;
}

export async function addPasskey(name) {
  const options = await api("/api/auth/passkeys/register/options", { method: "POST" });
  const cred = await navigator.credentials.create({ publicKey: creationOptions(options) });
  return api("/api/auth/passkeys/register", { method: "POST", body: { credential: credentialJSON(cred), name } });
}

export async function signInWithPasskey() {
  const options = await api("/api/auth/passkeys/login/options", { method: "POST" });
  const cred = await navigator.credentials.get({ publicKey: requestOptions(options) });
  return api("/api/auth/passkeys/login", { method: "POST", body: { credential: credentialJSON(cred) } });
}
