import axios from "axios";
import { baseURL } from "./config";

const instance = axios.create({
  baseURL,
  timeout: 3000,
});

const request = (method, url, data) =>
  instance
    .request({
      method,
      url,
      data,
    })
    .then(({ data }) => data)
    .catch(({ response, request }) => {
      if (response) {
        throw new Error(`${response.status} ${response.statusText}`);
      } else if (request) {
        throw new Error("the request was made but no response was received");
      } else {
        throw new Error("setting up the request triggered an error");
      }
    });

const post = (path, json) => request("post", path, json);
const get = (path) => request("get", path);

export { post, get };
