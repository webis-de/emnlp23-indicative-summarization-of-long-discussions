import Fuse from "fuse.js";
import React, { useDeferredValue, useMemo, useState } from "react";
import { FaSearch } from "react-icons/fa";

function Search({ query, setQuery }) {
  return (
    <div className="relative w-full">
      <div className="pointer-events-none absolute inset-y-0 left-0 z-10 flex items-center pl-[12px]">
        <FaSearch size={18} className="text-gray-600" />
      </div>
      <input
        type="text"
        placeholder="Search"
        value={query}
        onChange={(e) => setQuery(e.currentTarget.value)}
        className="block w-full rounded-lg bg-white py-[4px] pl-[38px] text-sm text-gray-900 outline outline-2 outline-slate-400 transition-[outline-color] hover:outline-slate-600 focus:bg-blue-50 focus:outline-blue-600"
      />
    </div>
  );
}

function useSearch(list, keys) {
  const fuse = useMemo(() => new Fuse(list, { keys }), [list, keys]);
  const [query, setQuery] = useState("");
  const deferredQuery = useDeferredValue(query);
  const filtered = useMemo(() => {
    if (!deferredQuery) return list;
    return fuse.search(deferredQuery).map(({ item }) => item);
  }, [fuse, list, deferredQuery]);
  return { query, setQuery, filtered, listKey: deferredQuery };
}

export { useSearch, Search };
