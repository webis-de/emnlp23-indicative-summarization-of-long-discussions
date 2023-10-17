import axios from "axios";

import { baseURL } from "./config";

class HTTPError extends Error {
  constructor(code, detail) {
    super(`${code} ${detail}`);
    this.code = code;
    this.detail = detail;
  }
}

const instance = axios.create({
  baseURL,
});

async function _request(method, url, data, extraArgs = {}) {
  try {
    const response = await instance({
      method,
      url,
      data,
      ...extraArgs,
    });
    return response.data;
  } catch (error) {
    const { message, response, request } = error;
    if (message.startsWith("timeout")) {
      throw new Error(message);
    } else if (response) {
      if (response?.data?.success !== undefined) return response.data;
      throw new HTTPError(response.status, response.data.detail);
    } else if (request) {
      throw new Error("the request was made but no response was received");
    } else {
      throw new Error("setting up the request triggered an error");
    }
  }
}

function post(path, json, extraArgs) {
  return _request("post", path, json, extraArgs);
}
function get(path, extraArgs) {
  return _request("get", path, extraArgs);
}

export { post, get, HTTPError };
