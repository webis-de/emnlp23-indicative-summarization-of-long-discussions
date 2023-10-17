import { MdDangerous, MdInfo, MdWarning } from "react-icons/md";

function HeadingSmall({ children, capitalize }) {
  return (
    <h4
      className={`text-bold ${
        capitalize ? "capitalize" : ""
      } text-sm font-semibold text-slate-600`}
    >
      {children}
    </h4>
  );
}

function HeadingMedium({ children, capitalize }) {
  return (
    <h3
      className={`text-bold ${
        capitalize ? "capitalize" : ""
      } font-semibold text-slate-600`}
    >
      {children}
    </h3>
  );
}

function HeadingSemiBig({ children, capitalize }) {
  return (
    <h2
      className={`text-xl ${
        capitalize ? "capitalize" : ""
      } font-semibold text-gray-900`}
    >
      {children}
    </h2>
  );
}

function HeadingBig({ children, capitalize }) {
  return (
    <h1
      className={`text-2xl ${
        capitalize ? "capitalize" : ""
      } font-semibold text-gray-900`}
    >
      {children}
    </h1>
  );
}

const typeToProps = {
  default: ["text-gray-500", null],
  info: ["text-blue-600", MdInfo],
  warning: ["text-yellow-600", MdWarning],
  danger: ["text-red-600", MdDangerous],
};

function Hint({ children, type = "default", noicon, small }) {
  const iconClass = small ? "w-[20px] h-[20px]" : "w-[25px] h-[25px]";
  const wrapperClass = small ? "block min-w-[20px]" : "block min-w-[25px]";
  const [textColor, Icon] = typeToProps[type];
  return (
    <div
      className={`flex items-start gap-2 ${
        small ? "text-sm" : "text-base"
      } ${textColor}`}
    >
      {!noicon && Icon && (
        <div className={wrapperClass}>
          <Icon className={iconClass} />
        </div>
      )}
      <div className="block tracking-tight">{children}</div>
    </div>
  );
}

export { HeadingSemiBig, HeadingBig, HeadingSmall, HeadingMedium, Hint };
