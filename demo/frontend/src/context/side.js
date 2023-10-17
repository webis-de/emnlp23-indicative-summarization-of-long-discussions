import React from "react";

const SideContext = React.createContext();

function SideProvider({ side, canActivate = false, parentRef, children, light }) {
  return (
    <SideContext.Provider
      value={{ side: side.toString(), canActivate, parentRef, light }}
    >
      {children}
    </SideContext.Provider>
  );
}

export { SideContext, SideProvider };
