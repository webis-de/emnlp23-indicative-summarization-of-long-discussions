import React, { useContext, useReducer, useRef, useState } from "react";
import { FaReddit } from "react-icons/fa";
import { TbMicrophone2 } from "react-icons/tb";

import { SettingsContext } from "../context/settings";
import { SideProvider } from "../context/side";
import { ThreadContext } from "../context/thread";
import { groupFrames, useThread } from "../hooks/thread";
import { defined } from "../util/common";
import { oempty, pack, transpose } from "../util/object";
import { Button } from "./Button";
import { Categories } from "./Categories";
import { GeneralError } from "./Error";
import { Highlight, HighlightLeading, HighlightedText } from "./Highlighting";
import { CenterLoading } from "./Loading";
import { Minimap } from "./Minimap";
import { ClusterSelect, LabelMeta } from "./Misc";
import { Modal, ModalTitle, useModal } from "./Modal";
import { ScatterChart } from "./ScatterChart";
import { HeadingMedium, HeadingSemiBig } from "./Text";
import { QuestionTooltip } from "./Tooltip";

const emptyComment = "[deleted]";

function Comment({ isSubmitter, name, text, comments, result }) {
  return (
    <div className="flex">
      <div className="flex py-1 pr-4">
        <div className="bg-gray-500 px-[1px]" />
      </div>
      <div className="flex min-w-0 flex-col gap-2">
        <div>
          {isSubmitter && (
            <TbMicrophone2
              title="original poster"
              size={18}
              className="ml-[2px] mr-[3px] mb-[3px] inline-block text-blue-500"
            />
          )}
          {text.length ? (
            <HighlightedText name={name} text={text} highlights={result} />
          ) : (
            <span>{emptyComment}</span>
          )}
        </div>
        <Comments comments={comments} result={result} />
      </div>
    </div>
  );
}

function Comments({ comments, result }) {
  if (!comments.length) return null;
  return (
    <div className="flex flex-col gap-4">
      {comments.map(({ isSubmitter, name, text, comments: subComments }) => (
        <Comment
          key={name}
          name={name}
          text={text}
          isSubmitter={isSubmitter}
          comments={subComments}
          result={result}
        />
      ))}
    </div>
  );
}

function ClusterList({ cluster }) {
  const { elements } = cluster;
  return (
    <HighlightLeading>
      <div className="flex flex-col divide-y">
        {elements.map((props) => (
          <div key={props.id} className="py-1">
            <Highlight {...props} />
          </div>
        ))}
      </div>
    </HighlightLeading>
  );
}

