import * as d3 from "d3";
import React, { useContext, useEffect, useMemo, useState } from "react";

import { ThreadContext } from "../context/thread";

function Circle({
  id,
  x,
  y,
  fill,
  radius,
  highlightedStrokeWidth,
  highlighted = false,
  ...props
}) {
  return (
    <circle
      cx={x}
      cy={y}
      r={highlighted ? radius + 40 : radius}
      opacity={highlighted ? 1 : 0.75}
      stroke="#555555"
      strokeWidth={highlighted ? highlightedStrokeWidth : 1}
      fill={highlighted ? "#eeee00" : fill}
      {...props}
    />
  );
}

function CircleRegistered({ id, side = 3, ...props }) {
  const {
    registerElement,
    unregisterElement,
    isHighlighted,
    hover,
    unHover,
    scrollTo,
  } = useContext(ThreadContext);
  const [highlighted, setHighlighted] = useState(() => isHighlighted(id));

  useEffect(() => {
    if (id !== undefined) {
      registerElement(id, side, { setHighlighted });
      return () => unregisterElement(id, side);
    }
  }, [id, side, setHighlighted, registerElement, unregisterElement]);

  let enter;
  let leave;
  if (id !== undefined) {
    enter = () => hover(id);
    leave = () => unHover(id);
  } else {
    leave = () => setHighlighted(false);
    enter = () => setHighlighted(true);
  }
  const onMouseEnter = () => {
    enter();
  };
  const onMouseLeave = () => {
    leave();
  };

  return (
    <Circle
      highlighted={highlighted}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      onClick={() => scrollTo(id, side)}
      {...props}
    />
  );
}

function CirclePre({ labelId, ...props }) {
  if (labelId < 0) return <Circle {...props} />;
  return <CircleRegistered {...props} />;
}

function ScatterChart({
  points,
  width = 4000,
  height = 1000,
  radius = 20,
  highlightedStrokeWidth = 10,
}) {
  const scaledPoints = useMemo(() => {
    const pointsWithoutNoise = points.filter(({ labelId }) => labelId !== -2);
    const offset = radius + highlightedStrokeWidth;
    const xScale = d3
      .scaleLinear()
      .domain(d3.extent(pointsWithoutNoise, ({ x }) => x))
      .range([offset, width - offset]);

    const yScale = d3
      .scaleLinear()
      .domain(d3.extent(pointsWithoutNoise, ({ y }) => y))
      .range([offset, height - offset]);

    return pointsWithoutNoise
      .filter(({ cluster }) => cluster !== -2)
      .map(
        ({
          x,
          y,
          cluster: { trueValue },
          color: { bgNeutral, fill },
          ...rest
        }) => ({
          x: xScale(x),
          y: yScale(y),
          fill: trueValue < 0 ? bgNeutral : fill,
          ...rest,
        })
      );
  }, [points, width, height, radius, highlightedStrokeWidth]);

  return (
    <div className="border-t-2 border-gray-500">
      <div>
        <svg
          height="100%"
          width="100%"
          viewBox={`0 0 ${width} ${height}`}
          preserveAspectRatio="xMidYMid meet"
        >
          {scaledPoints.map(({ id, ...props }) => (
            <CirclePre
              key={id}
              id={id}
              radius={radius}
              highlightedStrokeWidth={highlightedStrokeWidth}
              {...props}
            />
          ))}
        </svg>
      </div>
    </div>
  );
}

export { ScatterChart };
