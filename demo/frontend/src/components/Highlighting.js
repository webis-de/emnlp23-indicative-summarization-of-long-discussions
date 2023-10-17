import React, {
  Fragment,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";

import { SettingsContext } from "../context/settings";
import { SideContext } from "../context/side";
import { ThreadContext } from "../context/thread";

function useRegisteredHighlight(id) {
  const { side, canActivate, parentRef, light } = useContext(SideContext);
  const {
    registerElement,
    unregisterElement,
    isHighlighted,
    isActive,
    hover,
    unHover,
    scrollTo,
  } = useContext(ThreadContext);
  const [highlighted, setHighlighted] = useState(() => isHighlighted(id));
  const [active, setActive] = useState(() => isActive(id) || canActivate);
  const ref = useRef();

  const scroll = useCallback(() => {
    const parentHeight = parentRef.current.offsetHeight;
    const thisHeight = ref.current.offsetHeight;
    parentRef.current.scroll({
      top: ref.current.offsetTop - parentHeight / 2 + thisHeight / 2,
      left: 0,
    });
  }, [parentRef]);

  useEffect(() => {
    registerElement(id, side, {
      canActivate,
      setActive,
      setHighlighted,
      scroll,
    });
    return () => unregisterElement(id, side);
  }, [
    id,
    side,
    canActivate,
    setHighlighted,
    registerElement,
    scroll,
    unregisterElement,
  ]);

  return {
    highlighted,
    active,
    light,
    scroll,
    elementProps: {
      ref,
      onClick: () => scrollTo(id, side),
      onMouseEnter: () => hover(id),
      onMouseLeave: () => unHover(id),
    },
  };
}

function Highlight({ id, text, color }) {
  const { highlighted, active, scroll, elementProps, light } =
    useRegisteredHighlight(id);
  const { coloredText } = useContext(SettingsContext);
  let { fg } = color;
  const { bgText, bgLight } = color;
  let bg = bgText;
  // if (highlighted) [bg, fg] = ["#eeee00", "#000000"];
  if (!coloredText) {
    [bg, fg] = ["transparent", "#000000"];
  } else if (!active || light) [bg, fg] = [bgLight, "#000000"];

  useEffect(() => {
    if (highlighted) scroll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <span
      {...elementProps}
      className={`cursor-pointer p-[2px] ${
        highlighted ? "outline outline-2 outline-black" : ""
      }`}
      style={{ backgroundColor: bg, color: fg }}
    >
      {text}
    </span>
  );
}

function HighlightPre(props) {
  const {
    cluster: { trueValue },
    text,
  } = props;
  if (trueValue === -2)
    return <span className="text-slate-500 line-through">{text}</span>;
  if (trueValue < 0) return <span>{text}</span>;
  return <Highlight {...props} />;
}

function HighlightedText({ name, text, highlights }) {
  if (highlights)
    return highlights[name].map((props) => (
      <Fragment key={props.id}>
        <HighlightPre {...props} />{" "}
      </Fragment>
    ));
  return <span>{text.join(" ")}</span>;
}

function HighlightLeading({ children }) {
  return <div className="leading-[22px]">{children}</div>;
}

export { useRegisteredHighlight, Highlight, HighlightedText, HighlightLeading };
