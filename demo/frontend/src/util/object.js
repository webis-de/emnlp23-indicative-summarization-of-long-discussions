import { defaultdict } from "../python";

function omap(obj, func, kind = "value") {
  switch (kind) {
    case "value":
      return Object.fromEntries(
        Object.entries(obj).map(([key, value]) => [key, func(value, key)])
      );
    case "full":
      return Object.fromEntries(
        Object.entries(obj).map(([key, value]) => func(key, value))
      );
    case "key":
      return Object.fromEntries(
        Object.entries(obj).map(([key, value]) => [func(key, value), value])
      );
    default:
      throw new Error(`unknown kind ${kind}`);
  }
}

function ofilter(obj, func) {
  return Object.fromEntries(
    Object.entries(obj).filter(([key, value]) => func(key, value))
  );
}

function ofold(objects, func, values = []) {
  if (!objects.length) return func(values);
  const [obj, ...rest] = objects;
  return omap(obj, (value) => ofold(rest, func, [...values, value]));
}

function oempty(obj) {
  return Object.keys(obj).length === 0;
}

function pack(name, obj, other) {
  if (!obj) return null;
  return omap(obj, (value, key) => ({
    ...omap(other, (otherObj) => otherObj[key]),
    [name]: value,
  }));
}

function unpack(obj, subKey) {
  return omap(obj, (value) => value[subKey]);
}

function transpose(obj) {
  const transposed = defaultdict(() => ({}));
  Object.entries(obj).forEach(([key, subObj]) => {
    Object.entries(subObj).forEach(([subKey, value]) => {
      transposed[subKey][key] = value;
    });
  });
  return { ...transposed };
}

export { omap, ofilter, ofold, oempty, pack, unpack, transpose };
