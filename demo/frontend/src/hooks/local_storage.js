import { useCallback, useState } from "react";

function useLocalStorage(key, initialValue) {
  const [value, _setValue] = useState(() => {
    const item = window.localStorage.getItem(key);
    try {
      return item ? JSON.parse(item) : initialValue;
    } catch (_) {
      return initialValue;
    }
  });
  const setValue = useCallback(
    (newValue) => {
      _setValue((oldValue) => {
        const valueToStore =
          newValue instanceof Function ? newValue(oldValue) : newValue;
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
        return valueToStore;
      });
    },
    [key, _setValue]
  );
  return [value, setValue];
}

export { useLocalStorage };
