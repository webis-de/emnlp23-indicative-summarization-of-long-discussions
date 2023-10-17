import { useCallback } from "react";
import { FaReddit } from "react-icons/fa";
import { Link } from "react-router-dom";

import { useAsync } from "../hooks/async";
import {
  clusterToColor,
  extractClusters,
  extractIdsFromComments,
} from "../hooks/thread";
import { get } from "../request";
import { defined, setUrlParams } from "../util/common";
import { Button } from "./Button";
import { GeneralError, SuccessFalseError } from "./Error";
import { CenterLoading } from "./Loading";
import { LabelContent2 } from "./Misc";
import { Modal, useModal } from "./Modal";

function ClusterLabelView({ url, link }) {
  const getLabels = useCallback(async () => {
    const response = await get(url);
    if (response.success) {
      const { root, result } = response.data;
      const { name, comments } = root;
      const allSentences = Object.values(result).flat();
      allSentences.forEach((post, i) => {
        post.id = i;
      });
      await Promise.all(
        allSentences.map(async (post) => {
          const { trueValue } = post.cluster;
          post.labelId = trueValue;
          post.color = await clusterToColor(post.cluster);
        })
      );
      const orderedIds = [name, ...extractIdsFromComments(comments)];
      const [clusters] = await extractClusters(orderedIds, result);
      response.data.clusters = clusters;
    }
    return response;
  }, [url]);
  const { value, loading, error } = useAsync(getLabels);
  if (loading) {
    return <CenterLoading />;
  }
  if (error) {
    return <GeneralError error={error} />;
  }
  if (!value.success) {
    return <SuccessFalseError {...value} />;
  }
  return (
    <LabelContent2
      {...value.data}
      makeHref={(labelModel, frameModel, cluster) => {
        const params = { labelModel, cluster };
        if (frameModel) params.frameModel = frameModel;
        return setUrlParams(link, params);
      }}
    />
  );
}

function ShowLabels({ url, link, title }) {
  const [isOpen, openModal, closeModal] = useModal();
  return (
    <div className="flex">
      <Button onClick={openModal} appearance="fill" variant="success" small>
        View Summaries
      </Button>
      <Modal isOpen={isOpen} close={closeModal}>
        <div className="flex w-full flex-col overflow-hidden">
          <div className="border-b bg-slate-100 p-5 pb-3">
            <div className="flex items-center justify-between gap-4 pb-0">
              <span className="font-bold">{title}</span>
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
          </div>
          <ClusterLabelView url={url} link={link} />
        </div>
      </Modal>
    </div>
  );
}

const MODEL_COLOR_MAP = {
  "GPT3.5": "#6666c2",
  T0: "#aeaeae",
  "OPT-66B": "#aeaeae",
  "GPT-NeoX": "#aeaeae",
  BLOOM: "#aeaeae",
  OASST: "#6666c2",
  "LLaMA-65B": "#99c299",
  "LLaMA-30B": "#99c299",
  Pythia: "#6666c2",
  "Alpaca-7B": "#6666c2",
  "Baize-7B": "#99c299",
  "Baize-13B": "#99c299",
  "Falcon-40B": "#99c299",
  "Falcon-40B-Instruct": "#99c299",
  "LLaMA-30B-SuperCOT": "#6666c2",
  "Vicuna-13B": "#99c299",
  "Vicuna-7B": "#99c299",
  ChatGPT: "#6666c2",
  "GPT-4": "#6666c2",
};

function hexToRgb(hex) {
  const bigint = parseInt(hex.slice(1), 16);
  const r = (bigint >> 16) & 255;
  const g = (bigint >> 8) & 255;
  const b = bigint & 255;
  return [r, g, b];
}

function foregroundColor(hex, alpha = 1.0) {
  const [r, g, b] = hexToRgb(hex);
  return r * 0.299 + g * 0.587 + b * 0.114 + (1 - alpha) * 255 > 150
    ? "#000000"
    : "#ffffff";
}

function ListItem({ to, numComments, url, id, title, labels, labelsUrl }) {
  return (
    <div className="relative">
      <div className="rounded-lg border-2 border-slate-300 bg-slate-100 p-2">
        <div className="flex items-start justify-between gap-2 pb-2">
          <Link
            className="font-bold text-slate-800 hover:text-blue-500"
            key={id}
            to={to}
          >
            <div>{title}</div>
          </Link>
          <div className="flex items-center gap-2">
            {Boolean(labels.length) && defined(labelsUrl) && (
              <ShowLabels url={labelsUrl} link={to} title={title} />
            )}
            <a href={url} target="_blank" rel="noreferrer">
              <FaReddit
                className="rounded-full bg-white text-[#ff4500] hover:text-[#af4500]"
                size={26}
              />
            </a>
          </div>
        </div>
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <div className="py-1 text-sm font-bold text-blue-800">
              {numComments} comments
            </div>
          </div>
          {labels.length ? (
            <div className="flex flex-wrap gap-2">
              {labels.map((labelModel) => {
                const bgColor = MODEL_COLOR_MAP[labelModel] || "#ffffff";
                const fgColor = foregroundColor(bgColor);
                return (
                  <Link
                    className="rounded-full border-2 border-slate-600 px-2 pt-[1px] text-sm text-slate-800 hover:!bg-gray-400 hover:!text-black hover:outline"
                    key={labelModel}
                    style={{ backgroundColor: bgColor, color: fgColor }}
                    to={setUrlParams(to, { labelModel })}
                  >
                    {labelModel}
                  </Link>
                );
              })}
            </div>
          ) : (
            <div className="text-sm text-slate-600">no labels computed</div>
          )}
        </div>
      </div>
    </div>
  );
}

export { ListItem };
