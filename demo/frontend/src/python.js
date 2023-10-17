function defaultdict(init) {
  return new Proxy(
    {},
    {
      get: (object, name) => {
        if (!(name in object)) {
          object[name] = init();
        }
        return object[name];
      },
    }
  );
}

export { defaultdict };
