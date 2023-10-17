import { get, post } from "./request";

async function getPrecomputedList() {
  return get("/api/list_precomputed");
}

async function getThreadFromPrecomputed(id, signal) {
  return post("/api/from_precomputed", { id }, { signal });
}

async function getThreadFromURL(url, options, signal) {
  return post("/api/from_url", { url, ...options }, { signal });
}

async function getStoredList() {
  return get("/api/stored");
}

async function getStoredThread(id) {
  return post("/api/stored", { id });
}

export {
  getPrecomputedList,
  getThreadFromPrecomputed,
  getThreadFromURL,
  getStoredList,
  getStoredThread,
};
