import { useId } from "react";
import { FaQuestionCircle } from "react-icons/fa";
import { Tooltip as ReactTooltip } from "react-tooltip";
import "react-tooltip/dist/react-tooltip.css";

function Tooltip({ place = "left", tooltip, children, ...probs }) {
  const id = useId();
  return (
    <div className="inline-block">
      <div data-tooltip-id={id} data-tooltip-place={place}>
        {children}
      </div>
      <ReactTooltip
        id={id}
        {...probs}
        className="z-30 max-w-[700px] text-sm overflow-hidden whitespace-pre-wrap bg-[#363636] py-[4px] px-[10px] opacity-100"
        style={{ overflowWrap: "anywhere" }}
      >
        {tooltip}
      </ReactTooltip>
    </div>
  );
}

function QuestionTooltip({ children, soft, ...probs }) {
  let className = "text-blue-500 hover:text-blue-700";
  if (soft) className = "text-blue-300 hover:text-blue-500";
  return (
    <Tooltip {...probs} tooltip={children}>
      <FaQuestionCircle size={18} className={className} />
    </Tooltip>
  );
}

export { Tooltip, QuestionTooltip };
