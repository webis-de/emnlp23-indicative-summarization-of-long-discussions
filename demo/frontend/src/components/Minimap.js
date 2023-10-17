import { useRegisteredHighlight } from "./Highlighting";

function splitBar(offset, length, rowSize = 100) {
  const splits = [];
  let remaining = length;
  if (remaining <= 0) return splits;
  const first = Math.min(rowSize - (offset % rowSize), remaining);
  splits.push(first);
  remaining -= first;
  if (remaining <= 0) return splits;
  const numMiddle = Math.floor(remaining / rowSize);
  splits.push(...Array(numMiddle).fill(rowSize));
  remaining -= numMiddle * rowSize;
  if (remaining <= 0) return splits;
  splits.push(remaining);
  return splits;
}

function Bar({
  offset,
  length,
  className,
  backgroundColor = null,
  elementProps = {},
}) {
  const splits = splitBar(offset, length);
  return splits.map((size, i) => (
    <div
      key={i}
      {...elementProps}
      className={className}
      style={{ backgroundColor, width: `${size - 0.1}%` }}
    />
  ));
}

function BarRegistered({ id, color, ...props }) {
  const { highlighted, elementProps } = useRegisteredHighlight(id);
  const backgroundColor = highlighted ? "#eeee00" : color;
  return (
    <Bar
      {...props}
      className="h-[5px] cursor-pointer"
      backgroundColor={backgroundColor}
      elementProps={elementProps}
    />
  );
}

function BarPre({ labelId, ...props }) {
  if (labelId < 0) return <Bar {...props} />;
  return <BarRegistered {...props} />;
}

function Minimap({ minimap }) {
  return (
    <div className="flex flex-wrap">
      {minimap.map(({ id, ...props }) => (
        <BarPre key={id} id={id} {...props} />
      ))}
    </div>
  );
}

export { Minimap };