function LabelModal2({
  setCurrentLabelIndex,
  setCurrentCluster,
  groupedFrames,
  labels,
  labelKeys,
  clusters,
  meta,
}) {
  const [isOpen, openModal, closeModal] = useModal();
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
            setCurrentCluster={(cluster) => {
              closeModal();
              const labelIndex = labelKeys.indexOf(labelModel);
              setCurrentLabelIndex(labelIndex);
              setCurrentCluster(cluster);
            }}
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
    <div className="flex">
      <Button onClick={openModal} appearance="box" variant="success" small>
        View Summaries
      </Button>
      {isOpen && (
        <Modal isOpen={isOpen} close={closeModal}>
          <div className="flex w-full flex-col overflow-hidden">
            <div className="z-20 flex flex-wrap items-center justify-between gap-4 border-b bg-slate-100 p-5">
              <ModalTitle>Summaries</ModalTitle>
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
            <div
              className={`columns-1 gap-4 space-y-4 overflow-y-auto p-2 ${
                summaries.length > 1 ? "lg:columns-2" : ""
              }`}
            >
              {summaries}
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}

function ModelDisplay({ models, labelIndex, setLabelIndex }) {
  switch (models.length) {
    case 0:
      return <span className="font-bold text-slate-900">no model</span>;
    case 1:
      return <span className="font-bold text-slate-900">{models[0]}</span>;
    default:
      return (
        <div className="w-full">
          <Categories
            index={labelIndex}
            onChange={setLabelIndex}
            categories={models}
            notNullable
          />
        </div>
      );
  }
}

class ListManager {
  constructor(object) {
    if (Array.isArray(object)) {
      this.object = object ? Object.fromEntries(object) : null;
      this.keys = object ? object.map(([key]) => key) : [];
    } else {
      this.object = object || null;
      this.keys = object ? Object.keys(object) : [];
    }
  }

  toState({ index, key }) {
    if (defined(key)) {
      index = this.keys.indexOf(key);
    } else {
      key = this.keys[index];
    }
    if (key === undefined || index === -1) {
      if (this.keys.length) {
        index = 0;
        key = this.keys[index];
      } else {
        index = -1;
        key = null;
      }
    }
    const value = index !== -1 ? this.object[key] : null;
    return {
      index,
      key,
      value,
      manager: this,
    };
  }
}

function _getFrameManager(labelModel, frames, meta) {
  const frameMeta = meta?.frames || {};
  const transposed = transpose(frameMeta);
  return new ListManager(
    pack("frames", frames[labelModel], { meta: transposed?.[labelModel] || {} })
  );
}

function useLabels({
  meta,
  clusters,
  labels,
  groupedFrames,
  initialLabelModel,
  initialFrameModel,
  initialCluster,
}) {
  const [clusterManager] = useState(() => new ListManager(clusters));
  const [labelManager] = useState(
    () => new ListManager(pack("labels", labels, { meta: meta?.labels || {} }))
  );
  const getFrameManager = (labelModel) =>
    _getFrameManager(labelModel, groupedFrames, meta);
  const [labelState, updateLabelState] = useReducer(
    (state, action) => {
      switch (action.type) {
        case "SET_CLUSTER_INDEX":
          return {
            ...state,
            cluster: clusterManager.toState(action),
          };
        case "SET_LABEL_MODEL": {
          const labelModel = labelManager.toState(action);
          const frameModel = getFrameManager(labelModel.key).toState({
            index: 0,
          });
          return {
            ...state,
            labelModel,
            frameModel,
          };
        }
        case "SET_FRAME_MODEL": {
          const frameModel = state.frameModel.manager.toState(action);
          return {
            ...state,
            frameModel,
          };
        }
        default:
          throw Error(`unknown action ${action.type}`);
      }
    },
    null,
    () => {
      const labelModel = labelManager.toState({ key: initialLabelModel });
      const frameModel = getFrameManager(labelModel.key).toState({
        key: initialFrameModel,
      });
      return {
        cluster: clusterManager.toState({ key: initialCluster }),
        labelModel,
        frameModel,
      };
    }
  );
  const setClusterIndex = (index) =>
    updateLabelState({ type: "SET_CLUSTER_INDEX", index });
  const setLabelModel = (index) =>
    updateLabelState({ type: "SET_LABEL_MODEL", index });
  const setFrameModel = (index) =>
    updateLabelState({ type: "SET_FRAME_MODEL", index });
  return {
    labelState,
    setClusterIndex,
    setLabelModel,
    setFrameModel,
  };
}

function ClusterView({
  parentRef,
  clusters,
  initialLabelModel,
  initialFrameModel,
  initialCluster,
}) {
  const { thread, currentClusterRef, groupedFrames } =
    useContext(ThreadContext);
  const { labels, meta } = thread;
  const labelKeys = Object.keys(labels);
  const selectRef = useRef();
  const { labelState, setClusterIndex, setLabelModel, setFrameModel } =
    useLabels({
      meta,
      clusters,
      labels,
      groupedFrames,
      initialLabelModel,
      initialFrameModel,
      initialCluster,
    });
  currentClusterRef.current = {
    currentCluster: labelState.cluster.index,
    setCurrentCluster: setClusterIndex,
  };
  const { labelModel, frameModel } = labelState;
  const clusterOrder = groupFrames(
    labelState.frameModel.value?.frames,
    clusters
  );
  return (
    <>
      <div>
        <div className="flex flex-col gap-2 border-gray-500 p-1">
          <div className="flex flex-wrap items-center gap-y-1 gap-x-3 whitespace-nowrap">
            <span className="text-sm">Label Model</span>
            <div className="grow">
              <div className="flex items-center gap-1">
                <ModelDisplay
                  models={labelModel.manager.keys}
                  labelIndex={labelModel.index}
                  setLabelIndex={setLabelModel}
                />
                {labelModel?.value?.meta && (
                  <QuestionTooltip>
                    <LabelMeta meta={labelModel.value.meta} />
                  </QuestionTooltip>
                )}
              </div>
            </div>
          </div>
          {frameModel?.value?.frames && (
            <div className="flex flex-wrap items-center gap-y-1 gap-x-3 whitespace-nowrap">
              <span className="text-sm">Frame Model</span>
              <div className="grow">
                <div className="flex items-center gap-1">
                  <ModelDisplay
                    models={frameModel.manager.keys}
                    labelIndex={frameModel.index}
                    setLabelIndex={setFrameModel}
                  />
                  {frameModel?.value?.meta && (
                    <QuestionTooltip>
                      <LabelMeta meta={frameModel.value.meta} />
                    </QuestionTooltip>
                  )}
                </div>
              </div>
            </div>
          )}
          <div className="flex-between flex items-center justify-between">
            <h3 className="text-xl font-bold underline">Summary</h3>
            {Boolean(Object.keys(labels).length) && (
              <LabelModal2
                setCurrentLabelIndex={setLabelModel}
                setCurrentCluster={setClusterIndex}
                groupedFrames={groupedFrames}
                labels={labels}
                labelKeys={labelKeys}
                clusters={clusters}
                meta={thread.meta}
              />
            )}
          </div>
        </div>
        <div
          ref={selectRef}
          className="relative h-[20vh] min-h-[200px] overflow-y-scroll"
        >
          <ClusterSelect
            clusterOrder={clusterOrder}
            currentCluster={labelState.cluster.index}
            setCurrentCluster={setClusterIndex}
            currentLabel={labelModel.key}
            labels={labels}
            clusters={clusters}
            parentRef={selectRef}
          />
        </div>
      </div>
      <div className="flex flex-col overflow-hidden">
        <SideProvider side={1} canActivate parentRef={parentRef} light>
          <div
            key={labelState.cluster.index}
            ref={parentRef}
            className="relative overflow-y-auto p-1"
          >
            <div className="flex justify-center">
              <HeadingSemiBig>Cluster Arguments</HeadingSemiBig>
            </div>
            <ClusterList
              clusterId={labelState.cluster.index}
              cluster={labelState.cluster.value}
              currentLabel={labelState.labelModel.index}
              labels={labels}
            />
          </div>
        </SideProvider>
      </div>
    </>
  );
}

function ThreadResults({ labelModel, frameModel, cluster }) {
  const { clusters, points, minimap, thread } = useContext(ThreadContext);
  const { url, title, root, numComments, result } = thread;
  const { name, comments, text } = root;
  const { visualizeClusters, showMinimap } = useContext(SettingsContext);

  const leftRef = useRef();
  const rightRef = useRef();
  const minimapRef = useRef();

  const visibleMinimap = Boolean(showMinimap && minimap);
  const basis = visibleMinimap ? "w-[90%]" : "";

  return (
    <div
      className="flex overflow-hidden"
      style={{ overflowWrap: "break-word" }}
    >
      <div className="flex w-[30%] flex-col divide-y-2 divide-gray-500 border-r-2 border-gray-600">
        {clusters && (
          <ClusterView
            parentRef={rightRef}
            clusters={clusters}
            initialLabelModel={labelModel}
            initialFrameModel={frameModel}
            initialCluster={cluster}
          />
        )}
      </div>
      <div className="flex w-[70%]">
        <div className="flex overflow-hidden">
          {visibleMinimap && (
            <div ref={minimapRef} className="relative w-[10%] overflow-y-auto">
              <SideProvider side={2} parentRef={minimapRef}>
                <Minimap minimap={minimap} />
              </SideProvider>
            </div>
          )}
          <div className={`${basis} flex min-w-0 flex-col`}>
            <div
              ref={leftRef}
              className="relative overflow-y-auto px-[4%] pt-5 pb-10"
            >
              <SideProvider side={0} parentRef={leftRef}>
                <HighlightLeading>
                  <div className="border-2 border-black bg-slate-100 p-1">
                    <div className="flex justify-between gap-2 pb-2">
                      <HeadingSemiBig>{title}</HeadingSemiBig>
                      <a href={url} target="_blank" rel="noreferrer">
                        <FaReddit
                          className="rounded-full bg-white text-[#ff4500] hover:text-[#af4500]"
                          size={26}
                        />
                      </a>
                    </div>
                    <div>
                      <HighlightedText
                        text={text}
                        name={name}
                        highlights={result}
                      />
                    </div>
                  </div>
                  <div className="pt-2" />
                  <HeadingMedium>{numComments} comments</HeadingMedium>
                  <Comments comments={comments} result={result} />
                </HighlightLeading>
              </SideProvider>
            </div>
            {visualizeClusters && points && <ScatterChart points={points} />}
          </div>
        </div>
      </div>
    </div>
  );
}

function Thread({ thread, cluster, labelModel, frameModel }) {
  const computedValues = useThread(thread);
  const { computing, error } = computedValues;
  const { initialCluster } = computedValues;

  if (computing) {
    return <CenterLoading message="computing layout" />;
  }
  if (error) {
    return <GeneralError error={error} />;
  }
  return (
    <ThreadContext.Provider value={{ ...computedValues, thread }}>
      <ThreadResults
        labelModel={labelModel}
        frameModel={frameModel}
        cluster={defined(cluster) ? parseInt(cluster, 10) : initialCluster}
      />
    </ThreadContext.Provider>
  );
}

export { Thread };
