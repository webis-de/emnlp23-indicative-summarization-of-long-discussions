import { useState } from "react";
import { Link } from "react-router-dom";

import { groupFrames } from "../hooks/thread";
import { defaultdict } from "../python";
import { defined, toTitlecase } from "../util/common";
import { oempty, transpose } from "../util/object";
import { Button } from "./Button";
import { AltCategories, TreeCategories } from "./Categories";
import { Modal, ModalTitle } from "./Modal";
import { Table, Tbody, Td, Th, Thead, Tr } from "./Table";
import { QuestionTooltip } from "./Tooltip";

function FrameSentences({ content }) {
  const allSentences = [];
  content.forEach(({ elements }, i) => {
    const jitter = i / content.length / 2;
    elements
      .sort(({ lambda: lambdaA }, { lambda: lambdaB }) => lambdaA - lambdaB)
      .forEach(({ text }, j) => {
        allSentences.push({
          text,
          score: (j + jitter) / elements.length,
        });
      });
  });
  allSentences.sort(({ score: scoreA }, { score: scoreB }) => scoreB - scoreA);
  return (
    <div className="divide-y divide-slate-400 overflow-y-auto px-4 py-2">
      {allSentences.slice(10).map(({ text }, i) => (
        <div key={i} className="p-[2px]">
          {text}
        </div>
      ))}
    </div>
  );
}

function getLabel(currentLabel, clusterId, labels, numElements) {
  let label;
  if (clusterId === -2) label = "Noisy Texts";
  else if (clusterId === -1) label = "Unclustered";
  else if (currentLabel) label = `${labels[currentLabel][clusterId]}`;
  else label = `Cluster ${clusterId}`;

  if (defined(numElements)) label = `${label} [${numElements}]`;

  return label;
}

function ClusterSelect({
  clusterOrder,
  currentCluster,
  setCurrentCluster,
  currentLabel,
  makeHref,
  labels,
  clusters,
  parentRef,
  level = 1,
}) {
  const nodes = Object.fromEntries(
    clusters.map(([clusterId, { color, elements }]) => [
      clusterId,
      {
        clusterId,
        color,
        elements,
        label: getLabel(currentLabel, clusterId, labels, elements.length),
      },
    ])
  );
  const [modalState, setModalState] = useState(null);
  const openModal = (root) => setModalState({ root });
  const closeModal = () => setModalState(null);
  if (clusterOrder.hasFrames) {
    const categories = clusterOrder.order.map(([frameLabel, clusterIds]) => [
      frameLabel,
      clusterIds.map((clusterId) => nodes[clusterId]),
    ]);
    const byIndex = [];
    categories.forEach(([, subCategories]) =>
      subCategories.forEach((c) => {
        byIndex.push(c.clusterId);
      })
    );
    return (
      <div>
        {modalState && (
          <Modal isOpen={Boolean(modalState)} close={closeModal} level={level}>
            <div className="flex w-full flex-col overflow-hidden">
              <div className="z-20 flex flex-wrap items-center justify-between gap-4 border-b bg-slate-100 p-5">
                <ModalTitle>{toTitlecase(modalState.root)}</ModalTitle>
                <div className="flex flex-wrap items-center gap-2">
                  <Button
                    appearance="soft"
                    variant="primary"
                    onClick={closeModal}
                  >
                    Close
                  </Button>
                </div>
              </div>
              <FrameSentences
                content={Object.fromEntries(categories)[modalState.root]}
              />
            </div>
          </Modal>
        )}
        <TreeCategories
          index={byIndex.findIndex((clusterId) => clusterId === currentCluster)}
          onRootClick={openModal}
          onChange={
            makeHref ? null : (index) => setCurrentCluster(byIndex[index])
          }
          makeHref={makeHref && ((index) => makeHref(byIndex[index]))}
          parentRef={parentRef}
          scrollKey={currentLabel}
          categories={categories}
        />
      </div>
    );
  }
  const categories = clusterOrder.order.map((clusterId) => nodes[clusterId]);
  return (
    <AltCategories
      index={categories.findIndex(
        ({ clusterId }) => clusterId === currentCluster
      )}
      onChange={
        makeHref
          ? null
          : (index) => {
              setCurrentCluster(categories[index].clusterId);
            }
      }
      makeHref={makeHref && ((index) => makeHref(categories[index].clusterId))}
      scrollKey={currentLabel}
      categories={categories}
      parentRef={parentRef}
      notNullable
    />
  );
}

