import React from "react";

import { getPrecomputedList } from "../api";
import { useAsync } from "../hooks/async";

const PrecomputedListContext = React.createContext();

function PrecomputedListProvider({ children }) {
  const value = useAsync(getPrecomputedList);
  return (
    <PrecomputedListContext.Provider value={value}>
      {children}
    </PrecomputedListContext.Provider>
  );
}

export { PrecomputedListContext, PrecomputedListProvider };
