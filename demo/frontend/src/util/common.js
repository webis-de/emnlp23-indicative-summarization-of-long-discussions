function defined(obj) {
  return obj !== null && obj !== undefined;
}

function setUrlParams(url, params) {
  url = url.split("?");
  const usp = new URLSearchParams(url[1]);
  Object.entries(params).forEach(([key, value]) => {
    usp.set(key, value);
  });
  url[1] = usp.toString();
  return url.join("?");
}

function definedParseInt(integer) {
  if (defined(integer)) return parseInt(integer, 10);
  return integer;
}

function toTitlecase(string) {
  return string.substring(0, 1).toUpperCase() + string.substring(1);
}

export { defined, setUrlParams, definedParseInt, toTitlecase };