function LabelMeta({ meta }) {
  return (
    <div className="divide-y divide-gray-500">
      {Object.entries(meta).map(([key, value]) => (
        <div key={key}>
          <span className="font-mono font-bold text-green-400">{key}</span>:{" "}
          <span>{defined(value) ? value : "none"}</span>
        </div>
      ))}
    </div>
  );
}

function makeTable(obj) {
  const thead = [];
  let tbody = defaultdict(() => []);
  Object.entries(obj).forEach(([header, cells]) => {
    thead.push(header);
    Object.entries(cells).forEach(([i, cell]) => {
      tbody[i].push(cell);
    });
  });
  tbody = Object.entries(tbody)
    .map(([k, v]) => [parseInt(k, 10), v])
    .sort(([k1], [k2]) => k1 - k2);
  return [thead, tbody];
}

function LabelContent({ onClick, makeHref, labels, meta }) {
  const [thead, tbody] = makeTable(labels);
  let className = "flex h-full w-full text-left p-[5px]";
  if (onClick || makeHref) {
    className += " hover:bg-blue-200";
  }
  return (
    <div className="grow overflow-y-auto">
      <Table>
        <Thead sticky>
          <Th>ID</Th>
          {thead.map((e, i) => {
            const labelMeta = meta?.labels?.[e];
            return (
              <th key={i}>
                <div className="flex items-center justify-center gap-1 px-6">
                  <div className="whitespace-nowrap py-3 text-sm font-medium uppercase tracking-wider text-gray-700">
                    {e}
                  </div>
                  <div className="flex justify-center text-left font-normal">
                    {labelMeta && (
                      <QuestionTooltip place="bottom">
                        <LabelMeta meta={labelMeta} />
                      </QuestionTooltip>
                    )}
                  </div>
                </div>
              </th>
            );
          })}
        </Thead>
        <Tbody>
          {tbody.map(([cluster, row]) => (
            <Tr key={cluster} fullHeight>
              <Td>{cluster}</Td>
              {row.map((label, labelModelIndex) => {
                const labelModel = thead[labelModelIndex];
                let inner;
                if (onClick) {
                  inner = (
                    <button
                      type="button"
                      onClick={() => onClick(labelModel, cluster)}
                      className={className}
                    >
                      {label}
                    </button>
                  );
                } else if (makeHref) {
                  inner = (
                    <Link
                      to={makeHref(labelModel, cluster)}
                      className={className}
                    >
                      {label}
                    </Link>
                  );
                } else {
                  inner = <div className={className}>{label}</div>;
                }
                return (
                  <Td key={labelModelIndex} left loose fullHeight>
                    {inner}
                  </Td>
                );
              })}
            </Tr>
          ))}
        </Tbody>
      </Table>
    </div>
  );
}

function LabelContent2({ makeHref, labels, frames, meta, clusters }) {
  const groupedFrames = transpose(frames || {});
  const summaries = Object.keys(labels).map((labelModel) => {
    const labelMeta = meta?.labels?.[labelModel];
    const _grouped = { ...(groupedFrames[labelModel] || {}) };
    if (oempty(_grouped)) _grouped[labelModel] = null;
    return Object.entries(_grouped).map(([frameModel, frameInfo]) => {
      const clusterOrder = groupFrames(frameInfo, clusters);
      return (
        <div
          key={`${labelModel}:${frameModel}`}
          className="break-inside-avoid rounded-sm border-2 border-slate-600"
        >
          <div className="flex items-center gap-1 bg-gray-300 pl-2">
            <div className="whitespace-nowrap py-3 text-sm font-bold uppercase tracking-wider text-gray-700">
              {labelModel}
            </div>
            <div className="flex justify-center text-left font-normal">
              {labelMeta && (
                <QuestionTooltip place="bottom">
                  <LabelMeta meta={labelMeta} />
                </QuestionTooltip>
              )}
            </div>
            {frameModel && frameModel !== labelModel && (
              <div className="text-sm text-slate-700">
                (frames: {frameModel})
              </div>
            )}
          </div>
          <ClusterSelect
            clusterOrder={clusterOrder}
            currentCluster={null}
            makeHref={(cluster) => makeHref(labelModel, frameModel, cluster)}
            currentLabel={labelModel}
            labels={labels}
            clusters={clusters}
            level={2}
          />
        </div>
      );
    });
  });
  return (
    <div
      className={`columns-1 gap-4 space-y-4 overflow-y-auto p-2 ${
        summaries.length > 1 ? "lg:columns-2" : ""
      }`}
    >
      {summaries}
    </div>
  );
}

export { LabelMeta, LabelContent, LabelContent2, ClusterSelect };
