import { useEffect, useState } from "react";

function useAsync(asyncFunction) {
  const [loading, setLoading] = useState(true);
  const [value, setValue] = useState(null);
  const [error, setError] = useState(null);
  useEffect(() => {
    let isValid = true;
    const controller = new AbortController();
    setLoading(true);
    setValue(null);
    setError(null);
    asyncFunction(controller.signal)
      .then((e) => {
        if (isValid) setValue(e);
      })
      .catch((e) => {
        if (isValid) setError(e);
      })
      .finally(() => {
        if (isValid) setLoading(false);
      });
    return () => {
      isValid = false;
      controller.abort();
    };
  }, [asyncFunction]);
  return { loading, value, error };
}

export { useAsync };
