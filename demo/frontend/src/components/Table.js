function Table({ children }) {
  return (
    <table className="relative w-full divide-y divide-gray-200">
      {children}
    </table>
  );
}

function Thead({ children, sticky }) {
  return (
    <thead className={`${sticky ? "sticky top-0" : ""} w-full min-w-max`}>
      <tr className="bg-gray-200">{children}</tr>
    </thead>
  );
}

function Th({ children, loose, center }) {
  return (
    <th
      className={`${loose ? "p-1" : "py-3 px-6"} ${
        center ? "text-center" : "text-left"
      } whitespace-nowrap text-sm font-medium uppercase leading-normal tracking-wider text-gray-700`}
    >
      {children}
    </th>
  );
}

function Tbody({ children }) {
  return (
    <tbody className="divide-y divide-gray-200 bg-white">{children}</tbody>
  );
}

function Tr({ children, hover, striped, red, fullHeight }) {
  let className = "";

  if (red) className += " bg-red-200";
  else className += " bg-white";

  if (striped) className += " even:bg-gray-50";

  if (hover) className += " hover:bg-gray-100";

  if (fullHeight) className += " h-[1px]";

  return <tr className={className}>{children}</tr>;
}

function Td({
  children,
  nowrap,
  center,
  right,
  strong,
  loose,
  colSpan,
  fullHeight,
  className: extraClassName,
}) {
  let className = "text-sm font-medium";

  if (fullHeight) className += " h-[inherit]";

  if (center) className += " text-center";
  else if (right) className += " text-right";
  else className += " text-left";

  if (!loose) className += " py-4 px-6";

  if (nowrap) className += " whitespace-nowrap";

  if (strong) className += " text-gray-900";
  else className += " text-gray-500";

  if (extraClassName) className += ` ${extraClassName}`;

  return (
    <td colSpan={colSpan} className={className}>
      {children}
    </td>
  );
}

export { Table, Thead, Tbody, Th, Tr, Td };
