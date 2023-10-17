import { useCallback, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { getStoredList, getStoredThread } from "../api";
import { useAsync } from "../hooks/async";
import { GeneralError, SuccessFalseError } from "./Error";
import { ListItem } from "./ListItem";
import { CenterLoading } from "./Loading";
import { Pagination, usePagination } from "./Pagination";
import { Search, useSearch } from "./Search";
import { Thread } from "./Thread";

const searchKeys = ["title", "url", "labels"];

function StoredListResults({ list }) {
  const { query, setQuery, filtered } = useSearch(list, searchKeys);
  const [initialSize, setInitialSize] = useState(10);
  const pagination = usePagination(filtered.length, {
    maxSize: 100,
    initialSize,
  });
  const { page, size, setSize } = pagination;
  const paginationProps = {
    ...pagination,
    setSize: (newSize) => {
      setInitialSize(newSize);
      setSize(newSize);
    },
  };
  return (
    <div>
      <div className="flex flex-wrap justify-between gap-x-4 pb-2">
        <h1 className="text-xl font-bold text-blue-800">Past Computations</h1>
      </div>
      <div>
        <div className="flex items-center justify-between gap-4 pb-2">
          <div className="max-w-[400px] grow">
            <Search query={query} setQuery={setQuery} />
          </div>
          <Pagination {...paginationProps} />
        </div>
        <div className="flex flex-col gap-2">
          {filtered
            .slice((page - 1) * size, page * size)
            .map(({ id, ...props }) => (
              <ListItem
                key={id}
                to={`/stored?id=${id}`}
                labelsUrl={`/api/stored/labels?id=${id}`}
                id={id}
                {...props}
              />
            ))}
        </div>
      </div>
    </div>
  );
}

function StoredList() {
  const { loading, value, error } = useAsync(getStoredList);
  if (loading) {
    return <CenterLoading message="fetching past computations" />;
  }
  if (error) {
    return <GeneralError error={error} />;
  }
  if (!value.success) {
    return <SuccessFalseError {...value} />;
  }
  if (!value.data.length) {
    return (
      <div className="flex items-center justify-center">
        <span className="font-bold text-blue-800">
          No past computations yet
        </span>
      </div>
    );
  }
  return <StoredListResults list={value.data} />;
}

function Stored({ id, labelModel, frameModel, cluster }) {
  const getThread = useCallback(() => getStoredThread(id), [id]);
  const { value, loading, error } = useAsync(getThread);
  if (loading) {
    return <CenterLoading message="fetching stored discussion" />;
  }
  if (error) {
    return <GeneralError error={error} retryPath="/from_url" />;
  }
  if (!value.success) {
    return <SuccessFalseError {...value} retryPath="/from_url" />;
  }
  return (
    <Thread
      thread={value.data}
      labelModel={labelModel}
      frameModel={frameModel}
      cluster={cluster}
    />
  );
}

function StoredParams() {
  const [searchParams] = useSearchParams();
  const id = searchParams.get("id");
  const labelModel = searchParams.get("labelModel");
  const frameModel = searchParams.get("frameModel");
  const cluster = searchParams.get("cluster");
  if (id)
    return (
      <Stored
        id={id}
        labelModel={labelModel}
        frameModel={frameModel}
        cluster={cluster}
      />
    );
  return <div>id is not provided</div>;
}

export { StoredList, StoredParams };
