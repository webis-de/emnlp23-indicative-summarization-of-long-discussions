import { useCallback, useContext } from "react";
import { useLocation, useSearchParams } from "react-router-dom";

import { getThreadFromPrecomputed } from "../api";
import { PrecomputedListContext } from "../context/precomputed_list";
import { useAsync } from "../hooks/async";
import { Container } from "./Container";
import { GeneralError, SuccessFalseError } from "./Error";
import { ListItem } from "./ListItem";
import { CenterLoading } from "./Loading";
import { Thread } from "./Thread";

function Precomputed({ id, labelModel, frameModel, cluster }) {
  const getThread = useCallback(
    (signal) => getThreadFromPrecomputed(id, signal),
    [id]
  );
  const { value, loading, error } = useAsync(getThread);
  const { pathname } = useLocation();
  if (loading) {
    return <CenterLoading message="fetching precomputed discussion" />;
  }
  if (error) {
    return <GeneralError error={error} retryPath={pathname} />;
  }
  if (!value.success) {
    return <SuccessFalseError {...value} retryPath={pathname} />;
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

function PrecomputedList() {
  const { value, loading, error } = useContext(PrecomputedListContext);
  const { pathname } = useLocation();
  if (loading) {
    return <CenterLoading message="getting list of precomputed discussions" />;
  }
  if (error) {
    return <GeneralError error={error} retryPath={pathname} />;
  }
  if (!value.success) {
    return <SuccessFalseError {...value} retryPath={pathname} />;
  }
  return (
    <div className="overflow-y-auto pb-20 pt-2">
      <Container>
        <div className="flex items-center justify-end gap-4 pb-1 text-sm text-slate-700">
          <span className="inline-block font-bold">Legend:</span>
          <div className="flex items-center gap-1">
            <div className="inline-block rounded bg-[#aeaeae] p-2" />
            <span>Pre-Instruct</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="inline-block rounded bg-[#99c299] p-2" />
            <span>Dialogue Instruction</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="inline-block rounded bg-[#6666c2] p-2" />
            <span>Direct Instruction</span>
          </div>
        </div>
        <div className="flex flex-col gap-2">
          {value.data.map(({ id, ...props }) => (
            <ListItem
              key={id}
              to={`/precomputed?id=${id}`}
              labelsUrl={`/api/precomputed/labels?id=${id}`}
              id={id}
              {...props}
            />
          ))}
        </div>
      </Container>
    </div>
  );
}

function PrecomputedParams() {
  const [searchParams] = useSearchParams();
  const id = searchParams.get("id");
  const labelModel = searchParams.get("labelModel");
  const frameModel = searchParams.get("frameModel");
  const cluster = searchParams.get("cluster");
  if (id)
    return (
      <Precomputed
        id={id}
        labelModel={labelModel}
        frameModel={frameModel}
        cluster={cluster}
      />
    );
  return <PrecomputedList />;
}

export { PrecomputedParams };
